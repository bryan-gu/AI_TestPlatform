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
        <div style="display:flex;gap:8px">
          <el-select v-model="selectedProject" placeholder="全部项目" size="small" style="width: 150px" clearable @change="loadCases">
            <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.name" />
          </el-select>
          <el-button type="primary" size="small" @click="handleBatchExecute" :loading="batchExecuting">
            <el-icon><VideoPlay /></el-icon>批量执行
          </el-button>
          <el-button size="small" @click="handleDownloadTemplate" :loading="downloading">
            <el-icon><Download /></el-icon>下载模板
          </el-button>
          <el-button size="small" @click="openImportDialog">
            <el-icon><Download /></el-icon>导入
          </el-button>
          <el-button type="success" size="small" @click="handleExport" :loading="exporting">
            <el-icon><Upload /></el-icon>导出
          </el-button>
        </div>
      </div>
      <el-table :data="testCases" style="width: 100%" v-loading="loading" row-key="id">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <div class="expand-row">
                <div class="expand-label">前置条件</div>
                <div class="expand-value">{{ row.preconditions || '无' }}</div>
              </div>
              <div class="expand-row">
                <div class="expand-label">测试数据</div>
                <div class="expand-value">{{ row.test_data || '无' }}</div>
              </div>
              <div class="expand-row">
                <div class="expand-label">测试步骤</div>
                <div class="expand-value"><pre class="steps-pre">{{ row.test_steps || '无' }}</pre></div>
              </div>
              <div class="expand-row">
                <div class="expand-label">预期结果</div>
                <div class="expand-value">{{ row.expected_result || '无' }}</div>
              </div>
              <div class="expand-row">
                <div class="expand-label">实际结果</div>
                <div class="expand-value">{{ row.actual_result || '无' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="case_no" label="用例编号" width="160" />
        <el-table-column prop="module" label="模块" width="80">
          <template #default="{ row }">{{ row.module || '-' }}</template>
        </el-table-column>
        <el-table-column prop="title" label="用例标题" min-width="250" show-overflow-tooltip />
        <el-table-column label="优先级" width="80"><template #default="{ row }"><span :class="getPriorityClass(row.priority)">{{ row.priority }}</span></template></el-table-column>
        <el-table-column label="执行状态" width="100"><template #default="{ row }"><el-tag :type="getExecStatusType(row.exec_status)" size="small">{{ row.exec_status }}</el-tag></template></el-table-column>
        <el-table-column prop="executor" label="执行人" width="80"><template #default="{ row }">{{ row.executor || '-' }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }"><div class="action-btns"><el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button><el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button></div></template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建对话框 -->
    <el-dialog v-model="createVisible" title="新建用例" width="580px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="用例标题"><el-input v-model="createForm.title" placeholder="请输入用例标题" /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="优先级"><el-select v-model="createForm.priority" style="width: 100%"><el-option label="高" value="高" /><el-option label="中" value="中" /><el-option label="低" value="低" /></el-select></el-form-item>
          <el-form-item label="所属项目"><el-select v-model="createForm.project_id" style="width: 100%"><el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" /></el-select></el-form-item>
        </div>
        <el-form-item label="模块代码" required><el-input v-model="createForm.module" placeholder="英文/拼音缩写，如 DL、CFGM" maxlength="50" /></el-form-item>
        <el-form-item label="前置条件"><el-input v-model="createForm.preconditions" type="textarea" :rows="2" placeholder="请输入前置条件" /></el-form-item>
        <el-form-item label="测试数据"><el-input v-model="createForm.test_data" type="textarea" :rows="2" placeholder="测试所需数据，如：账号 admin，密码 123456" /></el-form-item>
        <el-form-item label="测试步骤"><el-input v-model="createForm.test_steps" type="textarea" :rows="3" placeholder="建议用编号列表格式，如：1. 打开登录页 2. 输入账号密码 3. 点击登录" /></el-form-item>
        <el-form-item label="预期结果"><el-input v-model="createForm.expected_result" type="textarea" :rows="2" placeholder="请输入预期结果" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="createVisible = false">取消</el-button><el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button></template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑用例" width="580px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用例标题"><el-input v-model="editForm.title" /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="优先级"><el-select v-model="editForm.priority" style="width: 100%"><el-option label="高" value="高" /><el-option label="中" value="中" /><el-option label="低" value="低" /></el-select></el-form-item>
          <el-form-item label="执行状态"><el-select v-model="editForm.exec_status" style="width: 100%"><el-option label="通过" value="通过" /><el-option label="失败" value="失败" /><el-option label="执行中" value="执行中" /><el-option label="待执行" value="待执行" /></el-select></el-form-item>
        </div>
        <el-form-item label="前置条件"><el-input v-model="editForm.preconditions" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="测试数据"><el-input v-model="editForm.test_data" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="测试步骤"><el-input v-model="editForm.test_steps" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="预期结果"><el-input v-model="editForm.expected_result" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="实际结果"><el-input v-model="editForm.actual_result" type="textarea" :rows="2" placeholder="执行后填写实际结果" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="editVisible = false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importVisible" title="导入测试用例" width="480px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="目标项目" required>
          <el-select v-model="importProjectId" placeholder="请选择项目" style="width: 100%">
            <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择文件" required>
          <el-upload
            ref="importUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-button size="small">选择文件</el-button>
            <template #tip><div class="el-upload__tip">仅支持 .xlsx 文件，请先下载模板填写数据</div></template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing">确认导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAppStore } from '../../stores/app'
import { Edit, Delete, VideoPlay, Download, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTestCases, getTestCaseStats, createTestCase, updateTestCase, deleteTestCase, batchExecuteTestCases, exportTestCases, downloadTemplate, importTestCases } from '../../api/testcase'
import { getProjects } from '../../api/project'

const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)
const batchExecuting = ref(false)
const exporting = ref(false)
const downloading = ref(false)
const importing = ref(false)
const importVisible = ref(false)
const importProjectId = ref(null)
const importFile = ref(null)
const importUploadRef = ref(null)
const stats = ref({ total: 0, projectCount: 0, passed: 0, passRate: 0, failed: 0, pending: 0 })
const selectedProject = ref('')
const projectOptions = ref([])
const testCases = ref([])

const createVisible = ref(false)
const createForm = reactive({ title: '', priority: '高', project_id: null, module: '', preconditions: '', test_data: '', test_steps: '', expected_result: '' })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ title: '', priority: '', exec_status: '', preconditions: '', test_data: '', test_steps: '', expected_result: '', actual_result: '' })

function getPriorityClass(p) { return { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }[p] || 'badge badge-gray' }
function getExecStatusType(s) { return { 通过: 'success', 失败: 'danger', 执行中: 'warning', 待执行: 'info' }[s] || 'info' }
function formatDate(d) { return d ? d.split('T')[0] : '' }

async function handleBatchExecute() {
  batchExecuting.value = true
  try {
    let projectId = null
    if (selectedProject.value) {
      const proj = projectOptions.value.find(p => p.name === selectedProject.value)
      if (proj) projectId = proj.id
    }
    const res = await batchExecuteTestCases(projectId)
    const count = res.data?.executed_count || 0
    ElMessage.success(`已批量执行 ${count} 条用例`)
    await loadCases()
    try { stats.value = (await getTestCaseStats()).data } catch (e) { /* ignore */ }
  } catch (e) {
    ElMessage.error('批量执行失败')
  } finally {
    batchExecuting.value = false
  }
}

// ── 导入导出 ──
function _triggerBlobDownload(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

async function handleExport() {
  exporting.value = true
  try {
    let projectId = null
    if (selectedProject.value) {
      const proj = projectOptions.value.find(p => p.name === selectedProject.value)
      if (proj) projectId = proj.id
    }
    const res = await exportTestCases(projectId)
    _triggerBlobDownload(res, 'testcases.xlsx')
    ElMessage.success('导出成功')
  } catch (e) { /* 拦截器已展示错误 */ } finally {
    exporting.value = false
  }
}

async function handleDownloadTemplate() {
  downloading.value = true
  try {
    const res = await downloadTemplate()
    _triggerBlobDownload(res, 'testcase_template.xlsx')
    ElMessage.success('模板下载成功')
  } catch (e) { /* 拦截器已展示错误 */ } finally {
    downloading.value = false
  }
}

function openImportDialog() {
  importProjectId.value = null
  importFile.value = null
  // 如果当前已选择项目，自动填入
  if (selectedProject.value) {
    const proj = projectOptions.value.find(p => p.name === selectedProject.value)
    if (proj) importProjectId.value = proj.id
  }
  importVisible.value = true
}

function handleFileChange(file) {
  importFile.value = file.raw
}

function handleFileRemove() {
  importFile.value = null
}

async function handleImport() {
  if (!importProjectId.value) {
    ElMessage.warning('请选择目标项目')
    return
  }
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  importing.value = true
  try {
    const res = await importTestCases(importProjectId.value, importFile.value)
    const data = res.data
    if (data.fail_count > 0) {
      const errorList = data.errors.map(e => `第 ${e.row} 行: ${e.reason}`).join('\n')
      ElMessageBox.alert(`成功导入 ${data.success_count} 条，失败 ${data.fail_count} 条：\n\n${errorList}`, '导入结果', { type: 'warning' })
    } else {
      ElMessage.success(`成功导入 ${data.success_count} 条用例`)
    }
    importVisible.value = false
    await loadCases()
    try { stats.value = (await getTestCaseStats()).data } catch (e) { /* ignore */ }
    appStore.refreshSidebarBadges()
  } catch (e) { /* 拦截器已展示错误 */ } finally {
    importing.value = false
  }
}

let loadTimer = null

async function loadCases() {
  loading.value = true
  try {
    const keyword = appStore.searchKeyword?.trim() || undefined
    testCases.value = (await getTestCases(selectedProject.value || undefined, keyword)).data
  } catch (e) { console.error(e) } finally { loading.value = false }
}

watch(() => appStore.searchKeyword, () => {
  if (loadTimer) clearTimeout(loadTimer)
  loadTimer = setTimeout(() => {
    loadCases()
  }, 300)
})

function openCreateDialog() {
  Object.assign(createForm, { title: '', priority: '高', project_id: null, module: '', preconditions: '', test_data: '', test_steps: '', expected_result: '' })
  createVisible.value = true
}

async function handleCreate() {
  if (!createForm.module.trim()) {
    ElMessage.warning('请填写模块代码')
    return
  }
  if (!/^[a-zA-Z0-9]+$/.test(createForm.module.trim())) {
    ElMessage.warning('模块代码只能包含英文字母和数字')
    return
  }
  creating.value = true
  try {
    await createTestCase({ ...createForm, module: createForm.module.trim().toUpperCase() })
    await loadCases()
    ElMessage.success('创建成功')
    createVisible.value = false
    appStore.refreshSidebarBadges()
  } catch (e) { ElMessage.error('创建失败') } finally { creating.value = false }
}

function handleEdit(row) {
  editId.value = row.id
  Object.assign(editForm, {
    title: row.title, priority: row.priority, exec_status: row.exec_status,
    preconditions: row.preconditions || '', test_data: row.test_data || '',
    test_steps: row.test_steps || '', expected_result: row.expected_result || '',
    actual_result: row.actual_result || '',
  })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try { await updateTestCase(editId.value, { ...editForm }); await loadCases(); ElMessage.success('保存成功'); editVisible.value = false } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除用例"${row.case_no}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteTestCase(row.id); await loadCases(); ElMessage.success('删除成功'); appStore.refreshSidebarBadges() }).catch(() => {})
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

.expand-content {
  padding: 12px 20px 16px 60px;
  background: #FAFBFC;
}

.expand-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13px;
}

.expand-row:last-child {
  margin-bottom: 0;
}

.expand-label {
  color: var(--color-text-tertiary);
  width: 70px;
  flex-shrink: 0;
  font-weight: 500;
}

.expand-value {
  color: var(--color-text-primary);
  flex: 1;
  white-space: pre-wrap;
  word-break: break-word;
}

.steps-pre {
  margin: 0;
  font-family: inherit;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
