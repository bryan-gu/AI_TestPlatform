<template>
  <div class="knowledge-base">
    <div class="two-col">
      <div class="stat-card"><div class="stat-label">知识库总数</div><div class="stat-value">{{ stats.totalBases }}</div><div class="stat-sub"><span class="stat-dot dot-blue"></span>覆盖全部项目</div></div>
      <div class="stat-card"><div class="stat-label">文档总数</div><div class="stat-value">{{ stats.totalDocs }}</div><div class="stat-sub"><span class="stat-dot dot-green"></span>本月新增 {{ stats.newDocs }} 篇</div></div>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title">知识库列表</div></div>
      <el-table :data="knowledgeBases" style="width: 100%" @row-click="goToDetail" v-loading="loading">
        <el-table-column label="知识库名称" min-width="200"><template #default="{ row }"><div class="kb-name"><el-icon style="color: #378ADD"><Files /></el-icon><span>{{ row.name }}</span></div></template></el-table-column>
        <el-table-column prop="description" label="描述" min-width="280" show-overflow-tooltip />
        <el-table-column prop="project" label="所属项目" width="150" />
        <el-table-column prop="creator" label="创建人" width="80" />
        <el-table-column prop="doc_count" label="文档数" width="80" />
        <el-table-column label="创建时间" width="120"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }"><div class="action-btns" @click.stop><el-button type="primary" link size="small" @click="handleEdit(row)"><el-icon><Edit /></el-icon>编辑</el-button><el-button type="danger" link size="small" @click="handleDelete($index, row)"><el-icon><Delete /></el-icon>删除</el-button></div></template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="createVisible" title="创建知识库" width="520px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="createForm.name" placeholder="请输入知识库名称" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入描述" /></el-form-item>
        <el-form-item label="所属项目"><el-select v-model="createForm.project_id" style="width: 100%" placeholder="选择项目"><el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="createVisible = false">取消</el-button><el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button></template>
    </el-dialog>

    <el-dialog v-model="editVisible" title="编辑知识库" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="editForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="editVisible = false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Files, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgeBases, getKnowledgeStats, createKnowledgeBase, updateKnowledgeBase, deleteKnowledgeBase } from '../../api/knowledge'
import { getProjects } from '../../api/project'

const router = useRouter()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)
const stats = ref({ totalBases: 0, totalDocs: 0, newDocs: 0 })
const knowledgeBases = ref([])
const projectOptions = ref([])

const createVisible = ref(false)
const createForm = reactive({ name: '', description: '', project_id: null })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '', description: '' })

function formatDate(d) { return d ? d.split('T')[0] : '' }
function goToDetail(row) { router.push(`/knowledge/${row.id}`) }

function openCreateDialog() {
  Object.assign(createForm, { name: '', description: '', project_id: null })
  createVisible.value = true
}

async function handleCreate() {
  creating.value = true
  try { await createKnowledgeBase({ ...createForm }); const res = await getKnowledgeBases(); knowledgeBases.value = res.data; ElMessage.success('创建成功'); createVisible.value = false } catch (e) { ElMessage.error('创建失败') } finally { creating.value = false }
}

function handleEdit(row) { editId.value = row.id; Object.assign(editForm, { name: row.name, description: row.description }); editVisible.value = true }

async function handleSave() {
  saving.value = true
  try { await updateKnowledgeBase(editId.value, { ...editForm }); const res = await getKnowledgeBases(); knowledgeBases.value = res.data; ElMessage.success('保存成功'); editVisible.value = false } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除知识库"${row.name}"吗？`, '确认删除', { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => { await deleteKnowledgeBase(row.id); knowledgeBases.value.splice(index, 1); ElMessage.success('删除成功') }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('knowledge', '知识库', '创建知识库', openCreateDialog)
  loading.value = true
  try {
    const [kbRes, statsRes, projRes] = await Promise.allSettled([getKnowledgeBases(), getKnowledgeStats(), getProjects()])
    if (kbRes.status === 'fulfilled') knowledgeBases.value = kbRes.value.data
    if (statsRes.status === 'fulfilled') stats.value = statsRes.value.data
    if (projRes.status === 'fulfilled') projectOptions.value = projRes.value.data
  } catch (e) { console.error(e) } finally { loading.value = false }
})
</script>

<style scoped>
.knowledge-base { max-width: 1400px; }
.kb-name { display: flex; align-items: center; gap: 8px; }
.el-table { cursor: pointer; }
.action-btns { display: flex; gap: 4px; }
</style>
