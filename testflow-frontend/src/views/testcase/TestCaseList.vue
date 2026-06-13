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
          <el-select v-model="selectedProject" placeholder="全部项目" size="small" style="width: 150px" clearable @change="handleProjectFilterChange">
            <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.name" />
          </el-select>
          <el-select v-model="selectedSprintId" placeholder="全部 Sprint" size="small" style="width: 150px" clearable @change="loadCases">
            <el-option v-for="s in sprintOptions" :key="s.id" :label="s.name" :value="s.id" />
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
        <el-table-column label="模块" width="120">
          <template #default="{ row }">
            <span v-if="row.module_name">{{ row.module_name }}</span>
            <span v-else-if="row.module">{{ row.module }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="用例标题" min-width="250" show-overflow-tooltip />
        <el-table-column label="Sprint" width="120"><template #default="{ row }">{{ row.sprint_name || '-' }}</template></el-table-column>
        <el-table-column label="来源" width="90"><template #default="{ row }">{{ getSourceText(row.source) }}</template></el-table-column>
        <el-table-column label="自动化" width="100"><template #default="{ row }"><el-tag :type="getAutomationStatusType(row.automation_status)" size="small">{{ getAutomationStatusText(row.automation_status) }}</el-tag></template></el-table-column>
        <el-table-column label="优先级" width="80"><template #default="{ row }"><span :class="getPriorityClass(row.priority)">{{ row.priority }}</span></template></el-table-column>
        <el-table-column label="执行状态" width="100"><template #default="{ row }"><el-tag :type="getExecStatusType(row.exec_status)" size="small">{{ row.exec_status }}</el-tag></template></el-table-column>
        <el-table-column prop="executor" label="执行人" width="80"><template #default="{ row }">{{ row.executor || '-' }}</template></el-table-column>
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="{ row, $index }"><div class="action-btns"><el-button type="primary" link size="small" @click="openDetail(row)"><el-icon><View /></el-icon>详情</el-button><el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button><el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button></div></template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建对话框 -->
    <el-dialog v-model="createVisible" title="新建用例" width="580px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="用例标题"><el-input v-model="createForm.title" placeholder="请输入用例标题" /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="优先级"><el-select v-model="createForm.priority" style="width: 100%"><el-option label="高" value="高" /><el-option label="中" value="中" /><el-option label="低" value="低" /></el-select></el-form-item>
          <el-form-item label="所属项目"><el-select v-model="createForm.project_id" style="width: 100%" @change="onCreateProjectChange"><el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" /></el-select></el-form-item>
        </div>
        <el-form-item label="所属模块" required>
          <el-select v-model="createForm.module_id" style="width: 100%" placeholder="选择模块" clearable filterable @change="onModuleSelect">
            <el-option v-for="m in createModuleOptions" :key="m.id" :label="`${m.name} (${m.code})`" :value="m.id" />
          </el-select>
        </el-form-item>
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
        <el-form-item label="所属模块">
          <el-select v-model="editForm.module_id" style="width: 100%" placeholder="选择模块" clearable filterable>
            <el-option v-for="m in editModuleOptions" :key="m.id" :label="`${m.name} (${m.code})`" :value="m.id" />
          </el-select>
        </el-form-item>
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
          <el-select v-model="importProjectId" placeholder="请选择项目" style="width: 100%" @change="handleImportProjectChange">
            <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Sprint">
          <el-select v-model="importSprintId" placeholder="可选，导入到指定 Sprint" style="width: 100%" clearable>
            <el-option v-for="s in importSprintOptions" :key="s.id" :label="s.name" :value="s.id" />
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

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" :title="`${currentCase?.case_no || ''} 详情`" size="560px">
      <div v-if="currentCase" v-loading="detailLoading">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="标题">{{ currentCase.title }}</el-descriptions-item>
          <el-descriptions-item label="Sprint">{{ currentCase.sprint_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="模块">{{ currentCase.module_name || currentCase.module || '-' }}</el-descriptions-item>
          <el-descriptions-item label="来源">{{ getSourceText(currentCase.source) }}</el-descriptions-item>
          <el-descriptions-item label="来源资产">{{ currentCase.source_asset_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="自动化状态">{{ getAutomationStatusText(currentCase.automation_status) }}</el-descriptions-item>
          <el-descriptions-item label="脚本路径">{{ currentCase.automation_path || '-' }}</el-descriptions-item>
          <el-descriptions-item label="选择器路径">{{ currentCase.selector_path || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-sub">来源功能点 ({{ detailFeatures.length }})</div>
        <el-table :data="detailFeatures" size="small" empty-text="暂无关联功能点">
          <el-table-column prop="feature_point_name" label="功能点" min-width="160" show-overflow-tooltip />
          <el-table-column label="覆盖类型" width="100"><template #default="{ row }">{{ row.coverage_type }}</template></el-table-column>
          <el-table-column label="置信度" width="80"><template #default="{ row }">{{ row.confidence || 0 }}%</template></el-table-column>
        </el-table>

        <div class="detail-sub">关联接口 ({{ detailApis.length }})</div>
        <el-table :data="detailApis" size="small" empty-text="暂无关联接口">
          <el-table-column label="接口" min-width="180">
            <template #default="{ row }">{{ row.api_method }} {{ row.api_path }}</template>
          </el-table-column>
          <el-table-column prop="api_summary" label="摘要" min-width="140" show-overflow-tooltip />
        </el-table>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Edit, Delete, VideoPlay, Download, Upload, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTestCases, getTestCaseStats, createTestCase, updateTestCase, deleteTestCase, batchExecuteTestCases, exportTestCases, downloadTemplate, importTestCases } from '../../api/testcase'
import { getProjects } from '../../api/project'
import { getModules, getSprints } from '../../api/sprint'
import { getTestCaseFeaturePoints } from '../../api/coverage'
import { getTestCaseApiEndpoints } from '../../api/apiEndpoint'

const appStore = useAppStore()
const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)
const batchExecuting = ref(false)
const exporting = ref(false)
const downloading = ref(false)
const importing = ref(false)
const importVisible = ref(false)
const importProjectId = ref(null)
const importSprintId = ref(null)
const importSprintOptions = ref([])
const importFile = ref(null)
const importUploadRef = ref(null)
const stats = ref({ total: 0, projectCount: 0, passed: 0, passRate: 0, failed: 0, pending: 0 })
const selectedProject = ref('')
const selectedSprintId = ref(null)
const projectOptions = ref([])
const sprintOptions = ref([])
const testCases = ref([])
const createModuleOptions = ref([])
const editModuleOptions = ref([])

const createVisible = ref(false)
const createForm = reactive({ title: '', priority: '高', project_id: null, module_id: null, module: '', preconditions: '', test_data: '', test_steps: '', expected_result: '' })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ title: '', priority: '', exec_status: '', module_id: null, preconditions: '', test_data: '', test_steps: '', expected_result: '', actual_result: '' })

// 详情抽屉
const detailVisible = ref(false)
const currentCase = ref(null)
const detailFeatures = ref([])
const detailApis = ref([])
const detailLoading = ref(false)

async function openDetail(row) {
  currentCase.value = row
  detailFeatures.value = []
  detailApis.value = []
  detailVisible.value = true
  detailLoading.value = true
  try {
    const [fpRes, apiRes] = await Promise.all([
      getTestCaseFeaturePoints(row.id),
      getTestCaseApiEndpoints(row.id),
    ])
    detailFeatures.value = fpRes.data || []
    detailApis.value = apiRes.data || []
  } catch (e) {
    console.error(e)
  } finally {
    detailLoading.value = false
  }
}

function getPriorityClass(p) { return { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }[p] || 'badge badge-gray' }
function getExecStatusType(s) { return { 通过: 'success', 失败: 'danger', 执行中: 'warning', 待执行: 'info' }[s] || 'info' }
function getSourceText(s) { return { manual: '手工', ai_generated: 'AI生成', imported: '导入', skill_generated: 'SKILL' }[s] || '手工' }
function getAutomationStatusText(s) { return { not_generated: '未生成', generated: '已生成', validated: '已验证', executed: '已执行', healed: '已自愈', failed: '失败' }[s] || '未生成' }
function getAutomationStatusType(s) { return { not_generated: 'info', generated: 'warning', validated: 'success', executed: 'success', healed: 'success', failed: 'danger' }[s] || 'info' }
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

async function handleProjectFilterChange() {
  selectedSprintId.value = null
  await loadSprintOptions()
  await loadCases()
}

async function loadSprintOptions() {
  try {
    const proj = selectedProject.value ? projectOptions.value.find(p => p.name === selectedProject.value) : null
    const res = await getSprints(proj?.id ? { project_id: proj.id } : {})
    sprintOptions.value = res.data || []
  } catch (e) {
    sprintOptions.value = []
  }
}

// ── 模块选择 ──
async function loadModulesForProject(projectId, targetRef) {
  if (!projectId) {
    targetRef.value = []
    return
  }
  try {
    const res = await getModules({ project_id: projectId })
    targetRef.value = res.data || []
  } catch (e) {
    targetRef.value = []
  }
}

function onCreateProjectChange(projectId) {
  createForm.module_id = null
  createForm.module = ''
  loadModulesForProject(projectId, createModuleOptions)
}

function onModuleSelect(moduleId) {
  if (moduleId) {
    const mod = createModuleOptions.value.find(m => m.id === moduleId)
    createForm.module = mod ? mod.code : ''
  } else {
    createForm.module = ''
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
    const res = await exportTestCases(projectId, selectedSprintId.value)
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
  importSprintId.value = null
  importSprintOptions.value = []
  importFile.value = null
  // 如果当前已选择项目，自动填入
  if (selectedProject.value) {
    const proj = projectOptions.value.find(p => p.name === selectedProject.value)
    if (proj) {
      importProjectId.value = proj.id
      handleImportProjectChange(proj.id)
    }
  }
  importVisible.value = true
}

async function handleImportProjectChange(projectId) {
  importSprintId.value = null
  try {
    const res = await getSprints(projectId ? { project_id: projectId } : {})
    importSprintOptions.value = res.data || []
  } catch (e) {
    importSprintOptions.value = []
  }
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
    const res = await importTestCases(importProjectId.value, importFile.value, importSprintId.value)
    const data = res.data
    if (data.fail_count > 0) {
      const errorList = data.errors.map(e => `第 ${e.row} 行: ${e.reason}`).join('\n')
      const updatedInfo = data.updated_count > 0 ? `，更新 ${data.updated_count} 条` : ''
      ElMessageBox.alert(`新增 ${data.success_count} 条${updatedInfo}，失败 ${data.fail_count} 条：\n\n${errorList}`, '导入结果', { type: 'warning' })
    } else {
      const updatedInfo = data.updated_count > 0 ? `，更新 ${data.updated_count} 条` : ''
      ElMessage.success(`新增 ${data.success_count} 条${updatedInfo}`)
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
    const filters = selectedSprintId.value ? { sprint_id: selectedSprintId.value } : {}
    testCases.value = (await getTestCases(selectedProject.value || undefined, keyword, filters)).data
  } catch (e) { console.error(e) } finally { loading.value = false }
}

async function loadStats() {
  try { stats.value = (await getTestCaseStats()).data } catch (e) { /* ignore */ }
}

watch(() => appStore.searchKeyword, () => {
  if (loadTimer) clearTimeout(loadTimer)
  loadTimer = setTimeout(() => {
    loadCases()
  }, 300)
})

function openCreateDialog() {
  Object.assign(createForm, { title: '', priority: '高', project_id: null, module_id: null, module: '', preconditions: '', test_data: '', test_steps: '', expected_result: '' })
  createModuleOptions.value = []
  createVisible.value = true
}

async function handleCreate() {
  if (!createForm.module_id) {
    ElMessage.warning('请选择模块')
    return
  }
  creating.value = true
  try {
    await createTestCase({ ...createForm })
    await loadCases()
    await loadStats()
    ElMessage.success('创建成功')
    createVisible.value = false
    appStore.refreshSidebarBadges()
  } catch (e) { ElMessage.error('创建失败') } finally { creating.value = false }
}

function handleEdit(row) {
  editId.value = row.id
  // 加载该项目的模块列表
  if (row.project_id) {
    loadModulesForProject(row.project_id, editModuleOptions)
  } else {
    editModuleOptions.value = []
  }
  Object.assign(editForm, {
    title: row.title, priority: row.priority, exec_status: row.exec_status,
    module_id: row.module_id || null,
    preconditions: row.preconditions || '', test_data: row.test_data || '',
    test_steps: row.test_steps || '', expected_result: row.expected_result || '',
    actual_result: row.actual_result || '',
  })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try { await updateTestCase(editId.value, { ...editForm }); await loadCases(); await loadStats(); ElMessage.success('保存成功'); editVisible.value = false } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除用例"${row.case_no}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteTestCase(row.id); await loadCases(); await loadStats(); ElMessage.success('删除成功'); appStore.refreshSidebarBadges() }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('testcases', '测试用例', '新建用例', openCreateDialog)
  loading.value = true
  try {
    const [casesRes, statsRes, projRes] = await Promise.allSettled([getTestCases(), getTestCaseStats(), getProjects()])
    if (casesRes.status === 'fulfilled') testCases.value = casesRes.value.data
    if (statsRes.status === 'fulfilled') stats.value = statsRes.value.data
    if (projRes.status === 'fulfilled') projectOptions.value = projRes.value.data
    await loadSprintOptions()

    // 支持 URL query 自动筛选：project_id / sprint_id
    const qProjectId = route.query.project_id ? Number(route.query.project_id) : null
    const qSprintId = route.query.sprint_id ? Number(route.query.sprint_id) : null
    if (qProjectId) {
      const proj = projectOptions.value.find(p => p.id === qProjectId)
      if (proj) {
        selectedProject.value = proj.name
        await loadSprintOptions()
      }
    }
    if (qSprintId) {
      selectedSprintId.value = qSprintId
    }
    if (qProjectId || qSprintId) {
      await loadCases()
    }
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

.detail-sub {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 16px 0 8px;
}
</style>
