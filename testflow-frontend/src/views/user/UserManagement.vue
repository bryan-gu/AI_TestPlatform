<template>
  <div class="user-management">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">用户总数</div>
        <div class="stat-value">{{ stats.totalUsers }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>本月新增 {{ stats.newUsers }} 人</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">活跃用户</div>
        <div class="stat-value">{{ stats.activeUsers }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>今日在线 {{ stats.onlineToday }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">禁用账号</div>
        <div class="stat-value">{{ stats.disabledUsers }}</div>
        <div class="stat-sub"><span class="stat-dot dot-red"></span>需要审查</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">待激活</div>
        <div class="stat-value">{{ stats.pendingUsers }}</div>
        <div class="stat-sub"><span class="stat-dot dot-amber"></span>等待邮件确认</div>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <div class="card-title">用户列表</div>
        <div class="card-action">邀请用户</div>
      </div>
      <el-table :data="users" style="width: 100%">
        <el-table-column label="姓名" min-width="160">
          <template #default="{ row }">
            <div class="user-name-cell">
              <div class="user-avatar" :style="{ background: row.avatarBg, color: row.avatarColor }">{{ row.initial }}</div>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="账号" min-width="180" />
        <el-table-column prop="role" label="角色" width="120" />
        <el-table-column label="所属项目" width="150">
          <template #default="{ row }">{{ row.project || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLogin" label="最近登录" width="120">
          <template #default="{ row }">{{ row.lastLogin || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns">
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

    <el-dialog v-model="editVisible" title="编辑用户" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="账号"><el-input v-model="editForm.email" disabled /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="角色">
            <el-select v-model="editForm.role" style="width: 100%">
              <el-option label="超级管理员" value="超级管理员" />
              <el-option label="项目管理员" value="项目管理员" />
              <el-option label="测试工程师" value="测试工程师" />
              <el-option label="只读观察员" value="只读观察员" />
            </el-select>
          </el-form-item>
          <el-form-item label="所属项目">
            <el-select v-model="editForm.project" style="width: 100%" clearable>
              <el-option label="全部" value="全部" />
              <el-option label="电商平台" value="电商平台" />
              <el-option label="支付系统" value="支付系统" />
              <el-option label="用户中心" value="用户中心" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="活跃" value="活跃" />
            <el-option label="离线" value="离线" />
            <el-option label="待激活" value="待激活" />
            <el-option label="禁用" value="禁用" />
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
import { useAppStore } from '../../stores/app'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const appStore = useAppStore()

const stats = ref({ totalUsers: 24, newUsers: 3, activeUsers: 18, onlineToday: 11, disabledUsers: 2, pendingUsers: 4 })

const users = ref([
  { id: 1, name: '张测试', initial: '张', email: 'zhang@test.com', role: '超级管理员', project: '全部', status: '活跃', lastLogin: '刚刚', avatarBg: '#E1F5EE', avatarColor: '#085041' },
  { id: 2, name: '李明', initial: '李', email: 'liming@test.com', role: '项目管理员', project: '电商平台', status: '活跃', lastLogin: '10 分钟前', avatarBg: '#E6F1FB', avatarColor: '#042C53' },
  { id: 3, name: '王芳', initial: '王', email: 'wangfang@test.com', role: '测试工程师', project: '支付系统', status: '活跃', lastLogin: '35 分钟前', avatarBg: '#EEEDFE', avatarColor: '#26215C' },
  { id: 4, name: '陈刚', initial: '陈', email: 'chengang@test.com', role: '测试工程师', project: '用户中心', status: '离线', lastLogin: '3 小时前', avatarBg: '#FAEEDA', avatarColor: '#633806' },
  { id: 5, name: '刘洋', initial: '刘', email: 'liuyang@test.com', role: '测试工程师', project: '', status: '待激活', lastLogin: '', avatarBg: '#F1EFE8', avatarColor: '#2C2C2A' }
])

const editVisible = ref(false)
const editIndex = ref(-1)
const editForm = reactive({ name: '', email: '', role: '', project: '', status: '' })

function getStatusType(status) {
  const map = { '活跃': 'success', '离线': 'warning', '待激活': '', '禁用': 'danger' }
  return map[status] || 'info'
}

function handleEdit(row) {
  editIndex.value = users.value.indexOf(row)
  Object.assign(editForm, { name: row.name, email: row.email, role: row.role, project: row.project, status: row.status })
  editVisible.value = true
}

function handleSave() {
  if (editIndex.value >= 0) {
    Object.assign(users.value[editIndex.value], editForm)
    ElMessage.success('保存成功')
  }
  editVisible.value = false
}

function handleDelete(index, name) {
  ElMessageBox.confirm(`确定要删除用户"${name}"吗？删除后数据将无法恢复。`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    users.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  appStore.setCurrentPage('users', '用户管理', '邀请用户')
})
</script>

<style scoped>
.user-management { max-width: 1400px; }
.user-name-cell { display: flex; align-items: center; gap: 10px; }
.user-avatar { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 500; flex-shrink: 0; }
.action-btns { display: flex; gap: 4px; }
</style>
