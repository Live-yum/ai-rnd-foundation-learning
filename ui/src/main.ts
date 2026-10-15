import { createApp } from 'vue'
import { installUiComponents } from './ui-components'
import 'ant-design-vue/dist/reset.css'
import './style.css'
import App from './App.vue'

const app = createApp(App)
installUiComponents(app)
app.mount('#app')
