<template>
  <div class="user-management">
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-label">用户总数</div><div class="stat-value">{{ stats.totalUsers }}</div><div class="stat-sub"><span class="stat-dot dot-blue"></span>本月新增 {{ stats.newUsers }} 人</div></div>
      <div class="stat-card"><div class="stat-label">活跃用户</div><div class="stat-value">{{ stats.activeUsers }}</div><div class="stat-sub"><span class="stat-dot dot-green"></span>今日在线 {{ stats.onlineToday }}</div></div>
      <div class="stat-card"><div class="stat-label">禁用账号</div><div class="stat-value">{{ stats.disabledUsers }}</div><div class="stat-sub"><span class="stat-dot dot-red"></span>需要审查</div></div>
      <div class="stat-card"><div class="stat-label">待激活</div><div class="stat-value">{{ stats.pendingUsers }}</div><div class="stat-sub"><span class="stat-dot dot-amber"></span>等待邮件确认</div></div>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title">用户列表</div></div>
      <el-table :data="users" style="width: 100%" v-loading="loading">
        <el-table-column label="姓名" min-width="160"><template #default="{ row }"><div class="user-name-cell"><div class="user-avatar" :style="{ background: getAvatarBg(row.name), color: getAvatarColor(row.name) }">{{ row.name.charAt(0) }}</div><span>{{ row.name }}</span></div></template></el-table-column>
        <el-table-column prop="email" label="账号" min-width="180" />
        <el-table-column prop="role_name" label="角色" width="120" />
        <el-table-column label="所属项目" width="150"><template #default="{ row }">{{ row.project || '-' }}</template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column label="最近登录" width="120"><template #default="{ row }">{{ formatDate(row.last_login) || '-' }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }"><div class="action-btns"><el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button><el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button></div></template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="createVisible" title="邀请用户" width="520px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="createForm.name" placeholder="请输入姓名" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="createForm.email" placeholder="请输入邮箱" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="createForm.password" type="password" placeholder="请输入密码" show-password /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="角色"><el-select v-model="createForm.role_id" style="width: 100%"><el-option v-for="r in roleOptions" :key="r.id" :label="r.name" :value="r.id" /></el-select></el-form-item>
          <el-form-item label="所属项目"><el-select v-model="createForm.project" filterable placeholder="请选择所属项目" style="width: 100%"><el-option v-for="p in projectOptions" :key="p" :label="p" :value="p" /></el-select></el-form-item>
        </div>
      </el-form>
      <template #footer><el-button @click="createVisible = false">取消</el-button><el-button type="primary" @click="handleCreate" :loading="creating">邀请</el-button></template>
    </el-dialog>

    <el-dialog v-model="editVisible" title="编辑用户" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="账号"><el-input v-model="editForm.email" disabled /></el-form-item>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px">
          <el-form-item label="角色"><el-select v-model="editForm.role_id" style="width: 100%"><el-option v-for="r in roleOptions" :key="r.id" :label="r.name" :value="r.id" /></el-select></el-form-item>
          <el-form-item label="所属项目"><el-select v-model="editForm.project" filterable placeholder="请选择所属项目" style="width: 100%"><el-option v-for="p in projectOptions" :key="p" :label="p" :value="p" /></el-select></el-form-item>
        </div>
        <el-form-item label="状态"><el-select v-model="editForm.status" style="width: 100%"><el-option label="活跃" value="活跃" /><el-option label="离线" value="离线" /><el-option label="待激活" value="待激活" /><el-option label="禁用" value="禁用" /></el-select></el-form-item>
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
import { getUsers, getUserStats, createUser, updateUser, deleteUser } from '../../api/user'
import { getRoles } from '../../api/role'
import { getProjects } from '../../api/project'

const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)
const stats = ref({ totalUsers: 0, newUsers: 0, activeUsers: 0, onlineToday: 0, disabledUsers: 0, pendingUsers: 0 })
const users = ref([])
const roleOptions = ref([])
const projectOptions = ref([])

const createVisible = ref(false)
const createForm = reactive({ name: '', email: '', password: '', role_id: null, project: '' })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '', email: '', role_id: null, project: '', status: '' })

const avatarBgMap = { '张': '#E1F5EE', '李': '#E6F1FB', '王': '#EEEDFE', '陈': '#FAEEDA', '刘': '#F1EFE8' }
const avatarColorMap = { '张': '#085041', '李': '#042C53', '王': '#26215C', '陈': '#633806', '刘': '#2C2C2A' }

function getAvatarBg(name) { return avatarBgMap[name.charAt(0)] || '#F1EFE8' }
function getAvatarColor(name) { return avatarColorMap[name.charAt(0)] || '#2C2C2A' }
function getStatusType(s) { return { '活跃': 'success', '离线': 'warning', '待激活': '', '禁用': 'danger' }[s] || 'info' }
function formatDate(d) { return d ? d.split('T')[0] : '' }

function openCreateDialog() {
  Object.assign(createForm, { name: '', email: '', password: '', role_id: null, project: '' })
  createVisible.value = true
}

async function handleCreate() {
  creating.value = true
  try {
    await createUser({ ...createForm })
    users.value = (await getUsers()).data
    ElMessage.success('邀请成功')
    createVisible.value = false
  } catch (e) { ElMessage.error('邀请失败') } finally { creating.value = false }
}

function handleEdit(row) {
  editId.value = row.id
  Object.assign(editForm, { name: row.name, email: row.email, role_id: row.role_id, project: row.project, status: row.status })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    await updateUser(editId.value, { name: editForm.name, role_id: editForm.role_id, project: editForm.project, status: editForm.status })
    users.value = (await getUsers()).data
    ElMessage.success('保存成功')
    editVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除用户"${row.name}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteUser(row.id); users.value.splice(index, 1); ElMessage.success('删除成功') }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('users', '用户管理', '邀请用户', openCreateDialog)
  loading.value = true
  try {
    const [usersRes, statsRes, rolesRes, projectsRes] = await Promise.allSettled([getUsers(), getUserStats(), getRoles(), getProjects()])
    if (usersRes.status === 'fulfilled') users.value = usersRes.value.data
    if (statsRes.status === 'fulfilled') stats.value = statsRes.value.data
    if (rolesRes.status === 'fulfilled') roleOptions.value = rolesRes.value.data
    if (projectsRes.status === 'fulfilled') projectOptions.value = (projectsRes.value.data || []).map(p => p.name)
  } catch (e) { console.error(e) } finally { loading.value = false }
})
</script>

<style scoped>
.user-management { max-width: 1400px; }
.user-name-cell { display: flex; align-items: center; gap: 10px; }
.user-avatar { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 500; flex-shrink: 0; }
.action-btns { display: flex; gap: 4px; }
</style>
