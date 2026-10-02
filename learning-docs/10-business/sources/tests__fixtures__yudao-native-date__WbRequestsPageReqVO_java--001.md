# tests/fixtures/yudao-native-date/WbRequestsPageReqVO.java · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/yudao-native-date/WbRequestsPageReqVO.java`；**本文件共有 1 段**。本段覆盖源文件 L1–L47。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1391`。本段原文没有结尾换行；手工保存时去掉围栏前为展示添加的最后一个换行，自动还原器会根据SHA判定。

<!-- learning-source: {"path": "tests/fixtures/yudao-native-date/WbRequestsPageReqVO.java", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "67700525e7f96eb0dbd4cbda78f7d290453449f01e6f96a9875b266042c25966"} -->
````java
// tests/fixtures/yudao-native-date/WbRequestsPageReqVO.java
package cn.iocoder.yudao.module.infra.controller.admin.wbrequests.vo;

import lombok.*;
import java.util.*;
import io.swagger.v3.oas.annotations.media.Schema;
import cn.iocoder.yudao.framework.common.pojo.PageParam;
import org.springframework.format.annotation.DateTimeFormat;
import java.time.LocalDateTime;

import static cn.iocoder.yudao.framework.common.util.date.DateUtils.FORMAT_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND;

@Schema(description = "管理后台 - 服务请求管理分页 Request VO")
@Data
public class WbRequestsPageReqVO extends PageParam {

    @Schema(description = "create_time")
    @DateTimeFormat(pattern = FORMAT_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND)
    private LocalDateTime[] createTime;

    @Schema(description = "title")
    private String title;

    @Schema(description = "detail")
    private String detail;

    @Schema(description = "customer_id", example = "30016")
    private Long customerId;

    @Schema(description = "assignee_id", example = "10985")
    private Long assigneeId;

    @Schema(description = "request_state")
    private String requestState;

    @Schema(description = "priority")
    private String priority;

    @Schema(description = "published_on")
    private LocalDate publishedOn;

    @Schema(description = "resolved_at")
    private LocalDateTime resolvedAt;

    @Schema(description = "due_at")
    private LocalDateTime dueAt;

}
````
