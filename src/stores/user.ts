import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, getCurrentUser, type UserInfo, type LoginResponse } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('quantum_token'))
  const userInfo = ref<UserInfo | null>(null)
  const role = ref<string | null>(localStorage.getItem('quantum_role'))
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'admin')

  // 登录
  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true
    try {
      const response: LoginResponse = await apiLogin({ email, password })
      
      token.value = response.access_token
      userInfo.value = response.user
      role.value = response.user.is_admin ? 'admin' : 'user'

      localStorage.setItem('quantum_token', response.access_token)
      localStorage.setItem('quantum_role', response.user.is_admin ? 'admin' : 'user')

      return true
    } catch (error: any) {
      console.error('Login failed:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  async function register(email: string, password: string, username: string): Promise<boolean> {
    loading.value = true
    try {
      const response: LoginResponse = await apiRegister({ email, username, password })
      
      token.value = response.access_token
      userInfo.value = response.user
      role.value = response.user.is_admin ? 'admin' : 'user'

      localStorage.setItem('quantum_token', response.access_token)
      localStorage.setItem('quantum_role', response.user.is_admin ? 'admin' : 'user')

      return true
    } catch (error: any) {
      console.error('Register failed:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取用户信息
  async function fetchUserInfo() {
    if (!token.value) return

    try {
      const user = await getCurrentUser()
      userInfo.value = user
      role.value = user.is_admin ? 'admin' : 'user'
      localStorage.setItem('quantum_role', user.is_admin ? 'admin' : 'user')
    } catch (error) {
      console.error('Fetch user info failed:', error)
    }
  }

  // 退出登录
  function logout() {
    token.value = null
    userInfo.value = null
    role.value = null
    localStorage.removeItem('quantum_token')
    localStorage.removeItem('quantum_role')
  }

  // 更新用户设置
  function updateUserSettings(settings: Partial<UserInfo>) {
    if (userInfo.value) {
      Object.assign(userInfo.value, settings)
    }
  }

  return {
    token,
    userInfo,
    role,
    loading,
    isLoggedIn,
    isAdmin,
    login,
    register,
    fetchUserInfo,
    logout,
    updateUserSettings,
  }
})
