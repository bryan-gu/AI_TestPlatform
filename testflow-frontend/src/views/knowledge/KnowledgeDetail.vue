<template>
  <div class="knowledge-detail">
    <!-- 面包屑 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item" @click="goToProject">
        <el-icon :size="13"><Folder /></el-icon>电商平台 v3.0
      </span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item" @click="goToKnowledge">Sprint 列表</span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item current">{{ sprint.name }}</span>
    </div>

    <!-- Sprint 信息卡片 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div style="display:flex;align-items:center;gap:8px">
          <el-icon :size="16" style="color:var(--accent)"><Promotion /></el-icon>
          <div>
            <div class="card-title">{{ sprint.name }}</div>
            <div style="font-size:11px;color:var(--color-text-tertiary);margin-top:2px">
              {{ sprint.project }} · {{ sprint.status }} · {{ modules.length }} 个模块
            </div>
          </div>
        </div>
      </div>
      <div class="sprint-meta">
        <span>所属项目：<strong>{{ sprint.project }}</strong></span>
        <span>文档数：<strong>{{ sprint.docCount }}</strong></span>
        <span>功能点：<strong>{{ sprint.featurePoints }}</strong></span>
        <span>图谱节点：<strong>{{ sprint.graphNodes }}</strong></span>
      </div>
    </div>

    <!-- 模块列表 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">模块列表</div>
        <div style="display:flex;gap:10px">
          <div class="card-action" @click="handleAddModule">添加模块</div>
          <div class="card-action" @click="handleUploadDoc">上传文档</div>
        </div>
      </div>
      <el-table :data="modules" style="width:100%" @row-click="goToDocs" v-loading="loading">
        <el-table-column label="模块名称" min-width="200">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px">
              <el-icon :size="15" :style="{ color: row.iconColor }"><Box /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="docCount" label="文档数" width="80" />
        <el-table-column prop="featurePoints" label="功能点" width="80" />
        <el-table-column prop="linkedCases" label="关联用例" width="90" />
        <el-table-column label="AI 状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.aiStatus === '已分析' ? 'success' : 'warning'" size="small" effect="plain" round>
              {{ row.aiStatus }}
            </el-tag>
          </template>
        </el-table-column>
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

    <!-- 编辑模块对话框 -->
    <el-dialog v-model="editVisible" title="编辑模块" width="400px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="模块名称"><el-input v-model="editForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加模块对话框 -->
    <el-dialog v-model="addVisible" title="添加模块" width="400px" destroy-on-close>
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="模块名称"><el-input v-model="addForm.name" placeholder="请输入模块名称" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddSave" :loading="saving">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Folder, Promotion, Box, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)

// Sprint 信息 (Mock)
const sprint = ref({
  id: route.params.id,
  name: 'Sprint 2',
  project: '电商平台 v3.0',
  status: '进行中',
  docCount: 10,
  featurePoints: 23,
  graphNodes: 18
})

// 模块列表 (Mock)
const modules = ref([
  { id: 'm1', name: '用户登录注册', docCount: 3, featurePoints: 8, linkedCases: 23, aiStatus: '已分析', iconColor: 'var(--accent)' },
  { id: 'm2', name: '购物车模块', docCount: 2, featurePoints: 6, linkedCases: 18, aiStatus: '已分析', iconColor: '#378ADD' },
  { id: 'm3', name: '订单模块', docCount: 3, featurePoints: 5, linkedCases: 14, aiStatus: '分析中', iconColor: '#E24B4A' },
  { id: 'm4', name: '支付模块', docCount: 2, featurePoints: 4, linkedCases: 11, aiStatus: '已分析', iconColor: '#EF9F27' }
])

const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '' })

const addVisible = ref(false)
const addForm = reactive({ name: '' })

function goToProject() { router.push('/projects') }
function goToKnowledge() { router.push('/knowledge') }
function goToDocs(row) { router.push(`/knowledge/${route.params.id}/folder/${row.id}`) }

function handleEdit(row) {
  editId.value = row.id
  editForm.name = row.name
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    await new Promise(r => setTimeout(r, 500))
    const mod = modules.value.find(m => m.id === editId.value)
    if (mod) mod.name = editForm.name
    ElMessage.success('保存成功')
    editVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

function handleDelete(index, row) {
  ElMessageBox.confirm(`确定要删除模块"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    await new Promise(r => setTimeout(r, 300))
    modules.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function handleAddModule() {
  addForm.name = ''
  addVisible.value = true
}

async function handleAddSave() {
  saving.value = true
  try {
    await new Promise(r => setTimeout(r, 500))
    const colors = ['var(--accent)', '#378ADD', '#E24B4A', '#EF9F27', '#8B5CF6']
    modules.value.push({
      id: `m-${Date.now()}`, name: addForm.name, docCount: 0, featurePoints: 0,
      linkedCases: 0, aiStatus: '待分析',
      iconColor: colors[modules.value.length % colors.length]
    })
    ElMessage.success('添加成功')
    addVisible.value = false
  } catch (e) { ElMessage.error('添加失败') } finally { saving.value = false }
}

function handleUploadDoc() {
  ElMessage.info('上传文档功能开发中...')
}

onMounted(() => {
  appStore.setCurrentPage('knowledge', '模块列表', '添加模块', handleAddModule)
  // TODO: 根据route.params.id加载Sprint和模块数据
})
</script>

<style scoped>
.knowledge-detail { max-width: 1400px; }

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

.sprint-meta {
  padding: 14px 18px;
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

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
