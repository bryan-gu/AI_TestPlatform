<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">进行中项目</div>
        <div class="stat-value">{{ stats.activeProjects }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-green"></span>
          全部正常运行
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">总测试用例</div>
        <div class="stat-value">{{ stats.totalCases }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-blue"></span>
          本月新增 +{{ stats.newCases }}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">通过率</div>
        <div class="stat-value">{{ stats.passRate }}%</div>
        <div class="stat-sub">
          <span class="stat-dot dot-amber"></span>
          较上周 +{{ stats.passRateChange }}%
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">待修复缺陷</div>
        <div class="stat-value">{{ stats.pendingBugs }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-red"></span>
          严重 {{ stats.severeBugs }} / 普通 {{ stats.normalBugs }}
        </div>
      </div>
    </div>

    <!-- 项目列表和动态 -->
    <div class="two-col">
      <div class="card">
        <div class="card-head">
          <div class="card-title">项目列表</div>
          <div class="card-action" @click="goToProjects">全部查看</div>
        </div>
        <el-table :data="projects" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="项目名称" />
          <el-table-column label="进度" width="180">
            <template #default="{ row }">
              <div style="display: flex; align-items: center; gap: 8px">
                <el-progress
                  :percentage="row.progress"
                  :stroke-width="5"
                  :show-text="false"
                  style="flex: 1"
                />
                <span style="font-size: 12px; color: var(--color-text-secondary)">
                  {{ row.progress }}%
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="owner" label="负责人" width="100" />
        </el-table>
      </div>

      <div class="card">
        <div class="card-head">
          <div class="card-title">近期动态</div>
        </div>
        <div class="activity-list" v-loading="loadingActivities">
          <div
            v-for="(activity, index) in activities"
            :key="index"
            class="activity-item"
          >
            <div
              class="act-icon"
              :style="{ background: activity.iconBg }"
            >
              <el-icon :style="{ color: activity.iconColor }">
                <component :is="activity.icon" />
              </el-icon>
            </div>
            <div class="act-text">
              <div class="act-main">{{ activity.text }}</div>
              <div class="act-time">{{ activity.time }} · {{ activity.user }}</div>
            </div>
          </div>
          <div v-if="!loadingActivities && activities.length === 0" style="padding: 40px; text-align: center; color: var(--color-text-tertiary); font-size: 13px">
            暂无动态
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardStats, getDashboardActivities } from '../../api/dashboard'
import { getProjects } from '../../api/project'
import { useAppStore } from '../../stores/app'

const router = useRouter()
const appStore = useAppStore()

const loading = ref(false)
const loadingActivities = ref(false)
const stats = ref({
  activeProjects: 0,
  totalCases: 0,
  newCases: 0,
  passRate: 0,
  passRateChange: 0,
  pendingBugs: 0,
  severeBugs: 0,
  normalBugs: 0
})

const projects = ref([])
const activities = ref([])

function getStatusType(status) {
  const map = { testing: '', completed: 'success', active: 'warning', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { testing: '测试中', completed: '已完成', active: '进行中', pending: '待启动' }
  return map[status] || status
}

function goToProjects() {
  router.push('/projects')
}

onMounted(async () => {
  appStore.setCurrentPage('dashboard', '项目总览')
  // 加载统计数据
  loading.value = true
  try {
    const [statsRes, projRes] = await Promise.allSettled([
      getDashboardStats(),
      getProjects()
    ])
    if (statsRes.status === 'fulfilled') {
      stats.value = statsRes.value.data
    }
    if (projRes.status === 'fulfilled') {
      projects.value = projRes.value.data.slice(0, 4) // 只显示前4个
    }
  } catch (e) {
    console.error('加载仪表盘数据失败:', e)
  } finally {
    loading.value = false
  }

  // 加载近期动态
  loadingActivities.value = true
  try {
    const actRes = await getDashboardActivities()
    activities.value = actRes.data || []
  } catch (e) {
    console.error('加载动态数据失败:', e)
  } finally {
    loadingActivities.value = false
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}
</style>
