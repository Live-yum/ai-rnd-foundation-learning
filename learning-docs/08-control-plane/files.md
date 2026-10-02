# API、CLI与Vue流式操作台：本阶段文件

[返回阶段导读](README.md)

按导读先后理解；同一组需全部写完再导入或运行测试。以下路径相对学生项目根目录，不是教材目录。所有文件逐字节收录，代码分段的第一行路径注释需删除。锁文件在 sources/locks，截图及Vue构建快照编码在 sources/assets 下，先读实现模块，需要校对时再打开资源。

- [scripts/guided_browser.cjs](sources/scripts__guided_browser_cjs--001.md)：在真实浏览器操作研发工作台；2 段
- [tests/test_api.py](sources/tests__test_api_py--001.md)：可重复的验收用例；1 段
- [tests/test_clarification_choices.py](sources/tests__test_clarification_choices_py--001.md)：可重复的验收用例；1 段
- [tests/test_cli_connection.py](sources/tests__test_cli_connection_py--001.md)：可重复的验收用例；1 段
- [tests/test_guided_selection.py](sources/tests__test_guided_selection_py--001.md)：可重复的验收用例；1 段
- [tests/test_model_settings.py](sources/tests__test_model_settings_py--001.md)：可重复的验收用例；1 段
- [tests/test_streaming_backend.py](sources/tests__test_streaming_backend_py--001.md)：可重复的验收用例；1 段
- [tests/test_tools_cli.py](sources/tests__test_tools_cli_py--001.md)：可重复的验收用例；1 段
- [ui/.gitignore](sources/ui___gitignore--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/.prettierrc.json](sources/ui___prettierrc_json--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/README.md](sources/ui__README_md--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/index.html](sources/ui__index_html--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/package-lock.json](sources/locks/ui__package-lock_json--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/package.json](sources/ui__package_json--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/App.vue](sources/ui__src__App_vue--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/api.ts](sources/ui__src__api_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/components/DataDocument.vue](sources/ui__src__components__DataDocument_vue--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/components/HomeView.vue](sources/ui__src__components__HomeView_vue--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/components/ProjectsView.vue](sources/ui__src__components__ProjectsView_vue--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/components/Questionnaire.vue](sources/ui__src__components__Questionnaire_vue--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/components/RunView.vue](sources/ui__src__components__RunView_vue--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/components/SettingsView.vue](sources/ui__src__components__SettingsView_vue--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/main.ts](sources/ui__src__main_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/presentation.ts](sources/ui__src__presentation_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/state.ts](sources/ui__src__state_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/style.css](sources/ui__src__style_css--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/src/types.ts](sources/ui__src__types_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/tests/capability.test.ts](sources/ui__tests__capability_test_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/tests/documents.test.ts](sources/ui__tests__documents_test_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/tests/protocol.test.ts](sources/ui__tests__protocol_test_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/tests/questions.test.ts](sources/ui__tests__questions_test_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/tests/settings.test.ts](sources/ui__tests__settings_test_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/tests/state.test.ts](sources/ui__tests__state_test_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/tsconfig.json](sources/ui__tsconfig_json--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [ui/vite.config.ts](sources/ui__vite_config_ts--001.md)：Vue 3 / Ant Design本机操作台源码；1 段
- [workbench/api.py](sources/workbench__api_py--001.md)：网页及CLI调用的HTTP接口；1 段
- [workbench/cli.py](sources/workbench__cli_py--001.md)：终端入口和运维命令；1 段
- [workbench/native.py](sources/workbench__native_py--001.md)：原生代码生成接口的公共适配；1 段
- [workbench/web/app.js](sources/assets/workbench__web__app_js--001.md)：Vue操作台的精确构建资产；1 段
- [workbench/web/index.html](sources/assets/workbench__web__index_html--001.md)：Vue操作台的精确构建资产；1 段
- [workbench/web/style.css](sources/assets/workbench__web__style_css--001.md)：Vue操作台的精确构建资产；1 段
