<template>
  <div class="layout">
    <AppSidebar />
    <div class="main">
      <AppHeader />
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  min-height: 640px;
  overflow: hidden;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: var(--color-background-tertiary);
}
</style>
