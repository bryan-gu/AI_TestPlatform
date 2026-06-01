<template>
  <div class="project-detail">
    <div class="card" style="margin-bottom: 16px">
      <div class="card-head">
        <div class="card-title">项目信息</div>
        <div class="card-action" @click="goBack">返回列表</div>
      </div>
      <div class="project-info" v-loading="loading">
        <div class="info-grid">
          <div class="info-item"><div class="info-label">项目名称</div><div class="info-value">{{ project.name }}</div></div>
          <div class="info-item"><div class="info-label">负责人</div><div class="info-value">{{ project.owner }}</div></div>
          <div class="info-item"><div class="info-label">状态</div><div class="info-value"><el-tag :type="getStatusType(project.status)" size="small">{{ getStatusText(project.status) }}</el-tag></div></div>
          <div class="info-item"><div class="info-label">创建时间</div><div class="info-value">{{ formatDate(project.created_at) }}</div></div>
        </div>
        <div class="info-item" style="margin-top: 12px"><div class="info-label">项目描述</div><div class="info-value">{{ project.description }}</div></div>
        <div class="info-item" style="margin-top: 12px"><div class="info-label">进度</div><div class="info-value" style="display: flex; align-items: center; gap: 10px; max-width: 400px"><el-progress :percentage="project.progress" :stroke-width="8" style="flex: 1" /></div></div>
      </div>
    </div>

    <div class="card" style="margin-bottom: 16px">
      <div class="card-head"><div class="card-title">关联测试用例</div></div>
      <el-table :data="testCases" style="width: 100%">
        <el-table-column prop="case_no" label="用例编号" width="120" />
        <el-table-column prop="title" label="用例标题" min-width="200" show-overflow-tooltip />
        <el-table-column label="优先级" width="80"><template #default="{ row }"><span :class="getPriorityClass(row.priority)">{{ row.priority }}</span></template></el-table-column>
        <el-table-column label="执行状态" width="100"><template #default="{ row }"><el-tag :type="getExecStatusType(row.exec_status)" size="small">{{ row.exec_status }}</el-tag></template></el-table-column>
        <el-table-column prop="executor" label="执行人" width="80" />
      </el-table>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title">关联测试报告</div></div>
      <el-table :data="testReports" style="width: 100%">
        <el-table-column prop="name" label="报告名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="通过率" width="100"><template #default="{ row }"><span :style="{ color: row.pass_rate >= 85 ? '#1D9E75' : '#EF9F27', fontWeight: 500 }">{{ row.pass_rate }}%</span></template></el-table-column>
        <el-table-column prop="defect_count" label="缺陷数" width="80" />
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="row.status === '已审批' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column label="生成时间" width="120"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { getProject, getProjectTestcases, getProjectReports } from '../../api/project'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const loading = ref(false)
const project = ref({})
const testCases = ref([])
const testReports = ref([])

function getStatusType(status) {
  const map = { testing: '', completed: 'success', active: 'warning', pending: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { testing: '测试中', completed: '已完成', active: '进行中', pending: '待启动' }
  return map[status] || status
}

function getPriorityClass(priority) {
  const map = { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }
  return map[priority] || 'badge badge-gray'
}

function getExecStatusType(status) {
  const map = { 通过: 'success', 失败: 'danger', 执行中: 'warning', 待执行: 'info' }
  return map[status] || 'info'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.split('T')[0]
}

function goBack() {
  router.push('/projects')
}

onMounted(async () => {
  appStore.setCurrentPage('projects', '项目详情', '编辑项目')
  const projectId = route.params.id
  loading.value = true
  try {
    const [projRes, casesRes, reportsRes] = await Promise.all([
      getProject(projectId),
      getProjectTestcases(projectId),
      getProjectReports(projectId)
    ])
    project.value = projRes.data
    testCases.value = casesRes.data
    testReports.value = reportsRes.data
  } catch (e) {
    console.error('加载项目详情失败:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.project-detail { max-width: 1400px; }
.project-info { padding: 16px 18px; }
.info-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.info-label { font-size: 12px; color: var(--color-text-tertiary); margin-bottom: 4px; }
.info-value { font-size: 14px; color: var(--color-text-primary); }
</style>
