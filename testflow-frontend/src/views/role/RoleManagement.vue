<template>
  <div class="role-management">
    <div class="two-col">
      <div class="stat-card"><div class="stat-label">角色总数</div><div class="stat-value">{{ stats.totalRoles }}</div><div class="stat-sub"><span class="stat-dot dot-blue"></span>系统内置 {{ stats.builtInRoles }} 个</div></div>
      <div class="stat-card"><div class="stat-label">权限数</div><div class="stat-value">{{ stats.totalPermissions }}</div><div class="stat-sub"><span class="stat-dot dot-green"></span>覆盖全部模块</div></div>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title">角色列表</div><div class="card-action">新建角色</div></div>
      <el-table :data="roles" style="width: 100%" v-loading="loading">
        <el-table-column label="角色名称" min-width="200">
          <template #default="{ row }">
            <div class="role-name">
              <div class="role-icon" :style="{ background: getIconBg(row.name), color: getIconColor(row.name) }"><el-icon><component :is="getIcon(row.name)" /></el-icon></div>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100"><template #default="{ row }"><el-tag :type="row.type === '内置' ? 'info' : ''" size="small">{{ row.type }}</el-tag></template></el-table-column>
        <el-table-column prop="member_count" label="成员数" width="80" />
        <el-table-column label="权限范围" min-width="200" show-overflow-tooltip><template #default="{ row }">{{ formatPermissions(row.permissions) }}</template></el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row, $index }">
            <template v-if="row.is_editable">
              <div class="action-btns">
                <el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button>
              </div>
            </template>
            <span v-else class="action-disabled">不可编辑</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="editVisible" title="编辑角色" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="角色名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="权限范围"><el-input v-model="editForm.permissionsText" type="textarea" :rows="3" placeholder="多个权限用逗号分隔" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="editVisible = false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import { Trophy, Lock, User, View, Edit, Delete } from '@element-plus/icons-vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoles, getRoleStats, updateRole, deleteRole } from '../../api/role'

const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const stats = ref({ totalRoles: 0, builtInRoles: 0, totalPermissions: 0 })
const roles = ref([])
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '', permissionsText: '' })

const iconMap = { '超级管理员': 'Trophy', '项目管理员': 'Lock', '测试工程师': 'User', '只读观察员': 'View' }
const iconBgMap = { '超级管理员': '#FAEEDA', '项目管理员': '#EEEDFE', '测试工程师': '#E1F5EE', '只读观察员': '#F1EFE8' }
const iconColorMap = { '超级管理员': '#BA7517', '项目管理员': '#534AB7', '测试工程师': '#1D9E75', '只读观察员': '#2C2C2A' }

function getIcon(name) { return icons[iconMap[name]] || icons.User }
function getIconBg(name) { return iconBgMap[name] || '#F1EFE8' }
function getIconColor(name) { return iconColorMap[name] || '#2C2C2A' }
function formatPermissions(perms) { return Array.isArray(perms) ? perms.join('、') : perms || '' }

function handleEdit(row) {
  editId.value = row.id
  Object.assign(editForm, { name: row.name, permissionsText: Array.isArray(row.permissions) ? row.permissions.join(',') : row.permissions || '' })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const permissions = editForm.permissionsText.split(',').map(s => s.trim()).filter(Boolean)
    await updateRole(editId.value, { name: editForm.name, permissions })
    const res = await getRoles()
    roles.value = res.data
    ElMessage.success('保存成功')
    editVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除角色"${row.name}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteRole(row.id); roles.value.splice(index, 1); ElMessage.success('删除成功') }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('roles', '角色管理', '新建角色')
  loading.value = true
  try {
    const [rolesRes, statsRes] = await Promise.all([getRoles(), getRoleStats()])
    roles.value = rolesRes.data
    stats.value = statsRes.data
  } catch (e) { console.error(e) } finally { loading.value = false }
})
</script>

<style scoped>
.role-management { max-width: 1400px; }
.role-name { display: flex; align-items: center; gap: 10px; }
.role-icon { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.role-icon .el-icon { font-size: 14px; }
.action-btns { display: flex; gap: 4px; }
.action-disabled { font-size: 13px; color: var(--color-text-tertiary); }
</style>
