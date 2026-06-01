<template>
  <div class="knowledge-base">
    <div class="two-col">
      <div class="stat-card">
        <div class="stat-label">知识库总数</div>
        <div class="stat-value">{{ stats.totalBases }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>覆盖全部项目</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">文档总数</div>
        <div class="stat-value">{{ stats.totalDocs }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>本月新增 {{ stats.newDocs }} 篇</div>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <div class="card-title">知识库列表</div>
        <div class="card-action">创建知识库</div>
      </div>
      <el-table :data="knowledgeBases" style="width: 100%" @row-click="goToDetail">
        <el-table-column label="知识库名称" min-width="200">
          <template #default="{ row }">
            <div class="kb-name">
              <el-icon :style="{ color: row.iconColor }"><Files /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="280" show-overflow-tooltip />
        <el-table-column prop="project" label="所属项目" width="150" />
        <el-table-column prop="creator" label="创建人" width="80" />
        <el-table-column prop="docCount" label="文档数" width="80" />
        <el-table-column prop="createdAt" label="创建时间" width="120" />
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

    <el-dialog v-model="editVisible" title="编辑知识库" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="知识库名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="editForm.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="所属项目">
          <el-select v-model="editForm.project" style="width: 100%">
            <el-option v-for="p in projectOptions" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
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
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Files, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const appStore = useAppStore()

const stats = ref({ totalBases: 4, totalDocs: 36, newDocs: 8 })
const projectOptions = ['电商平台 v3.0', '支付系统', '用户中心重构', '推荐算法 A/B']

const knowledgeBases = ref([
  { id: 1, name: '电商平台知识库', description: '电商平台 v3.0 项目需求文档、接口文档及会议纪要', project: '电商平台 v3.0', creator: '李明', docCount: 15, createdAt: '2026-03-15', iconColor: '#378ADD' },
  { id: 2, name: '支付系统知识库', description: '支付系统对接文档、安全规范及测试方案', project: '支付系统', creator: '王芳', docCount: 10, createdAt: '2026-02-20', iconColor: '#1D9E75' },
  { id: 3, name: '用户中心知识库', description: '用户中心重构项目 PRD、设计文档及评审记录', project: '用户中心重构', creator: '陈刚', docCount: 8, createdAt: '2026-04-01', iconColor: '#534AB7' },
  { id: 4, name: '推荐算法知识库', description: '推荐算法 A/B 实验方案及数据分析报告', project: '推荐算法 A/B', creator: '张丽', docCount: 3, createdAt: '2026-05-10', iconColor: '#EF9F27' }
])

const editVisible = ref(false)
const editIndex = ref(-1)
const editForm = reactive({ name: '', description: '', project: '' })

function goToDetail(row) { router.push(`/knowledge/${row.id}`) }

function handleEdit(row) {
  editIndex.value = knowledgeBases.value.indexOf(row)
  Object.assign(editForm, { name: row.name, description: row.description, project: row.project })
  editVisible.value = true
}

function handleSave() {
  if (editIndex.value >= 0) {
    Object.assign(knowledgeBases.value[editIndex.value], editForm)
    ElMessage.success('保存成功')
  }
  editVisible.value = false
}

function handleDelete(index, name) {
  ElMessageBox.confirm(`确定要删除知识库"${name}"吗？删除后数据将无法恢复。`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    knowledgeBases.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  appStore.setCurrentPage('knowledge', '知识库', '创建知识库')
})
</script>

<style scoped>
.knowledge-base { max-width: 1400px; }
.kb-name { display: flex; align-items: center; gap: 8px; }
.kb-name .el-icon { font-size: 16px; }
.el-table { cursor: pointer; }
.action-btns { display: flex; gap: 4px; }
</style>
