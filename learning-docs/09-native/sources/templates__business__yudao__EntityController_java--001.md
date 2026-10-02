# templates/business/yudao/EntityController.java · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Yudao生成实体的受保护控制器。** 保留原生路由、VO与认证接线，将实体读写转交合同服务，避免旧生成CRUD旁路跳过角色、关系和事件规则。

**对应关系：** Vben生成API → 此Controller → RndBusinessService → 原生Mapper。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/business/yudao/EntityController.java`；**本文件共有 1 段**。本段覆盖源文件 L1–L21。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1548`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/yudao/EntityController.java", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "bcbdd70fc1e390d3203aef8871908fdb7ce3c57e8449ad6f54d1cb42f03d9eee"} -->
````java
// templates/business/yudao/EntityController.java
package cn.iocoder.yudao.module.infra.controller.admin.__SLUG__;

import cn.iocoder.yudao.framework.common.pojo.CommonResult;
import cn.iocoder.yudao.module.infra.business.RndBusinessService;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;
import java.util.*;
import static cn.iocoder.yudao.framework.common.pojo.CommonResult.success;

/** Façade over the actual Infra-generated DO and MyBatis Mapper; no unguarded CRUD route remains. */
@RestController
@RequestMapping("/infra/__KEBAB__")
public class __CLASS__Controller {
    @Resource private RndBusinessService business;
    @PostMapping("/create") public CommonResult<Object> create(@RequestBody Map<String,Object> data) { return success(business.create("__ENTITY__",data)); }
    @PutMapping("/update") public CommonResult<Boolean> update(@RequestBody Map<String,Object> data) { business.update("__ENTITY__",data); return success(true); }
    @DeleteMapping("/delete") public CommonResult<Boolean> delete(@RequestParam String id) { business.archive("__ENTITY__",id); return success(true); }
    @DeleteMapping("/delete-list") public CommonResult<Boolean> deleteList(@RequestParam List<String> ids) { business.archiveBatch("__ENTITY__",ids); return success(true); }
    @GetMapping("/get") public CommonResult<Object> get(@RequestParam String id) { return success(business.get("__ENTITY__",id)); }
    @GetMapping("/page") public CommonResult<Object> page(@RequestParam Map<String,String> query) { return success(business.page("__ENTITY__",query)); }
}
````
