<template>
  <div class="project-detail">
    <div class="card" style="margin-bottom: 16px">
      <div class="card-head">
        <div class="card-title">项目信息</div>
        <div class="card-action" @click="goBack">返回列表</div>
      </div>
      <div class="project-info" v-loading="loading">
        <div class="info-grid">
          <div class="info-item"><div class="info-label">项目名称</div><div class="info-value">{{ project.name }}</div></div>
          <div class="info-item"><div class="info-label">负责人</div><div class="info-value">{{ project.owner }}</div></div>
          <div class="info-item"><div class="info-label">状态</div><div class="info-value"><el-tag :type="getStatusType(project.status)" size="small">{{ getStatusText(project.status) }}</el-tag></div></div>
          <div class="info-item"><div class="info-label">创建时间</div><div class="info-value">{{ formatDate(project.created_at) }}</div></div>
        </div>
        <div class="info-item" style="margin-top: 12px"><div class="info-label">项目描述</div><div class="info-value">{{ project.description }}</div></div>
        <div class="info-item" style="margin-top: 12px"><div class="info-label">进度</div><div class="info-value" style="display: flex; align-items: center; gap: 10px; max-width: 400px"><el-progress :percentage="project.progress" :stroke-width="8" style="flex: 1" /></div></div>
      </div>
    </div>

    <div class="card" style="margin-bottom: 16px">
      <div class="card-head">
        <div class="card-title">功能模块</div>
        <div class="card-action" @click="showAddModule = true">添加模块</div>
      </div>
      <!-- 添加模块行 -->
      <div v-if="showAddModule" style="padding:12px 18px;display:flex;gap:8px;align-items:center;border-bottom:1px solid var(--color-border)">
        <el-input v-model="newModuleName" placeholder="模块名称（中文）" style="flex:1" size="small" />
        <el-input v-model="newModuleCode" placeholder="英文缩写" style="width:140px" size="small" />
        <el-color-picker v-model="newModuleColor" size="small" />
        <el-button type="primary" size="small" @click="handleAddModule" :loading="moduleSaving">添加</el-button>
        <el-button size="small" @click="showAddModule = false">取消</el-button>
      </div>
      <el-table :data="modules" style="width:100%" size="small" v-loading="moduleLoading" empty-text="暂无模块，点击「添加模块」创建">
        <el-table-column label="模块名称" min-width="160">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px">
              <span :style="{ width: '10px', height: '10px', borderRadius: '50%', background: row.color || 'var(--accent)' }"></span>
              <span>{{ row.name }}</span>
              <span v-if="row.code" style="color:var(--color-text-tertiary);font-size:11px">({{ row.code }})</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="doc_count" label="关联文档" width="80" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <div class="action-btns">
              <el-button type="primary" link size="small" @click="handleEditModule(row)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDeleteModule(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <!-- 编辑模块行 -->
      <div v-if="editingModule" style="padding:12px 18px;display:flex;gap:8px;align-items:center;border-top:1px solid var(--color-border)">
        <el-input v-model="editingModule.name" size="small" style="flex:1" placeholder="模块名称" />
        <el-input v-model="editingModule.code" size="small" style="width:140px" placeholder="英文缩写" />
        <el-color-picker v-model="editingModule.color" size="small" />
        <el-button type="primary" size="small" @click="handleSaveModule" :loading="moduleSaving">保存</el-button>
        <el-button size="small" @click="editingModule = null">取消</el-button>
      </div>
    </div>

    <div class="card" style="margin-bottom: 16px">
      <div class="card-head"><div class="card-title">关联测试用例</div></div>
      <el-table :data="testCases" style="width: 100%">
        <el-table-column prop="case_no" label="用例编号" width="160" />
        <el-table-column label="模块" width="120"><template #default="{ row }"><span v-if="row.module_name">{{ row.module_name }}</span><span v-else-if="row.module">{{ row.module }}</span><span v-else>-</span></template></el-table-column>
        <el-table-column prop="title" label="用例标题" min-width="200" show-overflow-tooltip />
        <el-table-column label="优先级" width="80"><template #default="{ row }"><span :class="getPriorityClass(row.priority)">{{ row.priority }}</span></template></el-table-column>
        <el-table-column label="执行状态" width="100"><template #default="{ row }"><el-tag :type="getExecStatusType(row.exec_status)" size="small">{{ row.exec_status }}</el-tag></template></el-table-column>
        <el-table-column prop="executor" label="执行人" width="80" />
      </el-table>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title">关联测试报告</div></div>
      <el-table :data="testReports" style="width: 100%">
        <el-table-column prop="name" label="报告名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="通过率" width="100"><template #default="{ row }"><span :style="{ color: row.pass_rate >= 85 ? '#1D9E75' : '#EF9F27', fontWeight: 500 }">{{ row.pass_rate }}%</span></template></el-table-column>
        <el-table-column prop="defect_count" label="缺陷数" width="80" />
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="row.status === '已审批' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column label="生成时间" width="120"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProject, getProjectTestcases, getProjectReports } from '../../api/project'
import { getModules, createModule, updateModule, deleteModule } from '../../api/sprint'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const loading = ref(false)
const project = ref({})
const testCases = ref([])
const testReports = ref([])

// 模块管理
const modules = ref([])
const moduleLoading = ref(false)
const moduleSaving = ref(false)
const showAddModule = ref(false)
const newModuleName = ref('')
const newModuleCode = ref('')
const newModuleColor = ref('#378ADD')
const editingModule = ref(null)

function getStatusType(status) {
  const map = { testing: '', completed: 'success', active: 'warning', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { testing: '测试中', completed: '已完成', active: '进行中', pending: '待启动' }
  return map[status] || status
}

function getPriorityClass(priority) {
  const map = { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }
  return map[priority] || 'badge badge-gray'
}

function getExecStatusType(status) {
  const map = { 通过: 'success', 失败: 'danger', 执行中: 'warning', 待执行: 'info' }
  return map[status] || 'info'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.split('T')[0]
}

function goBack() {
  router.push('/projects')
}

// ========== 模块管理 ==========
async function loadModules() {
  const projectId = route.params.id
  moduleLoading.value = true
  try {
    const res = await getModules({ project_id: projectId })
    modules.value = res.data || []
  } catch (e) {
    console.error('加载模块失败:', e)
  } finally {
    moduleLoading.value = false
  }
}

async function handleAddModule() {
  if (!newModuleName.value.trim()) {
    ElMessage.warning('请输入模块名称')
    return
  }
  if (!newModuleCode.value.trim()) {
    ElMessage.warning('请输入英文缩写')
    return
  }
  moduleSaving.value = true
  try {
    await createModule({
      name: newModuleName.value.trim(),
      code: newModuleCode.value.trim().toUpperCase(),
      project_id: parseInt(route.params.id),
      color: newModuleColor.value,
    })
    ElMessage.success('添加成功')
    newModuleName.value = ''
    newModuleCode.value = ''
    newModuleColor.value = '#378ADD'
    showAddModule.value = false
    await loadModules()
  } catch (e) {
    ElMessage.error('添加失败')
  } finally {
    moduleSaving.value = false
  }
}

function handleEditModule(row) {
  editingModule.value = { ...row }
}

async function handleSaveModule() {
  if (!editingModule.value) return
  moduleSaving.value = true
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
    moduleSaving.value = false
  }
}

function handleDeleteModule(row) {
  ElMessageBox.confirm(`确定要删除模块"${row.name}"吗？`, '确认删除', {
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

onMounted(async () => {
  appStore.setCurrentPage('projects', '项目详情', '编辑项目')
  const projectId = route.params.id
  loading.value = true
  try {
    const [projRes, casesRes, reportsRes] = await Promise.all([
      getProject(projectId),
      getProjectTestcases(projectId),
      getProjectReports(projectId)
    ])
    project.value = projRes.data
    testCases.value = casesRes.data
    testReports.value = reportsRes.data
    loadModules()
  } catch (e) {
    console.error('加载项目详情失败:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.project-detail { max-width: 1400px; }
.action-btns { display: flex; gap: 4px; }
.project-info { padding: 16px 18px; }
.info-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.info-label { font-size: 12px; color: var(--color-text-tertiary); margin-bottom: 4px; }
.info-value { font-size: 14px; color: var(--color-text-primary); }
</style>
