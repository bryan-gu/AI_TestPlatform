<template>
  <div class="knowledge-detail">
    <div class="back-link" @click="goBack">
      <el-icon><ArrowLeft /></el-icon>
      <span>返回知识库列表</span>
    </div>

    <div class="card" style="margin-bottom: 16px">
      <div class="card-head">
        <div class="kb-info">
          <el-icon :style="{ color: kb.iconColor, fontSize: '16px' }"><Files /></el-icon>
          <div>
            <div class="card-title">{{ kb.name }}</div>
            <div class="kb-desc">{{ kb.description }}</div>
          </div>
        </div>
      </div>
      <div class="kb-meta">
        <span>所属项目：<strong>{{ kb.project }}</strong></span>
        <span>创建人：<strong>{{ kb.creator }}</strong></span>
        <span>创建时间：<strong>{{ kb.createdAt }}</strong></span>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <div class="card-title">文件夹列表</div>
        <div class="card-actions">
          <div class="card-action">创建文件夹</div>
          <div class="card-action">上传文档</div>
        </div>
      </div>
      <el-table :data="folders" style="width: 100%" @row-click="goToDocs">
        <el-table-column label="文件夹名称" min-width="250">
          <template #default="{ row }">
            <div class="folder-name">
              <el-icon style="color: #EF9F27"><Folder /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="docCount" label="文档数量" width="120" />
        <el-table-column prop="createdAt" label="创建时间" width="150" />
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

    <el-dialog v-model="editVisible" title="编辑文件夹" width="400px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="文件夹名称"><el-input v-model="editForm.name" /></el-form-item>
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
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { ArrowLeft, Files, Folder, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const kb = ref({ id: 1, name: '电商平台知识库', description: '电商平台 v3.0 项目需求文档、接口文档及会议纪要', project: '电商平台 v3.0', creator: '李明', createdAt: '2026-03-15', iconColor: '#378ADD' })

const folders = ref([
  { id: 1, name: 'Sprint 0', docCount: 5, createdAt: '2026-03-15' },
  { id: 2, name: 'Sprint 1', docCount: 4, createdAt: '2026-03-28' },
  { id: 3, name: 'Sprint 2', docCount: 3, createdAt: '2026-04-15' },
  { id: 4, name: 'Sprint 3', docCount: 3, createdAt: '2026-05-10' }
])

const editVisible = ref(false)
const editIndex = ref(-1)
const editForm = reactive({ name: '' })

function goBack() { router.push('/knowledge') }
function goToDocs(row) { router.push(`/knowledge/${route.params.id}/folder/${row.id}`) }

function handleEdit(row) {
  editIndex.value = folders.value.indexOf(row)
  editForm.name = row.name
  editVisible.value = true
}

function handleSave() {
  if (editIndex.value >= 0) {
    folders.value[editIndex.value].name = editForm.name
    ElMessage.success('保存成功')
  }
  editVisible.value = false
}

function handleDelete(index, name) {
  ElMessageBox.confirm(`确定要删除文件夹"${name}"吗？删除后数据将无法恢复。`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    folders.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  appStore.setCurrentPage('knowledge', '知识库详情', '创建文件夹')
})
</script>

<style scoped>
.knowledge-detail { max-width: 1400px; }
.back-link { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; color: var(--accent); cursor: pointer; margin-bottom: 16px; }
.back-link:hover { text-decoration: underline; }
.kb-info { display: flex; align-items: center; gap: 8px; }
.kb-desc { font-size: 11px; color: var(--color-text-tertiary); margin-top: 2px; }
.kb-meta { padding: 14px 18px; display: flex; gap: 20px; font-size: 12px; color: var(--color-text-secondary); }
.card-actions { display: flex; gap: 10px; }
.folder-name { display: flex; align-items: center; gap: 6px; }
.folder-name .el-icon { font-size: 16px; }
.el-table { cursor: pointer; }
.action-btns { display: flex; gap: 4px; }
</style>
