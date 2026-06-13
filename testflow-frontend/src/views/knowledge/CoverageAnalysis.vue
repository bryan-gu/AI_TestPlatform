<template>
  <div class="coverage-analysis">
    <div class="card">
      <div class="card-head">
        <div class="card-title">覆盖分析</div>
        <div class="filter-bar">
          <el-select v-model="projectId" placeholder="项目" size="small" style="width:160px" clearable filterable @change="onProjectChange">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-select v-model="sprintId" placeholder="Sprint" size="small" style="width:160px" clearable filterable @change="loadFeatures">
            <el-option v-for="s in sprints" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </div>
      </div>

      <!-- 总览统计 -->
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-label">功能点总数</div>
          <div class="stat-value">{{ stats.total }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">已覆盖</div>
          <div class="stat-value" style="color: #16a34a">{{ stats.covered }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">未覆盖</div>
          <div class="stat-value" style="color: #E24B4A">{{ stats.uncovered }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">覆盖率</div>
          <div class="stat-value" style="color: var(--accent)">{{ stats.rate }}</div>
        </div>
      </div>

      <!-- 模块维度 -->
      <div class="section-title">按模块统计</div>
      <el-table :data="moduleStats" style="width:100%" size="small" empty-text="暂无数据">
        <el-table-column prop="module" label="模块" min-width="140" show-overflow-tooltip />
        <el-table-column prop="total" label="功能点" width="90" />
        <el-table-column prop="covered" label="已覆盖" width="90" />
        <el-table-column prop="uncovered" label="未覆盖" width="90" />
        <el-table-column label="覆盖率" width="180">
          <template #default="{ row }">
            <el-progress :percentage="row.rateNum" :stroke-width="10" :status="row.rateNum >= 80 ? 'success' : (row.rateNum < 40 ? 'exception' : '')" />
          </template>
        </el-table-column>
      </el-table>

      <!-- 未覆盖功能点明细 -->
      <div class="section-title">未覆盖功能点</div>
      <el-table :data="uncoveredFeatures" style="width:100%" size="small" empty-text="全部功能点均已覆盖">
        <el-table-column prop="name" label="功能点" min-width="160" show-overflow-tooltip />
        <el-table-column prop="module_name" label="模块" width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ row.module_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="优先级" width="80">
          <template #default="{ row }"><span :class="priorityClass(row.priority)">{{ row.priority || '中' }}</span></template>
        </el-table-column>
        <el-table-column prop="source_type" label="来源" width="90">
          <template #default="{ row }">{{ sourceText(row.source_type) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getFeaturePoints } from '../../api/featurePoint'
import { getProjects } from '../../api/project'
import { getSprints } from '../../api/sprint'
import { useAppStore } from '../../stores/app'

const appStore = useAppStore()
const projects = ref([])
const sprints = ref([])
const projectId = ref(null)
const sprintId = ref(null)
const features = ref([])
const loading = ref(false)

const stats = computed(() => {
  const total = features.value.length
  const covered = features.value.filter(f => (f.coverage_count || 0) > 0).length
  const uncovered = total - covered
  const rate = total > 0 ? Math.round((covered / total) * 100) : 0
  return { total, covered, uncovered, rate: `${rate}%` }
})

const moduleStats = computed(() => {
  const map = {}
  for (const f of features.value) {
    const key = f.module_name || '未分类'
    if (!map[key]) map[key] = { module: key, total: 0, covered: 0, uncovered: 0 }
    map[key].total += 1
    if ((f.coverage_count || 0) > 0) map[key].covered += 1
    else map[key].uncovered += 1
  }
  return Object.values(map).map(m => ({
    ...m,
    rateNum: m.total > 0 ? Math.round((m.covered / m.total) * 100) : 0,
  })).sort((a, b) => b.total - a.total)
})

const uncoveredFeatures = computed(() => features.value.filter(f => (f.coverage_count || 0) === 0))

function priorityClass(p) {
  return { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }[p] || 'badge badge-gray'
}
function sourceText(t) {
  return { requirement: '需求', ui_explore: 'UI', api_doc: '接口', manual: '手工', ai_generated: 'AI', baseline_draft: '基线' }[t] || '手工'
}

async function loadProjects() {
  const res = await getProjects()
  projects.value = res.data || []
}

async function onProjectChange() {
  sprintId.value = null
  if (projectId.value) {
    const res = await getSprints({ project_id: projectId.value })
    sprints.value = res.data || []
  } else {
    sprints.value = []
  }
  await loadFeatures()
}

async function loadFeatures() {
  if (!sprintId.value) {
    features.value = []
    return
  }
  loading.value = true
  try {
    const res = await getFeaturePoints({ sprint_id: sprintId.value })
    features.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  appStore.setCurrentPage('coverage-analysis', '覆盖分析')
  await loadProjects()
})
</script>

<style scoped>
.coverage-analysis { max-width: 1400px; }

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
  flex-wrap: wrap;
  gap: 8px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.filter-bar {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 16px 18px;
}

.stat-card {
  background: var(--color-background-secondary);
  border-radius: var(--border-radius-md);
  padding: 14px 16px;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-bottom: 6px;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  padding: 0 18px 10px;
  margin-top: 4px;
}

.section-title + .el-table {
  margin: 0 18px 16px;
  width: calc(100% - 36px) !important;
}
</style>
