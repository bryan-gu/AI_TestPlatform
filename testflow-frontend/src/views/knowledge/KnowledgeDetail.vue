<template>
  <div class="knowledge-detail">
    <div class="back-link" @click="goBack"><el-icon><ArrowLeft /></el-icon><span>返回知识库列表</span></div>

    <div class="card" style="margin-bottom: 16px" v-loading="loading">
      <div class="card-head">
        <div class="kb-info">
          <el-icon style="color: #378ADD; font-size: 16px"><Files /></el-icon>
          <div><div class="card-title">{{ kb.name }}</div><div class="kb-desc">{{ kb.description }}</div></div>
        </div>
      </div>
      <div class="kb-meta">
        <span>所属项目：<strong>{{ kb.project }}</strong></span>
        <span>创建人：<strong>{{ kb.creator }}</strong></span>
        <span>创建时间：<strong>{{ formatDate(kb.created_at) }}</strong></span>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <div class="card-title">文件夹列表</div>
        <div class="card-actions"><div class="card-action">创建文件夹</div><div class="card-action">上传文档</div></div>
      </div>
      <el-table :data="folders" style="width: 100%" @row-click="goToDocs">
        <el-table-column label="文件夹名称" min-width="250">
          <template #default="{ row }"><div class="folder-name"><el-icon style="color: #EF9F27"><Folder /></el-icon><span>{{ row.name }}</span></div></template>
        </el-table-column>
        <el-table-column prop="doc_count" label="文档数量" width="120" />
        <el-table-column label="创建时间" width="150"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns" @click.stop>
              <el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="editVisible" title="编辑文件夹" width="400px" destroy-on-close>
      <el-form :model="editForm" label-width="80px"><el-form-item label="文件夹名称"><el-input v-model="editForm.name" /></el-form-item></el-form>
      <template #footer><el-button @click="editVisible = false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { ArrowLeft, Files, Folder, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgeBase, getFolders, updateFolder, deleteFolder } from '../../api/knowledge'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const kb = ref({})
const folders = ref([])
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '' })

function formatDate(d) { return d ? d.split('T')[0] : '' }
function goBack() { router.push('/knowledge') }
function goToDocs(row) { router.push(`/knowledge/${route.params.id}/folder/${row.id}`) }

function handleEdit(row) { editId.value = row.id; editForm.name = row.name; editVisible.value = true }

async function handleSave() {
  saving.value = true
  try {
    await updateFolder(route.params.id, editId.value, { name: editForm.name })
    const res = await getFolders(route.params.id)
    folders.value = res.data
    ElMessage.success('保存成功')
    editVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除文件夹"${row.name}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteFolder(route.params.id, row.id); folders.value.splice(index, 1); ElMessage.success('删除成功') }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('knowledge', '知识库详情', '创建文件夹')
  const kbId = route.params.id
  loading.value = true
  try {
    const [kbRes, foldersRes] = await Promise.all([getKnowledgeBase(kbId), getFolders(kbId)])
    kb.value = kbRes.data
    folders.value = foldersRes.data
  } catch (e) { console.error(e) } finally { loading.value = false }
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
.el-table { cursor: pointer; }
.action-btns { display: flex; gap: 4px; }
</style>
