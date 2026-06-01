<template>
  <div class="report-list">
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-label">本月报告</div><div class="stat-value">{{ stats.monthlyReports }}</div><div class="stat-sub"><span class="stat-dot dot-blue"></span>较上月 +{{ stats.monthlyChange }}</div></div>
      <div class="stat-card"><div class="stat-label">平均通过率</div><div class="stat-value">{{ stats.avgPassRate }}%</div><div class="stat-sub"><span class="stat-dot dot-green"></span>持续提升</div></div>
      <div class="stat-card"><div class="stat-label">缺陷总计</div><div class="stat-value">{{ stats.totalDefects }}</div><div class="stat-sub"><span class="stat-dot dot-red"></span>已修复 {{ stats.fixedDefects }}</div></div>
      <div class="stat-card"><div class="stat-label">待审批报告</div><div class="stat-value">{{ stats.pendingApproval }}</div><div class="stat-sub"><span class="stat-dot dot-amber"></span>需要处理</div></div>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title">测试报告列表</div><div class="card-action">生成报告</div></div>
      <el-table :data="reports" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="报告名称" min-width="250" show-overflow-tooltip />
        <el-table-column prop="project" label="所属项目" width="150" />
        <el-table-column label="通过率" width="100"><template #default="{ row }"><span :style="{ color: row.pass_rate >= 85 ? '#1D9E75' : '#EF9F27', fontWeight: 500 }">{{ row.pass_rate }}%</span></template></el-table-column>
        <el-table-column prop="defect_count" label="缺陷数" width="80" />
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="row.status === '已审批' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column label="生成时间" width="120"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns">
              <el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="editVisible" title="编辑报告" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="报告名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="editForm.status" style="width: 100%"><el-option label="已审批" value="已审批" /><el-option label="待审批" value="待审批" /></el-select></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getReports, getReportStats, updateReport, deleteReport } from '../../api/report'

const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const stats = ref({ monthlyReports: 0, monthlyChange: 0, avgPassRate: 0, totalDefects: 0, fixedDefects: 0, pendingApproval: 0 })
const reports = ref([])
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '', status: '' })

function formatDate(d) { return d ? d.split('T')[0] : '' }

function handleEdit(row) {
  editId.value = row.id
  Object.assign(editForm, { name: row.name, status: row.status })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    await updateReport(editId.value, { ...editForm })
    const res = await getReports()
    reports.value = res.data
    ElMessage.success('保存成功')
    editVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除报告"${row.name}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteReport(row.id); reports.value.splice(index, 1); ElMessage.success('删除成功') }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('reports', '测试报告', '生成报告')
  loading.value = true
  try {
    const [repRes, statsRes] = await Promise.all([getReports(), getReportStats()])
    reports.value = repRes.data
    stats.value = statsRes.data
  } catch (e) { console.error(e) } finally { loading.value = false }
})
</script>

<style scoped>
.report-list { max-width: 1400px; }
.action-btns { display: flex; gap: 4px; }
</style>
