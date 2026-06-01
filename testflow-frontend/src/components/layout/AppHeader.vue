<template>
  <header class="header">
    <div class="header-title">{{ appStore.pageTitle }}</div>
    <div class="header-search">
      <el-icon><Search /></el-icon>
      <span>搜索...</span>
    </div>
    <el-button type="primary" class="btn-primary">
      <el-icon><Plus /></el-icon>
      <span>{{ appStore.mainButtonText }}</span>
    </el-button>
  </header>
</template>

<script setup>
import { Search, Plus } from '@element-plus/icons-vue'
import { useAppStore } from '../../stores/app'

const appStore = useAppStore()
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
  cursor: text;
  min-width: 180px;
  transition: border-color 0.2s;
}

.header-search:hover {
  border-color: var(--color-border-primary);
}

.header-search .el-icon {
  font-size: 15px;
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
