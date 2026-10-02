# tests/fixtures/yudao-native-date/WbRequestsDO.java · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/yudao-native-date/WbRequestsDO.java`；**本文件共有 1 段**。本段覆盖源文件 L1–L70。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1404`。本段原文没有结尾换行；手工保存时去掉围栏前为展示添加的最后一个换行，自动还原器会根据SHA判定。

<!-- learning-source: {"path": "tests/fixtures/yudao-native-date/WbRequestsDO.java", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "135b456126ac65b24c9a914cbf84323f42afc0797ea0671c8182b5e17ac81a5e"} -->
````java
// tests/fixtures/yudao-native-date/WbRequestsDO.java
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
````
