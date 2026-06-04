<template>
  <div class="dashboard">
    <!-- 统计卡片 — 测试概览 -->
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

    <!-- 统计卡片 — 知识库 & AI -->
    <div class="stats-grid" style="margin-top:12px">
      <div class="stat-card">
        <div class="stat-label">知识库 Sprint</div>
        <div class="stat-value">{{ stats.totalSprints }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-blue"></span>
          文档 {{ stats.totalDocuments }} 份
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">AI 流水线执行</div>
        <div class="stat-value">{{ stats.pipelineExecutions }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-green"></span>
          AI 调用 {{ stats.aiCallCount }} 次
        </div>
      </div>
      <div class="stat-card" style="cursor:pointer" @click="goTo('/testcases')">
        <div class="stat-label">测试用例覆盖</div>
        <div class="stat-value">{{ coverageDisplay }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-amber"></span>
          查看用例列表
        </div>
      </div>
      <div class="stat-card" style="cursor:pointer" @click="goTo('/ai-workbench')">
        <div class="stat-label">AI 工作台</div>
        <div class="stat-value">
          <el-icon :size="20" style="color:var(--accent);vertical-align:middle"><Cpu /></el-icon>
        </div>
        <div class="stat-sub">
          <span class="stat-dot dot-green"></span>
          进入工作台
        </div>
      </div>
    </div>

    <!-- 项目列表和动态 -->
    <div class="two-col">
      <div class="card">
        <div class="card-head">
          <div class="card-title">项目列表</div>
          <div class="card-action" @click="goTo('/projects')">全部查看</div>
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

    <!-- 最近流水线执行 -->
    <div class="card" style="margin-top:16px" v-if="recentExecutions.length > 0">
      <div class="card-head">
        <div class="card-title">最近 AI 流水线执行</div>
        <div class="card-action" @click="goTo('/ai-workbench')">查看全部</div>
      </div>
      <el-table :data="recentExecutions" style="width: 100%">
        <el-table-column label="执行" min-width="200">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px">
              <el-icon :size="16" style="color:var(--accent)"><Cpu /></el-icon>
              <span>{{ row.project_name || '未指定' }}</span>
              <el-tag size="small" effect="plain" round>{{ row.mode === 'incremental' ? '增量' : '全量' }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Sprint" width="120">
          <template #default="{ row }">
            {{ row.sprint_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="pipelineStatusType(row.status)" size="small" effect="plain" round>
              {{ pipelineStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration_display || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="执行时间" width="120">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Cpu } from '@element-plus/icons-vue'
import { getDashboardStats, getDashboardActivities } from '../../api/dashboard'
import { getProjects } from '../../api/project'
import { getExecutions } from '../../api/pipeline'
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
  normalBugs: 0,
  totalSprints: 0,
  totalDocuments: 0,
  pipelineExecutions: 0,
  aiCallCount: 0,
})

const projects = ref([])
const activities = ref([])
const recentExecutions = ref([])

const coverageDisplay = computed(() => {
  if (stats.value.totalCases === 0) return '0%'
  return `${stats.value.passRate}%`
})

function getStatusType(status) {
  const map = { testing: '', completed: 'success', active: 'warning', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { testing: '测试中', completed: '已完成', active: '进行中', pending: '待启动' }
  return map[status] || status
}

function pipelineStatusType(status) {
  const map = { completed: 'success', running: '', paused: 'warning', waiting: 'info', failed: 'danger' }
  return map[status] || 'info'
}

function pipelineStatusLabel(status) {
  const map = { completed: '已完成', running: '运行中', paused: '已暂停', waiting: '等待中', failed: '失败' }
  return map[status] || status
}

function formatTime(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} 天前`
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function goTo(path) {
  router.push(path)
}

onMounted(async () => {
  appStore.setCurrentPage('dashboard', '项目总览')
  loading.value = true
  try {
    const [statsRes, projRes] = await Promise.allSettled([
      getDashboardStats(),
      getProjects()
    ])
    if (statsRes.status === 'fulfilled') {
      const s = statsRes.value.data?.data || statsRes.value.data || {}
      stats.value = { ...stats.value, ...s }
    }
    if (projRes.status === 'fulfilled') {
      const list = projRes.value.data?.data || projRes.value.data || []
      projects.value = list.slice(0, 4)
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
    activities.value = actRes.data?.data || actRes.data || []
  } catch (e) {
    console.error('加载动态数据失败:', e)
  } finally {
    loadingActivities.value = false
  }

  // 加载最近流水线执行
  try {
    const execRes = await getExecutions({})
    const list = execRes.data?.data || execRes.data || []
    recentExecutions.value = list.slice(0, 5)
  } catch (e) {
    console.error('加载流水线执行失败:', e)
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
