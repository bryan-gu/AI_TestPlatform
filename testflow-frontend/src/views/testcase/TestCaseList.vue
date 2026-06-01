<template>
  <div class="testcase-list">
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-label">全部用例</div><div class="stat-value">{{ stats.total }}</div><div class="stat-sub"><span class="stat-dot dot-blue"></span>跨 {{ stats.projectCount }} 个项目</div></div>
      <div class="stat-card"><div class="stat-label">已通过</div><div class="stat-value">{{ stats.passed }}</div><div class="stat-sub"><span class="stat-dot dot-green"></span>通过率 {{ stats.passRate }}%</div></div>
      <div class="stat-card"><div class="stat-label">未通过</div><div class="stat-value">{{ stats.failed }}</div><div class="stat-sub"><span class="stat-dot dot-red"></span>需要处理</div></div>
      <div class="stat-card"><div class="stat-label">未执行</div><div class="stat-value">{{ stats.pending }}</div><div class="stat-sub"><span class="stat-dot dot-amber"></span>待排期</div></div>
    </div>

    <div class="card">
      <div class="card-head">
        <div class="card-title">测试用例列表</div>
        <el-select v-model="selectedProject" placeholder="全部项目" size="small" style="width: 150px" clearable @change="loadCases">
          <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.name" />
        </el-select>
      </div>
      <el-table :data="testCases" style="width: 100%" v-loading="loading">
        <el-table-column prop="case_no" label="用例编号" width="100" />
        <el-table-column prop="title" label="用例标题" min-width="250" show-overflow-tooltip />
        <el-table-column label="优先级" width="80"><template #default="{ row }"><span :class="getPriorityClass(row.priority)">{{ row.priority }}</span></template></el-table-column>
        <el-table-column label="执行状态" width="100"><template #default="{ row }"><el-tag :type="getExecStatusType(row.exec_status)" size="small">{{ row.exec_status }}</el-tag></template></el-table-column>
        <el-table-column prop="executor" label="执行人" width="80"><template #default="{ row }">{{ row.executor || '-' }}</template></el-table-column>
        <el-table-column label="更新时间" width="120"><template #default="{ row }">{{ formatDate(row.updated_at) }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }"><div class="action-btns"><el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button><el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button></div></template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建对话框 -->
    <el-dialog v-model="createVisible" title="新建用例" width="520px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="用例标题"><el-input v-model="createForm.title" placeholder="请输入用例标题" /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="优先级"><el-select v-model="createForm.priority" style="width: 100%"><el-option label="高" value="高" /><el-option label="中" value="中" /><el-option label="低" value="低" /></el-select></el-form-item>
          <el-form-item label="所属项目"><el-select v-model="createForm.project_id" style="width: 100%"><el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" /></el-select></el-form-item>
        </div>
      </el-form>
      <template #footer><el-button @click="createVisible = false">取消</el-button><el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button></template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑用例" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用例标题"><el-input v-model="editForm.title" /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="优先级"><el-select v-model="editForm.priority" style="width: 100%"><el-option label="高" value="高" /><el-option label="中" value="中" /><el-option label="低" value="低" /></el-select></el-form-item>
          <el-form-item label="执行状态"><el-select v-model="editForm.exec_status" style="width: 100%"><el-option label="通过" value="通过" /><el-option label="失败" value="失败" /><el-option label="执行中" value="执行中" /><el-option label="待执行" value="待执行" /></el-select></el-form-item>
        </div>
      </el-form>
      <template #footer><el-button @click="editVisible = false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTestCases, getTestCaseStats, createTestCase, updateTestCase, deleteTestCase } from '../../api/testcase'
import { getProjects } from '../../api/project'

const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)
const stats = ref({ total: 0, projectCount: 0, passed: 0, passRate: 0, failed: 0, pending: 0 })
const selectedProject = ref('')
const projectOptions = ref([])
const testCases = ref([])

const createVisible = ref(false)
const createForm = reactive({ title: '', priority: '中', project_id: null })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ title: '', priority: '', exec_status: '' })

function getPriorityClass(p) { return { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }[p] || 'badge badge-gray' }
function getExecStatusType(s) { return { 通过: 'success', 失败: 'danger', 执行中: 'warning', 待执行: 'info' }[s] || 'info' }
function formatDate(d) { return d ? d.split('T')[0] : '' }

async function loadCases() {
  loading.value = true
  try { testCases.value = (await getTestCases(selectedProject.value || undefined)).data } catch (e) { console.error(e) } finally { loading.value = false }
}

function openCreateDialog() {
  Object.assign(createForm, { title: '', priority: '中', project_id: null })
  createVisible.value = true
}

async function handleCreate() {
  creating.value = true
  try {
    await createTestCase({ ...createForm })
    await loadCases()
    ElMessage.success('创建成功')
    createVisible.value = false
  } catch (e) { ElMessage.error('创建失败') } finally { creating.value = false }
}

function handleEdit(row) { editId.value = row.id; Object.assign(editForm, { title: row.title, priority: row.priority, exec_status: row.exec_status }); editVisible.value = true }

async function handleSave() {
  saving.value = true
  try { await updateTestCase(editId.value, { ...editForm }); await loadCases(); ElMessage.success('保存成功'); editVisible.value = false } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除用例"${row.case_no}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteTestCase(row.id); testCases.value.splice(index, 1); ElMessage.success('删除成功') }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('testcases', '测试用例', '新建用例', openCreateDialog)
  loading.value = true
  try {
    const [casesRes, statsRes, projRes] = await Promise.allSettled([getTestCases(), getTestCaseStats(), getProjects()])
    if (casesRes.status === 'fulfilled') testCases.value = casesRes.value.data
    if (statsRes.status === 'fulfilled') stats.value = statsRes.value.data
    if (projRes.status === 'fulfilled') projectOptions.value = projRes.value.data
  } catch (e) { console.error(e) } finally { loading.value = false }
})
</script>

<style scoped>
.testcase-list { max-width: 1400px; }
.action-btns { display: flex; gap: 4px; }
</style>
