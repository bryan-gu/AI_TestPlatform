<template>
  <div class="change-item-list">
    <div class="page-header">
      <div>
        <div class="page-title">
          <el-icon :size="18"><Refresh /></el-icon>
          <span>变更项</span>
        </div>
        <div class="page-subtitle">按项目、Sprint、变更类型和影响等级查看增量变更与影响范围</div>
      </div>
      <el-button type="primary" size="small" :disabled="!filters.sprint_id" :loading="analyzing" @click="handleAnalyze">
        <el-icon><MagicStick /></el-icon>增量分析
      </el-button>
      <el-button type="success" size="small" :disabled="!filters.sprint_id" :loading="merging" @click="handleMergeToAll">
        <el-icon><Promotion /></el-icon>应用到最新汇总
      </el-button>
    </div>

    <div class="stats-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px">
      <div class="stat-card">
        <div class="stat-label">变更总数</div>
        <div class="stat-value">{{ total }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">新增</div>
        <div class="stat-value">{{ addedCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>新增实体</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">修改</div>
        <div class="stat-value">{{ modifiedCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>内容变化</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">高影响</div>
        <div class="stat-value">{{ highImpactCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-red"></span>需重点回归</div>
      </div>
    </div>

    <div class="card">
      <div class="card-head change-card-head">
        <div class="card-title">变更项列表</div>
        <div class="filter-bar">
          <el-select v-model="filters.project_id" placeholder="选择项目" size="small" style="width:160px" clearable @change="handleProjectChange">
            <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-select v-model="filters.sprint_id" placeholder="选择 Sprint" size="small" style="width:180px" clearable @change="handleFilterChange">
            <el-option v-for="s in sprintOptions" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
          <el-select v-model="filters.change_type" placeholder="变更类型" size="small" style="width:110px" clearable @change="handleFilterChange">
            <el-option label="新增" value="added" />
            <el-option label="修改" value="modified" />
            <el-option label="删除" value="removed" />
            <el-option label="废弃" value="deprecated" />
          </el-select>
          <el-select v-model="filters.target_type" placeholder="目标类型" size="small" style="width:110px" clearable @change="handleFilterChange">
            <el-option label="功能点" value="feature" />
            <el-option label="接口" value="api" />
            <el-option label="用例" value="testcase" />
            <el-option label="模块" value="module" />
          </el-select>
          <el-select v-model="filters.impact_level" placeholder="影响" size="small" style="width:90px" clearable @change="handleFilterChange">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
          <el-select v-model="filters.status" placeholder="状态" size="small" style="width:110px" clearable @change="handleFilterChange">
            <el-option label="待处理" value="open" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已忽略" value="ignored" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已应用" value="applied" />
          </el-select>
          <el-input
            v-model="filters.keyword"
            placeholder="搜索标题 / 描述 / 证据"
            size="small"
            style="width:220px"
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

      <el-table :data="items" style="width:100%" border v-loading="loading" empty-text="暂无变更项" @row-click="openDetail">
        <el-table-column prop="title" label="变更标题" min-width="220" show-overflow-tooltip />
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag :type="getChangeTypeTag(row.change_type)" size="small" effect="plain" round>{{ getChangeTypeText(row.change_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="目标" min-width="170" show-overflow-tooltip>
          <template #default="{ row }">{{ getTargetTypeText(row.target_type) }}：{{ row.target_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="Sprint" min-width="100" show-overflow-tooltip>
          <template #default="{ row }">{{ row.sprint_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="模块" width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ row.module_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="影响" width="80">
          <template #default="{ row }"><span :class="getImpactClass(row.impact_level)">{{ row.impact_level || '中' }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }"><el-tag :type="getStatusTag(row.status)" size="small" effect="plain" round>{{ getStatusText(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column label="置信度" width="80">
          <template #default="{ row }">{{ row.confidence || 0 }}%</template>
        </el-table-column>
        <el-table-column label="来源" width="80">
          <template #default="{ row }">
            <el-tag :type="row.raw_data?.analyzer === 'llm' ? 'warning' : 'info'" size="small" effect="plain">
              {{ row.raw_data?.analyzer === 'llm' ? 'LLM' : '规则' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" class-name="col-no-resize">
          <template #default="{ row }">
            <div class="action-btns" @click.stop>
              <el-button type="primary" link size="small" @click="openDetail(row)"><el-icon><View /></el-icon>详情</el-button>
              <el-button v-if="row.status === 'confirmed' || row.status === 'resolved'" type="success" link size="small" @click="handleApplySingle(row)">应用</el-button>
              <el-dropdown trigger="click" @command="cmd => handleStatusCommand(row, cmd)">
                <el-button type="primary" link size="small">状态</el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="confirmed">确认</el-dropdown-item>
                    <el-dropdown-item command="ignored">忽略</el-dropdown-item>
                    <el-dropdown-item command="resolved">解决</el-dropdown-item>
                    <el-dropdown-item command="applied">已应用</el-dropdown-item>
                    <el-dropdown-item command="open">重开</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button type="danger" link size="small" @click="handleDelete(row)"><el-icon><Delete /></el-icon>删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > pageSize" style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="loadItems" />
      </div>
    </div>

    <el-drawer v-model="detailVisible" :title="detailTitle" size="620px" destroy-on-close>
      <div v-if="detailData" class="detail-content" v-loading="detailLoading">
        <div class="detail-section">
          <div class="detail-row"><span class="detail-label">标题</span><span>{{ detailData.title }}</span></div>
          <div class="detail-row"><span class="detail-label">类型</span><el-tag :type="getChangeTypeTag(detailData.change_type)" size="small" effect="plain">{{ getChangeTypeText(detailData.change_type) }}</el-tag></div>
          <div class="detail-row"><span class="detail-label">目标</span><span>{{ getTargetTypeText(detailData.target_type) }}：{{ detailData.target_name || '-' }}</span></div>
          <div class="detail-row"><span class="detail-label">影响等级</span><span :class="getImpactClass(detailData.impact_level)">{{ detailData.impact_level || '中' }}</span></div>
          <div class="detail-row"><span class="detail-label">状态</span><el-tag :type="getStatusTag(detailData.status)" size="small" effect="plain">{{ getStatusText(detailData.status) }}</el-tag></div>
          <div class="detail-row"><span class="detail-label">置信度</span><span>{{ detailData.confidence || 0 }}%</span></div>
          <div class="detail-row" v-if="detailData.description"><span class="detail-label">描述</span><span style="white-space:pre-wrap">{{ detailData.description }}</span></div>
          <div class="detail-row" v-if="detailData.evidence"><span class="detail-label">证据</span><span style="white-space:pre-wrap">{{ detailData.evidence }}</span></div>
        </div>

        <div class="detail-section">
          <div class="detail-section-title">影响范围</div>
          <div class="impact-groups" v-if="hasImpactData">
            <div v-for="group in impactGroups" :key="group.key" class="impact-group" v-show="group.items.length">
              <div class="impact-label">{{ group.label }} · {{ group.items.length }}</div>
              <div class="impact-tags">
                <el-tag v-for="item in group.items" :key="`${item.type}-${item.id}`" size="small" effect="plain">{{ item.name }}</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无影响数据" :image-size="64" />
        </div>

        <div class="detail-section" v-if="detailLinks.length">
          <div class="detail-section-title">一跳关系</div>
          <el-table :data="detailLinks" size="small" style="width:100%">
            <el-table-column label="关系" width="90"><template #default="{ row }">{{ row.relation_label || row.relation_type }}</template></el-table-column>
            <el-table-column label="来源" min-width="150"><template #default="{ row }">{{ formatEntity(row.source_type, row.source_name) }}</template></el-table-column>
            <el-table-column label="目标" min-width="150"><template #default="{ row }">{{ formatEntity(row.target_type, row.target_name) }}</template></el-table-column>
            <el-table-column label="置信度" width="70"><template #default="{ row }">{{ row.confidence || 0 }}%</template></el-table-column>
          </el-table>
        </div>

        <div class="detail-section" v-if="detailData.raw_data && detailData.raw_data.applied_to_all">
          <div class="detail-section-title">合并信息</div>
          <div class="detail-row"><span class="detail-label">应用时间</span><span>{{ detailData.raw_data.applied_at || '-' }}</span></div>
          <div class="detail-row"><span class="detail-label">目标汇总</span><span>sprint_all #{{ detailData.raw_data.target_sprint_all_id || '-' }}</span></div>
          <div class="detail-row"><span class="detail-label">合并结果</span><span>{{ { created: '新增', updated: '更新', deprecated: '标记废弃', skipped: '跳过' }[detailData.raw_data.merge_result] || detailData.raw_data.merge_result }}</span></div>
        </div>

        <div class="detail-section" v-if="hasSnapshot(detailData.before_snapshot)">
          <div class="detail-section-title">变更前</div>
          <pre class="schema-block">{{ JSON.stringify(detailData.before_snapshot, null, 2) }}</pre>
        </div>
        <div class="detail-section" v-if="hasSnapshot(detailData.after_snapshot)">
          <div class="detail-section-title">变更后</div>
          <pre class="schema-block">{{ JSON.stringify(detailData.after_snapshot, null, 2) }}</pre>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh, Search, View, Delete, MagicStick, Promotion } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '../../stores/app'
import { getProjects } from '../../api/project'
import { getSprints, getSprint, mergeSprintToAll } from '../../api/sprint'
import { getEntityTraceLinks } from '../../api/traceLink'
import {
  getChangeItems,
  getChangeItem,
  updateChangeItem,
  deleteChangeItem,
  analyzeSprintChangeItems,
  getChangeItemImpact,
} from '../../api/changeItem'

const route = useRoute()
const appStore = useAppStore()

const loading = ref(false)
const analyzing = ref(false)
const merging = ref(false)
const items = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 50

const filters = reactive({
  project_id: null,
  sprint_id: null,
  change_type: null,
  target_type: null,
  impact_level: null,
  status: null,
  keyword: '',
})

const projectOptions = ref([])
const sprintOptions = ref([])
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)
const detailImpact = ref({})
const detailLinks = ref([])

const detailTitle = computed(() => detailData.value?.title || '变更详情')
const addedCount = computed(() => items.value.filter(i => i.change_type === 'added').length)
const modifiedCount = computed(() => items.value.filter(i => i.change_type === 'modified').length)
const highImpactCount = computed(() => items.value.filter(i => i.impact_level === '高').length)
const impactGroups = computed(() => [
  { key: 'features', label: '功能点', items: detailImpact.value.features || [] },
  { key: 'api_endpoints', label: '接口', items: detailImpact.value.api_endpoints || [] },
  { key: 'testcases', label: '测试用例', items: detailImpact.value.testcases || [] },
  { key: 'modules', label: '模块', items: detailImpact.value.modules || [] },
  { key: 'assets', label: '知识资产', items: detailImpact.value.assets || [] },
  { key: 'scripts', label: '脚本', items: detailImpact.value.scripts || [] },
])
const hasImpactData = computed(() => impactGroups.value.some(group => group.items.length > 0))

onMounted(async () => {
  appStore.setCurrentPage('change-items', '变更项')
  const queryProjectId = parseQueryInt(route.query.project_id)
  const querySprintId = parseQueryInt(route.query.sprint_id)
  if (queryProjectId) filters.project_id = queryProjectId
  if (querySprintId) {
    filters.sprint_id = querySprintId
    if (!filters.project_id) await resolveProjectBySprint(querySprintId)
  }
  await loadProjects()
  await loadSprintOptions(filters.project_id)
  await loadItems()
})

function parseQueryInt(value) {
  const raw = Array.isArray(value) ? value[0] : value
  const num = parseInt(raw)
  return Number.isNaN(num) ? null : num
}

async function resolveProjectBySprint(sprintId) {
  try {
    const res = await getSprint(sprintId)
    const sprint = res.data || {}
    if (sprint.project_id) filters.project_id = sprint.project_id
  } catch (e) {
    console.error(e)
  }
}

async function loadProjects() {
  try {
    const res = await getProjects()
    projectOptions.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

async function loadSprintOptions(projectId) {
  try {
    const res = await getSprints(projectId ? { project_id: projectId } : {})
    sprintOptions.value = res.data || []
  } catch (e) {
    sprintOptions.value = []
    console.error(e)
  }
}

async function handleProjectChange(projectId) {
  filters.sprint_id = null
  await loadSprintOptions(projectId)
  handleFilterChange()
}

async function loadItems() {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    }
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== '') params[key] = value
    })
    const res = await getChangeItems(params)
    const data = res.data || {}
    items.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  currentPage.value = 1
  loadItems()
}

async function handleAnalyze() {
  if (!filters.sprint_id) {
    ElMessage.warning('请先选择 Sprint')
    return
  }
  analyzing.value = true
  try {
    const res = await analyzeSprintChangeItems(filters.sprint_id, { overwrite: false })
    const result = res.data || {}
    ElMessage.success(`分析完成：共 ${result.total || 0} 个变更，新增 ${result.created || 0} 个，更新 ${result.updated || 0} 个`)
    await loadItems()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '增量分析失败')
  } finally {
    analyzing.value = false
  }
}

async function openDetail(row) {
  detailVisible.value = true
  detailLoading.value = true
  detailData.value = null
  detailImpact.value = {}
  detailLinks.value = []
  try {
    const [detailRes, impactRes, linksRes] = await Promise.all([
      getChangeItem(row.id),
      getChangeItemImpact(row.id),
      getEntityTraceLinks('change', row.id),
    ])
    detailData.value = detailRes.data || row
    detailImpact.value = impactRes.data || {}
    detailLinks.value = linksRes.data || []
  } catch (e) {
    ElMessage.error('加载变更详情失败')
  } finally {
    detailLoading.value = false
  }
}

async function handleStatusCommand(row, status) {
  try {
    await updateChangeItem(row.id, { status })
    ElMessage.success('状态已更新')
    await loadItems()
  } catch (e) {
    ElMessage.error('状态更新失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除变更项 "${row.title}" 吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteChangeItem(row.id)
      ElMessage.success('删除成功')
      await loadItems()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

async function handleMergeToAll() {
  if (!filters.sprint_id) {
    ElMessage.warning('请先选择 Sprint')
    return
  }
  ElMessageBox.confirm(
    '确定将当前 Sprint 下已确认/已解决的变更项应用到 sprint_all 最新汇总吗？应用后变更项状态将变为"已应用"，sprint_all 中对应实体将被新增或更新。',
    '应用到最新汇总',
    { confirmButtonText: '确认应用', cancelButtonText: '取消', type: 'warning' },
  ).then(async () => {
    merging.value = true
    try {
      const res = await mergeSprintToAll(filters.sprint_id, {
        statuses: ['confirmed', 'resolved'],
        target_types: ['feature', 'api'],
      })
      const data = res.data || {}
      const features = data.features || {}
      const apis = data.api_endpoints || {}
      const graph = data.graph || {}
      ElMessage.success(
        `已应用 ${data.applied || 0} 个变更（功能点：新增 ${features.created || 0}、更新 ${features.updated || 0}；接口：新增 ${apis.created || 0}、更新 ${apis.updated || 0}）`,
      )
      await loadItems()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '应用失败')
    } finally {
      merging.value = false
    }
  }).catch(() => {})
}

async function handleApplySingle(row) {
  ElMessageBox.confirm(
    `确定将变更项 "${row.title}" 应用到 sprint_all 最新汇总吗？`,
    '应用变更',
    { confirmButtonText: '确认应用', cancelButtonText: '取消', type: 'warning' },
  ).then(async () => {
    try {
      const res = await mergeSprintToAll(row.sprint_id, {
        change_item_ids: [row.id],
        statuses: ['confirmed', 'resolved'],
        target_types: ['feature', 'api'],
      })
      const data = res.data || {}
      ElMessage.success(`已应用 ${data.applied || 0} 个变更到最新汇总`)
      await loadItems()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '应用失败')
    }
  }).catch(() => {})
}

function getChangeTypeText(type) {
  return { added: '新增', modified: '修改', removed: '删除', deprecated: '废弃', unknown: '未知' }[type] || type
}

function getChangeTypeTag(type) {
  return { added: 'success', modified: 'warning', removed: 'danger', deprecated: 'info' }[type] || 'info'
}

function getTargetTypeText(type) {
  return { feature: '功能点', api: '接口', testcase: '用例', module: '模块', document: '文档', asset: '资产' }[type] || type
}

function getStatusText(status) {
  return { open: '待处理', confirmed: '已确认', ignored: '已忽略', resolved: '已解决', applied: '已应用' }[status] || status
}

function getStatusTag(status) {
  return { open: 'warning', confirmed: 'success', ignored: 'info', resolved: 'primary', applied: 'success' }[status] || 'info'
}

function getImpactClass(level) {
  return { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }[level] || 'badge badge-gray'
}

function formatEntity(type, name) {
  return `${getTargetTypeText(type)}：${name || '-'}`
}

function hasSnapshot(snapshot) {
  return snapshot && Object.keys(snapshot).length > 0
}
</script>

<style scoped>
.change-item-list { max-width: 1400px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 16px; }
.page-title { display: flex; align-items: center; gap: 8px; font-size: 20px; font-weight: 600; color: var(--color-text-primary); line-height: 1.3; }
.page-title .el-icon { color: var(--accent); }
.page-subtitle { margin-top: 4px; font-size: 12px; color: var(--color-text-secondary); }
.change-card-head { align-items: flex-start; gap: 12px; }
.filter-bar { display: flex; gap: 10px; align-items: center; justify-content: flex-end; flex-wrap: wrap; }
@media (max-width: 1100px) {
  .change-card-head { flex-direction: column; align-items: stretch; }
  .filter-bar { justify-content: flex-start; }
}
.stats-grid { display: grid; gap: 12px; }
.stat-card { background: var(--color-background-primary); border: 0.5px solid var(--color-border-tertiary); border-radius: var(--border-radius-md, 8px); padding: 16px 18px; }
.stat-label { font-size: 11px; color: var(--color-text-tertiary); margin-bottom: 4px; }
.stat-value { font-size: 22px; font-weight: 600; color: var(--color-text-primary); }
.stat-sub { font-size: 11px; color: var(--color-text-tertiary); margin-top: 4px; display: flex; align-items: center; gap: 4px; }
.stat-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.dot-green { background: #16a34a; }
.dot-blue { background: var(--accent); }
.dot-red { background: #E24B4A; }
.action-btns { display: flex; gap: 4px; flex-wrap: nowrap; white-space: nowrap; align-items: center; }

/* 隐藏操作列的列宽拖拽手柄 */
:deep(.col-no-resize .el-table__column-resize-proxy) { display: none; }
:deep(.col-no-resize) { cursor: default !important; }

/* 隐藏表格内边框线（保留列宽拖拽能力） */
:deep(.el-table--border .el-table__inner-wrapper::after),
:deep(.el-table--border .el-table__body-wrapper)::after { display: none; }
:deep(.el-table--border th.el-table__cell),
:deep(.el-table--border td.el-table__cell) { border-right: none; }
:deep(.el-table--border tr.el-table__row:last-child td.el-table__cell) { border-bottom: none; }

.detail-content { padding: 0 8px; }
.detail-section { margin-bottom: 20px; }
.detail-section-title { font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 10px; padding-bottom: 6px; border-bottom: 0.5px solid var(--color-border-tertiary); }
.detail-row { display: flex; align-items: baseline; gap: 12px; padding: 6px 0; font-size: 13px; }
.detail-label { min-width: 80px; color: var(--color-text-tertiary); font-size: 12px; flex-shrink: 0; }
.impact-groups { display: flex; flex-direction: column; gap: 12px; }
.impact-label { font-size: 12px; color: var(--color-text-secondary); margin-bottom: 6px; }
.impact-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.schema-block { background: var(--color-background-secondary, #f5f5f5); border: 0.5px solid var(--color-border-tertiary); border-radius: 6px; padding: 12px; font-size: 12px; font-family: monospace; max-height: 300px; overflow-y: auto; white-space: pre-wrap; word-break: break-all; margin: 0; }
.el-table { cursor: pointer; }
</style>
