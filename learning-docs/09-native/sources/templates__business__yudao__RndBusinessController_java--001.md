# templates/business/yudao/RndBusinessController.java · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Yudao业务动作与管理路由。** 公开角色、关系、分配、命名转换、历史、通知和统计入口；身份来自原生登录，接口参数不能伪造操作者。

**对应关系：** Vben业务面板 → Controller → RndBusinessService事务。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/business/yudao/RndBusinessController.java`；**本文件共有 1 段**。本段覆盖源文件 L1–L28。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2349`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/yudao/RndBusinessController.java", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ddb5955250952cebf60bd767d67b11cb617edb3e4b4d6b89b8dda8492771f75c"} -->
````java
// templates/business/yudao/RndBusinessController.java
package cn.iocoder.yudao.module.infra.controller.admin.rndbusiness;

import cn.iocoder.yudao.module.infra.business.RndBusinessService;

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
    @GetMapping("/related") public CommonResult<Object> related(@RequestParam String entity,@RequestParam String id) { return success(business.related(entity,id)); }
    @GetMapping("/history") public CommonResult<Object> history(@RequestParam String entity,@RequestParam String id,@RequestParam(defaultValue="false") boolean audit) { return success(business.history(entity,id,audit)); }
    @GetMapping("/metrics") public CommonResult<Object> metrics() { return success(business.metrics()); }
    @GetMapping("/notifications") public CommonResult<Object> notifications() { return success(business.notifications()); }
    @PostMapping("/notifications/read") public CommonResult<Boolean> read(@RequestBody Map<String,Object> data) { business.readNotification(data.get("id")); return success(true); }
    @GetMapping("/me") public CommonResult<Object> me() { return success(business.me()); }
    @GetMapping("/users") public CommonResult<Object> users() { return success(business.users()); }
    @PostMapping("/roles") public CommonResult<Boolean> roles(@RequestBody Map<String,Object> data) { business.changeRole(data); return success(true); }
    @GetMapping("/references") public CommonResult<Object> references(@RequestParam String entity) { return success(business.references(entity)); }
}
````
