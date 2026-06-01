import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, logout, getCurrentUser } from '../api/auth'

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
        console.error('获取用户信息失败:', error)
        token.value = ''
        localStorage.removeItem('token')
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
      throw error
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
      throw error
    } finally {
      loading.value = false
    }
  }

  // 登出
  async function logoutAction() {
    try {
      await logout()
    } catch (error) {
      // 忽略登出请求错误
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
