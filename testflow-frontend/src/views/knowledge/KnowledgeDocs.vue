<template>
  <div class="knowledge-docs">
    <div class="back-link" @click="goBack">
      <el-icon><ArrowLeft /></el-icon>
      <span>返回文件夹列表</span>
    </div>

    <div class="card" style="margin-bottom: 16px">
      <div class="card-head">
        <div class="folder-info">
          <el-icon style="color: #EF9F27; font-size: 16px"><Folder /></el-icon>
          <div>
            <div class="card-title">{{ folder.name }}</div>
            <div class="folder-path">{{ kb.name }} / {{ folder.name }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <div class="card-title">文档列表</div>
        <div class="card-action">上传文档</div>
      </div>
      <el-table :data="documents" style="width: 100%">
        <el-table-column label="文档名称" min-width="280">
          <template #default="{ row }">
            <div class="doc-name">
              <el-icon :style="{ color: row.iconColor }"><Document /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <span :class="getTypeClass(row.type)">{{ row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="uploader" label="上传人" width="80" />
        <el-table-column prop="uploadedAt" label="上传时间" width="120" />
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

    <el-dialog v-model="editVisible" title="编辑文档" width="400px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="文档名称"><el-input v-model="editForm.name" /></el-form-item>
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
import { ArrowLeft, Folder, Document, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const kb = ref({ id: 1, name: '电商平台知识库' })
const folder = ref({ id: 2, name: 'Sprint 1' })

const documents = ref([
  { id: 1, name: '用户登录注册需求说明.pdf', type: 'PDF', uploader: '李明', uploadedAt: '2026-03-28', iconColor: '#378ADD' },
  { id: 2, name: '购物车模块 PRD v1.2.docx', type: 'Word', uploader: '王芳', uploadedAt: '2026-03-30', iconColor: '#1D9E75' },
  { id: 3, name: '订单流程评审会议纪要.md', type: 'Markdown', uploader: '陈刚', uploadedAt: '2026-04-02', iconColor: '#534AB7' },
  { id: 4, name: '支付接口对接方案.xlsx', type: 'Excel', uploader: '李明', uploadedAt: '2026-04-05', iconColor: '#EF9F27' }
])

const editVisible = ref(false)
const editIndex = ref(-1)
const editForm = reactive({ name: '' })

function getTypeClass(type) {
  const map = { 'PDF': 'badge badge-blue', 'Word': 'badge badge-green', 'Markdown': 'badge badge-purple', 'Excel': 'badge badge-amber' }
  return map[type] || 'badge badge-gray'
}

function goBack() { router.push(`/knowledge/${route.params.id}`) }

function handleEdit(row) {
  editIndex.value = documents.value.indexOf(row)
  editForm.name = row.name
  editVisible.value = true
}

function handleSave() {
  if (editIndex.value >= 0) {
    documents.value[editIndex.value].name = editForm.name
    ElMessage.success('保存成功')
  }
  editVisible.value = false
}

function handleDelete(index, name) {
  ElMessageBox.confirm(`确定要删除文档"${name}"吗？删除后数据将无法恢复。`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    documents.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  appStore.setCurrentPage('knowledge', '文档列表', '上传文档')
})
</script>

<style scoped>
.knowledge-docs { max-width: 1400px; }
.back-link { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; color: var(--accent); cursor: pointer; margin-bottom: 16px; }
.back-link:hover { text-decoration: underline; }
.folder-info { display: flex; align-items: center; gap: 8px; }
.folder-path { font-size: 11px; color: var(--color-text-tertiary); margin-top: 2px; }
.doc-name { display: flex; align-items: center; gap: 8px; }
.doc-name .el-icon { font-size: 16px; }
.badge-purple { background: #EEEDFE; color: #26215C; }
.action-btns { display: flex; gap: 4px; }
</style>
