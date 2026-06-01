<template>
  <div class="role-management">
    <div class="two-col">
      <div class="stat-card">
        <div class="stat-label">角色总数</div>
        <div class="stat-value">{{ stats.totalRoles }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>系统内置 {{ stats.builtInRoles }} 个</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">权限数</div>
        <div class="stat-value">{{ stats.totalPermissions }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>覆盖全部模块</div>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <div class="card-title">角色列表</div>
        <div class="card-action">新建角色</div>
      </div>
      <el-table :data="roles" style="width: 100%">
        <el-table-column label="角色名称" min-width="200">
          <template #default="{ row }">
            <div class="role-name">
              <div class="role-icon" :style="{ background: row.iconBg, color: row.iconColor }">
                <el-icon><component :is="icons[row.icon]" /></el-icon>
              </div>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === '内置' ? 'info' : ''" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="memberCount" label="成员数" width="80" />
        <el-table-column prop="permissions" label="权限范围" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="160">
          <template #default="{ row, $index }">
            <template v-if="row.editable">
              <div class="action-btns">
                <el-button type="primary" link size="small" @click="handleEdit(row)">
                  <el-icon><Edit /></el-icon>编辑
                </el-button>
                <el-button type="danger" link size="small" @click="handleDelete($index, row.name)">
                  <el-icon><Delete /></el-icon>删除
                </el-button>
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
        <el-form-item label="权限范围"><el-input v-model="editForm.permissions" type="textarea" :rows="3" /></el-form-item>
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
import * as icons from '@element-plus/icons-vue'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const appStore = useAppStore()

const stats = ref({ totalRoles: 5, builtInRoles: 2, totalPermissions: 32 })

const roles = ref([
  { id: 1, name: '超级管理员', type: '内置', memberCount: 2, permissions: '全部权限', editable: false, icon: 'Trophy', iconBg: '#FAEEDA', iconColor: '#BA7517' },
  { id: 2, name: '项目管理员', type: '自定义', memberCount: 5, permissions: '项目、用例、报告', editable: true, icon: 'Lock', iconBg: '#EEEDFE', iconColor: '#534AB7' },
  { id: 3, name: '测试工程师', type: '自定义', memberCount: 12, permissions: '用例执行、报告查看', editable: true, icon: 'User', iconBg: '#E1F5EE', iconColor: '#1D9E75' },
  { id: 4, name: '只读观察员', type: '自定义', memberCount: 5, permissions: '仅查看', editable: true, icon: 'View', iconBg: '#F1EFE8', iconColor: '#2C2C2A' }
])

const editVisible = ref(false)
const editIndex = ref(-1)
const editForm = reactive({ name: '', permissions: '' })

function handleEdit(row) {
  editIndex.value = roles.value.indexOf(row)
  Object.assign(editForm, { name: row.name, permissions: row.permissions })
  editVisible.value = true
}

function handleSave() {
  if (editIndex.value >= 0) {
    Object.assign(roles.value[editIndex.value], editForm)
    ElMessage.success('保存成功')
  }
  editVisible.value = false
}

function handleDelete(index, name) {
  ElMessageBox.confirm(`确定要删除角色"${name}"吗？删除后数据将无法恢复。`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    roles.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  appStore.setCurrentPage('roles', '角色管理', '新建角色')
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
