<template>
  <header class="header">
    <div class="header-title">{{ appStore.pageTitle }}</div>
    <div class="header-search">
      <el-icon><Search /></el-icon>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索..."
        clearable
        @input="handleSearch"
        @clear="handleSearch"
      />
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
import { ref } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { useAppStore } from '../../stores/app'

const appStore = useAppStore()
const searchKeyword = ref('')
let searchTimer = null

function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    appStore.setSearchKeyword(searchKeyword.value)
  }, 300)
}

function handleButtonClick() {
  appStore.triggerMainButton()
}
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
}

.header-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-primary);
  flex: 1;
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
  min-width: 200px;
  transition: border-color 0.2s;
}

.header-search:hover {
  border-color: var(--color-border-primary);
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
