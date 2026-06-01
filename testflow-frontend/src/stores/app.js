import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')
  const currentPage = ref('dashboard')
  const pageTitle = ref('项目总览')
  const mainButtonText = ref('')
  const showMainButton = ref(false)

  // 切换侧边栏折叠状态
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value.toString())
  }

  // 设置当前页面信息
  function setCurrentPage(page, title, buttonText) {
    currentPage.value = page
    pageTitle.value = title
    if (buttonText) {
      mainButtonText.value = buttonText
      showMainButton.value = true
    } else {
      mainButtonText.value = ''
      showMainButton.value = false
    }
  }

  return {
    sidebarCollapsed,
    currentPage,
    pageTitle,
    mainButtonText,
    showMainButton,
    toggleSidebar,
    setCurrentPage
  }
})
