<template>
  <div class="testcase-list">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">全部用例</div>
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-blue"></span>
          跨 {{ stats.projectCount }} 个项目
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已通过</div>
        <div class="stat-value">{{ stats.passed }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-green"></span>
          通过率 {{ stats.passRate }}%
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">未通过</div>
        <div class="stat-value">{{ stats.failed }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-red"></span>
          需要处理
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">未执行</div>
        <div class="stat-value">{{ stats.pending }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-amber"></span>
          待排期
        </div>
      </div>
    </div>

    <!-- 用例列表 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">测试用例列表</div>
        <div class="card-filter">
          <el-select v-model="selectedProject" placeholder="全部项目" size="small" style="width: 150px" clearable>
            <el-option v-for="p in projectOptions" :key="p" :label="p" :value="p" />
          </el-select>
        </div>
      </div>
      <el-table :data="filteredCases" style="width: 100%">
        <el-table-column prop="caseNo" label="用例编号" width="100" />
        <el-table-column prop="title" label="用例标题" min-width="250" show-overflow-tooltip />
        <el-table-column label="优先级" width="80">
          <template #default="{ row }">
            <span :class="getPriorityClass(row.priority)">{{ row.priority }}</span>
          </template>
        </el-table-column>
        <el-table-column label="执行状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getExecStatusType(row.execStatus)" size="small">{{ row.execStatus }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="executor" label="执行人" width="80">
          <template #default="{ row }">{{ row.executor || '-' }}</template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="120" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns">
              <el-button type="primary" link size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete($index, row.caseNo)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑用例" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用例编号">
          <el-input v-model="editForm.caseNo" disabled />
        </el-form-item>
        <el-form-item label="用例标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="优先级">
            <el-select v-model="editForm.priority" style="width: 100%">
              <el-option label="高" value="高" />
              <el-option label="中" value="中" />
              <el-option label="低" value="低" />
            </el-select>
          </el-form-item>
          <el-form-item label="执行状态">
            <el-select v-model="editForm.execStatus" style="width: 100%">
              <el-option label="通过" value="通过" />
              <el-option label="失败" value="失败" />
              <el-option label="执行中" value="执行中" />
              <el-option label="待执行" value="待执行" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="执行人">
          <el-select v-model="editForm.executor" style="width: 100%" clearable>
            <el-option label="李明" value="李明" />
            <el-option label="王芳" value="王芳" />
            <el-option label="陈刚" value="陈刚" />
            <el-option label="张丽" value="张丽" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const appStore = useAppStore()

const stats = ref({ total: 128, projectCount: 4, passed: 96, passRate: 75, failed: 18, pending: 14 })
const selectedProject = ref('')
const projectOptions = ['电商平台 v3.0', '支付系统', '用户中心重构', '推荐算法 A/B']

const testCases = ref([
  { caseNo: 'TC-001', title: '用户登录 - 正常账号密码', priority: '高', execStatus: '通过', executor: '李明', project: '电商平台 v3.0', updatedAt: '今天 09:12' },
  { caseNo: 'TC-002', title: '购物车添加商品', priority: '高', execStatus: '通过', executor: '王芳', project: '电商平台 v3.0', updatedAt: '今天 10:05' },
  { caseNo: 'TC-047', title: '订单结算 - 优惠券叠加', priority: '中', execStatus: '失败', executor: '陈刚', project: '电商平台 v3.0', updatedAt: '35 分钟前' },
  { caseNo: 'TC-063', title: '退款申请流程', priority: '中', execStatus: '执行中', executor: '张丽', project: '支付系统', updatedAt: '今天 11:30' },
  { caseNo: 'TC-091', title: '支付接口超时处理', priority: '低', execStatus: '待执行', executor: '', project: '支付系统', updatedAt: '昨天' },
  { caseNo: 'TC-112', title: '消息推送 - 订单状态变更', priority: '低', execStatus: '通过', executor: '李明', project: '用户中心重构', updatedAt: '2 天前' }
])

const filteredCases = computed(() => {
  if (!selectedProject.value) return testCases.value
  return testCases.value.filter(c => c.project === selectedProject.value)
})

const editVisible = ref(false)
const editIndex = ref(-1)
const editForm = reactive({ caseNo: '', title: '', priority: '', execStatus: '', executor: '' })

function getPriorityClass(priority) {
  const map = { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }
  return map[priority] || 'badge badge-gray'
}

function getExecStatusType(status) {
  const map = { 通过: 'success', 失败: 'danger', 执行中: 'warning', 待执行: 'info' }
  return map[status] || 'info'
}

function handleEdit(row) {
  editIndex.value = testCases.value.indexOf(row)
  Object.assign(editForm, { caseNo: row.caseNo, title: row.title, priority: row.priority, execStatus: row.execStatus, executor: row.executor })
  editVisible.value = true
}

function handleSave() {
  if (editIndex.value >= 0) {
    Object.assign(testCases.value[editIndex.value], editForm)
    ElMessage.success('保存成功')
  }
  editVisible.value = false
}

function handleDelete(index, caseNo) {
  ElMessageBox.confirm(`确定要删除用例"${caseNo}"吗？删除后数据将无法恢复。`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    testCases.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  appStore.setCurrentPage('testcases', '测试用例', '新建用例')
})
</script>

<style scoped>
.testcase-list { max-width: 1400px; }
.card-filter { display: flex; align-items: center; gap: 8px; }
.action-btns { display: flex; gap: 4px; }
</style>
