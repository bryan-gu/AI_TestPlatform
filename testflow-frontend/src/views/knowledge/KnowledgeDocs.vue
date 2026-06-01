<template>
  <div class="knowledge-docs">
    <div class="back-link" @click="goBack"><el-icon><ArrowLeft /></el-icon><span>返回文件夹列表</span></div>

    <div class="card" style="margin-bottom: 16px">
      <div class="card-head">
        <div class="folder-info">
          <el-icon style="color: #EF9F27; font-size: 16px"><Folder /></el-icon>
          <div><div class="card-title">{{ folder.name }}</div><div class="folder-path">{{ kb.name }} / {{ folder.name }}</div></div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title">文档列表</div><div class="card-action">上传文档</div></div>
      <el-table :data="documents" style="width: 100%" v-loading="loading">
        <el-table-column label="文档名称" min-width="280">
          <template #default="{ row }"><div class="doc-name"><el-icon style="color: #378ADD"><Document /></el-icon><span>{{ row.name }}</span></div></template>
        </el-table-column>
        <el-table-column label="类型" width="100"><template #default="{ row }"><span :class="getTypeClass(row.file_type)">{{ row.file_type }}</span></template></el-table-column>
        <el-table-column prop="uploader" label="上传人" width="80" />
        <el-table-column label="上传时间" width="120"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
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

    <el-dialog v-model="editVisible" title="编辑文档" width="400px" destroy-on-close>
      <el-form :model="editForm" label-width="80px"><el-form-item label="文档名称"><el-input v-model="editForm.name" /></el-form-item></el-form>
      <template #footer><el-button @click="editVisible = false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { ArrowLeft, Folder, Document, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgeBase, getFolders, getDocuments, updateDocument, deleteDocument } from '../../api/knowledge'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const kb = ref({})
const folder = ref({})
const documents = ref([])
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '' })

function getTypeClass(t) { return { 'PDF': 'badge badge-blue', 'Word': 'badge badge-green', 'Markdown': 'badge badge-purple', 'Excel': 'badge badge-amber' }[t] || 'badge badge-gray' }
function formatDate(d) { return d ? d.split('T')[0] : '' }
function goBack() { router.push(`/knowledge/${route.params.id}`) }

function handleEdit(row) { editId.value = row.id; editForm.name = row.name; editVisible.value = true }

async function handleSave() {
  saving.value = true
  try {
    await updateDocument(route.params.id, route.params.folderId, editId.value, { name: editForm.name })
    const res = await getDocuments(route.params.id, route.params.folderId)
    documents.value = res.data
    ElMessage.success('保存成功')
    editVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除文档"${row.name}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteDocument(route.params.id, route.params.folderId, row.id); documents.value.splice(index, 1); ElMessage.success('删除成功') }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('knowledge', '文档列表', '上传文档')
  const { id: kbId, folderId } = route.params
  loading.value = true
  try {
    const [kbRes, foldersRes, docsRes] = await Promise.all([getKnowledgeBase(kbId), getFolders(kbId), getDocuments(kbId, folderId)])
    kb.value = kbRes.data
    folder.value = foldersRes.data.find(f => f.id === Number(folderId)) || { name: '未知文件夹' }
    documents.value = docsRes.data
  } catch (e) { console.error(e) } finally { loading.value = false }
})
</script>

<style scoped>
.knowledge-docs { max-width: 1400px; }
.back-link { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; color: var(--accent); cursor: pointer; margin-bottom: 16px; }
.back-link:hover { text-decoration: underline; }
.folder-info { display: flex; align-items: center; gap: 8px; }
.folder-path { font-size: 11px; color: var(--color-text-tertiary); margin-top: 2px; }
.doc-name { display: flex; align-items: center; gap: 8px; }
.badge-purple { background: #EEEDFE; color: #26215C; }
.action-btns { display: flex; gap: 4px; }
</style>
