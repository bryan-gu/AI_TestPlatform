import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'
import './assets/styles/global.css'

const app = createApp(App)

// 配置Pinia
const pinia = createPinia()
app.use(pinia)

// 配置路由
app.use(router)

// 配置Element Plus
app.use(ElementPlus, {
  locale: zhCn,
  size: 'default'
})

// 挂载应用
app.mount('#app')
