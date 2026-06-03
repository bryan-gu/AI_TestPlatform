<template>
  <div class="graph-list">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">图谱总数</div>
        <div class="stat-value">{{ stats.totalGraphs }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-blue"></span>
          覆盖 {{ stats.projectCount }} 个项目
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">节点总数</div>
        <div class="stat-value">{{ stats.totalNodes }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-green"></span>
          本月新增 +{{ stats.newNodes }}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">关联总数</div>
        <div class="stat-value">{{ stats.totalEdges }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-amber"></span>
          平均每图 {{ stats.avgEdges }} 条
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">孤立节点</div>
        <div class="stat-value">{{ stats.isolatedNodes }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-red"></span>
          需要处理
        </div>
      </div>
    </div>

    <!-- 图谱列表 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">知识图谱列表</div>
        <el-button type="primary" size="small" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建图谱
        </el-button>
      </div>

      <el-table :data="graphs" style="width: 100%">
        <el-table-column prop="name" label="图谱名称" min-width="200">
          <template #default="{ row }">
            <div class="graph-name" @click="goToDetail(row)">
              <el-icon><Share /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="project" label="所属项目" width="150" />
        <el-table-column prop="nodeCount" label="节点数" width="100" />
        <el-table-column prop="edgeCount" label="关联数" width="100" />
        <el-table-column label="创建时间" width="120">
          <template #default="{ row }">{{ row.createdAt }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="action-btns">
              <button class="btn-edit" @click="goToDetail(row)">
                <el-icon><View /></el-icon> 查看
              </button>
              <button class="btn-delete" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon> 删除
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建知识图谱" width="500px">
      <el-form :model="formData" label-width="80px">
        <el-form-item label="图谱名称">
          <el-input v-model="formData.name" placeholder="请输入图谱名称" />
        </el-form-item>
        <el-form-item label="所属项目">
          <el-select v-model="formData.projectId" placeholder="请选择项目" style="width: 100%">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入图谱描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Share, View, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// 统计数据
const stats = reactive({
  totalGraphs: 4,
  projectCount: 3,
  totalNodes: 48,
  newNodes: 12,
  totalEdges: 86,
  avgEdges: 21,
  isolatedNodes: 2
})

// 图谱列表
const graphs = ref([
  {
    id: 1,
    name: '电商平台需求图谱',
    project: '电商平台 v3.0',
    nodeCount: 24,
    edgeCount: 38,
    createdAt: '2024-03-15'
  },
  {
    id: 2,
    name: '支付系统模块图谱',
    project: '支付系统',
    nodeCount: 12,
    edgeCount: 18,
    createdAt: '2024-03-20'
  },
  {
    id: 3,
    name: '用户中心功能图谱',
    project: '用户中心重构',
    nodeCount: 8,
    edgeCount: 15,
    createdAt: '2024-03-25'
  },
  {
    id: 4,
    name: '推荐算法依赖图谱',
    project: '推荐算法 A/B',
    nodeCount: 4,
    edgeCount: 15,
    createdAt: '2024-03-28'
  }
])

// 项目列表（用于下拉选择）
const projects = ref([
  { id: 1, name: '电商平台 v3.0' },
  { id: 2, name: '支付系统' },
  { id: 3, name: '用户中心重构' },
  { id: 4, name: '推荐算法 A/B' }
])

// 对话框
const showCreateDialog = ref(false)
const formData = reactive({
  name: '',
  projectId: '',
  description: ''
})

// 跳转到详情
function goToDetail(row) {
  router.push(`/graphs/${row.id}`)
}

// 新建图谱
function handleCreate() {
  if (!formData.name || !formData.projectId) {
    ElMessage.warning('请填写必填项')
    return
  }

  const project = projects.value.find(p => p.id === formData.projectId)
  graphs.value.push({
    id: Date.now(),
    name: formData.name,
    project: project?.name || '',
    nodeCount: 0,
    edgeCount: 0,
    createdAt: new Date().toISOString().split('T')[0]
  })

  ElMessage.success('创建成功')
  showCreateDialog.value = false
  formData.name = ''
  formData.projectId = ''
  formData.description = ''
}

// 删除图谱
function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除图谱"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    graphs.value = graphs.value.filter(g => g.id !== row.id)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  // TODO: 从API获取数据
})
</script>

<style scoped>
.graph-list {
  max-width: 1400px;
}

.graph-name {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--accent);
  cursor: pointer;
}

.graph-name:hover {
  text-decoration: underline;
}

.action-btns {
  display: flex;
  gap: 8px;
}

.btn-edit,
.btn-delete {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12.5px;
  cursor: pointer;
  border: none;
  background: none;
  padding: 2px 0;
  transition: opacity 0.15s;
}

.btn-edit {
  color: var(--accent);
}

.btn-delete {
  color: #E24B4A;
}

.btn-edit:hover,
.btn-delete:hover {
  opacity: 0.7;
  text-decoration: underline;
}
</style>
