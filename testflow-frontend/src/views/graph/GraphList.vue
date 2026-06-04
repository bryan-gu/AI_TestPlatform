<template>
  <div class="graph-list">
    <!-- 项目上下文栏 -->
    <div class="project-context-bar">
      <div class="project-icon">
        <el-icon :size="16" style="color:var(--accent)"><Folder /></el-icon>
      </div>
      <div style="flex:1">
        <div style="display:flex;align-items:center;gap:8px">
          <el-select v-model="selectedProject" style="width:200px" size="small" @change="onProjectChange">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-tag v-if="currentProjectStatus" type="primary" size="small" effect="plain" round>{{ currentProjectStatus }}</el-tag>
        </div>
        <div style="font-size:12px;color:var(--color-text-secondary);margin-top:2px">
          该知识图谱由 AI 在需求分析阶段自动生成 · 共 {{ stats.totalGraphs }} 张图谱、{{ stats.totalNodes }} 个节点
        </div>
      </div>
    </div>

    <!-- AI 自动生成提示条 -->
    <div class="ai-notice">
      <el-icon :size="18" style="color:var(--accent)"><MagicStick /></el-icon>
      <div style="flex:1">
        <div style="font-size:13px;font-weight:500;color:var(--color-text-primary)">AI 自动生成</div>
        <div style="font-size:12px;color:var(--color-text-secondary)">知识图谱由 AI 在需求分析阶段自动生成，作为后续测试用例和脚本生成的预处理数据层。</div>
      </div>
      <el-button size="small" @click="handleRegenerate" :loading="regenerating">
        <el-icon><Refresh /></el-icon>重新生成
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px">
      <div class="stat-card">
        <div class="stat-label">图谱总数</div>
        <div class="stat-value">{{ stats.totalGraphs }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>AI 自动生成</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">总节点数</div>
        <div class="stat-value">{{ stats.totalNodes }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>文档 + 模块 + 用例</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">总关联数</div>
        <div class="stat-value">{{ stats.totalEdges }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>跨模块关联</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">覆盖率</div>
        <div class="stat-value">{{ stats.coverage }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>全部文档已关联</div>
      </div>
    </div>

    <!-- 图谱列表 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">知识图谱列表</div>
        <div style="display:flex;gap:8px">
          <el-select v-model="filterProjectId" size="small" style="width:160px" placeholder="全部项目" clearable @change="loadGraphs">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
      </div>
      <el-table :data="graphs" style="width:100%" @row-click="goToDetail" v-loading="loading">
        <el-table-column label="图谱名称" min-width="200">
          <template #default="{ row }">
            <div class="graph-name">
              <el-icon :size="15" :style="{ color: row.iconColor || 'var(--accent)' }"><Share /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="所属项目" width="140" />
        <el-table-column label="Sprint" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.sprint_name" type="primary" size="small" effect="plain" round>{{ row.sprint_name }}</el-tag>
            <span v-else style="color:var(--color-text-tertiary)">-</span>
          </template>
        </el-table-column>
        <el-table-column label="节点数" width="80">
          <template #default="{ row }">
            <span class="mono-val">{{ row.node_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="关联数" width="80">
          <template #default="{ row }">
            <span class="mono-val">{{ row.edge_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="生成时间" width="120">
          <template #default="{ row }">
            {{ formatTime(row.generated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === '最新' ? 'success' : 'warning'" size="small" effect="plain" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="action-btns" @click.stop>
              <el-button v-if="row.status === '需更新'" type="primary" link size="small" @click="handleRefresh(row)">
                <el-icon><Refresh /></el-icon>刷新
              </el-button>
              <el-button type="primary" link size="small" @click="goToDetail(row)">
                <el-icon><View /></el-icon>查看
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && graphs.length === 0" description="暂无图谱数据，请在 AI 工作台中生成" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Folder, Share, View, Refresh, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getProjects } from '../../api/project'
import { getGraphs, getGraphStats, regenerateGraph } from '../../api/graph'

const router = useRouter()
const regenerating = ref(false)
const loading = ref(false)
const selectedProject = ref(null)
const filterProjectId = ref('')
const currentProjectStatus = ref('')

const projects = ref([])
const graphs = ref([])

const stats = reactive({
  totalGraphs: 0,
  totalNodes: 0,
  totalEdges: 0,
  coverage: '0%'
})

const GRAPH_COLORS = ['var(--accent)', '#378ADD', '#8B5CF6', '#EF9F27', '#10B981', '#F43F5E']

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

function onProjectChange(pid) {
  const p = projects.value.find(p => p.id === pid)
  currentProjectStatus.value = p?.status || ''
  filterProjectId.value = pid
  loadGraphs()
}

async function loadProjects() {
  try {
    const res = await getProjects()
    projects.value = res.data?.data || res.data || []
    if (projects.value.length > 0 && !selectedProject.value) {
      selectedProject.value = projects.value[0].id
      currentProjectStatus.value = projects.value[0].status || ''
    }
  } catch (e) {
    console.error('加载项目失败', e)
  }
}

async function loadGraphs() {
  loading.value = true
  try {
    const params = {}
    if (filterProjectId.value) params.project_id = filterProjectId.value
    else if (selectedProject.value) params.project_id = selectedProject.value
    const res = await getGraphs(params)
    const list = res.data?.data || res.data || []
    graphs.value = list.map((g, i) => ({
      ...g,
      iconColor: GRAPH_COLORS[i % GRAPH_COLORS.length]
    }))
  } catch (e) {
    console.error('加载图谱失败', e)
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const res = await getGraphStats()
    const s = res.data?.data || res.data || {}
    stats.totalGraphs = s.total_graphs ?? 0
    stats.totalNodes = s.total_nodes ?? 0
    stats.totalEdges = s.total_edges ?? 0
    stats.coverage = s.coverage ?? '0%'
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

function goToDetail(row) {
  router.push(`/graphs/${row.id}`)
}

async function handleRegenerate() {
  regenerating.value = true
  try {
    // 对当前筛选条件下的第一张图谱触发重新生成
    if (graphs.value.length > 0) {
      await regenerateGraph(graphs.value[0].id)
      ElMessage.success('图谱重新生成完成')
      await loadGraphs()
      await loadStats()
    } else {
      ElMessage.info('暂无图谱可重新生成')
    }
  } catch (e) {
    ElMessage.error('重新生成失败')
  } finally {
    regenerating.value = false
  }
}

async function handleRefresh(row) {
  try {
    await regenerateGraph(row.id)
    ElMessage.success(`"${row.name}" 已刷新`)
    await loadGraphs()
    await loadStats()
  } catch (e) {
    ElMessage.error('刷新失败')
  }
}

onMounted(async () => {
  await loadProjects()
  await Promise.all([loadGraphs(), loadStats()])
})
</script>

<style scoped>
.graph-list { max-width: 1400px; }

.project-context-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-lg);
  margin-bottom: 16px;
}

.project-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-notice {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: var(--accent-light, #EBF5FF);
  border-radius: var(--border-radius-md, 8px);
  border: 1px solid rgba(37,99,235,0.15);
}

.graph-name {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--accent);
  cursor: pointer;
}

.graph-name:hover { text-decoration: underline; }

.mono-val {
  font-family: var(--font-mono, monospace);
  font-weight: 500;
}

.action-btns { display: flex; gap: 4px; }
.el-table { cursor: pointer; }
</style>
