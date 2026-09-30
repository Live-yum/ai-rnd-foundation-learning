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