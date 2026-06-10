import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  async error => {
    // blob 响应类型下，后端返回的 JSON 错误体会被包成 Blob，需先解析出 detail
    if (error.response?.data instanceof Blob && error.response.data.type?.includes('json')) {
      try {
        const text = await error.response.data.text()
        error.response.data = JSON.parse(text)
      } catch (e) { /* 解析失败则保持原样 */ }
    }

    const message = error.response?.data?.detail || error.message || '请求失败'

    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
