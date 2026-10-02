package cn.iocoder.yudao.module.infra.controller.admin.wbrequests.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.*;
import java.util.*;
import org.springframework.format.annotation.DateTimeFormat;
import java.time.LocalDateTime;
import cn.idev.excel.annotation.*;

@Schema(description = "管理后台 - 服务请求管理 Response VO")
@Data
@ExcelIgnoreUnannotated
public class WbRequestsRespVO {

    @Schema(description = "id", requiredMode = Schema.RequiredMode.REQUIRED, example = "6061")
    @ExcelProperty("id")
    private Long id;

    @Schema(description = "create_time", requiredMode = Schema.RequiredMode.REQUIRED)
    @ExcelProperty("create_time")
    private LocalDateTime createTime;

    @Schema(description = "title", requiredMode = Schema.RequiredMode.REQUIRED)
    @ExcelProperty("title")
    private String title;

    @Schema(description = "detail", requiredMode = Schema.RequiredMode.REQUIRED)
    @ExcelProperty("detail")
    private String detail;

    @Schema(description = "customer_id", requiredMode = Schema.RequiredMode.REQUIRED, example = "30016")
    @ExcelProperty("customer_id")
    private Long customerId;

    @Schema(description = "assignee_id", example = "10985")
    @ExcelProperty("assignee_id")
    private Long assigneeId;

    @Schema(description = "request_state", requiredMode = Schema.RequiredMode.REQUIRED)
    @ExcelProperty("request_state")
    private String requestState;

    @Schema(description = "priority", requiredMode = Schema.RequiredMode.REQUIRED)
    @ExcelProperty("priority")
    private String priority;

    @Schema(description = "published_on")
    @ExcelProperty("published_on")
    private LocalDate publishedOn;

    @Schema(description = "resolved_at")
    @ExcelProperty("resolved_at")
    private LocalDateTime resolvedAt;

    @Schema(description = "due_at")
    @ExcelProperty("due_at")
    private LocalDateTime dueAt;

}