# ui/src/components/DataDocument.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 把结构化需求、计划或报告变成可阅读字段；输出作为文本显示，不执行模型提供的HTML。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/DataDocument.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L4。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`113`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/DataDocument.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "bb5e22e00d2b9b60e681cf4b68fef5910f59a0cb269bb9b4a98c4f9874866865"} -->
````vue
<!-- ui/src/components/DataDocument.vue -->
<script lang="ts">
import Component from '../features/plans/DataDocument.vue'
export default Component
</script>
````
