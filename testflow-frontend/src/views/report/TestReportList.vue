<template>
  <div class="report-list">
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-label">本月报告</div><div class="stat-value">{{ stats.monthlyReports }}</div><div class="stat-sub"><span class="stat-dot dot-blue"></span>较上月 +{{ stats.monthlyChange }}</div></div>
      <div class="stat-card"><div class="stat-label">平均通过率</div><div class="stat-value">{{ stats.avgPassRate }}%</div><div class="stat-sub"><span class="stat-dot dot-green"></span>持续提升</div></div>
      <div class="stat-card"><div class="stat-label">缺陷总计</div><div class="stat-value">{{ stats.totalDefects }}</div><div class="stat-sub"><span class="stat-dot dot-red"></span>已修复 {{ stats.fixedDefects }}</div></div>
      <div class="stat-card"><div class="stat-label">待审批报告</div><div class="stat-value">{{ stats.pendingApproval }}</div><div class="stat-sub"><span class="stat-dot dot-amber"></span>需要处理</div></div>
    </div>

    <div class="card">
      <div class="card-head">
        <div class="card-title">测试报告列表</div>
        <div class="card-action" @click="openCreateDialog">生成报告</div>
      </div>
      <el-table :data="reports" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="报告名称" min-width="220" show-overflow-tooltip />
        <el-table-column prop="project" label="所属项目" width="130" />
        <el-table-column label="报告类型" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.report_type" :type="getReportTypeTag(row.report_type)" size="small" effect="plain">{{ row.report_type }}</el-tag>
            <span v-else style="color:var(--color-text-tertiary)">-</span>
          </template>
        </el-table-column>
        <el-table-column label="通过率" width="100"><template #default="{ row }"><span :style="{ color: row.pass_rate >= 85 ? '#1D9E75' : '#EF9F27', fontWeight: 500 }">{{ row.pass_rate }}%</span></template></el-table-column>
        <el-table-column prop="defect_count" label="缺陷数" width="80" />
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="row.status === '已审批' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column label="生成时间" width="120"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row, $index }"><div class="action-btns"><el-button v-if="row.status === '待审批'" type="success" link size="small" @click="handleApprove(row)" style="background:#dcfce7;color:#16a34a;border-radius:4px;padding:2px 8px"><el-icon><Check /></el-icon>审批</el-button><el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button><el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button></div></template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="createVisible" title="生成报告" width="560px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="报告名称"><el-input v-model="createForm.name" placeholder="请输入报告名称" /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="所属项目"><el-select v-model="createForm.project_id" style="width: 100%" placeholder="选择项目"><el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" /></el-select></el-form-item>
          <el-form-item label="报告类型"><el-select v-model="createForm.report_type" style="width: 100%" placeholder="选择类型"><el-option label="回归" value="回归" /><el-option label="冒烟" value="冒烟" /><el-option label="迭代" value="迭代" /><el-option label="全量" value="全量" /></el-select></el-form-item>
        </div>
        <el-form-item label="测试范围"><el-input v-model="createForm.test_scope" type="textarea" :rows="3" placeholder="描述纳入报告的用例范围" /></el-form-item>
      </el-form>
      <div style="padding: 0 0 12px 80px; font-size: 12px; color: var(--color-text-tertiary)">
        <el-icon style="vertical-align: -1px"><InfoFilled /></el-icon> 报告将基于已执行的测试用例结果自动生成
      </div>
      <template #footer><el-button @click="createVisible = false">取消</el-button><el-button type="primary" @click="handleCreate" :loading="creating">生成报告</el-button></template>
    </el-dialog>

    <el-dialog v-model="editVisible" title="编辑报告" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="报告名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="报告类型"><el-select v-model="editForm.report_type" style="width: 100%"><el-option label="回归" value="回归" /><el-option label="冒烟" value="冒烟" /><el-option label="迭代" value="迭代" /><el-option label="全量" value="全量" /></el-select></el-form-item>
        <el-form-item label="状态"><el-select v-model="editForm.status" style="width: 100%"><el-option label="已审批" value="已审批" /><el-option label="待审批" value="待审批" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="editVisible = false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAppStore } from '../../stores/app'
import { Edit, Delete, Check, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getReports, getReportStats, createReport, updateReport, deleteReport, approveReport } from '../../api/report'
import { getProjects } from '../../api/project'

const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)
const stats = ref({ monthlyReports: 0, monthlyChange: 0, avgPassRate: 0, totalDefects: 0, fixedDefects: 0, pendingApproval: 0 })
const reports = ref([])
const projectOptions = ref([])

const createVisible = ref(false)
const createForm = reactive({ name: '', project_id: null, report_type: '', test_scope: '' })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '', status: '', report_type: '' })

function formatDate(d) { return d ? d.split('T')[0] : '' }

function getReportTypeTag(type) {
  return { '回归': '', '冒烟': 'warning', '迭代': 'success', '全量': 'danger' }[type] || 'info'
}

async function handleApprove(row) {
  try {
    const res = await approveReport(row.id)
    Object.assign(row, res.data)
    ElMessage.success('报告已审批')
    // 刷新统计
    try { stats.value = (await getReportStats()).data } catch (e) { /* ignore */ }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '审批失败')
  }
}

let loadTimer = null

async function loadReports() {
  loading.value = true
  try {
    const keyword = appStore.searchKeyword?.trim() || undefined
    reports.value = (await getReports(keyword)).data
  } catch (e) { console.error(e) } finally { loading.value = false }
}

// 监听搜索关键词变化（防抖）
watch(() => appStore.searchKeyword, () => {
  if (loadTimer) clearTimeout(loadTimer)
  loadTimer = setTimeout(() => {
    loadReports()
  }, 300)
})

function openCreateDialog() {
  Object.assign(createForm, { name: '', project_id: null, report_type: '', test_scope: '' })
  createVisible.value = true
}

async function handleCreate() {
  creating.value = true
  try { await createReport({ ...createForm }); await loadReports(); ElMessage.success('报告生成中...'); createVisible.value = false; appStore.refreshSidebarBadges() } catch (e) { ElMessage.error('生成失败') } finally { creating.value = false }
}

function handleEdit(row) {
  editId.value = row.id
  Object.assign(editForm, { name: row.name, status: row.status, report_type: row.report_type || '' })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try { await updateReport(editId.value, { ...editForm }); await loadReports(); ElMessage.success('保存成功'); editVisible.value = false } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除报告"${row.name}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteReport(row.id); await loadReports(); ElMessage.success('删除成功'); appStore.refreshSidebarBadges() }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('reports', '测试报告', '生成报告', openCreateDialog)
  loading.value = true
  try {
    const [repRes, statsRes, projRes] = await Promise.allSettled([getReports(), getReportStats(), getProjects()])
    if (repRes.status === 'fulfilled') reports.value = repRes.value.data
    if (statsRes.status === 'fulfilled') stats.value = statsRes.value.data
    if (projRes.status === 'fulfilled') projectOptions.value = projRes.value.data
  } catch (e) { console.error(e) } finally { loading.value = false }
})
</script>

<style scoped>
.report-list { max-width: 1400px; }
.action-btns { display: flex; gap: 4px; }
.card-action { font-size: 12px; color: var(--accent); cursor: pointer; font-weight: 500; }
.card-action:hover { text-decoration: underline; }
</style>
