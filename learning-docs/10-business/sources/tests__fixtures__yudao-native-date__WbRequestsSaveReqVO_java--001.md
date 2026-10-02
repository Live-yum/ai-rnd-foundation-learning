# tests/fixtures/yudao-native-date/WbRequestsSaveReqVO.java · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/yudao-native-date/WbRequestsSaveReqVO.java`；**本文件共有 1 段**。本段覆盖源文件 L1–L49。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1683`。本段原文没有结尾换行；手工保存时去掉围栏前为展示添加的最后一个换行，自动还原器会根据SHA判定。

<!-- learning-source: {"path": "tests/fixtures/yudao-native-date/WbRequestsSaveReqVO.java", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b32d0892cbe6a7c1b1794ec277cd0f50939054db7dda3576a8198e1c2862bdc0"} -->
````java
// tests/fixtures/yudao-native-date/WbRequestsSaveReqVO.java
package cn.iocoder.yudao.module.infra.controller.admin.wbrequests.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.*;
import java.util.*;
import jakarta.validation.constraints.*;
import org.springframework.format.annotation.DateTimeFormat;
import java.time.LocalDateTime;

@Schema(description = "管理后台 - 服务请求管理新增/修改 Request VO")
@Data
public class WbRequestsSaveReqVO {

    @Schema(description = "id", requiredMode = Schema.RequiredMode.REQUIRED, example = "6061")
    private Long id;

    @Schema(description = "title", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotEmpty(message = "title不能为空")
    private String title;

    @Schema(description = "detail", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotEmpty(message = "detail不能为空")
    private String detail;

    @Schema(description = "customer_id", requiredMode = Schema.RequiredMode.REQUIRED, example = "30016")
    @NotNull(message = "customer_id不能为空")
    private Long customerId;

    @Schema(description = "assignee_id", example = "10985")
    private Long assigneeId;

    @Schema(description = "request_state", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotEmpty(message = "request_state不能为空")
    private String requestState;

    @Schema(description = "priority", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotEmpty(message = "priority不能为空")
    private String priority;

    @Schema(description = "published_on")
    private LocalDate publishedOn;

    @Schema(description = "resolved_at")
    private LocalDateTime resolvedAt;

    @Schema(description = "due_at")
    private LocalDateTime dueAt;

}
````
