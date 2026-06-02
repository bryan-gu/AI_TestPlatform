import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')
  const currentPage = ref('dashboard')
  const pageTitle = ref('项目总览')
  const mainButtonText = ref('')
  const showMainButton = ref(false)
  const mainButtonCallback = ref(null)
  const sidebarBadgesVersion = ref(0)

  // 切换侧边栏折叠状态
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value.toString())
  }

  // 设置当前页面信息
  function setCurrentPage(page, title, buttonText, callback) {
    currentPage.value = page
    pageTitle.value = title
    if (buttonText) {
      mainButtonText.value = buttonText
      showMainButton.value = true
      mainButtonCallback.value = callback || null
    } else {
      mainButtonText.value = ''
      showMainButton.value = false
      mainButtonCallback.value = null
    }
  }

  // 触发Header按钮点击
  function triggerMainButton() {
    if (mainButtonCallback.value) {
      mainButtonCallback.value()
    }
  }

  // 触发侧边栏 badges 刷新
  function refreshSidebarBadges() {
    sidebarBadgesVersion.value++
  }

  return {
    sidebarCollapsed,
    currentPage,
    pageTitle,
    mainButtonText,
    showMainButton,
    mainButtonCallback,
    sidebarBadgesVersion,
    toggleSidebar,
    setCurrentPage,
    triggerMainButton,
    refreshSidebarBadges
  }
})
