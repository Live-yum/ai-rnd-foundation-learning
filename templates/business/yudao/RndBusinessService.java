package cn.iocoder.yudao.module.infra.business;

import cn.iocoder.yudao.framework.security.core.util.SecurityFrameworkUtils;
import cn.iocoder.yudao.framework.tenant.core.context.TenantContextHolder;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.fasterxml.jackson.databind.*;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.Resource;
import org.springframework.beans.BeanWrapper;
import org.springframework.beans.BeanWrapperImpl;
import org.springframework.context.ApplicationContext;
import org.springframework.core.io.ClassPathResource;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.*;
import java.util.*;
import java.util.stream.Collectors;

/** Generic approved-contract runtime over the real Infra-generated MyBatis entities. */
@Service
@Transactional(rollbackFor = Exception.class)
public class RndBusinessService {
    @Resource private ObjectMapper json;
    @Resource private ApplicationContext context;
    @Resource private RndBusinessMapper sidecar;
    @Resource private jakarta.validation.Validator validator;
    @Resource private cn.iocoder.yudao.module.infra.service.config.ConfigService nativeConfiguration;
    private final Map<String, Class<?>> validators = new HashMap<>();
    private JsonNode cfg;
    private final Map<String, BaseMapper<Object>> mappers = new HashMap<>();
    private final Map<String, Class<?>> types = new HashMap<>();

    @PostConstruct
    @SuppressWarnings("unchecked")
    public void initialize() throws Exception {
        try (var stream = new ClassPathResource("rnd-business-contract.json").getInputStream()) {
            cfg = json.readTree(stream);
        }
        for (JsonNode binding : cfg.path("bindings")) {
            String entity = binding.path("entity").asText();
            Class<?> mapperType = Class.forName(binding.path("mapper").asText());
            mappers.put(entity, (BaseMapper<Object>) context.getBean(mapperType));
            types.put(entity, Class.forName(binding.path("dataObject").asText()));
            validators.put(entity, Class.forName(binding.path("requestVO").asText()));
        }
    }

    private Long actor() {
        Long user = SecurityFrameworkUtils.getLoginUserId();
        if (user == null) throw new AccessDeniedException("Native authentication required");
        return user;
    }
    private Long tenant() { return TenantContextHolder.getRequiredTenantId(); }
    private IllegalArgumentException bad(String detail) { return new IllegalArgumentException(detail); }
    private AccessDeniedException denied() { return new AccessDeniedException("Business permission denied"); }
    private String wire(String name) {
        StringBuilder result = new StringBuilder(); boolean upper = false;
        for (char c : name.toCharArray()) { if(c=='_') upper=true; else { result.append(upper?Character.toUpperCase(c):c); upper=false; } }
        return result.toString();
    }
    private JsonNode entity(String name) {
        for (JsonNode e : cfg.path("entities")) if(e.path("name").asText().equals(name)) return e;
        throw bad("Unknown business resource");
    }
    private JsonNode resource(String name) {
        entity(name);
        for (JsonNode e : cfg.path("business").path("resources")) if(e.path("entity").asText().equals(name)) return e;
        throw bad("Missing resource policy");
    }
    private JsonNode workflow(String name) {
        for (JsonNode w : cfg.path("business").path("workflows")) if(w.path("entity").asText().equals(name)) return w;
        return null;
    }
    private JsonNode relation(String name, String field) {
        for (JsonNode r : cfg.path("business").path("relations")) if(r.path("entity").asText().equals(name)&&r.path("field").asText().equals(field)) return r;
        return null;
    }
    private String roleCode(String role) {
        for(JsonNode r:cfg.path("business").path("roles")) if(r.path("name").asText().equals(role)) return cfg.path("rolePrefix").asText()+role;
        throw bad("Role not declared by this product");
    }
    private Set<String> rolesFor(Long user) {
        if(sidecar.setupReady(tenant(),cfg.path("specDigest").asText())!=1) throw new IllegalStateException("Business bootstrap not complete");
        Set<String> codes = new HashSet<>(sidecar.roles(tenant(),user));
        Set<String> result = new HashSet<>();
        for(JsonNode role:cfg.path("business").path("roles")) if(codes.contains(roleCode(role.path("name").asText()))) result.add(role.path("name").asText());
        if(result.size()>1) throw new AccessDeniedException("Ambiguous native business roles");
        return result;
    }
    private Set<String> roles() { return rolesFor(actor()); }
    private boolean contains(JsonNode array,String value) { for(JsonNode n:array) if(n.asText().equals(value)) return true; return false; }
    private Object value(Object row,String property) { return new BeanWrapperImpl(row).getPropertyValue(property); }
    private Long number(Object value) {
        if(value==null || !String.valueOf(value).matches("[1-9][0-9]{0,18}")) throw bad("Expected canonical positive identifier");
        try { return Long.valueOf(String.valueOf(value)); } catch(NumberFormatException e){ throw bad("Identifier out of range"); }
    }
    private Long id(Object row) { return number(value(row,"id")); }
    private BaseMapper<Object> mapper(String name) { entity(name); return mappers.get(name); }
    private boolean archived(Object row) { return value(row,"rndArchivedAt")!=null; }
    private Object load(String name,Object identifier,boolean lock) {
        var query = new QueryWrapper<Object>().eq("id",number(identifier));
        if(lock) query.last("FOR UPDATE");
        Object row=mapper(name).selectOne(query);
        if(row==null) throw bad("Business record not found");
        return row;
    }
    private List<Object> all(String name) {
        // Fail explicitly rather than publishing a silently truncated report.
        List<Object> rows=mapper(name).selectList(new QueryWrapper<Object>().orderByAsc("id").last("LIMIT 10001"));
        if(rows.size()>10000) throw bad("Business query exceeds the explicit 10000-record execution budget");
        return rows;
    }
    private boolean allowed(String name,Object row,String action) {
        Long user=actor(); Set<String> roleSet=rolesFor(user);
        for(JsonNode p:cfg.path("business").path("permissions")) {
            if(!p.path("entity").asText().equals(name)||!roleSet.contains(p.path("role").asText())||!contains(p.path("actions"),action)) continue;
            String scope=p.path("scope").asText();
            if(scope.equals("all")) return true;
            if(row==null) { if(action.equals("create")&&scope.equals("own")) return true; continue; }
            if(scope.equals("own")&&String.valueOf(user).equals(String.valueOf(value(row,"creator")))) return true;
            String field=resource(name).path("assignee_field").asText("");
            if(scope.equals("assigned")&&!field.isEmpty()&&String.valueOf(user).equals(String.valueOf(value(row,wire(field))))) return true;
        }
        return false;
    }
    private boolean hasAction(String name,String action) {
        Set<String> roleSet=roles();
        for(JsonNode p:cfg.path("business").path("permissions")) if(p.path("entity").asText().equals(name)&&roleSet.contains(p.path("role").asText())&&contains(p.path("actions"),action)) return true;
        return false;
    }
    private boolean eligibleAssignee(String name,Long user) {
        Set<String> roleSet=rolesFor(user);
        for(JsonNode p:cfg.path("business").path("permissions")) {
            if(!p.path("entity").asText().equals(name)||!roleSet.contains(p.path("role").asText())||!contains(p.path("actions"),"read")) continue;
            String scope=p.path("scope").asText();
            if(scope.equals("all")||scope.equals("assigned")) return true;
        }
        return false;
    }
    private void require(String name,Object row,String action) { if(!allowed(name,row,action)) throw denied(); }
    private Instant instant(Object value) {
        if(value instanceof LocalDateTime t) return t.toInstant(ZoneOffset.UTC);
        if(value instanceof OffsetDateTime t) return t.toInstant();
        if(value instanceof java.util.Date t) return t.toInstant();
        return OffsetDateTime.parse(String.valueOf(value)).toInstant();
    }
    private Object external(Object value) {
        if(value instanceof LocalDateTime || value instanceof OffsetDateTime || value instanceof java.util.Date) return instant(value).toString();
        if(value instanceof LocalDate) return value.toString();
        return value;
    }
    private Map<String,Object> out(String name,Object row) {
        Map<String,Object> result=new LinkedHashMap<>(); result.put("id",String.valueOf(id(row)));
        for(JsonNode f:entity(name).path("fields")) {
            String field=f.path("name").asText(); Object v=value(row,wire(field));
            result.put(wire(field),v==null?null:relation(name,field)!=null?String.valueOf(v):f.path("kind").asText().equals("date")?(v instanceof LocalDate?v.toString():instant(v).atOffset(ZoneOffset.UTC).toLocalDate().toString()):external(v));
        }
        result.put("createdBy",String.valueOf(value(row,"creator")));
        result.put("createdAt",external(value(row,"createTime")));
        result.put("updatedAt",external(value(row,"updateTime")));
        result.put("archivedAt",external(value(row,"rndArchivedAt")));
        return result;
    }
    /** Request-local caches: presentation never changes audit/metric wire values or recursively expands rows. */
    private static class Presentation {
        final Map<String,String> users=new HashMap<>();
        final Map<String,String> references=new HashMap<>();
    }
    private String recordLabel(String name,Object row) {
        for(JsonNode field:entity(name).path("fields")) {
            String key=field.path("name").asText();
            if(field.path("kind").asText().equals("text")&&relation(name,key)==null) {
                Object title=value(row,wire(key));
                if(title!=null&&!title.toString().isBlank()) return title.toString();
            }
        }
        return entity(name).path("description").asText(name)+" #"+id(row);
    }
    private String userLabel(Object identifier,Presentation display) {
        if(identifier==null||!identifier.toString().matches("[1-9][0-9]{0,18}")) return "—";
        String key=identifier.toString();
        return display.users.computeIfAbsent(key,ignored->{
            // Callers only supply creators, assignees, or actors of already authorized records/history.
            if(rolesFor(number(key)).isEmpty()) return "用户 #"+key;
            Map<String,Object> user=sidecar.displayUser(tenant(),number(key));
            if(user==null) return "用户 #"+key;
            for(String property:List.of("nickname","username")) {
                Object label=user.get(property);if(label!=null&&!label.toString().isBlank()) return label.toString();
            }
            return "用户 #"+key;
        });
    }
    private String referenceLabel(String target,Object identifier,Presentation display) {
        if(identifier==null) return "—";
        if(target.equals("$users")) return userLabel(identifier,display);
        String key=target+":"+identifier;
        return display.references.computeIfAbsent(key,ignored->{
            Object linked=mapper(target).selectById(number(identifier));
            if(linked==null||!allowed(target,linked,"read")) return "关联记录 #"+identifier;
            return recordLabel(target,linked);
        });
    }
    private Map<String,Object> present(String name,Object row,Presentation display) {
        Map<String,Object> result=out(name,row);Map<String,String> labels=new LinkedHashMap<>();
        for(JsonNode field:entity(name).path("fields")) {
            String key=field.path("name").asText();JsonNode reference=relation(name,key);
            if(reference!=null) labels.put(wire(key),referenceLabel(reference.path("target_entity").asText(),value(row,wire(key)),display));
        }
        labels.put("createdBy",userLabel(value(row,"creator"),display));
        result.put("_display",labels);result.put("_recordLabel",recordLabel(name,row));return result;
    }
    private Object metricValue(String name,Object row,String field) {
        return switch(field) {
            case "created_by" -> String.valueOf(value(row,"creator"));
            case "created_at" -> external(value(row,"createTime"));
            case "updated_at" -> external(value(row,"updateTime"));
            case "archived_at" -> external(value(row,"rndArchivedAt"));
            case "id" -> String.valueOf(id(row));
            default -> out(name,row).get(wire(field));
        };
    }
    private Set<String> controlled(String name) {
        Set<String> result=new HashSet<>(); JsonNode w=workflow(name);
        if(w!=null) { result.add(w.path("status_field").asText()); for(JsonNode t:w.path("transitions")) if(!t.path("set_timestamp").isNull()) result.add(t.path("set_timestamp").asText()); }
        String assignee=resource(name).path("assignee_field").asText(""); if(!assignee.isEmpty()) result.add(assignee);
        result.remove(""); return result;
    }
    private void set(Object row,String field,Object incoming) {
        BeanWrapper bean=new BeanWrapperImpl(row); Class<?> type=bean.getPropertyType(field);
        Object v=incoming;
        if(v!=null) {
            if(type==Long.class||type==long.class) v=Long.valueOf(v.toString());
            else if(type==Integer.class||type==int.class) v=Integer.valueOf(v.toString());
            else if(type==LocalDateTime.class) v=v instanceof String && v.toString().length()==10?LocalDate.parse(v.toString()).atStartOfDay():instant(v).atOffset(ZoneOffset.UTC).toLocalDateTime();
            else if(type==LocalDate.class) v=LocalDate.parse(v.toString());
            else if(type==String.class) v=v.toString();
        }
        bean.setPropertyValue(field,v);
    }
    private Object validate(String name,JsonNode field,Object incoming) {
        String key=field.path("name").asText();
        if(incoming==null||"".equals(incoming)) { if(field.path("required").asBoolean()) throw bad("Required field: "+key); return null; }
        JsonNode relation=relation(name,key);
        if(relation!=null) {
            if(!(incoming instanceof String)) throw bad("Relation IDs must be wire strings");
            Long ref=number(incoming); String target=relation.path("target_entity").asText();
            if(target.equals("$users")) { if(sidecar.activeUser(tenant(),ref)==null||rolesFor(ref).isEmpty()) throw bad("Unknown active business user"); }
            else { Object linked=load(target,ref,true); if(archived(linked)) throw bad("Archived relation target"); require(target,linked,"read"); }
            return ref;
        }
        switch(field.path("kind").asText()) {
            case "text": case "enum":
                if(!(incoming instanceof String)) throw bad("Expected text: "+key);
                int length=((String)incoming).codePointCount(0,((String)incoming).length());
                if(length<field.path("min_length").asInt(0)||length>field.path("max_length").asInt(200)) throw bad("Text length: "+key);
                if(field.path("kind").asText().equals("enum")&&!contains(field.path("choices"),incoming.toString())) throw bad("Invalid enum: "+key);
                break;
            case "boolean": if(!(incoming instanceof Boolean)) throw bad("Expected boolean: "+key); break;
            case "integer": if(!(incoming instanceof Integer)&&!(incoming instanceof Long)) throw bad("Expected integer: "+key); if(((Number)incoming).longValue()<Integer.MIN_VALUE||((Number)incoming).longValue()>Integer.MAX_VALUE) throw bad("Integer out of range"); break;
            case "date": LocalDate.parse(String.valueOf(incoming)); break;
            case "datetime": instant(incoming); break;
            default: throw bad("Unsupported field type");
        }
        return incoming;
    }
    private void apply(String name,Object row,Map<String,Object> data,boolean create) {
        Set<String> known=new HashSet<>(); known.add("id"); Set<String> protectedFields=controlled(name); JsonNode w=workflow(name);
        for(JsonNode f:entity(name).path("fields")) {
            String field=f.path("name").asText(), property=wire(field); known.add(property);
            if(protectedFields.contains(field)) {
                Object expected=create?(w!=null&&w.path("status_field").asText().equals(field)?w.path("initial").asText():null):external(value(row,property));
                if(data.containsKey(property)&&!Objects.equals(data.get(property),expected)&&!(data.get(property)!=null&&expected!=null&&data.get(property).toString().equals(expected.toString()))) throw denied();
                if(create) set(row,property,expected);
                continue;
            }
            if(create||data.containsKey(property)) set(row,property,validate(name,f,data.get(property)));
        }
        if(!known.containsAll(data.keySet())) throw bad("Unknown or server-owned field");
    }
    private void persist(String name,Object row) {
        var update=new UpdateWrapper<Object>().eq("id",id(row));
        for(JsonNode field:entity(name).path("fields")){String column=field.path("name").asText();update.set(column,value(row,wire(column)));}
        update.set("rnd_archived_at",value(row,"rndArchivedAt")).set("updater",actor().toString()).set("update_time",LocalDateTime.now(ZoneOffset.UTC));
        if(mapper(name).update(null,update)!=1) throw bad("Concurrent or missing business record");
    }
    private void validateNative(String name,Object row) {
        try {Object request=validators.get(name).getDeclaredConstructor().newInstance();org.springframework.beans.BeanUtils.copyProperties(row,request);if(!validator.validate(request).isEmpty()) throw bad("Native generated request validation failed");}
        catch(ReflectiveOperationException error){throw bad("Native request validator unavailable");}
    }
    private void active(Object row) { if(archived(row)) throw bad("Archived record is immutable"); }
    private String encode(Object value) { try { return json.writeValueAsString(value); } catch(Exception e){ throw bad("Cannot serialize business event"); } }
    private long event(String name,Object row,String action,Object before,String note) {
        Map<String,Object> e=new HashMap<>(); e.put("tenant",tenant());e.put("entity",name);e.put("record",id(row));e.put("actor",actor());e.put("action",action);e.put("before",encode(before));e.put("after",encode(out(name,row)));e.put("note",note);
        sidecar.event(e); return ((Number)e.get("id")).longValue();
    }
    private void notify(String name,Object row,String event,String transition,long audit) {
        for(JsonNode n:cfg.path("business").path("notifications")) {
            if(!n.path("entity").asText().equals(name)||!n.path("event").asText().equals(event)) continue;
            if(event.equals("transitioned")&&!n.path("transition").asText().equals(transition)) continue;
            Object recipient=n.path("recipient").asText().equals("creator")?value(row,"creator"):value(row,wire(resource(name).path("assignee_field").asText()));
            if(recipient!=null&&!recipient.toString().isEmpty()) notification(name,row,number(recipient),"event:"+audit,name+" #"+id(row)+" "+event);
        }
    }
    private void notification(String name,Object row,Long recipient,String eventKey,String message) {
        Map<String,Object> n=new HashMap<>();n.put("tenant",tenant());n.put("entity",name);n.put("record",id(row));n.put("recipient",recipient);n.put("eventKey",eventKey);n.put("message",message);sidecar.notification(n);
    }

    public Object create(String name,Map<String,Object> data) {
        actor(); if(data.containsKey("id")) throw bad("Server assigns identifiers"); require(name,null,"create");
        try {
            Object row=types.get(name).getDeclaredConstructor().newInstance(); apply(name,row,data,true);
            set(row,"creator",actor().toString());set(row,"updater",actor().toString());
            var now=LocalDateTime.now(ZoneOffset.UTC);set(row,"createTime",now);set(row,"updateTime",now);
            validateNative(name,row);mapper(name).insert(row); long audit=event(name,row,"created",null,"");notify(name,row,"created",null,audit);return String.valueOf(id(row));
        } catch(ReflectiveOperationException e){ throw bad("Native entity constructor unavailable"); }
    }
    public void update(String name,Map<String,Object> data) {
        Object row=load(name,data.get("id"),true); require(name,row,"update");active(row);Map<String,Object> before=out(name,row);apply(name,row,data,false);set(row,"updater",actor().toString());set(row,"updateTime",LocalDateTime.now(ZoneOffset.UTC));validateNative(name,row);persist(name,row);event(name,row,"updated",before,"");
    }
    public Object get(String name,String identifier) { Object row=load(name,identifier,false);require(name,row,"read");return present(name,row,new Presentation()); }
    public Object page(String name,Map<String,String> query) {
        if(!hasAction(name,"read")) throw denied();
        int page=Math.max(1,Integer.parseInt(query.getOrDefault("pageNo","1"))),size=Integer.parseInt(query.getOrDefault("pageSize","20"));
        if(size<1||size>100) throw bad("Page size outside 1..100");
        List<Object> rows=new ArrayList<>();
        for(Object row:all(name)) {
            if(!allowed(name,row,"read")||archived(row)!=Boolean.parseBoolean(query.getOrDefault("archived","false"))) continue;
            Map<String,Object> external=out(name,row);boolean matches=true;
            for(JsonNode f:entity(name).path("fields")) {
                String key=wire(f.path("name").asText());String expected=query.get(key);
                if(expected!=null&&!expected.isEmpty()&&!String.valueOf(external.get(key)).contains(expected)) matches=false;
            }
            if(matches) rows.add(row);
        }
        int start=Math.min(rows.size(),Math.multiplyExact(page-1,size)),end=Math.min(rows.size(),start+size);
        Presentation display=new Presentation();List<Map<String,Object>> visible=new ArrayList<>();
        for(Object row:rows.subList(start,end)) visible.add(present(name,row,display));
        return Map.of("list",visible,"total",rows.size());
    }
    public void archive(String name,String identifier) {
        Object row=load(name,identifier,true);require(name,row,"archive");active(row);
        for(JsonNode r:cfg.path("business").path("relations")) if(r.path("target_entity").asText().equals(name)) for(Object child:all(r.path("entity").asText())) if(!archived(child)&&String.valueOf(id(row)).equals(String.valueOf(value(child,wire(r.path("field").asText()))))) throw bad("Referenced record cannot be archived while active links exist");
        Map<String,Object> before=out(name,row);set(row,"rndArchivedAt",LocalDateTime.now(ZoneOffset.UTC));persist(name,row);event(name,row,"archived",before,"");
    }
    public void archiveBatch(String name,List<String> ids) { if(ids.size()>100) throw bad("Batch too large");for(String id:ids) archive(name,id); }
    public Object action(Map<String,Object> data) {
        if(!Set.of("entity","id","action","transition","assigneeId","note").containsAll(data.keySet())) throw bad("Unknown action field");
        String name=String.valueOf(data.get("entity")),action=String.valueOf(data.get("action"));Object row=load(name,data.get("id"),true);active(row);require(name,row,action);Map<String,Object> before=out(name,row);String transition=null;
        String note=data.get("note")==null?"":String.valueOf(data.get("note"));if(note.length()>4000) throw bad("Note too long");
        if(action.equals("assign")) {
            String field=resource(name).path("assignee_field").asText("");if(field.isEmpty()) throw bad("No assignee field");Object recipient=data.get("assigneeId");
            if(recipient!=null&&!recipient.toString().isEmpty()) {Long user=number(recipient);if(sidecar.activeUser(tenant(),user)==null) throw bad("Unknown active business assignee");if(!eligibleAssignee(name,user)) throw bad("Assignee cannot handle this resource");set(row,wire(field),user);} else set(row,wire(field),null);
        } else if(action.equals("transition")) {
            JsonNode w=workflow(name);if(w==null) throw bad("No workflow");transition=String.valueOf(data.get("transition"));JsonNode selected=null;
            for(JsonNode t:w.path("transitions")) if(t.path("name").asText().equals(transition)) selected=t;
            if(selected==null||!contains(selected.path("from_states"),String.valueOf(value(row,wire(w.path("status_field").asText()))))) throw bad("Invalid state transition");
            Set<String> actorRoles=roles();boolean valid=false;for(JsonNode r:selected.path("roles")) if(actorRoles.contains(r.asText())) valid=true;if(!valid) throw denied();
            set(row,wire(w.path("status_field").asText()),selected.path("to_state").asText());
            if(!selected.path("set_timestamp").isNull()&&!selected.path("set_timestamp").isMissingNode()) set(row,wire(selected.path("set_timestamp").asText()),LocalDateTime.now(ZoneOffset.UTC));
        } else if(action.equals("add_note")) {if(!resource(name).path("notes").asBoolean()||note.isBlank()) throw bad("A nonempty note is required");}
        else throw bad("Unknown named action");
        set(row,"updater",actor().toString());set(row,"updateTime",LocalDateTime.now(ZoneOffset.UTC));validateNative(name,row);persist(name,row);
        long audit=event(name,row,action,before,note);String notificationEvent=switch(action){case "assign"->"assigned";case "transition"->"transitioned";case "add_note"->"note_added";default->throw bad("Unknown named action");};notify(name,row,notificationEvent,transition,audit);return out(name,row);
    }
    public Object related(String name,String identifier) {
        Object parent=load(name,identifier,false);require(name,parent,"read");
        List<Map<String,Object>> groups=new ArrayList<>();Presentation display=new Presentation();
        for(JsonNode relation:cfg.path("business").path("relations")) {
            if(!relation.path("target_entity").asText().equals(name)) continue;
            String child=relation.path("entity").asText(),field=relation.path("field").asText();
            if(!hasAction(child,"read")) continue;
            List<Object> candidates=mapper(child).selectList(new QueryWrapper<Object>().eq(field,id(parent)).orderByDesc("id").last("LIMIT 10001"));
            if(candidates.size()>10000) throw bad("Related history exceeds explicit 10000-record execution budget");
            List<Map<String,Object>> records=new ArrayList<>();
            for(Object row:candidates) {
                if(!allowed(child,row,"read")) continue;
                records.add(Map.of("record",present(child,row,display),"actions",allowed(child,row,"read_history")?List.of("read_history"):List.of()));
            }
            List<String> columns=new ArrayList<>();boolean title=false;
            for(JsonNode f:entity(child).path("fields")) {
                String key=f.path("name").asText();
                if(f.path("kind").asText().equals("enum")||(!title&&f.path("kind").asText().equals("text")&&relation(child,key)==null)) {columns.add(key);if(f.path("kind").asText().equals("text")) title=true;}
            }
            groups.add(Map.of("entity",child,"label",entity(child).path("description").asText(),"field",field,"columns",columns,"records",records));
        }
        return Map.of("parent",Map.of("entity",name,"id",String.valueOf(id(parent))),"groups",groups);
    }
    public Object history(String name,String identifier,boolean audit) {
        Object row=load(name,identifier,false);require(name,row,audit?"read_audit":"read_history");
        List<Map<String,Object>> result=sidecar.history(tenant(),name,id(row));Presentation display=new Presentation();
        for(Map<String,Object> item:result) {item.put("actor_name",userLabel(item.get("actor_id"),display));item.put("created_at",external(item.get("created_at")));item.put("actor_id",String.valueOf(item.get("actor_id")));item.put("id",String.valueOf(item.get("id")));if(!audit){item.remove("before_data");item.remove("after_data");}}
        return result;
    }
    public void bootstrap() {
        Long user=actor();sidecar.lockProject(tenant());
        if(!sidecar.roles(tenant(),user).contains("super_admin")) throw denied();
        if(sidecar.setupCount(tenant())!=0) { if(sidecar.setupReady(tenant(),cfg.path("specDigest").asText())==1) return; throw bad("Business setup belongs to another plan"); }
        Map<String,String> functions=Map.of("read","query","read_history","query","read_audit","query","read_metrics","query","create","create","update","update","assign","update","transition","update","add_note","update","archive","delete");
        for(JsonNode declaration:cfg.path("business").path("roles")) {
            String roleName=declaration.path("name").asText(), code=roleCode(roleName);
            if(sidecar.role(tenant(),code)!=null) throw bad("Business role exists without owned setup marker");
            Map<String,Object> role=new HashMap<>();role.put("tenant",tenant());role.put("name",declaration.path("label").asText().substring(0,Math.min(30,declaration.path("label").asText().length())));role.put("code",code);role.put("marker","rnd-business:"+cfg.path("specDigest").asText());role.put("actor",user.toString());sidecar.createRole(role);
            Long roleId=sidecar.role(tenant(),code);Set<String> permissions=new HashSet<>();
            for(JsonNode grant:cfg.path("business").path("permissions")) if(grant.path("role").asText().equals(roleName)) {
                String prefix=null;for(JsonNode binding:cfg.path("bindings")) if(binding.path("entity").asText().equals(grant.path("entity").asText())) prefix=binding.path("permission").asText();
                if(prefix==null||prefix.isEmpty()) throw bad("Missing native permission binding");
                for(JsonNode action:grant.path("actions")) permissions.add(prefix+":"+functions.get(action.asText()));
            }
            Set<Long> menus=new HashSet<>();
            if(!permissions.isEmpty()) for(Map<String,Object> row:sidecar.permissionMenus(new ArrayList<>(permissions))) {
                Long next=number(row.get("id"));int depth=0;
                while(next!=null&&next>0&&depth++<10) {if(!menus.add(next)) break;Map<String,Object> menu=sidecar.menu(next);if(menu==null) throw bad("Native business menu missing");Object parent=menu.get("parent_id");next=parent==null?0L:Long.valueOf(parent.toString());}
                if(depth>=10) throw bad("Native menu cycle or depth exceeded");
            }
            for(Long menu:menus) sidecar.grantMenu(tenant(),roleId,menu,user.toString());
        }
        Long bootstrapRole=sidecar.role(tenant(),roleCode(cfg.path("business").path("bootstrap_role").asText()));sidecar.grant(tenant(),user,bootstrapRole,user.toString());
        sidecar.initialize(tenant(),cfg.path("specDigest").asText(),user);
        if(cfg.path("business").path("registration").path("enabled").asBoolean()) {
            var previous=nativeConfiguration.getConfigByKey("system.user.register-enabled");if(previous==null) throw bad("Native registration setting missing");
            var request=new cn.iocoder.yudao.module.infra.controller.admin.config.vo.ConfigSaveReqVO();org.springframework.beans.BeanUtils.copyProperties(previous,request);request.setKey(previous.getConfigKey());request.setValue("true");nativeConfiguration.updateConfig(request);
        }
    }
    public Object meta(String name,String identifier) {
        actor();if(sidecar.setupReady(tenant(),cfg.path("specDigest").asText())!=1) {if(!sidecar.roles(tenant(),actor()).contains("super_admin")) throw denied();return Map.of("bootstrapRequired",true,"actions",List.of(),"transitions",List.of(),"roles",cfg.path("business").path("roles"),"roleAdmin",false);}
        Object row=identifier==null?null:load(name,identifier,false);if(row!=null) require(name,row,"read");
        List<String> actions=new ArrayList<>();for(String action:List.of("create","read","update","archive","assign","transition","add_note","read_history","read_audit","read_metrics")) if(allowed(name,row,action)) actions.add(action);
        List<JsonNode> transitions=new ArrayList<>();JsonNode w=workflow(name);Set<String> rs=roles();
        if(row!=null&&w!=null&&actions.contains("transition")&&!archived(row)) for(JsonNode t:w.path("transitions")) if(contains(t.path("from_states"),String.valueOf(value(row,wire(w.path("status_field").asText()))))) for(JsonNode role:t.path("roles")) if(rs.contains(role.asText())) {transitions.add(t);break;}
        boolean admin=false;for(JsonNode r:cfg.path("business").path("role_admin_roles")) if(rs.contains(r.asText())) admin=true;
        Map<String,Object> result=new LinkedHashMap<>();result.put("actions",actions);result.put("transitions",transitions);result.put("roleAdmin",admin);result.put("roles",cfg.path("business").path("roles"));result.put("record",row==null?null:present(name,row,new Presentation()));result.put("fields",entity(name).path("fields"));return result;
    }
    public Object me() { return Map.of("id",actor().toString(),"roles",roles(),"initialized",true); }
    public Object users() {
        actor();if(roles().isEmpty()) throw denied();List<Map<String,Object>> result=new ArrayList<>();
        for(Map<String,Object> user:sidecar.users(tenant())) if(!rolesFor(number(user.get("id"))).isEmpty()) {user.put("id",user.get("id").toString());Object nickname=user.get("nickname");user.put("displayName",nickname!=null&&!nickname.toString().isBlank()?nickname:user.get("username"));List<String> eligibleEntities=new ArrayList<>();for(JsonNode r:cfg.path("business").path("resources")) {String name=r.path("entity").asText();if(!r.path("assignee_field").asText("").isEmpty()&&eligibleAssignee(name,number(user.get("id")))) eligibleEntities.add(name);}user.put("eligibleEntities",eligibleEntities);result.add(user);}return result;
    }
    public void changeRole(Map<String,Object> data) {
        actor();sidecar.lockProject(tenant());
        Set<String> current=roles();boolean admin=false;for(JsonNode role:cfg.path("business").path("role_admin_roles")) if(current.contains(role.asText())) admin=true;if(!admin) throw denied();
        if(!Set.of("userId","role","grant").containsAll(data.keySet())||!(data.get("grant") instanceof Boolean)) throw bad("Invalid role request");
        Long user=number(data.get("userId"));if(sidecar.activeUser(tenant(),user)==null) throw bad("Unknown user");String code=roleCode(String.valueOf(data.get("role")));Long role=sidecar.role(tenant(),code);if(role==null) throw bad("Owned business role is not installed");
        List<String> administratorCodes=new ArrayList<>();Set<String> administratorNames=new HashSet<>();
        for(JsonNode r:cfg.path("business").path("role_admin_roles")){administratorCodes.add(roleCode(r.asText()));administratorNames.add(r.asText());}
        Set<String> oldRoles=rolesFor(user);boolean oldAdmin=oldRoles.stream().anyMatch(administratorNames::contains);
        boolean newAdmin=Boolean.TRUE.equals(data.get("grant"))&&administratorNames.contains(String.valueOf(data.get("role")));
        if(oldAdmin&&!newAdmin&&sidecar.administratorCount(tenant(),administratorCodes)<=1) throw denied();
        if(Boolean.TRUE.equals(data.get("grant"))) {
            for(JsonNode declared:cfg.path("business").path("roles")){Long prior=sidecar.role(tenant(),roleCode(declared.path("name").asText()));if(prior!=null&&!prior.equals(role)) sidecar.revoke(tenant(),user,prior,actor().toString());}
            sidecar.grant(tenant(),user,role,actor().toString());
        } else sidecar.revoke(tenant(),user,role,actor().toString());
        Map<String,Object> e=new HashMap<>();e.put("tenant",tenant());e.put("entity","_roles");e.put("record",user);e.put("actor",actor());e.put("action",Boolean.TRUE.equals(data.get("grant"))?"role_granted":"role_revoked");e.put("before","{}");e.put("after",encode(Map.of("role",data.get("role"))));e.put("note","");sidecar.event(e);
    }
    public void registered(Long user) {
        sidecar.lockProject(tenant());if(sidecar.setupReady(tenant(),cfg.path("specDigest").asText())!=1) throw bad("Business bootstrap must complete before registration");
        if(!cfg.path("business").path("registration").path("enabled").asBoolean()) throw denied();
        Long role=sidecar.role(tenant(),roleCode(cfg.path("business").path("registration").path("default_role").asText()));if(role==null) throw bad("Default business role not installed");sidecar.grant(tenant(),user,role,"registration");
    }
    public Object references(String name) {
        if(!hasAction(name,"read")) throw denied();List<Map<String,Object>> result=new ArrayList<>();Presentation display=new Presentation();for(Object row:all(name)) if(!archived(row)&&allowed(name,row,"read")) result.add(present(name,row,display));return result;
    }
    private boolean predicate(String name,Object row,JsonNode predicate) {
        Object actual=metricValue(name,row,predicate.path("field").asText());Object expected=json.convertValue(predicate.path("value"),Object.class);String operation=predicate.path("op").asText("eq");
        boolean equal=Objects.equals(actual,expected)||(actual instanceof Number&&expected instanceof Number&&Double.compare(((Number)actual).doubleValue(),((Number)expected).doubleValue())==0);
        if(operation.equals("eq")) return equal;if(operation.equals("ne")) return !equal;
        if(operation.equals("in")) {for(JsonNode n:predicate.path("value")) if(Objects.equals(actual,json.convertValue(n,Object.class))) return true;return false;}
        if(actual==null||expected==null) return false;
        int compare=actual instanceof Number&&expected instanceof Number?Double.compare(((Number)actual).doubleValue(),((Number)expected).doubleValue()):String.valueOf(actual).compareTo(String.valueOf(expected));return operation.equals("gte")?compare>=0:compare<=0;
    }
    public Object metrics() {
        actor();List<Map<String,Object>> result=new ArrayList<>();
        for(JsonNode m:cfg.path("business").path("metrics")) {
            String name=m.path("entity").asText();if(!hasAction(name,"read_metrics")) continue;
            List<Object> rows=all(name).stream().filter(r->!archived(r)&&allowed(name,r,"read_metrics")).filter(r->{for(JsonNode p:m.path("filters")) if(!predicate(name,r,p)) return false;return true;}).collect(Collectors.toList());
            Map<String,Object> item=new LinkedHashMap<>();item.put("name",m.path("name").asText());item.put("label",m.path("label").asText());item.put("kind",m.path("kind").asText());
            String kind=m.path("kind").asText();
            if(kind.equals("count")) item.put("value",rows.size());
            else if(kind.equals("average_duration")) {double sum=0;int samples=0;for(Object row:rows) {Object start=metricValue(name,row,m.path("start_field").asText()),end=metricValue(name,row,m.path("end_field").asText());if(start!=null&&end!=null) {double seconds=Duration.between(instant(start),instant(end)).toMillis()/1000.0;if(seconds<0) throw bad("Invalid duration interval");sum+=seconds;samples++;}}item.put("value",samples==0?null:sum/samples);item.put("samples",samples);item.put("unit","seconds");}
            else {Map<String,Long> counts=new TreeMap<>();for(Object row:rows) {Object v=metricValue(name,row,m.path(kind.equals("group_count")?"group_by":"time_field").asText());if(kind.equals("time_count")&&v==null) continue;String bucket=v==null?"(none)":kind.equals("time_count")?instant(v).atOffset(ZoneOffset.UTC).toLocalDate().toString():v.toString();counts.merge(bucket,1L,Long::sum);}item.put("buckets",counts);item.put("timezone","UTC");
                if(kind.equals("group_count")) {
                    Map<String,String> labels=new LinkedHashMap<>();Presentation display=new Presentation();String field=m.path("group_by").asText();JsonNode reference=relation(name,field);
                    for(String bucket:counts.keySet()) {
                        String label=bucket.equals("(none)")?"未设置":bucket;
                        if(!bucket.equals("(none)")&&reference!=null) label=referenceLabel(reference.path("target_entity").asText(),bucket,display);
                        else if(!bucket.equals("(none)")&&field.equals("created_by")) label=userLabel(bucket,display);
                        else for(JsonNode f:entity(name).path("fields")) if(f.path("name").asText().equals(field)) label=f.path("choice_labels").path(bucket).asText(label);
                        labels.put(bucket,label);
                    }
                    item.put("bucketLabels",labels);
                }
            }result.add(item);
        }
        return result;
    }
    public Object notifications() {
        Long user=actor();
        for(JsonNode n:cfg.path("business").path("notifications")) if(n.path("event").asText().equals("due")) {
            String name=n.path("entity").asText(),field=n.path("due_field").asText();
            for(Object row:all(name)) {if(archived(row)||!allowed(name,row,"read")) continue;Object recipient=n.path("recipient").asText().equals("creator")?value(row,"creator"):value(row,wire(resource(name).path("assignee_field").asText()));Object date=metricValue(name,row,field);
                if(recipient!=null&&recipient.toString().equals(user.toString())&&date!=null&&!instant(date).isAfter(Instant.now())) notification(name,row,user,"due:"+name+":"+id(row)+":"+field+":"+instant(date),name+" #"+id(row)+" due");}
        }
        List<Map<String,Object>> result=new ArrayList<>();for(Map<String,Object> n:sidecar.notifications(tenant(),user)) {try {Object row=load(n.get("entity").toString(),n.get("record_id"),false);if(allowed(n.get("entity").toString(),row,"read")) {n.put("created_at",external(n.get("created_at")));n.put("read_at",external(n.get("read_at")));n.put("record_id",String.valueOf(n.get("record_id")));String message=String.valueOf(n.get("message"));String event=message.substring(message.lastIndexOf(' ')+1);String action=switch(event){case "created"->"已创建";case "assigned"->"已分配负责人";case "transitioned"->"状态已更新";case "note_added"->"有新的备注";case "due"->"已到期，请及时处理";default->"有新的提醒";};n.put("display_message",entity(n.get("entity").toString()).path("description").asText()+"「"+recordLabel(n.get("entity").toString(),row)+"」"+action);result.add(n);}}catch(IllegalArgumentException ignored){}}
        return result;
    }
    public void readNotification(Object identifier) {if(sidecar.readNotification(tenant(),actor(),number(identifier))!=1) throw denied();}
}
