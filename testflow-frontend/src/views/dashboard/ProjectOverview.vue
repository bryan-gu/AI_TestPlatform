<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">进行中项目</div>
        <div class="stat-value">{{ stats.activeProjects }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-green"></span>
          全部正常运行
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">总测试用例</div>
        <div class="stat-value">{{ stats.totalCases }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-blue"></span>
          本月新增 +{{ stats.newCases }}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">通过率</div>
        <div class="stat-value">{{ stats.passRate }}%</div>
        <div class="stat-sub">
          <span class="stat-dot dot-amber"></span>
          较上周 +{{ stats.passRateChange }}%
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">待修复缺陷</div>
        <div class="stat-value">{{ stats.pendingBugs }}</div>
        <div class="stat-sub">
          <span class="stat-dot dot-red"></span>
          严重 {{ stats.severeBugs }} / 普通 {{ stats.normalBugs }}
        </div>
      </div>
    </div>

    <!-- 项目列表和动态 -->
    <div class="two-col">
      <div class="card">
        <div class="card-head">
          <div class="card-title">项目列表</div>
          <div class="card-action" @click="goToProjects">全部查看</div>
        </div>
        <el-table :data="projects" style="width: 100%">
          <el-table-column prop="name" label="项目名称" />
          <el-table-column label="进度" width="180">
            <template #default="{ row }">
              <div style="display: flex; align-items: center; gap: 8px">
                <el-progress
                  :percentage="row.progress"
                  :stroke-width="5"
                  :show-text="false"
                  style="flex: 1"
                />
                <span style="font-size: 12px; color: var(--color-text-secondary)">
                  {{ row.progress }}%
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="owner" label="负责人" width="100" />
        </el-table>
      </div>

      <div class="card">
        <div class="card-head">
          <div class="card-title">近期动态</div>
        </div>
        <div class="activity-list">
          <div
            v-for="(activity, index) in activities"
            :key="index"
            class="activity-item"
          >
            <div
              class="act-icon"
              :style="{ background: activity.iconBg }"
            >
              <el-icon :style="{ color: activity.iconColor }">
                <component :is="activity.icon" />
              </el-icon>
            </div>
            <div class="act-text">
              <div class="act-main">{{ activity.text }}</div>
              <div class="act-time">{{ activity.time }} · {{ activity.user }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  CircleCheck,
  Warning,
  Document,
  UserFilled,
  Connection
} from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({
  activeProjects: 4,
  totalCases: 128,
  newCases: 23,
  passRate: 87,
  passRateChange: 2.4,
  pendingBugs: 9,
  severeBugs: 2,
  normalBugs: 7
})

const projects = ref([
  {
    id: 1,
    name: '电商平台 v3.0',
    progress: 72,
    status: 'testing',
    owner: '李明'
  },
  {
    id: 2,
    name: '支付系统',
    progress: 94,
    status: 'completed',
    owner: '王芳'
  },
  {
    id: 3,
    name: '用户中心重构',
    progress: 38,
    status: 'active',
    owner: '陈刚'
  },
  {
    id: 4,
    name: '推荐算法 A/B',
    progress: 15,
    status: 'pending',
    owner: '张丽'
  }
])

const activities = ref([
  {
    icon: 'CircleCheck',
    iconBg: '#E1F5EE',
    iconColor: '#1D9E75',
    text: '支付系统测试报告已生成',
    time: '10 分钟前',
    user: '王芳'
  },
  {
    icon: 'Warning',
    iconBg: '#FCEBEB',
    iconColor: '#E24B4A',
    text: '用例 #TC-047 执行失败，已创建缺陷',
    time: '35 分钟前',
    user: '陈刚'
  },
  {
    icon: 'Document',
    iconBg: '#E6F1FB',
    iconColor: '#378ADD',
    text: '《电商平台需求 v3.2》已上传至知识库',
    time: '1 小时前',
    user: '李明'
  },
  {
    icon: 'UserFilled',
    iconBg: '#EEEDFE',
    iconColor: '#534AB7',
    text: '新用户刘洋已加入测试团队',
    time: '3 小时前',
    user: '张测试'
  },
  {
    icon: 'Connection',
    iconBg: '#FAEEDA',
    iconColor: '#BA7517',
    text: '知识图谱关联更新：新增 12 条关系',
    time: '昨天 18:22',
    user: '系统'
  }
])

function getStatusType(status) {
  const map = {
    testing: '',
    completed: 'success',
    active: 'warning',
    pending: 'info'
  }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = {
    testing: '测试中',
    completed: '已完成',
    active: '进行中',
    pending: '待启动'
  }
  return map[status] || status
}

function goToProjects() {
  router.push('/projects')
}

onMounted(() => {
  // TODO: 从API获取数据
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}
</style>
