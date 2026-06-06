<template>
  <div class="knowledge-detail">
    <!-- 面包屑 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item" @click="goToProject">
        <el-icon :size="13"><Folder /></el-icon>{{ sprint.projectName || '项目' }}
      </span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item" @click="goToKnowledge">Sprint 列表</span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item current">{{ sprint.name }}</span>
    </div>

    <!-- Sprint 信息卡片 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div style="display:flex;align-items:center;gap:8px">
          <el-icon :size="16" style="color:var(--accent)"><Promotion /></el-icon>
          <div>
            <div class="card-title">{{ sprint.name }}</div>
            <div style="font-size:11px;color:var(--color-text-tertiary);margin-top:2px">
              {{ sprint.projectName }} · {{ sprint.status }} · {{ sprint.moduleCount }} 个模块
            </div>
          </div>
        </div>
        <div style="display:flex;gap:10px">
          <el-tag :type="getSprintStatusType(sprint.status)" size="small" effect="plain" round>{{ sprint.status }}</el-tag>
        </div>
      </div>
      <div class="sprint-meta">
        <span>文档数：<strong>{{ documents.length }}</strong></span>
        <span>模块数：<strong>{{ sprint.moduleCount }}</strong></span>
        <span v-if="sprint.description" style="flex:1">描述：{{ sprint.description }}</span>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div class="card-title">文档列表</div>
        <div style="display:flex;gap:10px">
          <div class="card-action" @click="openUploadDialog">上传文档</div>
          <div class="card-action" @click="openModuleManager">管理模块标签</div>
        </div>
      </div>
      <el-table :data="documents" style="width:100%" @row-click="goToPreview" v-loading="loading">
        <el-table-column label="文档名称" min-width="240">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:8px">
              <el-icon :size="15" :style="{ color: getFileIconColor(row.file_type) }"><Document /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.file_type)" size="small" effect="plain" round>{{ row.file_type || '其他' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="模块标签" min-width="160">
          <template #default="{ row }">
            <div style="display:flex;gap:4px;flex-wrap:wrap">
              <el-tag v-for="m in row.module_names" :key="m" size="small" effect="plain" type="info">{{ m }}</el-tag>
              <span v-if="!row.module_names?.length" style="color:var(--color-text-tertiary);font-size:12px">待分析</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="AI 状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getAiStatusType(row.ai_status)" size="small" effect="plain" round>{{ row.ai_status || '待分析' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploader_name" label="上传人" width="80" />
        <el-table-column label="上传时间" width="110">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns" @click.stop>
              <el-button type="primary" link size="small" @click="handleEditDoc(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteDoc($index, row)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="!loading && documents.length === 0" style="text-align:center;padding:40px;color:var(--color-text-tertiary)">
        暂无文档，点击"上传文档"添加
      </div>
    </div>

    <!-- 上传文档对话框 -->
    <el-dialog v-model="uploadVisible" title="上传文档" width="500px" destroy-on-close>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        drag
      >
        <el-icon style="font-size:40px;color:var(--color-text-tertiary)"><Upload /></el-icon>
        <div style="margin-top:8px">拖拽文件到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div style="font-size:12px;color:var(--color-text-tertiary);margin-top:8px">
            支持 PDF、Word、Markdown、Excel 文件
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>

    <!-- 编辑文档对话框 -->
    <el-dialog v-model="editDocVisible" title="编辑文档" width="400px" destroy-on-close>
      <el-form :model="editDocForm" label-width="80px">
        <el-form-item label="文档名称"><el-input v-model="editDocForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDocVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDoc" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 功能点列表 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div style="display:flex;align-items:center;gap:8px">
          <el-icon :size="16" style="color:#8B5CF6"><MagicStick /></el-icon>
          <div class="card-title">功能点</div>
          <span style="font-size:11px;color:var(--color-text-tertiary)">AI 从文档中提取</span>
        </div>
        <div class="card-action" @click="openCreateFpDialog">添加功能点</div>
      </div>
      <el-table :data="featurePoints" style="width:100%" v-loading="fpLoading">
        <el-table-column prop="name" label="功能点名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="来源文档" width="160">
          <template #default="{ row }">
            <span v-if="row.source_doc_name" style="color:var(--accent);cursor:pointer" @click="goToPreview({id: row.source_doc_id})">{{ row.source_doc_name }}</span>
            <span v-else style="color:var(--color-text-tertiary)">-</span>
          </template>
        </el-table-column>
        <el-table-column label="模块标签" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.module_name" size="small" effect="plain" type="info">{{ row.module_name }}</el-tag>
            <span v-else style="color:var(--color-text-tertiary)">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="linked_cases" label="关联用例" width="140">
          <template #default="{ row }">{{ row.linked_cases || '-' }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="110">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns">
              <el-button type="primary" link size="small" @click="handleEditFp(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteFp($index, row)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="!fpLoading && featurePoints.length === 0" style="text-align:center;padding:40px;color:var(--color-text-tertiary)">
        暂无功能点，点击"添加功能点"手动添加
      </div>
    </div>

    <!-- 新建功能点对话框 -->
    <el-dialog v-model="createFpVisible" title="添加功能点" width="520px" destroy-on-close>
      <el-form :model="createFpForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="createFpForm.name" placeholder="请输入功能点名称" /></el-form-item>
        <el-form-item label="来源文档">
          <el-select v-model="createFpForm.source_doc_id" style="width:100%" placeholder="选择文档（可选）" clearable>
            <el-option v-for="d in documents" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 16px">
          <el-form-item label="模块标签">
            <el-select v-model="createFpForm.module_id" style="width:100%" placeholder="选择模块" clearable>
              <el-option v-for="m in modules" :key="m.id" :label="m.name" :value="m.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="关联用例"><el-input v-model="createFpForm.linked_cases" placeholder="如 TC-001~TC-005" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="createFpVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateFp" :loading="fpSaving">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑功能点对话框 -->
    <el-dialog v-model="editFpVisible" title="编辑功能点" width="520px" destroy-on-close>
      <el-form :model="editFpForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="editFpForm.name" /></el-form-item>
        <el-form-item label="来源文档">
          <el-select v-model="editFpForm.source_doc_id" style="width:100%" placeholder="选择文档（可选）" clearable>
            <el-option v-for="d in documents" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 16px">
          <el-form-item label="模块标签">
            <el-select v-model="editFpForm.module_id" style="width:100%" placeholder="选择模块" clearable>
              <el-option v-for="m in modules" :key="m.id" :label="m.name" :value="m.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="关联用例"><el-input v-model="editFpForm.linked_cases" placeholder="如 TC-001~TC-005" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="editFpVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveFp" :loading="fpSaving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 模块标签管理对话框 -->
    <el-dialog v-model="moduleManagerVisible" title="模块标签管理" width="560px" destroy-on-close>
      <div style="margin-bottom:12px;display:flex;gap:8px">
        <el-input v-model="newModuleName" placeholder="模块名称（中文）" style="flex:1" size="small" />
        <el-input v-model="newModuleCode" placeholder="英文缩写" style="width:120px" size="small" />
        <el-color-picker v-model="newModuleColor" size="small" />
        <el-button type="primary" size="small" @click="handleAddModule" :loading="saving">添加</el-button>
      </div>
      <el-table :data="modules" style="width:100%" size="small">
        <el-table-column label="模块名称" min-width="160">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px">
              <span :style="{ width: '10px', height: '10px', borderRadius: '50%', background: row.color || 'var(--accent)' }"></span>
              {{ row.name }}
              <span v-if="row.code" style="color:var(--color-text-tertiary);font-size:11px">({{ row.code }})</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="doc_count" label="关联文档" width="80" />
        <el-table-column label="操作" width="120">
          <template #default="{ row, $index }">
            <div class="action-btns">
              <el-button type="primary" link size="small" @click="handleEditModule(row)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDeleteModule($index, row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 编辑模块 -->
      <div v-if="editingModule" style="margin-top:12px;display:flex;gap:8px;align-items:center">
        <el-input v-model="editingModule.name" size="small" style="flex:1" placeholder="模块名称" />
        <el-input v-model="editingModule.code" size="small" style="width:120px" placeholder="英文缩写" />
        <el-color-picker v-model="editingModule.color" size="small" />
        <el-button type="primary" size="small" @click="handleSaveModule">保存</el-button>
        <el-button size="small" @click="editingModule = null">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Folder, Promotion, Document, Edit, Delete, Upload, MagicStick } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getSprint, getSprintDocuments, uploadSprintDocument,
  updateSprintDocument, deleteSprintDocument,
  getModules, createModule, updateModule, deleteModule,
} from '../../api/sprint'
import {
  getFeaturePoints, createFeaturePoint, updateFeaturePoint, deleteFeaturePoint,
} from '../../api/featurePoint'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const fpLoading = ref(false)
const fpSaving = ref(false)

const sprintId = route.params.id

// Sprint 信息
const sprint = ref({
  id: sprintId,
  name: '',
  projectName: '',
  status: '',
  moduleCount: 0,
  description: '',
})

// 文档列表
const documents = ref([])

// 模块标签
const modules = ref([])
const moduleManagerVisible = ref(false)
const newModuleName = ref('')
const newModuleCode = ref('')
const newModuleColor = ref('#378ADD')
const editingModule = ref(null)

// 上传
const uploadVisible = ref(false)
const uploadRef = ref(null)
const selectedFile = ref(null)

// 编辑文档
const editDocVisible = ref(false)
const editDocId = ref(null)
const editDocForm = reactive({ name: '' })

// 功能点
const featurePoints = ref([])
const createFpVisible = ref(false)
const editFpVisible = ref(false)
const editFpId = ref(null)
const createFpForm = reactive({ name: '', source_doc_id: null, module_id: null, linked_cases: '' })
const editFpForm = reactive({ name: '', source_doc_id: null, module_id: null, linked_cases: '' })

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

function getTypeTagType(t) {
  return { 'PDF': '', 'Word': 'success', 'Markdown': 'warning', 'Excel': 'danger' }[t] || 'info'
}

function getAiStatusType(status) {
  return { '已分析': 'success', '分析中': 'warning', '解析失败': 'danger' }[status] || 'info'
}

function getFileIconColor(type) {
  return { 'PDF': '#E24B4A', 'Word': '#16a34a', 'Markdown': '#8B5CF6', 'Excel': '#EF9F27' }[type] || 'var(--accent)'
}

function goToProject() { router.push('/projects') }
function goToKnowledge() { router.push('/knowledge') }
function goToPreview(row) { router.push(`/knowledge/doc/${row.id}`) }

async function loadData() {
  loading.value = true
  try {
    const [sprintRes, docsRes] = await Promise.all([
      getSprint(sprintId),
      getSprintDocuments(sprintId),
    ])
    if (sprintRes.data) {
      sprint.value = {
        id: sprintRes.data.id,
        name: sprintRes.data.name,
        projectName: sprintRes.data.project_name || '',
        status: sprintRes.data.status,
        moduleCount: sprintRes.data.module_count || 0,
        description: sprintRes.data.description || '',
      }
    }
    documents.value = docsRes.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// ========== 文档操作 ==========

function openUploadDialog() {
  selectedFile.value = null
  uploadVisible.value = true
}

function handleFileChange(file) {
  selectedFile.value = file
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value.raw)
    await uploadSprintDocument(sprintId, formData)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

function handleEditDoc(row) {
  editDocId.value = row.id
  editDocForm.name = row.name
  editDocVisible.value = true
}

async function handleSaveDoc() {
  saving.value = true
  try {
    await updateSprintDocument(sprintId, editDocId.value, { name: editDocForm.name })
    ElMessage.success('保存成功')
    editDocVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function handleDeleteDoc(index, row) {
  ElMessageBox.confirm(`确定要删除文档"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteSprintDocument(sprintId, row.id)
      ElMessage.success('删除成功')
      await loadData()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// ========== 功能点操作 ==========

async function loadFeaturePoints() {
  fpLoading.value = true
  try {
    const res = await getFeaturePoints({ sprint_id: sprintId })
    featurePoints.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    fpLoading.value = false
  }
}

function openCreateFpDialog() {
  Object.assign(createFpForm, { name: '', source_doc_id: null, module_id: null, linked_cases: '' })
  createFpVisible.value = true
}

async function handleCreateFp() {
  if (!createFpForm.name.trim()) {
    ElMessage.warning('请输入功能点名称')
    return
  }
  fpSaving.value = true
  try {
    await createFeaturePoint({
      ...createFpForm,
      sprint_id: parseInt(sprintId),
    })
    ElMessage.success('创建成功')
    createFpVisible.value = false
    await loadFeaturePoints()
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    fpSaving.value = false
  }
}

function handleEditFp(row) {
  editFpId.value = row.id
  Object.assign(editFpForm, {
    name: row.name,
    source_doc_id: row.source_doc_id,
    module_id: row.module_id,
    linked_cases: row.linked_cases || '',
  })
  editFpVisible.value = true
}

async function handleSaveFp() {
  fpSaving.value = true
  try {
    await updateFeaturePoint(editFpId.value, { ...editFpForm })
    ElMessage.success('保存成功')
    editFpVisible.value = false
    await loadFeaturePoints()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    fpSaving.value = false
  }
}

function handleDeleteFp(index, row) {
  ElMessageBox.confirm(`确定要删除功能点"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteFeaturePoint(row.id)
      ElMessage.success('删除成功')
      await loadFeaturePoints()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// ========== 模块标签管理 ==========

async function openModuleManager() {
  moduleManagerVisible.value = true
  editingModule.value = null
  await loadModules()
}

async function loadModules() {
  try {
    const res = await getModules({ project_id: sprint.value.projectId })
    modules.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

async function handleAddModule() {
  if (!newModuleName.value.trim()) {
    ElMessage.warning('请输入模块名称')
    return
  }
  saving.value = true
  try {
    await createModule({
      name: newModuleName.value,
      code: newModuleCode.value.trim().toUpperCase(),
      project_id: null, // TODO: 传入实际 project_id
      color: newModuleColor.value,
    })
    ElMessage.success('添加成功')
    newModuleName.value = ''
    newModuleCode.value = ''
    newModuleColor.value = '#378ADD'
    await loadModules()
  } catch (e) {
    ElMessage.error('添加失败')
  } finally {
    saving.value = false
  }
}

function handleEditModule(row) {
  editingModule.value = { ...row }
}

async function handleSaveModule() {
  if (!editingModule.value) return
  saving.value = true
  try {
    await updateModule(editingModule.value.id, {
      name: editingModule.value.name,
      code: editingModule.value.code ? editingModule.value.code.trim().toUpperCase() : '',
      color: editingModule.value.color,
    })
    ElMessage.success('保存成功')
    editingModule.value = null
    await loadModules()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function handleDeleteModule(index, row) {
  ElMessageBox.confirm(`确定要删除模块标签"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteModule(row.id)
      ElMessage.success('删除成功')
      await loadModules()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  appStore.setCurrentPage('knowledge', '文档列表', '上传文档', openUploadDialog)
  loadData()
  loadFeaturePoints()
})
</script>

<style scoped>
.knowledge-detail { max-width: 1400px; }

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 16px;
  font-size: 13px;
}

.breadcrumb-item {
  color: var(--accent);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.breadcrumb-item:hover { text-decoration: underline; }
.breadcrumb-item.current { color: var(--color-text-primary); cursor: default; font-weight: 500; }
.breadcrumb-item.current:hover { text-decoration: none; }

.breadcrumb-sep {
  margin: 0 8px;
  color: var(--color-text-tertiary);
}

.sprint-meta {
  padding: 14px 18px;
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.card-action {
  font-size: 12px;
  color: var(--accent);
  cursor: pointer;
  font-weight: 500;
}

.card-action:hover { text-decoration: underline; }

.action-btns { display: flex; gap: 4px; }
.el-table { cursor: pointer; }
</style>
