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
