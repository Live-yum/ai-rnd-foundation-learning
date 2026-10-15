import type { App } from 'vue'
import {
  Alert,
  AutoComplete,
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

// Share the production registry with component regressions; avoid all-Antd test-only coverage.
export function installUiComponents(app: App) {
  for (const component of [
    Alert,
    AutoComplete,
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
}
