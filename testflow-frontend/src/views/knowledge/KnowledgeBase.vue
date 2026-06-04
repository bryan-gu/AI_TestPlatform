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
        <div class="stat-sub"><span class="stat-dot dot-amber"></span>项目级汇总</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">功能点</div>
        <div class="stat-value">{{ stats.featurePointCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>AI 提取</div>
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
        <el-table-column label="更新时间" width="120">
          <template #default="{ row }">{{ formatDate(row.updatedAt || row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <div class="action-btns" @click.stop>
              <el-button v-if="row.isAll" type="primary" link size="small" @click="goToGraphList">
                <el-icon><Share /></el-icon>图谱
              </el-button>
              <template v-else>
                <el-button type="primary" link size="small" @click="handleEdit(row)">
                  <el-icon><Edit /></el-icon>编辑
                </el-button>
                <el-button type="danger" link size="small" @click="handleDelete(row)">
                  <el-icon><Delete /></el-icon>删除
                </el-button>
              </template>
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
import { Folder, Plus, Edit, Delete, Promotion, CopyDocument, Share } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjects } from '../../api/project'
import { getSprints, getSprintStats, createSprint, updateSprint, deleteSprint } from '../../api/sprint'

const router = useRouter()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)

const selectedProject = ref(null)
const currentProjectStatus = ref('')
const projectOptions = ref([])

const stats = ref({
  sprintCount: 0,
  moduleCount: 0,
  totalDocs: 0,
  featurePointCount: 0,
})

const sprints = ref([])

const createVisible = ref(false)
const createForm = reactive({ name: '', description: '' })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '', description: '' })

function formatDate(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function getSprintStatusType(status) {
  const map = { '基线': 'info', '已完成': 'success', '进行中': '', '最新汇总': 'warning', '待启动': 'info' }
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

async function loadData() {
  if (!selectedProject.value) return
  loading.value = true
  try {
    const [sprintRes, statsRes] = await Promise.all([
      getSprints({ project_id: selectedProject.value }),
      getSprintStats(selectedProject.value),
    ])
    sprints.value = sprintRes.data || []
    stats.value = statsRes.data || { sprintCount: 0, moduleCount: 0, totalDocs: 0, featurePointCount: 0 }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!createForm.name.trim()) {
    ElMessage.warning('请输入 Sprint 名称')
    return
  }
  creating.value = true
  try {
    await createSprint({
      name: createForm.name,
      description: createForm.description,
      project_id: selectedProject.value,
    })
    ElMessage.success('创建成功')
    createVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

function handleEdit(row) {
  editId.value = row.id
  Object.assign(editForm, { name: row.name, description: row.description || '' })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    await updateSprint(editId.value, { name: editForm.name, description: editForm.description })
    ElMessage.success('保存成功')
    editVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除 Sprint"${row.name}"吗？关联的文档也将被删除。`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteSprint(row.id)
      ElMessage.success('删除成功')
      await loadData()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

function handleProjectChange(id) {
  const proj = projectOptions.value.find(p => p.id === id)
  if (proj) currentProjectStatus.value = proj.status || ''
  loadData()
}

// 监听搜索关键词
let loadTimer = null
watch(() => appStore.searchKeyword, (kw) => {
  if (loadTimer) clearTimeout(loadTimer)
  loadTimer = setTimeout(async () => {
    if (!selectedProject.value) return
    loading.value = true
    try {
      const res = await getSprints({ project_id: selectedProject.value, keyword: kw || undefined })
      sprints.value = res.data || []
    } catch (e) { console.error(e) } finally { loading.value = false }
  }, 300)
})

onMounted(async () => {
  appStore.setCurrentPage('knowledge', '知识库', '新建 Sprint', openCreateDialog)
  try {
    const projRes = await getProjects()
    if (projRes.data?.length) {
      projectOptions.value = projRes.data.map(p => ({
        id: p.id, name: p.name, status: p.status || '进行中',
      }))
      selectedProject.value = projectOptions.value[0].id
      currentProjectStatus.value = projectOptions.value[0].status
      await loadData()
    }
  } catch (e) { console.error(e) }
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
