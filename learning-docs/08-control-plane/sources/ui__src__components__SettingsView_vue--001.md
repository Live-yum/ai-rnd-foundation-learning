# ui/src/components/SettingsView.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 编辑默认与分阶段模型配置；已保存密钥不回填，保存使用版本号防止覆盖另一窗口的修改。保存成功不表示连通性测试或付费模型调用通过。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**带着一个具体问题阅读：** 页面显示‘Key已配置’不代表拿到了Key原文；留空表示不修改，明确清除才删除覆盖。保存只验证并落盘，不能显示‘模型连接成功’。如果另一窗口先保存导致409，应读取新版本让用户复核，而不是自动拿新revision重发旧表单。

**创建路径：** `ui/src/components/SettingsView.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L4。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`116`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/SettingsView.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1c0a9b044b24a79d119b3e5707e18728d21ca24db636d360c2336f71019b7b11"} -->
````vue
<!-- ui/src/components/SettingsView.vue -->
<script lang="ts">
import Component from '../features/settings/SettingsView.vue'
export default Component
</script>
````
