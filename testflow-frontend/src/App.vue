<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  if (authStore.token) {
    await authStore.initUser()
  }
})
</script>

<style>
#app {
  width: 100%;
  height: 100%;
}
</style>
