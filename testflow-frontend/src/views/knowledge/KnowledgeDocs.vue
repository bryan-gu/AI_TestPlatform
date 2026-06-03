<template>
  <div class="knowledge-docs">
    <!-- 面包屑 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item" @click="goToProject">
        <el-icon :size="13"><Folder /></el-icon>电商平台 v3.0
      </span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item" @click="goToSprint">Sprint 2</span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item current">{{ module.name }}</span>
    </div>

    <!-- 模块信息卡片 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div style="display:flex;align-items:center;gap:8px">
          <el-icon :size="16" style="color:var(--accent)"><Box /></el-icon>
          <div>
            <div class="card-title">{{ module.name }}</div>
            <div style="font-size:11px;color:var(--color-text-tertiary);margin-top:2px">
              Sprint 2 / 电商平台 v3.0 · {{ module.docCount }} 个文档 · {{ module.featurePoints }} 个功能点
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div class="card-title">文档列表</div>
        <div class="card-action" @click="handleUploadDoc">上传文档</div>
      </div>
      <el-table :data="documents" style="width:100%" @row-click="goToPreview" v-loading="loading">
        <el-table-column label="文档名称" min-width="280">
          <template #default="{ row }">
            <div class="doc-name">
              <el-icon :size="15" :style="{ color: row.iconColor }"><Document /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.file_type)" size="small" effect="plain" round>{{ row.file_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploader" label="上传人" width="80" />
        <el-table-column prop="uploadDate" label="上传时间" width="120" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns" @click.stop>
              <el-button type="primary" link size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete($index, row)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- AI 提取的功能点 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">AI 提取的功能点</div>
        <el-tag type="success" size="small" effect="plain" round>已提取 {{ featurePoints.length }} 个</el-tag>
      </div>
      <el-table :data="featurePoints" style="width:100%">
        <el-table-column prop="name" label="功能点" min-width="200" />
        <el-table-column label="来源文档" min-width="200">
          <template #default="{ row }">
            <span style="font-size:12px;color:var(--color-text-tertiary)">{{ row.sourceDoc }}</span>
          </template>
        </el-table-column>
        <el-table-column label="关联用例" width="160">
          <template #default="{ row }">
            <span class="linked-cases" @click="goToTestCases">{{ row.linkedCases }}</span>
          </template>
        </el-table-column>
        <el-table-column label="图谱" width="60">
          <template #default>
            <el-icon style="color:var(--accent);cursor:pointer" @click="goToGraphs"><Share /></el-icon>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑文档对话框 -->
    <el-dialog v-model="editVisible" title="编辑文档" width="400px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="文档名称"><el-input v-model="editForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Folder, Box, Document, Edit, Delete, Share } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)

// 模块信息 (Mock)
const module = ref({
  id: route.params.folderId,
  name: '用户登录注册',
  docCount: 3,
  featurePoints: 8
})

// 文档列表 (Mock)
const documents = ref([
  { id: 1, name: '用户登录注册需求说明.pdf', file_type: 'PDF', uploader: '李明', uploadDate: '2026-03-28', iconColor: 'var(--accent)' },
  { id: 2, name: '第三方登录对接文档.docx', file_type: 'Word', uploader: '王芳', uploadDate: '2026-03-30', iconColor: '#16a34a' },
  { id: 3, name: '登录安全评审会议纪要.md', file_type: 'Markdown', uploader: '陈刚', uploadDate: '2026-04-02', iconColor: '#8B5CF6' }
])

// AI 提取的功能点 (Mock)
const featurePoints = ref([
  { name: '手机号注册流程', sourceDoc: '用户登录注册需求说明.pdf', linkedCases: 'TC-001~TC-005' },
  { name: '短信验证码校验', sourceDoc: '用户登录注册需求说明.pdf', linkedCases: 'TC-006~TC-008' },
  { name: '密码强度校验', sourceDoc: '用户登录注册需求说明.pdf', linkedCases: 'TC-009~TC-011' },
  { name: '微信 OAuth 登录', sourceDoc: '第三方登录对接文档.docx', linkedCases: 'TC-012~TC-015' },
  { name: '支付宝授权登录', sourceDoc: '第三方登录对接文档.docx', linkedCases: 'TC-016~TC-018' },
  { name: '第三方账号绑定手机号', sourceDoc: '第三方登录对接文档.docx', linkedCases: 'TC-019~TC-021' },
  { name: '密码找回流程', sourceDoc: '用户登录注册需求说明.pdf', linkedCases: 'TC-022' },
  { name: '登录态管理', sourceDoc: '登录安全评审会议纪要.md', linkedCases: 'TC-023' }
])

const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '' })

function getTypeTagType(t) {
  return { 'PDF': '', 'Word': 'success', 'Markdown': 'warning', 'Excel': 'danger' }[t] || 'info'
}

function goToProject() { router.push('/projects') }
function goToSprint() { router.push(`/knowledge/${route.params.id}`) }
function goToPreview(row) { router.push(`/knowledge/doc/${row.id}`) }
function goToTestCases() { router.push('/testcases') }
function goToGraphs() { router.push('/graphs') }

function handleUploadDoc() {
  ElMessage.info('上传文档功能开发中...')
}

function handleEdit(row) {
  editId.value = row.id
  editForm.name = row.name
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    await new Promise(r => setTimeout(r, 500))
    const doc = documents.value.find(d => d.id === editId.value)
    if (doc) doc.name = editForm.name
    ElMessage.success('保存成功')
    editVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除文档"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    await new Promise(r => setTimeout(r, 300))
    documents.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  appStore.setCurrentPage('knowledge', '文档列表', '上传文档', handleUploadDoc)
  // TODO: 根据route参数加载真实数据
})
</script>

<style scoped>
.knowledge-docs { max-width: 1400px; }

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 16px;
  font-size: 13px;
}

.breadcrumb-item {
  color: var(--accent);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.breadcrumb-item:hover { text-decoration: underline; }
.breadcrumb-item.current { color: var(--color-text-primary); cursor: default; font-weight: 500; }
.breadcrumb-item.current:hover { text-decoration: none; }

.breadcrumb-sep {
  margin: 0 8px;
  color: var(--color-text-tertiary);
}

.doc-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.linked-cases {
  font-family: var(--font-mono, monospace);
  color: var(--accent);
  cursor: pointer;
}

.linked-cases:hover { text-decoration: underline; }

.card-action {
  font-size: 12px;
  color: var(--accent);
  cursor: pointer;
  font-weight: 500;
}

.card-action:hover { text-decoration: underline; }

.action-btns { display: flex; gap: 4px; }
.el-table { cursor: pointer; }
</style>
