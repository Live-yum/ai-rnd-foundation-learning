package cn.iocoder.yudao.module.infra.business;

import cn.iocoder.yudao.framework.common.pojo.CommonResult;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;
import java.util.*;
import static cn.iocoder.yudao.framework.common.pojo.CommonResult.success;

/** Native Spring authentication is retained; the service performs per-action and row checks. */
@RestController
@RequestMapping("/infra/rnd-business")
public class RndBusinessController {
    @Resource private RndBusinessService business;
    @PostMapping("/bootstrap") public CommonResult<Boolean> bootstrap() { business.bootstrap(); return success(true); }
    @GetMapping("/meta") public CommonResult<Object> meta(@RequestParam String entity, @RequestParam(required=false) String id) { return success(business.meta(entity,id)); }
    @PostMapping("/action") public CommonResult<Object> action(@RequestBody Map<String,Object> data) { return success(business.action(data)); }
    @GetMapping("/history") public CommonResult<Object> history(@RequestParam String entity,@RequestParam String id,@RequestParam(defaultValue="false") boolean audit) { return success(business.history(entity,id,audit)); }
    @GetMapping("/metrics") public CommonResult<Object> metrics() { return success(business.metrics()); }
    @GetMapping("/notifications") public CommonResult<Object> notifications() { return success(business.notifications()); }
    @PostMapping("/notifications/read") public CommonResult<Boolean> read(@RequestBody Map<String,Object> data) { business.readNotification(data.get("id")); return success(true); }
    @GetMapping("/me") public CommonResult<Object> me() { return success(business.me()); }
    @GetMapping("/users") public CommonResult<Object> users() { return success(business.users()); }
    @PostMapping("/roles") public CommonResult<Boolean> roles(@RequestBody Map<String,Object> data) { business.changeRole(data); return success(true); }
    @GetMapping("/references") public CommonResult<Object> references(@RequestParam String entity) { return success(business.references(entity)); }
}
