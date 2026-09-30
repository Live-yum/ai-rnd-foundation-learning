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