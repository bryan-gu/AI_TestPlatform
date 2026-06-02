<template>
  <aside class="sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
    <div class="logo">
      <div class="logo-icon">
        <el-icon><component :is="icons.Operation" /></el-icon>
      </div>
      <div class="logo-text">
        <div class="logo-name">TestFlow</div>
        <div class="logo-sub">测试管理平台</div>
      </div>
      <button class="collapse-btn" @click="appStore.toggleSidebar" title="收起菜单">
        <el-icon><component :is="icons.ArrowLeft" /></el-icon>
      </button>
      <button class="expand-btn" @click="appStore.toggleSidebar" title="展开菜单">
        <el-icon><component :is="icons.ArrowRight" /></el-icon>
      </button>
    </div>

    <div class="nav-section">
      <div class="nav-label">项目</div>
      <div
        v-for="item in projectMenus"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentRoute === item.path }"
        @click="navigateTo(item)"
        :title="item.title"
      >
        <el-icon><component :is="icons[item.icon]" /></el-icon>
        <span>{{ item.title }}</span>
        <span v-if="item.badge != null && item.badge > 0" class="nav-badge">{{ item.badge }}</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-label">知识</div>
      <div
        v-for="item in knowledgeMenus"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentRoute === item.path }"
        @click="navigateTo(item)"
        :title="item.title"
      >
        <el-icon><component :is="icons[item.icon]" /></el-icon>
        <span>{{ item.title }}</span>
        <span v-if="item.badge != null && item.badge > 0" class="nav-badge">{{ item.badge }}</span>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-label">系统管理</div>
      <div
        v-for="item in systemMenus"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentRoute === item.path }"
        @click="navigateTo(item)"
        :title="item.title"
      >
        <el-icon><component :is="icons[item.icon]" /></el-icon>
        <span>{{ item.title }}</span>
        <span v-if="item.badge != null && item.badge > 0" class="nav-badge">{{ item.badge }}</span>
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="user-row" :title="`${user?.name} · ${user?.role?.name}`">
        <div class="avatar">{{ user?.name?.charAt(0) || '用' }}</div>
        <div class="user-info">
          <div class="user-name">{{ user?.name || '用户' }}</div>
          <div class="user-role">{{ user?.role?.name || '普通用户' }}</div>
        </div>
        <el-icon><component :is="icons.Setting" /></el-icon>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { useAuthStore } from '../../stores/auth'
import * as icons from '@element-plus/icons-vue'
import { getProjects } from '../../api/project'
import { getTestCaseStats } from '../../api/testcase'
import { getReportStats } from '../../api/report'
import { getKnowledgeStats } from '../../api/knowledge'
import { getUsers } from '../../api/user'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const currentRoute = computed(() => route.path)

const projectMenus = reactive([
  { path: '/dashboard', title: '项目总览', icon: 'Odometer' },
  { path: '/projects', title: '项目管理', icon: 'Folder', badge: 0 },
  { path: '/testcases', title: '测试用例', icon: 'Finished', badge: 0 },
  { path: '/reports', title: '测试报告', icon: 'DataAnalysis', badge: 0 }
])

const knowledgeMenus = reactive([
  { path: '/knowledge', title: '知识库', icon: 'Collection', badge: 0 },
  { path: '/knowledge/graph', title: '知识图谱', icon: 'Share' }
])

const systemMenus = reactive([
  { path: '/roles', title: '角色管理', icon: 'Lock' },
  { path: '/users', title: '用户管理', icon: 'User', badge: 0 }
])

function navigateTo(item) {
  router.push(item.path)
}

async function loadBadges() {
  try {
    const [projRes, caseStatsRes, reportStatsRes, kbStatsRes, usersRes] = await Promise.allSettled([
      getProjects(),
      getTestCaseStats(),
      getReportStats(),
      getKnowledgeStats(),
      getUsers()
    ])

    if (projRes.status === 'fulfilled') {
      projectMenus[1].badge = projRes.value.data?.length || 0
    }
    if (caseStatsRes.status === 'fulfilled') {
      projectMenus[2].badge = caseStatsRes.value.data?.total || 0
    }
    if (reportStatsRes.status === 'fulfilled') {
      projectMenus[3].badge = reportStatsRes.value.data?.monthlyReports || 0
    }
    if (kbStatsRes.status === 'fulfilled') {
      knowledgeMenus[0].badge = kbStatsRes.value.data?.totalDocs || 0
    }
    if (usersRes.status === 'fulfilled') {
      systemMenus[1].badge = usersRes.value.data?.length || 0
    }
  } catch (e) {
    console.error('加载侧边栏数据失败:', e)
  }
}

// 监听 sidebarBadgesVersion 变化，刷新 badges
watch(() => appStore.sidebarBadgesVersion, () => {
  loadBadges()
})

onMounted(() => {
  loadBadges()
})
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-w);
  background: var(--color-background-primary);
  border-right: 0.5px solid var(--color-border-tertiary);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
  transition: width 0.3s ease;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  height: var(--header-h);
  min-height: var(--header-h);
  border-bottom: 0.5px solid var(--color-border-tertiary);
}

.logo-icon {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon .el-icon {
  color: #fff;
  font-size: 16px;
}

.logo-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.logo-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.logo-sub {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.collapse-btn,
.expand-btn {
  width: 28px;
  height: 28px;
  border-radius: var(--border-radius-md);
  background: transparent;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-text-tertiary);
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}

.collapse-btn:hover,
.expand-btn:hover {
  background: var(--color-background-secondary);
  color: var(--color-text-primary);
}

.expand-btn {
  display: none;
  position: absolute;
  right: -14px;
  top: 50%;
  transform: translateY(-50%);
  border-radius: 50%;
  background: var(--color-background-primary);
  border: 1px solid var(--color-border-tertiary);
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.nav-section {
  padding: 16px 10px 6px;
}

.nav-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  padding: 0 8px 6px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 7px 10px;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: background 0.12s;
  color: var(--color-text-secondary);
  font-size: 13.5px;
  margin-bottom: 2px;
  user-select: none;
}

.nav-item:hover {
  background: var(--color-background-secondary);
  color: var(--color-text-primary);
}

.nav-item.active {
  background: var(--accent-light);
  color: var(--accent-dark);
  font-weight: 500;
}

.nav-item .el-icon {
  font-size: 16px;
  width: 18px;
  text-align: center;
  flex-shrink: 0;
}

.nav-badge {
  margin-left: auto;
  font-size: 11px;
  font-weight: 500;
  background: var(--color-background-secondary);
  color: var(--color-text-tertiary);
  padding: 1px 7px;
  border-radius: 10px;
}

.nav-item.active .nav-badge {
  background: rgba(29, 158, 117, 0.15);
  color: var(--accent);
}

.sidebar-footer {
  margin-top: auto;
  padding: 12px 10px;
  border-top: 0.5px solid var(--color-border-tertiary);
}

.user-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--border-radius-md);
  cursor: pointer;
}

.user-row:hover {
  background: var(--color-background-secondary);
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  color: #fff;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.user-role {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

/* 折叠状态 */
.collapsed {
  width: var(--sidebar-collapsed-w);
}

.collapsed .logo-text,
.collapsed .nav-label,
.collapsed .nav-item span:not(.nav-badge),
.collapsed .user-info,
.collapsed .nav-badge {
  display: none;
}

.collapsed .logo {
  justify-content: center;
  padding: 0 10px;
  position: relative;
}

.collapsed .collapse-btn {
  display: none;
}

.collapsed .expand-btn {
  display: flex;
}

.collapsed .nav-section {
  padding: 16px 8px 6px;
}

.collapsed .nav-item {
  justify-content: center;
  padding: 10px;
  position: relative;
}

.collapsed .nav-item .el-icon {
  font-size: 20px;
}

.collapsed .sidebar-footer {
  padding: 12px 8px;
}

.collapsed .user-row {
  justify-content: center;
  padding: 8px;
}

.collapsed .user-row .el-icon:last-child {
  display: none;
}
</style>
