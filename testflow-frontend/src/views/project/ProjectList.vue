<template>
  <div class="project-list">
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-label">进行中项目</div><div class="stat-value">{{ stats.activeProjects }}</div><div class="stat-sub"><span class="stat-dot dot-green"></span>全部正常运行</div></div>
      <div class="stat-card"><div class="stat-label">总测试用例</div><div class="stat-value">{{ stats.totalCases }}</div><div class="stat-sub"><span class="stat-dot dot-blue"></span>本月新增 +{{ stats.newCases }}</div></div>
      <div class="stat-card"><div class="stat-label">通过率</div><div class="stat-value">{{ stats.passRate }}%</div><div class="stat-sub"><span class="stat-dot dot-amber"></span>较上周 +{{ stats.passRateChange }}%</div></div>
      <div class="stat-card"><div class="stat-label">待修复缺陷</div><div class="stat-value">{{ stats.pendingBugs }}</div><div class="stat-sub"><span class="stat-dot dot-red"></span>严重 {{ stats.severeBugs }} / 普通 {{ stats.normalBugs }}</div></div>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title">项目列表</div></div>
      <el-table :data="filteredProjects" style="width: 100%" @row-click="goToDetail" v-loading="loading">
        <el-table-column prop="name" label="项目名称" min-width="200" />
        <el-table-column label="进度" width="200">
          <template #default="{ row }"><div style="display: flex; align-items: center; gap: 8px"><el-progress :percentage="row.progress" :stroke-width="5" :show-text="false" style="flex: 1" /><span style="font-size: 12px; color: var(--color-text-secondary); white-space: nowrap">{{ row.progress }}%</span></div></template>
        </el-table-column>
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column prop="owner" label="负责人" width="100" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="创建时间" width="120"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }"><div class="action-btns" @click.stop><el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button><el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button></div></template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建对话框 -->
    <el-dialog v-model="createVisible" title="新建项目" width="520px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="项目名称"><el-input v-model="createForm.name" placeholder="请输入项目名称" /></el-form-item>
        <el-form-item label="项目描述"><el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入项目描述" /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="状态"><el-select v-model="createForm.status" style="width: 100%"><el-option label="待启动" value="pending" /><el-option label="进行中" value="active" /><el-option label="测试中" value="testing" /></el-select></el-form-item>
          <el-form-item label="进度"><el-input-number v-model="createForm.progress" :min="0" :max="100" style="width: 100%" /></el-form-item>
        </div>
      </el-form>
      <template #footer><el-button @click="createVisible = false">取消</el-button><el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button></template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑项目" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="项目名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="项目描述"><el-input v-model="editForm.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="负责人"><el-input v-model="editForm.owner" placeholder="请输入负责人（选填）" /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="状态"><el-select v-model="editForm.status" style="width: 100%"><el-option label="待启动" value="pending" /><el-option label="进行中" value="active" /><el-option label="测试中" value="testing" /><el-option label="已完成" value="completed" /></el-select></el-form-item>
          <el-form-item label="进度"><el-input-number v-model="editForm.progress" :min="0" :max="100" style="width: 100%" /></el-form-item>
        </div>
      </el-form>
      <template #footer><el-button @click="editVisible = false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjects, createProject, updateProject, deleteProject } from '../../api/project'
import { getDashboardStats } from '../../api/dashboard'

const router = useRouter()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)
const stats = ref({ activeProjects: 0, totalCases: 0, newCases: 0, passRate: 0, passRateChange: 0, pendingBugs: 0, severeBugs: 0, normalBugs: 0 })
const projects = ref([])

const createVisible = ref(false)
const createForm = reactive({ name: '', description: '', status: 'pending', progress: 0 })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '', description: '', status: '', progress: 0, owner: '' })

function getStatusType(s) { return { testing: '', completed: 'success', active: 'warning', pending: 'info' }[s] || 'info' }
function getStatusText(s) { return { testing: '测试中', completed: '已完成', active: '进行中', pending: '待启动' }[s] || s }
function formatDate(d) { return d ? d.split('T')[0] : '' }
function goToDetail(row) { router.push(`/projects/${row.id}`) }

const filteredProjects = computed(() => {
  const keyword = appStore.searchKeyword?.trim().toLowerCase()
  if (!keyword) return projects.value
  return projects.value.filter(p => p.name?.toLowerCase().includes(keyword))
})

function openCreateDialog() {
  Object.assign(createForm, { name: '', description: '', status: 'pending', progress: 0 })
  createVisible.value = true
}

async function handleCreate() {
  creating.value = true
  try {
    await createProject({ ...createForm })
    const res = await getProjects()
    projects.value = res.data
    ElMessage.success('创建成功')
    createVisible.value = false
    appStore.refreshSidebarBadges()
  } catch (e) { ElMessage.error('创建失败') } finally { creating.value = false }
}

function handleEdit(row) {
  editId.value = row.id
  Object.assign(editForm, { name: row.name, description: row.description, status: row.status, progress: row.progress, owner: row.owner || '' })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    await updateProject(editId.value, { ...editForm })
    const res = await getProjects()
    projects.value = res.data
    ElMessage.success('保存成功')
    editVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除项目"${row.name}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteProject(row.id); projects.value.splice(index, 1); ElMessage.success('删除成功'); appStore.refreshSidebarBadges() }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('projects', '项目管理', '新建项目', openCreateDialog)
  loading.value = true
  try {
    const [projRes, statsRes] = await Promise.allSettled([getProjects(), getDashboardStats()])
    if (projRes.status === 'fulfilled') projects.value = projRes.value.data
    if (statsRes.status === 'fulfilled') stats.value = statsRes.value.data
  } catch (e) { console.error(e) } finally { loading.value = false }
})
</script>

<style scoped>
.project-list { max-width: 1400px; }
.el-table { cursor: pointer; }
.action-btns { display: flex; gap: 4px; }
</style>
