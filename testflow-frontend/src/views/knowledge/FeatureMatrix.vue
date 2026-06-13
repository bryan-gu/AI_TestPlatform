<template>
  <div class="feature-matrix">
    <div class="card">
      <div class="card-head">
        <div class="card-title">功能点矩阵</div>
        <div class="filter-bar">
          <el-select v-model="projectId" placeholder="项目" size="small" style="width:160px" clearable filterable @change="onProjectChange">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-select v-model="sprintId" placeholder="Sprint" size="small" style="width:160px" clearable filterable @change="loadFeatures">
            <el-option v-for="s in sprints" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
          <el-input v-model="keyword" placeholder="搜索功能点" size="small" style="width:170px" clearable @change="loadFeatures">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
      </div>

      <el-table :data="features" style="width:100%" v-loading="loading" empty-text="暂无功能点，请先选择 Sprint 或运行需求分析">
        <el-table-column prop="name" label="功能点" min-width="160" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ row.description || '-' }}</template>
        </el-table-column>
        <el-table-column prop="entry_path" label="操作入口" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.entry_path || '-' }}</template>
        </el-table-column>
        <el-table-column label="优先级" width="80">
          <template #default="{ row }"><span :class="priorityClass(row.priority)">{{ row.priority || '中' }}</span></template>
        </el-table-column>
        <el-table-column prop="module_name" label="模块" width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ row.module_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="来源" width="80">
          <template #default="{ row }">{{ sourceText(row.source_type) }}</template>
        </el-table-column>
        <el-table-column label="覆盖用例" width="90">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :type="(row.coverage_count || 0) > 0 ? 'success' : 'info'">{{ row.coverage_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :type="row.status === 'deprecated' ? 'danger' : 'success'">{{ row.status || 'active' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openCases(row)">
              <el-icon><Connection /></el-icon>关联用例
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 覆盖用例抽屉 -->
    <el-drawer v-model="casesVisible" :title="`${currentFeature?.name || '功能点'} - 覆盖用例`" size="520px">
      <el-table :data="coverages" size="small" v-loading="casesLoading" empty-text="暂无覆盖用例">
        <el-table-column prop="testcase_no" label="用例编号" width="150" show-overflow-tooltip />
        <el-table-column prop="testcase_title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="覆盖类型" width="100">
          <template #default="{ row }">{{ row.coverage_type }}</template>
        </el-table-column>
        <el-table-column label="置信度" width="80">
          <template #default="{ row }">{{ row.confidence || 0 }}%</template>
        </el-table-column>
      </el-table>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Connection } from '@element-plus/icons-vue'
import { getFeaturePoints } from '../../api/featurePoint'
import { getProjects } from '../../api/project'
import { getSprints } from '../../api/sprint'
import { getFeaturePointTestCases } from '../../api/coverage'

const loading = ref(false)
const features = ref([])
const projects = ref([])
const sprints = ref([])
const projectId = ref(null)
const sprintId = ref(null)
const keyword = ref('')

const casesVisible = ref(false)
const casesLoading = ref(false)
const currentFeature = ref(null)
const coverages = ref([])

function priorityClass(p) {
  return { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }[p] || 'badge badge-gray'
}
function sourceText(t) {
  return { requirement: '需求', ui_explore: 'UI', api_doc: '接口', manual: '手工', ai_generated: 'AI', baseline_draft: '基线' }[t] || '手工'
}

async function loadProjects() {
  const res = await getProjects()
  projects.value = res.data || []
}

async function onProjectChange() {
  sprintId.value = null
  if (projectId.value) {
    const res = await getSprints({ project_id: projectId.value })
    sprints.value = res.data || []
  } else {
    sprints.value = []
  }
  await loadFeatures()
}

async function loadFeatures() {
  if (!sprintId.value) {
    features.value = []
    return
  }
  loading.value = true
  try {
    const params = { sprint_id: sprintId.value }
    if (keyword.value) params.keyword = keyword.value
    const res = await getFeaturePoints(params)
    features.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function openCases(row) {
  currentFeature.value = row
  coverages.value = []
  casesVisible.value = true
  casesLoading.value = true
  try {
    const res = await getFeaturePointTestCases(row.id)
    coverages.value = res.data || []
  } catch (e) {
    coverages.value = []
  } finally {
    casesLoading.value = false
  }
}

onMounted(async () => {
  await loadProjects()
})
</script>

<style scoped>
.feature-matrix { max-width: 1400px; }

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
  flex-wrap: wrap;
  gap: 8px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.filter-bar {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
</style>
