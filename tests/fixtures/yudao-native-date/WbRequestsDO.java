package cn.iocoder.yudao.module.infra.dal.dataobject.wbrequests;

import lombok.*;
import java.util.*;
import java.time.LocalDateTime;
import java.time.LocalDateTime;
import java.time.LocalDateTime;
import java.time.LocalDateTime;
import com.baomidou.mybatisplus.annotation.*;
import cn.iocoder.yudao.framework.mybatis.core.dataobject.BaseDO;

/**
 * 服务请求管理 DO
 *
 * @author Workbench
 */
@TableName("wb_e9ad81c0_requests")
@KeySequence("wb_e9ad81c0_requests_seq") // 用于 Oracle、PostgreSQL、Kingbase、DB2、H2 数据库的主键自增。如果是 MySQL 等数据库，可不写。
@Data
@EqualsAndHashCode(callSuper = true)
@ToString(callSuper = true)
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WbRequestsDO extends BaseDO {

    /**
     * id
     */
    @TableId
    private Long id;
    /**
     * title
     */
    private String title;
    /**
     * detail
     */
    private String detail;
    /**
     * customer_id
     */
    private Long customerId;
    /**
     * assignee_id
     */
    private Long assigneeId;
    /**
     * request_state
     */
    private String requestState;
    /**
     * priority
     */
    private String priority;
    /**
     * published_on
     */
    private LocalDate publishedOn;
    /**
     * resolved_at
     */
    private LocalDateTime resolvedAt;
    /**
     * due_at
     */
    private LocalDateTime dueAt;


}