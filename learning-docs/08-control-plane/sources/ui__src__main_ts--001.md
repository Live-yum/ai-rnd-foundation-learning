# ui/src/main.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 创建Vue应用并挂载顶层组件，统一导入界面样式。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/main.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L51。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`671`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/main.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "05d5d6fec008f2eb2884d100ce084bfe74c13d14481d61ba233cbacdad7f51b6"} -->
````typescript
// ui/src/main.ts
import { createApp } from 'vue'
import {
  Alert,
  Button,
  Checkbox,
  Collapse,
  ConfigProvider,
  Descriptions,
  Drawer,
  Empty,
  Input,
  InputNumber,
  Modal,
  Radio,
  Select,
  Segmented,
  Skeleton,
  Switch,
  Tabs,
  Tag,
  Tooltip,
} from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './style.css'
import App from './App.vue'

const app = createApp(App)
for (const component of [
  Alert,
  Button,
  Checkbox,
  Collapse,
  ConfigProvider,
  Descriptions,
  Drawer,
  Empty,
  Input,
  InputNumber,
  Modal,
  Radio,
  Select,
  Segmented,
  Skeleton,
  Switch,
  Tabs,
  Tag,
  Tooltip,
]) {
  app.use(component)
}
app.mount('#app')
````
