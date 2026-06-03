<template>
  <div class="knowledge-base">
    <!-- 项目上下文栏 -->
    <div class="project-context-bar">
      <div class="project-icon">
        <el-icon :size="16" style="color: var(--accent)"><Folder /></el-icon>
      </div>
      <div style="flex:1">
        <div style="display:flex;align-items:center;gap:8px">
          <el-select
            v-model="selectedProject"
            style="width:200px"
            size="small"
            @change="handleProjectChange"
          >
            <el-option
              v-for="p in projectOptions"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
          <span class="badge badge-blue" style="font-size:10px">{{ currentProjectStatus }}</span>
        </div>
        <div style="font-size:12px;color:var(--color-text-secondary);margin-top:2px">
          知识库按 Sprint 组织 · 每个 Sprint 是独立快照 · 共 {{ stats.sprintCount }} 个 Sprint、{{ stats.totalDocs }} 篇文档
        </div>
      </div>
      <el-button type="primary" size="small" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>新建 Sprint
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="stat-card">
        <div class="stat-label">Sprint 数</div>
        <div class="stat-value">{{ stats.sprintCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>含 sprint_all</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">模块数</div>
        <div class="stat-value">{{ stats.moduleCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>全部已关联</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">文档总数</div>
        <div class="stat-value">{{ stats.totalDocs }}</div>
        <div class="stat-sub"><span class="stat-dot dot-amber"></span>本月新增 {{ stats.newDocs }} 篇</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">功能点</div>
        <div class="stat-value">{{ stats.featurePoints }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>AI 已提取</div>
      </div>
    </div>

    <!-- Sprint 知识快照表格 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">Sprint 知识快照</div>
      </div>
      <el-table :data="sprints" style="width:100%" @row-click="goToDetail" v-loading="loading">
        <el-table-column label="Sprint" min-width="180">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px">
              <el-icon :size="15" :style="{ color: row.isAll ? '#8B5CF6' : 'var(--accent)' }">
                <component :is="row.isAll ? 'CopyDocument' : 'Promotion'" />
              </el-icon>
              <strong>{{ row.name }}</strong>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getSprintStatusType(row.status)" size="small" effect="plain" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="moduleCount" label="模块数" width="80" />
        <el-table-column prop="docCount" label="文档数" width="80" />
        <el-table-column prop="featurePoints" label="功能点" width="80" />
        <el-table-column prop="graphNodes" label="图谱节点" width="90" />
        <el-table-column label="更新时间" width="120">
          <template #default="{ row }">{{ row.updatedAt }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <div class="action-btns" @click.stop>
              <el-button v-if="row.isAll" type="primary" link size="small" @click="goToGraphList(row)">
                <el-icon><Share /></el-icon>图谱
              </el-button>
              <el-button v-else type="primary" link size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建 Sprint 对话框 -->
    <el-dialog v-model="createVisible" title="新建 Sprint" width="520px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="Sprint 名称">
          <el-input v-model="createForm.name" placeholder="例如：Sprint 3" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑 Sprint 对话框 -->
    <el-dialog v-model="editVisible" title="编辑 Sprint" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="Sprint 名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Folder, Plus, Edit, Promotion, CopyDocument, Share } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getProjects } from '../../api/project'

const router = useRouter()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)

const selectedProject = ref(1)
const currentProjectStatus = ref('测试中')
const projectOptions = ref([
  { id: 1, name: '电商平台 v3.0', status: '测试中' },
  { id: 2, name: '支付系统', status: '已完成' },
  { id: 3, name: '用户中心重构', status: '进行中' },
  { id: 4, name: '推荐算法 A/B', status: '待启动' }
])

const stats = ref({
  sprintCount: 4,
  moduleCount: 12,
  totalDocs: 36,
  newDocs: 8,
  featurePoints: 89
})

// Sprint 数据 (Mock)
const sprints = ref([
  {
    id: 'sprint-0', name: 'Sprint 0', status: '基线', moduleCount: 3, docCount: 8,
    featurePoints: 21, graphNodes: 15, updatedAt: '2026-03-15', isAll: false
  },
  {
    id: 'sprint-1', name: 'Sprint 1', status: '已完成', moduleCount: 5, docCount: 12,
    featurePoints: 34, graphNodes: 22, updatedAt: '2026-04-01', isAll: false
  },
  {
    id: 'sprint-2', name: 'Sprint 2', status: '进行中', moduleCount: 4, docCount: 10,
    featurePoints: 23, graphNodes: 18, updatedAt: '今天 10:30', isAll: false
  },
  {
    id: 'sprint-all', name: 'sprint_all', status: '最新汇总', moduleCount: 12, docCount: 36,
    featurePoints: 89, graphNodes: 29, updatedAt: '自动同步', isAll: true
  }
])

const createVisible = ref(false)
const createForm = reactive({ name: '', description: '' })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '', description: '' })

function getSprintStatusType(status) {
  const map = { '基线': 'info', '已完成': 'success', '进行中': '', '最新汇总': 'warning' }
  return map[status] || 'info'
}

function goToDetail(row) {
  if (row.isAll) {
    router.push('/graphs')
  } else {
    router.push(`/knowledge/${row.id}`)
  }
}

function goToGraphList() {
  router.push('/graphs')
}

function openCreateDialog() {
  Object.assign(createForm, { name: '', description: '' })
  createVisible.value = true
}

async function handleCreate() {
  creating.value = true
  try {
    // TODO: 调用API
    await new Promise(r => setTimeout(r, 500))
    sprints.value.splice(sprints.value.length - 1, 0, {
      id: `sprint-${Date.now()}`, name: createForm.name, status: '待启动',
      moduleCount: 0, docCount: 0, featurePoints: 0, graphNodes: 0,
      updatedAt: new Date().toISOString().split('T')[0], isAll: false
    })
    stats.value.sprintCount++
    ElMessage.success('创建成功')
    createVisible.value = false
  } catch (e) { ElMessage.error('创建失败') } finally { creating.value = false }
}

function handleEdit(row) {
  editId.value = row.id
  Object.assign(editForm, { name: row.name, description: '' })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    // TODO: 调用API
    await new Promise(r => setTimeout(r, 500))
    const sprint = sprints.value.find(s => s.id === editId.value)
    if (sprint) sprint.name = editForm.name
    ElMessage.success('保存成功')
    editVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleProjectChange(id) {
  const proj = projectOptions.value.find(p => p.id === id)
  if (proj) currentProjectStatus.value = proj.status
  // TODO: 重新加载该项目的Sprint数据
}

// 监听搜索关键词
let loadTimer = null
watch(() => appStore.searchKeyword, () => {
  if (loadTimer) clearTimeout(loadTimer)
  loadTimer = setTimeout(() => {
    // TODO: 搜索过滤Sprint
  }, 300)
})

onMounted(async () => {
  appStore.setCurrentPage('knowledge', '知识库', '新建 Sprint', openCreateDialog)
  loading.value = true
  try {
    const projRes = await Promise.allSettled([getProjects()])
    if (projRes[0].status === 'fulfilled' && projRes[0].value.data?.length) {
      projectOptions.value = projRes[0].value.data.map(p => ({
        id: p.id, name: p.name, status: p.status || '进行中'
      }))
      if (projectOptions.value.length > 0) {
        selectedProject.value = projectOptions.value[0].id
        currentProjectStatus.value = projectOptions.value[0].status
      }
    }
  } catch (e) { console.error(e) } finally { loading.value = false }
})
</script>

<style scoped>
.knowledge-base { max-width: 1400px; }

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

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.badge-blue {
  background: #E6F1FB;
  color: #378ADD;
}

.action-btns { display: flex; gap: 4px; }
.el-table { cursor: pointer; }
</style>
