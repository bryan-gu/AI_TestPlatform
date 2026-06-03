<template>
  <div class="graph-list">
    <!-- 项目上下文栏 -->
    <div class="project-context-bar">
      <div class="project-icon">
        <el-icon :size="16" style="color:var(--accent)"><Folder /></el-icon>
      </div>
      <div style="flex:1">
        <div style="display:flex;align-items:center;gap:8px">
          <el-select v-model="selectedProject" style="width:200px" size="small">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-tag type="primary" size="small" effect="plain" round>{{ currentProjectStatus }}</el-tag>
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
          <el-select v-model="filterProject" size="small" style="width:160px" placeholder="全部项目">
            <el-option label="全部项目" value="" />
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
      </div>
      <el-table :data="filteredGraphs" style="width:100%" @row-click="goToDetail">
        <el-table-column label="图谱名称" min-width="200">
          <template #default="{ row }">
            <div class="graph-name">
              <el-icon :size="15" :style="{ color: row.iconColor }"><Share /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="project" label="所属项目" width="140" />
        <el-table-column label="Sprint" width="100">
          <template #default="{ row }">
            <el-tag type="primary" size="small" effect="plain" round>{{ row.sprint }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="节点数" width="80">
          <template #default="{ row }">
            <span class="mono-val">{{ row.nodeCount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="关联数" width="80">
          <template #default="{ row }">
            <span class="mono-val">{{ row.edgeCount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="generatedAt" label="生成时间" width="120" />
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
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Folder, Share, View, Refresh, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const regenerating = ref(false)
const selectedProject = ref(1)
const filterProject = ref('')
const currentProjectStatus = ref('测试中')

const projects = ref([
  { id: 1, name: '电商平台 v3.0', status: '测试中' },
  { id: 2, name: '支付系统', status: '已完成' },
  { id: 3, name: '用户中心重构', status: '进行中' },
  { id: 4, name: '推荐算法 A/B', status: '待启动' }
])

const stats = reactive({
  totalGraphs: 4,
  totalNodes: 29,
  totalEdges: 47,
  coverage: '100%'
})

const graphs = ref([
  { id: 1, name: '电商平台需求图谱', project: '电商平台 v3.0', sprint: 'sprint_all', nodeCount: 10, edgeCount: 14, generatedAt: '今天 10:30', status: '最新', iconColor: 'var(--accent)' },
  { id: 2, name: '支付系统接口图谱', project: '支付系统', sprint: 'sprint_all', nodeCount: 8, edgeCount: 11, generatedAt: '昨天 16:20', status: '最新', iconColor: '#378ADD' },
  { id: 3, name: '用户中心重构图谱', project: '用户中心重构', sprint: 'sprint_all', nodeCount: 6, edgeCount: 9, generatedAt: '3 天前', status: '最新', iconColor: '#8B5CF6' },
  { id: 4, name: '推荐算法实验图谱', project: '推荐算法 A/B', sprint: 'sprint_all', nodeCount: 5, edgeCount: 7, generatedAt: '1 周前', status: '需更新', iconColor: '#EF9F27' }
])

const filteredGraphs = computed(() => {
  if (!filterProject.value) return graphs.value
  return graphs.value.filter(g => g.project === projects.value.find(p => p.id === filterProject.value)?.name)
})

function goToDetail(row) {
  router.push(`/graphs/${row.id}`)
}

async function handleRegenerate() {
  regenerating.value = true
  try {
    await new Promise(r => setTimeout(r, 2000))
    ElMessage.success('图谱重新生成完成')
  } catch (e) {
    ElMessage.error('重新生成失败')
  } finally {
    regenerating.value = false
  }
}

function handleRefresh(row) {
  ElMessage.info(`正在刷新"${row.name}"...`)
}

onMounted(() => {
  // TODO: 从API获取数据
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
