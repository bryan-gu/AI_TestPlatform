<template>
  <header class="header">
    <div class="header-title">{{ appStore.pageTitle }}</div>
    <div class="search-wrapper" ref="searchWrapperRef">
      <div class="header-search">
        <el-icon><Search /></el-icon>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索项目、用例、文档、用户..."
          clearable
          @input="handleSearch"
          @clear="handleSearch"
          @focus="onFocus"
        />
      </div>
      <!-- 搜索结果下拉面板 -->
      <div class="search-dropdown" v-if="showDropdown && searchKeyword.trim()">
        <div v-if="searching" class="search-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>搜索中...</span>
        </div>
        <template v-else>
          <div v-if="searchResults.total === 0" class="search-empty">
            未找到「{{ searchKeyword }}」相关结果
          </div>
          <template v-else>
            <!-- 项目 -->
            <div v-if="searchResults.projects.length > 0" class="search-group">
              <div class="search-group-title">
                <el-icon :size="14"><Folder /></el-icon>
                项目 ({{ searchResults.projects.length }})
              </div>
              <div
                v-for="item in searchResults.projects"
                :key="'p-' + item.id"
                class="search-item"
                @click="goTo(item)"
              >
                <span class="search-item-title">{{ item.title }}</span>
                <span class="search-item-desc">{{ item.description }}</span>
              </div>
            </div>
            <!-- 用例 -->
            <div v-if="searchResults.testcases.length > 0" class="search-group">
              <div class="search-group-title">
                <el-icon :size="14"><List /></el-icon>
                测试用例 ({{ searchResults.testcases.length }})
              </div>
              <div
                v-for="item in searchResults.testcases"
                :key="'t-' + item.id"
                class="search-item"
                @click="goTo(item)"
              >
                <span class="search-item-title">{{ item.title }}</span>
                <span class="search-item-desc">{{ item.description }}</span>
              </div>
            </div>
            <!-- 文档 -->
            <div v-if="searchResults.documents.length > 0" class="search-group">
              <div class="search-group-title">
                <el-icon :size="14"><Document /></el-icon>
                文档 ({{ searchResults.documents.length }})
              </div>
              <div
                v-for="item in searchResults.documents"
                :key="'d-' + item.id"
                class="search-item"
                @click="goTo(item)"
              >
                <span class="search-item-title">{{ item.title }}</span>
                <span class="search-item-desc">{{ item.description }}</span>
              </div>
            </div>
            <!-- 用户 -->
            <div v-if="searchResults.users.length > 0" class="search-group">
              <div class="search-group-title">
                <el-icon :size="14"><User /></el-icon>
                用户 ({{ searchResults.users.length }})
              </div>
              <div
                v-for="item in searchResults.users"
                :key="'u-' + item.id"
                class="search-item"
                @click="goTo(item)"
              >
                <span class="search-item-title">{{ item.title }}</span>
                <span class="search-item-desc">{{ item.description }}</span>
              </div>
            </div>
          </template>
        </template>
      </div>
    </div>
    <el-button
      v-if="appStore.showMainButton"
      type="primary"
      class="btn-primary"
      @click="handleButtonClick"
    >
      <el-icon><Plus /></el-icon>
      <span>{{ appStore.mainButtonText }}</span>
    </el-button>
  </header>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Plus, Folder, List, Document, User, Loading } from '@element-plus/icons-vue'
import { useAppStore } from '../../stores/app'
import { globalSearch } from '../../api/search'

const appStore = useAppStore()
const router = useRouter()
const searchKeyword = ref('')
const searching = ref(false)
const showDropdown = ref(false)
const searchWrapperRef = ref(null)

const searchResults = reactive({
  total: 0,
  projects: [],
  testcases: [],
  documents: [],
  users: [],
})

let searchTimer = null

function onFocus() {
  if (searchKeyword.value.trim()) {
    showDropdown.value = true
  }
}

function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  appStore.setSearchKeyword(searchKeyword.value)

  if (!searchKeyword.value.trim()) {
    showDropdown.value = false
    resetResults()
    return
  }

  showDropdown.value = true
  searching.value = true

  searchTimer = setTimeout(async () => {
    try {
      const res = await globalSearch(searchKeyword.value.trim())
      const data = res.data?.data || res.data || {}
      searchResults.total = data.total || 0
      searchResults.projects = data.projects || []
      searchResults.testcases = data.testcases || []
      searchResults.documents = data.documents || []
      searchResults.users = data.users || []
    } catch (e) {
      console.error('搜索失败', e)
      resetResults()
    } finally {
      searching.value = false
    }
  }, 300)
}

function resetResults() {
  searchResults.total = 0
  searchResults.projects = []
  searchResults.testcases = []
  searchResults.documents = []
  searchResults.users = []
}

function goTo(item) {
  showDropdown.value = false
  searchKeyword.value = ''
  appStore.setSearchKeyword('')
  if (item.route) {
    router.push(item.route)
  }
}

function handleButtonClick() {
  appStore.triggerMainButton()
}

// 点击外部关闭下拉
document.addEventListener('click', (e) => {
  if (searchWrapperRef.value && !searchWrapperRef.value.contains(e.target)) {
    showDropdown.value = false
  }
})
</script>

<style scoped>
.header {
  height: var(--header-h);
  min-height: var(--header-h);
  background: var(--color-background-primary);
  border-bottom: 0.5px solid var(--color-border-tertiary);
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 16px;
  position: relative;
}

.header-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-primary);
  flex: 1;
}

/* 搜索区域 */
.search-wrapper {
  position: relative;
  width: 320px;
  flex-shrink: 0;
}

.header-search {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--color-background-secondary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-md);
  padding: 6px 12px;
  font-size: 13px;
  color: var(--color-text-tertiary);
  transition: border-color 0.2s;
}

.header-search:focus-within {
  border-color: var(--accent);
}

.header-search .el-icon {
  font-size: 15px;
  flex-shrink: 0;
}

.header-search :deep(.el-input) {
  flex: 1;
}

.header-search :deep(.el-input__wrapper) {
  background: transparent;
  box-shadow: none !important;
  padding: 0;
}

.header-search :deep(.el-input__inner) {
  font-size: 13px;
  color: var(--color-text-primary);
}

.header-search :deep(.el-input__inner::placeholder) {
  color: var(--color-text-tertiary);
}

/* 搜索下拉面板 */
.search-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  min-width: 360px;
  max-height: 420px;
  overflow-y: auto;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-md);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 100;
  padding: 8px 0;
}

.search-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.search-empty {
  text-align: center;
  padding: 24px;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.search-group {
  border-bottom: 0.5px solid var(--color-border-tertiary);
}

.search-group:last-child {
  border-bottom: none;
}

.search-group-title {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.search-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.15s;
}

.search-item:hover {
  background: var(--color-background-secondary);
}

.search-item-title {
  font-size: 13px;
  color: var(--color-text-primary);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.search-item-desc {
  font-size: 11px;
  color: var(--color-text-tertiary);
  flex-shrink: 1;
  margin-left: 12px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 按钮 */
.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--accent);
  border-color: var(--accent);
  font-size: 13px;
  font-weight: 500;
}

.btn-primary:hover {
  background: var(--accent-dark);
  border-color: var(--accent-dark);
}

.btn-primary .el-icon {
  font-size: 15px;
}
</style>
