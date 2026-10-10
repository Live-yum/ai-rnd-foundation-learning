# ui/src/components/ProjectsView.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 读取、筛选和打开已有项目，将导航交给上层；不在项目列表中另造创建运行的业务逻辑。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/ProjectsView.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L4。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`116`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/ProjectsView.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "db78aa5e4dfded15fdbbf0bec87db0981efaad572140d39b8b0a10f3d5a1def0"} -->
````vue
<!-- ui/src/components/ProjectsView.vue -->
<script lang="ts">
import Component from '../features/projects/ProjectsView.vue'
export default Component
</script>
````
