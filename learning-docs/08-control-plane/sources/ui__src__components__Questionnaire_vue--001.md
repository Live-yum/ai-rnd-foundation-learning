# ui/src/components/Questionnaire.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 按后端当前问题渲染单选、多选或文字回答，提交问题ID和选项ID；必填和自定义约束在浏览器提示后仍由后端复验。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/Questionnaire.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L4。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`118`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/Questionnaire.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fc91e3586e2fae031e35f10886caf52914b4f8764516d7fe4b5b10ec1159684d"} -->
````vue
<!-- ui/src/components/Questionnaire.vue -->
<script lang="ts">
import Component from '../features/approvals/Questionnaire.vue'
export default Component
</script>
````
