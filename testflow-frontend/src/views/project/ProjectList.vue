<template>
  <div class="project-list">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">进行中项目</div>
        <div class="stat-value">{{ stats.activeProjects }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-green"></span>
          全部正常运行
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">总测试用例</div>
        <div class="stat-value">{{ stats.totalCases }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-blue"></span>
          本月新增 +{{ stats.newCases }}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">通过率</div>
        <div class="stat-value">{{ stats.passRate }}%</div>
        <div class="stat-sub">
          <span class="stat-dot dot-amber"></span>
          较上周 +{{ stats.passRateChange }}%
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">待修复缺陷</div>
        <div class="stat-value">{{ stats.pendingBugs }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-red"></span>
          严重 {{ stats.severeBugs }} / 普通 {{ stats.normalBugs }}
        </div>
      </div>
    </div>

    <!-- 项目表格 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">项目列表</div>
      </div>
      <el-table :data="projects" style="width: 100%" @row-click="goToDetail">
        <el-table-column prop="name" label="项目名称" min-width="200" />
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 8px">
              <el-progress
                :percentage="row.progress"
                :stroke-width="5"
                :show-text="false"
                style="flex: 1"
              />
              <span style="font-size: 12px; color: var(--color-text-secondary); white-space: nowrap">
                {{ row.progress }}%
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner" label="负责人" width="100" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="创建时间" width="120" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns" @click.stop>
              <el-button type="primary" link size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete($index, row.name)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑项目" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="项目名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="状态">
            <el-select v-model="editForm.status" style="width: 100%">
              <el-option label="待启动" value="pending" />
              <el-option label="进行中" value="active" />
              <el-option label="测试中" value="testing" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item label="进度">
            <el-input-number v-model="editForm.progress" :min="0" :max="100" style="width: 100%" />
          </el-form-item>
        </div>
        <el-form-item label="负责人">
          <el-select v-model="editForm.owner" style="width: 100%">
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const appStore = useAppStore()

const stats = ref({
  activeProjects: 4,
  totalCases: 128,
  newCases: 23,
  passRate: 87,
  passRateChange: 2.4,
  pendingBugs: 9,
  severeBugs: 2,
  normalBugs: 7
})

const projects = ref([
  { id: 1, name: '电商平台 v3.0', progress: 72, status: 'testing', owner: '李明', description: '电商平台核心功能迭代，包含购物车、订单、支付等模块', createdAt: '2026-03-15' },
  { id: 2, name: '支付系统', progress: 94, status: 'completed', owner: '王芳', description: '支付网关对接，支持微信、支付宝、银联等支付方式', createdAt: '2026-02-20' },
  { id: 3, name: '用户中心重构', progress: 38, status: 'active', owner: '陈刚', description: '用户中心架构升级，优化登录、注册、权限管理流程', createdAt: '2026-04-01' },
  { id: 4, name: '推荐算法 A/B', progress: 15, status: 'pending', owner: '张丽', description: '推荐算法 A/B 测试，验证新算法对转化率的影响', createdAt: '2026-05-10' }
])

const editVisible = ref(false)
const editIndex = ref(-1)
const editForm = reactive({ name: '', description: '', status: '', progress: 0, owner: '' })

function getStatusType(status) {
  const map = { testing: '', completed: 'success', active: 'warning', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { testing: '测试中', completed: '已完成', active: '进行中', pending: '待启动' }
  return map[status] || status
}

function goToDetail(row) {
  router.push(`/projects/${row.id}`)
}

function handleEdit(row) {
  editIndex.value = projects.value.indexOf(row)
  Object.assign(editForm, { name: row.name, description: row.description, status: row.status, progress: row.progress, owner: row.owner })
  editVisible.value = true
}

function handleSave() {
  if (editIndex.value >= 0) {
    Object.assign(projects.value[editIndex.value], editForm)
    ElMessage.success('保存成功')
  }
  editVisible.value = false
}

function handleDelete(index, name) {
  ElMessageBox.confirm(`确定要删除项目"${name}"吗？删除后数据将无法恢复。`, '确认删除', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    projects.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  appStore.setCurrentPage('projects', '项目管理', '新建项目')
})
</script>

<style scoped>
.project-list {
  max-width: 1400px;
}

.action-btns {
  display: flex;
  gap: 4px;
}
</style>
