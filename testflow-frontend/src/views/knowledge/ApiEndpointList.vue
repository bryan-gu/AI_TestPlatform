<template>
  <div class="api-endpoint-list">
    <!-- 面包屑 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item" @click="goToKnowledge">
        <el-icon :size="13"><Collection /></el-icon>知识库
      </span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item current">接口清单</span>
    </div>

    <!-- 筛选栏 -->
    <div class="card" style="margin-bottom:16px">
      <div class="filter-bar">
        <el-select v-model="filters.project_id" placeholder="选择项目" size="small" style="width:160px" clearable @change="handleFilterChange">
          <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-select v-model="filters.sprint_id" placeholder="选择 Sprint" size="small" style="width:180px" clearable @change="handleFilterChange">
          <el-option v-for="s in sprintOptions" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="filters.method" placeholder="Method" size="small" style="width:110px" clearable @change="handleFilterChange">
          <el-option v-for="m in methodOptions" :key="m" :label="m" :value="m" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" size="small" style="width:110px" clearable @change="handleFilterChange">
          <el-option label="活跃" value="active" />
          <el-option label="废弃" value="deprecated" />
          <el-option label="停用" value="disabled" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索路径 / Summary / Tag"
          size="small"
          style="width:240px"
          clearable
          @clear="handleFilterChange"
          @keyup.enter="handleFilterChange"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" size="small" @click="handleFilterChange">
          <el-icon><Search /></el-icon>搜索
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px">
      <div class="stat-card">
        <div class="stat-label">接口总数</div>
        <div class="stat-value">{{ total }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">活跃接口</div>
        <div class="stat-value">{{ activeCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>可使用</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已覆盖用例</div>
        <div class="stat-value">{{ coveredCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>有测试用例</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">未覆盖用例</div>
        <div class="stat-value">{{ total - coveredCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-amber"></span>缺少测试</div>
      </div>
    </div>

    <!-- 接口列表 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">接口列表</div>
      </div>
      <el-table :data="endpoints" style="width:100%" border v-loading="loading" empty-text="暂无接口数据" @row-click="openDetail">
        <el-table-column label="Method" min-width="90">
          <template #default="{ row }">
            <span :class="['method-badge', `method-${row.method?.toLowerCase()}`]">{{ row.method }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Path" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="font-family:monospace;font-size:12.5px">{{ row.path }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="summary" label="Summary" min-width="180" show-overflow-tooltip />
        <el-table-column label="Tag" min-width="100" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag v-if="row.tag" size="small" effect="plain" type="info">{{ row.tag }}</el-tag>
            <span v-else style="color:var(--color-text-tertiary)">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="plain" round>{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源资产" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.source_asset_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="Sprint" min-width="100" show-overflow-tooltip>
          <template #default="{ row }">{{ row.sprint_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="覆盖用例" min-width="80">
          <template #default="{ row }">
            <span :style="{ color: row.testcase_count > 0 ? 'var(--accent)' : 'var(--color-text-tertiary)' }">
              {{ row.testcase_count }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right" class-name="col-no-resize">
          <template #default="{ row }">
            <div class="action-btns" @click.stop>
              <el-button type="primary" link size="small" @click="openDetail(row)">
                <el-icon><View /></el-icon>详情
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div v-if="total > pageSize" style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="loadEndpoints"
        />
      </div>
    </div>

    <!-- 接口详情抽屉 -->
    <el-drawer v-model="detailVisible" :title="detailTitle" size="560px" destroy-on-close>
      <div v-if="detailData" class="detail-content" v-loading="detailLoading">
        <div class="detail-section">
          <div class="detail-row">
            <span class="detail-label">Method</span>
            <span :class="['method-badge', `method-${detailData.method?.toLowerCase()}`]">{{ detailData.method }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Path</span>
            <span style="font-family:monospace">{{ detailData.path }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Summary</span>
            <span>{{ detailData.summary || '-' }}</span>
          </div>
          <div class="detail-row" v-if="detailData.tag">
            <span class="detail-label">Tag</span>
            <el-tag size="small" effect="plain" type="info">{{ detailData.tag }}</el-tag>
          </div>
          <div class="detail-row">
            <span class="detail-label">状态</span>
            <el-tag :type="getStatusType(detailData.status)" size="small" effect="plain" round>{{ getStatusText(detailData.status) }}</el-tag>
          </div>
          <div class="detail-row" v-if="detailData.description">
            <span class="detail-label">描述</span>
            <span style="white-space:pre-wrap">{{ detailData.description }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">来源资产</span>
            <span>{{ detailData.source_asset_name || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Sprint</span>
            <span>{{ detailData.sprint_name || '-' }}</span>
          </div>
        </div>

        <!-- Parameters -->
        <div v-if="detailData.parameters?.length" class="detail-section">
          <div class="detail-section-title">Parameters</div>
          <el-table :data="detailData.parameters" size="small" style="width:100%">
            <el-table-column prop="name" label="名称" min-width="120" />
            <el-table-column prop="in" label="位置" width="80" />
            <el-table-column prop="required" label="必填" width="60">
              <template #default="{ row }">{{ row.required ? '是' : '否' }}</template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="140" show-overflow-tooltip />
          </el-table>
        </div>

        <!-- Request Schema -->
        <div v-if="detailData.request_schema && Object.keys(detailData.request_schema).length" class="detail-section">
          <div class="detail-section-title">Request Schema</div>
          <pre class="schema-block">{{ JSON.stringify(detailData.request_schema, null, 2) }}</pre>
        </div>

        <!-- Response Schema -->
        <div v-if="detailData.response_schema && Object.keys(detailData.response_schema).length" class="detail-section">
          <div class="detail-section-title">Response Schema</div>
          <pre class="schema-block">{{ JSON.stringify(detailData.response_schema, null, 2) }}</pre>
        </div>

        <!-- Error Codes -->
        <div v-if="detailData.error_codes?.length" class="detail-section">
          <div class="detail-section-title">Error Codes</div>
          <el-table :data="detailData.error_codes" size="small" style="width:100%">
            <el-table-column prop="code" label="状态码" width="80" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          </el-table>
        </div>

        <!-- 关联测试用例 -->
        <div class="detail-section">
          <div class="detail-section-title">关联测试用例 ({{ detailTestcases.length }})</div>
          <el-table v-if="detailTestcases.length" :data="detailTestcases" size="small" style="width:100%">
            <el-table-column label="用例编号" width="100">
              <template #default="{ row }">{{ row.testcase_case_no || '-' }}</template>
            </el-table-column>
            <el-table-column prop="testcase_name" label="用例名称" min-width="160" show-overflow-tooltip />
            <el-table-column label="覆盖类型" width="90">
              <template #default="{ row }">{{ getCoverageTypeText(row.coverage_type) }}</template>
            </el-table-column>
            <el-table-column label="置信度" width="70">
              <template #default="{ row }">{{ row.confidence }}%</template>
            </el-table-column>
            <el-table-column label="操作" width="70">
              <template #default="{ row }">
                <el-button type="danger" link size="small" @click="handleUnlink(row)">取消</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无关联用例" :image-size="48" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Collection, Search, View, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getApiEndpoints, getApiEndpoint, deleteApiEndpoint, getApiEndpointTestCases, unlinkApiEndpointTestCase } from '../../api/apiEndpoint'
import { getProjects } from '../../api/project'
import { getKnowledgeStats } from '../../api/knowledge'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const endpoints = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 50

// 筛选
const filters = reactive({
  project_id: null,
  sprint_id: null,
  method: null,
  status: null,
  keyword: '',
})

const methodOptions = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
const projectOptions = ref([])
const sprintOptions = ref([])

// 详情
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)
const detailTestcases = ref([])

const detailTitle = computed(() => {
  if (!detailData.value) return '接口详情'
  return `${detailData.value.method} ${detailData.value.path}`
})

const activeCount = computed(() => endpoints.value.filter(e => e.status === 'active').length)
const coveredCount = computed(() => endpoints.value.filter(e => e.testcase_count > 0).length)

// 从 URL query 接收参数（从 Sprint 详情跳转时使用）
onMounted(async () => {
  // 从 query 初始化筛选
  if (route.query.source_asset_id) {
    // 不直接筛选 source_asset_id，但保持页面简洁
  }
  if (route.query.sprint_id) {
    filters.sprint_id = parseInt(route.query.sprint_id)
  }
  await loadProjects()
  await loadEndpoints()
})

async function loadProjects() {
  try {
    const res = await getProjects()
    projectOptions.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

async function loadEndpoints() {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    }
    if (filters.project_id) params.project_id = filters.project_id
    if (filters.sprint_id) params.sprint_id = filters.sprint_id
    if (filters.method) params.method = filters.method
    if (filters.status) params.status = filters.status
    if (filters.keyword) params.keyword = filters.keyword
    // 支持 URL query 传入的 source_asset_id
    if (route.query.source_asset_id) params.source_asset_id = parseInt(route.query.source_asset_id)

    const res = await getApiEndpoints(params)
    const data = res.data || {}
    endpoints.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  currentPage.value = 1
  loadEndpoints()
}

function goToKnowledge() { router.push('/knowledge') }

function getStatusType(status) {
  return { active: 'success', deprecated: 'warning', disabled: 'info' }[status] || 'info'
}

function getStatusText(status) {
  return { active: '活跃', deprecated: '废弃', disabled: '停用' }[status] || status
}

function getCoverageTypeText(type) {
  return { functional: '功能', negative: '异常', boundary: '边界', smoke: '冒烟' }[type] || type
}

async function openDetail(row) {
  detailVisible.value = true
  detailLoading.value = true
  detailData.value = null
  detailTestcases.value = []
  try {
    const [epRes, tcRes] = await Promise.all([
      getApiEndpoint(row.id),
      getApiEndpointTestCases(row.id),
    ])
    detailData.value = epRes.data || row
    detailTestcases.value = tcRes.data || []
  } catch (e) {
    ElMessage.error('加载接口详情失败')
  } finally {
    detailLoading.value = false
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(
    `确定要删除接口 "${row.method} ${row.path}" 吗？`,
    '确认删除',
    { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    try {
      await deleteApiEndpoint(row.id)
      ElMessage.success('删除成功')
      await loadEndpoints()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

async function handleUnlink(link) {
  try {
    await unlinkApiEndpointTestCase(link.api_endpoint_id, link.testcase_id)
    ElMessage.success('取消关联成功')
    // 刷新详情
    detailTestcases.value = detailTestcases.value.filter(
      t => !(t.testcase_id === link.testcase_id && t.api_endpoint_id === link.api_endpoint_id)
    )
    await loadEndpoints()
  } catch (e) {
    ElMessage.error('取消关联失败')
  }
}
</script>

<style scoped>
.api-endpoint-list { max-width: 1400px; }

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
.breadcrumb-sep { margin: 0 8px; color: var(--color-text-tertiary); }

.filter-bar {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.stats-grid { display: grid; gap: 12px; }
.stat-card {
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-md, 8px);
  padding: 16px 18px;
}
.stat-label { font-size: 11px; color: var(--color-text-tertiary); margin-bottom: 4px; }
.stat-value { font-size: 22px; font-weight: 600; color: var(--color-text-primary); }
.stat-sub { font-size: 11px; color: var(--color-text-tertiary); margin-top: 4px; display: flex; align-items: center; gap: 4px; }
.stat-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.dot-green { background: #16a34a; }
.dot-blue { background: var(--accent); }
.dot-amber { background: #EF9F27; }

.action-btns { display: flex; gap: 4px; flex-wrap: nowrap; white-space: nowrap; }

/* 隐藏操作列的列宽拖拽手柄 */
:deep(.col-no-resize .el-table__column-resize-proxy) { display: none; }
:deep(.col-no-resize) { cursor: default !important; }

/* 隐藏表格内边框线（保留列宽拖拽能力） */
:deep(.el-table--border .el-table__inner-wrapper::after),
:deep(.el-table--border .el-table__body-wrapper)::after { display: none; }
:deep(.el-table--border th.el-table__cell),
:deep(.el-table--border td.el-table__cell) { border-right: none; }
:deep(.el-table--border tr.el-table__row:last-child td.el-table__cell) { border-bottom: none; }

/* Method Badge */
.method-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  font-family: monospace;
  letter-spacing: 0.5px;
}
.method-get { background: #e8f5e9; color: #2e7d32; }
.method-post { background: #e3f2fd; color: #1565c0; }
.method-put { background: #fff3e0; color: #e65100; }
.method-delete { background: #fce4ec; color: #c62828; }
.method-patch { background: #f3e5f5; color: #7b1fa2; }
.method-options { background: #e0f2f1; color: #00695c; }
.method-head { background: #eceff1; color: #546e7a; }

/* Detail Drawer */
.detail-content { padding: 0 8px; }
.detail-section { margin-bottom: 20px; }
.detail-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}
.detail-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 6px 0;
  font-size: 13px;
}
.detail-label {
  min-width: 80px;
  color: var(--color-text-tertiary);
  font-size: 12px;
  flex-shrink: 0;
}
.schema-block {
  background: var(--color-background-secondary, #f5f5f5);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: 6px;
  padding: 12px;
  font-size: 12px;
  font-family: monospace;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.el-table { cursor: pointer; }
</style>
