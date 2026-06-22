import axios from 'axios'

// 创建axios实例 - 使用相对路径，通过vite代理转发到后端
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('quantum_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 处理401未授权
    if (error.response?.status === 401) {
      localStorage.removeItem('quantum_token')
      localStorage.removeItem('quantum_role')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
