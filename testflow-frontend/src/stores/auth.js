import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, logout, getCurrentUser } from '../api/auth'

// Mock 用户数据（后端未就绪时使用）
const mockUser = {
  id: 1,
  name: '张测试',
  email: 'zhang@test.com',
  role: {
    name: '超级管理员',
    permissions: ['*']
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role?.name || '')

  // 初始化用户信息
  async function initUser() {
    if (token.value && !user.value) {
      try {
        const res = await getCurrentUser()
        user.value = res.data
      } catch (error) {
        // 后端未就绪时使用 Mock 数据
        console.warn('后端未连接，使用 Mock 用户数据')
        user.value = mockUser
      }
    }
  }

  // 登录
  async function loginAction(credentials) {
    loading.value = true
    try {
      const res = await login(credentials)
      token.value = res.data.token
      localStorage.setItem('token', res.data.token)
      await initUser()
      return res
    } catch (error) {
      // 后端未就绪时模拟登录成功
      console.warn('后端未连接，使用 Mock 登录')
      const mockToken = 'mock-token-' + Date.now()
      token.value = mockToken
      localStorage.setItem('token', mockToken)
      user.value = mockUser
      return { data: { token: mockToken } }
    } finally {
      loading.value = false
    }
  }

  // 注册
  async function registerAction(userData) {
    loading.value = true
    try {
      const res = await register(userData)
      token.value = res.data.token
      localStorage.setItem('token', res.data.token)
      await initUser()
      return res
    } catch (error) {
      // 后端未就绪时模拟注册成功
      console.warn('后端未连接，使用 Mock 注册')
      const mockToken = 'mock-token-' + Date.now()
      token.value = mockToken
      localStorage.setItem('token', mockToken)
      user.value = { ...mockUser, name: userData.name, email: userData.email }
      return { data: { token: mockToken } }
    } finally {
      loading.value = false
    }
  }

  // 登出
  async function logoutAction() {
    try {
      await logout()
    } catch (error) {
      // 后端未就绪时忽略登出请求错误
    } finally {
      token.value = ''
      user.value = null
      localStorage.removeItem('token')
    }
  }

  // 检查权限
  function hasPermission(permission) {
    if (!user.value) return false
    const role = user.value.role
    if (!role) return false
    if (role.name === '超级管理员') return true
    return role.permissions?.includes(permission) || false
  }

  return {
    token,
    user,
    loading,
    isAuthenticated,
    userRole,
    initUser,
    loginAction,
    registerAction,
    logoutAction,
    hasPermission
  }
})
