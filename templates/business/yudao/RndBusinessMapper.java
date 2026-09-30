package cn.iocoder.yudao.module.infra.business;

import com.baomidou.mybatisplus.annotation.InterceptorIgnore;
import org.apache.ibatis.annotations.*;
import java.util.*;

/** Sidecar data uses explicit native tenant identity, never caller supplied tenant IDs. */
@Mapper
@InterceptorIgnore(tenantLine = "true")
public interface RndBusinessMapper {
    @Select("SELECT COUNT(*) FROM __PREFIX___setup WHERE tenant_id=#{tenant}")
    Integer setupCount(@Param("tenant") Long tenant);

    @Insert("INSERT INTO __PREFIX___setup(tenant_id,spec_digest,bootstrap_user_id) VALUES(#{tenant},#{digest},#{user})")
    int initialize(@Param("tenant") Long tenant,@Param("digest") String digest,@Param("user") Long user);

    @Insert("INSERT INTO system_role(id,name,code,sort,data_scope,status,type,remark,tenant_id,creator,updater) VALUES(nextval('system_role_seq'),#{name},#{code},99,1,0,2,#{marker},#{tenant},#{actor},#{actor})")
    int createRole(Map<String,Object> role);

    @Select("<script>SELECT id,parent_id FROM system_menu WHERE deleted=0 AND status=0 AND permission IN <foreach collection='permissions' item='permission' open='(' separator=',' close=')'>#{permission}</foreach></script>")
    List<Map<String,Object>> permissionMenus(@Param("permissions") List<String> permissions);

    @Select("SELECT id,parent_id FROM system_menu WHERE id=#{id} AND deleted=0 AND status=0")
    Map<String,Object> menu(@Param("id") Long id);

    @Insert("INSERT INTO system_role_menu(id,role_id,menu_id,tenant_id,creator,updater) VALUES(nextval('system_role_menu_seq'),#{role},#{menu},#{tenant},#{actor},#{actor})")
    int grantMenu(@Param("tenant") Long tenant,@Param("role") Long role,@Param("menu") Long menu,@Param("actor") String actor);

    @Select("SELECT 1 FROM (SELECT pg_advisory_xact_lock(hashtextextended('__PREFIX__:' || CAST(#{tenant} AS text),0))) locked")
    Integer lockProject(@Param("tenant") Long tenant);

    @Select("SELECT COUNT(*) FROM __PREFIX___setup WHERE tenant_id=#{tenant} AND spec_digest=#{digest}")
    Integer setupReady(@Param("tenant") Long tenant, @Param("digest") String digest);

    @Select("<script>SELECT COUNT(DISTINCT u.user_id) FROM system_user_role u JOIN system_role r ON r.id=u.role_id AND r.tenant_id=u.tenant_id JOIN system_users a ON a.id=u.user_id AND a.tenant_id=u.tenant_id WHERE u.tenant_id=#{tenant} AND u.deleted=0 AND r.deleted=0 AND r.status=0 AND a.deleted=0 AND a.status=0 AND r.code IN <foreach collection='codes' item='code' open='(' separator=',' close=')'>#{code}</foreach></script>")
    Integer administratorCount(@Param("tenant") Long tenant, @Param("codes") List<String> codes);

    @Select("SELECT r.code FROM system_role r JOIN system_user_role u ON r.id=u.role_id AND r.tenant_id=u.tenant_id WHERE u.user_id=#{user} AND u.tenant_id=#{tenant} AND u.deleted=0 AND r.deleted=0 AND r.status=0")
    List<String> roles(@Param("tenant") Long tenant, @Param("user") Long user);

    @Select("SELECT id, nickname, username FROM system_users WHERE tenant_id=#{tenant} AND deleted=0 AND status=0 ORDER BY id")
    List<Map<String,Object>> users(@Param("tenant") Long tenant);

    @Select("SELECT id FROM system_role WHERE tenant_id=#{tenant} AND code=#{code} AND deleted=0 AND status=0")
    Long role(@Param("tenant") Long tenant, @Param("code") String code);

    @Select("SELECT id FROM system_users WHERE tenant_id=#{tenant} AND id=#{user} AND deleted=0 AND status=0 FOR UPDATE")
    Long activeUser(@Param("tenant") Long tenant, @Param("user") Long user);

    @Insert("INSERT INTO system_user_role(id,user_id,role_id,tenant_id,creator,updater) SELECT nextval('system_user_role_seq'),#{user},#{role},#{tenant},#{actor},#{actor} WHERE NOT EXISTS (SELECT 1 FROM system_user_role WHERE user_id=#{user} AND role_id=#{role} AND tenant_id=#{tenant} AND deleted=0)")
    int grant(@Param("tenant") Long tenant, @Param("user") Long user, @Param("role") Long role, @Param("actor") String actor);

    @Update("UPDATE system_user_role SET deleted=1,updater=#{actor},update_time=CURRENT_TIMESTAMP WHERE tenant_id=#{tenant} AND user_id=#{user} AND role_id=#{role} AND deleted=0")
    int revoke(@Param("tenant") Long tenant, @Param("user") Long user, @Param("role") Long role, @Param("actor") String actor);

    @Insert("INSERT INTO __PREFIX___audit(tenant_id,entity,record_id,actor_id,action,before_data,after_data,note) VALUES(#{tenant},#{entity},#{record},#{actor},#{action},#{before},#{after},#{note})")
    @Options(useGeneratedKeys=true, keyProperty="id", keyColumn="id")
    int event(Map<String,Object> event);

    @Select("SELECT id,actor_id,action,before_data,after_data,note,created_at FROM __PREFIX___audit WHERE tenant_id=#{tenant} AND entity=#{entity} AND record_id=#{record} ORDER BY id")
    List<Map<String,Object>> history(@Param("tenant") Long tenant, @Param("entity") String entity, @Param("record") Long record);

    @Insert("INSERT INTO __PREFIX___notifications(tenant_id,entity,record_id,recipient_id,event_key,message) VALUES(#{tenant},#{entity},#{record},#{recipient},#{eventKey},#{message}) ON CONFLICT(tenant_id,recipient_id,event_key) DO NOTHING")
    int notification(Map<String,Object> notification);

    @Select("SELECT id,entity,record_id,message,created_at,read_at FROM __PREFIX___notifications WHERE tenant_id=#{tenant} AND recipient_id=#{user} ORDER BY id DESC LIMIT 500")
    List<Map<String,Object>> notifications(@Param("tenant") Long tenant, @Param("user") Long user);

    @Update("UPDATE __PREFIX___notifications SET read_at=COALESCE(read_at,CURRENT_TIMESTAMP) WHERE tenant_id=#{tenant} AND recipient_id=#{user} AND id=#{id}")
    int readNotification(@Param("tenant") Long tenant, @Param("user") Long user, @Param("id") Long id);
}
