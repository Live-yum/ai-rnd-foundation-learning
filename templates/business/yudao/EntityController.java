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
