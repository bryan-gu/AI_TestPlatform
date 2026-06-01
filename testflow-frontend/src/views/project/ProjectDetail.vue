<template>
  <div class="project-detail">
    <!-- 项目基本信息 -->
    <div class="card" style="margin-bottom: 16px">
      <div class="card-head">
        <div class="card-title">项目信息</div>
        <div class="card-action" @click="goBack">返回列表</div>
      </div>
      <div class="project-info">
        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">项目名称</div>
            <div class="info-value">{{ project.name }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">负责人</div>
            <div class="info-value">{{ project.owner }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">状态</div>
            <div class="info-value">
              <el-tag :type="getStatusType(project.status)" size="small">
                {{ getStatusText(project.status) }}
              </el-tag>
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">创建时间</div>
            <div class="info-value">{{ project.createdAt }}</div>
          </div>
        </div>
        <div class="info-item" style="margin-top: 12px">
          <div class="info-label">项目描述</div>
          <div class="info-value">{{ project.description }}</div>
        </div>
        <div class="info-item" style="margin-top: 12px">
          <div class="info-label">进度</div>
          <div class="info-value" style="display: flex; align-items: center; gap: 10px; max-width: 400px">
            <el-progress
              :percentage="project.progress"
              :stroke-width="8"
              style="flex: 1"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 关联测试用例 -->
    <div class="card" style="margin-bottom: 16px">
      <div class="card-head">
        <div class="card-title">关联测试用例</div>
        <div class="card-action">查看全部</div>
      </div>
      <el-table :data="testCases" style="width: 100%">
        <el-table-column prop="caseNo" label="用例编号" width="120" />
        <el-table-column prop="title" label="用例标题" min-width="200" show-overflow-tooltip />
        <el-table-column label="优先级" width="80">
          <template #default="{ row }">
            <span :class="getPriorityClass(row.priority)">{{ row.priority }}</span>
          </template>
        </el-table-column>
        <el-table-column label="执行状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getExecStatusType(row.execStatus)" size="small">
              {{ row.execStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="executor" label="执行人" width="80" />
      </el-table>
    </div>

    <!-- 关联测试报告 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">关联测试报告</div>
        <div class="card-action">查看全部</div>
      </div>
      <el-table :data="testReports" style="width: 100%">
        <el-table-column prop="name" label="报告名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="通过率" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.passRate >= 85 ? '#1D9E75' : '#EF9F27', fontWeight: 500 }">
              {{ row.passRate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="defectCount" label="缺陷数" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '已审批' ? 'success' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="生成时间" width="120" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const project = ref({
  id: 1,
  name: '电商平台 v3.0',
  progress: 72,
  status: 'testing',
  owner: '李明',
  description: '电商平台核心功能迭代，包含购物车、订单、支付等模块。本版本重点优化了支付流程和订单状态管理，新增了优惠券叠加功能。',
  createdAt: '2026-03-15'
})

const testCases = ref([
  { caseNo: 'TC-001', title: '用户登录 - 正常账号密码', priority: '高', execStatus: '通过', executor: '李明' },
  { caseNo: 'TC-002', title: '购物车添加商品', priority: '高', execStatus: '通过', executor: '王芳' },
  { caseNo: 'TC-015', title: '订单创建 - 普通商品', priority: '高', execStatus: '通过', executor: '李明' },
  { caseNo: 'TC-032', title: '支付流程 - 微信支付', priority: '中', execStatus: '执行中', executor: '陈刚' },
  { caseNo: 'TC-047', title: '订单结算 - 优惠券叠加', priority: '中', execStatus: '失败', executor: '王芳' }
])

const testReports = ref([
  { name: '电商平台迭代测试报告 #8', passRate: 81, defectCount: 9, status: '已审批', createdAt: '2026-05-28' },
  { name: '电商平台迭代测试报告 #7', passRate: 92, defectCount: 6, status: '已审批', createdAt: '2026-05-20' },
  { name: '电商平台冒烟测试报告 #2', passRate: 95, defectCount: 3, status: '待审批', createdAt: '2026-05-15' }
])

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

function goBack() {
  router.push('/projects')
}

onMounted(() => {
  appStore.setCurrentPage('projects', '项目详情', '编辑项目')
  // TODO: 根据 route.params.id 从API获取项目详情
  const projectId = route.params.id
  console.log('加载项目详情:', projectId)
})
</script>

<style scoped>
.project-detail {
  max-width: 1400px;
}

.project-info {
  padding: 16px 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.info-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  color: var(--color-text-primary);
}
</style>
