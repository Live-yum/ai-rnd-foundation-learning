# 模型连接与任务反馈：验证记录

本次修复针对真实连接测试、校验失败可排查信息、提交回答后仍保留历史澄清/模板提示。失败模型响应仍不得批准，历史问题不重新作为用户要求。

## 已完成的本地检查

- Python 3.14：133项针对模型设置、连接探测、流式诊断、历史恢复、报名澄清的测试通过。
- Vue：42项组件/状态/协议测试通过；类型检查与生产构建通过。
- Ruff lint与格式检查通过。
- 离线HTTP模型夹具验证失败后的持久Store：一条历史关卡、原始精确回答、两次有诊断的失败响应均保存。
- 真实Chromium脚本已扩展：同一报名运行恢复、历史问题/能力提示、错误阶段/代码/追踪ID及刷新后的重复性检查。当前本地OS拒绝Chromium的Unix socket，未将此项记为通过；Actions browser任务运行该脚本。
- 上述模型测试均为明确离线夹具，不冒充DeepSeek付费实测。付费探测另由手動任务输出经过脱敏的独立回执。

## 本地全量检查限制与基线对照

命令：pytest -m 'not postgres and not node_tools' -q（此轮暂未含两个教材同步测试文件，教材在源码定稿后另行验证）。结果：5083通过、119跳过、54取消选择、23失败；不是全绿。

同一环境从main提交0a735be42a2064028416c8c17e222652c96041f0导出无修改源码，逐项复跑上述23个失败node ID，23个全部同样失败。18个工作流失败的落盘tool-failure回执明确为BrowserPrerequisite：缺少固定Playwright/Chromium工具；5个直接浏览器测试同样在缺失模块/浏览器前置阶段失败，未执行到其预期断言。不能以基线同样失败替代最终提交的Actions必需验收。

逐项分类如下：

- `tests/test_customer_workflow.py::test_customer_smart_workflow_reaches_independent_delivery`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_delivery_clearance.py::test_explicit_review_gap_blocks_smart_delivery`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_description_facts.py::test_exact_original_legacy_blocked_run_recovers_without_losing_facts`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_guided_workflow.py::test_smart_from_any_gate_finishes_without_another_user_input[clarification]`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_guided_workflow.py::test_smart_from_any_gate_finishes_without_another_user_input[requirements]`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_guided_workflow.py::test_smart_from_any_gate_finishes_without_another_user_input[design]`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_guided_workflow.py::test_smart_from_any_gate_finishes_without_another_user_input[delivery]`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_guided_workflow.py::test_optional_review_model_does_not_replace_executable_tests`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_native_style_selectors.py::test_native_style_checks_ignore_hidden_header_button_and_id_field`：直接Node浏览器驱动：固定Playwright模块不可用（ToolFailure）；基线同样失败。
- `tests/test_news_delivery.py::test_reported_news_requirements_run_in_real_product_process`：直接产品浏览器验收：BrowserPrerequisite，尚未执行目标页面断言；基线同样失败。
- `tests/test_product_browser_gate.py::test_real_browser_spec_and_cleanroom_gate`：直接产品浏览器验收：BrowserPrerequisite，尚未执行目标页面断言；基线同样失败。
- `tests/test_product_browser_gate.py::test_real_browser_rejects_broken_generated_search_ui`：直接产品浏览器验收：BrowserPrerequisite，尚未执行目标页面断言；基线同样失败。
- `tests/test_product_browser_gate.py::test_optional_text_omitted_in_approved_rule_sample_still_checks_limits`：直接产品浏览器验收：BrowserPrerequisite，尚未执行目标页面断言；基线同样失败。
- `tests/test_recommendation_recovery.py::test_news_http_model_protocol_through_real_clean_delivery[False]`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_recommendation_recovery.py::test_news_http_model_protocol_through_real_clean_delivery[True]`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_recommendation_recovery.py::test_existing_legacy_blocked_checkpoint_recovers_same_run`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_recommendation_recovery.py::test_design_recommendation_receives_blockers_without_reanalysing_approved_scope`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_recommendation_stage_budget.py::test_clarification_does_not_spend_design_repair_allowance[True]`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_requirement_coverage.py::test_smart_replans_dropped_search_without_reanalysing_requirements`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_requirement_coverage.py::test_chinese_correction_reconciles_legacy_text_and_records_provenance`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_workflow.py::test_complete_default_flow`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_workflow.py::test_rule_coding_repair_is_bounded`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。
- `tests/test_workflow.py::test_tampered_delivery_not_released`：工作流落盘回执：BrowserPrerequisite，后续READY/BLOCKED/关卡断言因此失败；基线同样失败。

## 首次真实 DeepSeek 检查（2026-10-03）

[受限手动运行37132989503](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/37132989503) 检查提交 `2780495baa985a5fbffd8f05dd5ddb43bfa4a976`，使用已有配置中的 `deepseek-flash`，仅发送合成报名需求及固定连接探测。原有大范围客服模型任务明确跳过。

- 真实连接探测通过：HTTP200，输入71Token、输出24Token。
- 原始报名回答与范围均保留；未发生批准或代码生成。
- 报名任务未通过：一次后续模型请求后记录 `unexpected_model_error`，不能把这一轮报告为完整验收成功。
- 实际发起2次HTTP请求；按请求大小与输出上限预留的保守累计金额为0.224108元。只有探测返回用量，其高峰单价估算为0.000334元；第二次请求没有完整用量回执，整轮实际账单未知。
- 后续离线发现可复现的流式边界问题：SSE协议封装本身可能超过2MB，即使解码后的JSON仍在限制内。首次真实回执未保留完整字节/异常类型证据，因此它是否正是该轮失败原因尚未证实。修复将协议传输上限与解码内容上限分离，并新增脱敏错误类别、状态和字节诊断，保留严格Schema校验。
- 真实Chromium同时发现设置页提示浮层在移动端缩放后产生横向溢出；移除冗余浮层，保留可见费用说明。后续提交仍须通过完整浏览器与教材重建检查。

任何再次付费检查都必须使用已审核提交、剩余累计预算和同一受限入口，不自动重跑失败的付费任务。
