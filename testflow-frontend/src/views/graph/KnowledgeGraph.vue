<template>
  <div class="knowledge-graph">
    <div class="card" v-loading="loading">
      <div class="card-head">
        <div class="card-title">
          知识图谱 — {{ graphData.name || '需求关联可视化' }}
        </div>
        <div class="card-action">
          <el-button size="small" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>返回列表
          </el-button>
        </div>
      </div>

      <div class="graph-content">
        <div class="graph-desc">
          节点代表知识资产、文档、功能点、用例或模块，连线代表可追踪关系
        </div>

        <!-- 筛选栏 -->
        <div class="graph-filter">
          <el-input
            v-model="keyword"
            placeholder="搜索节点名称"
            size="small"
            clearable
            style="width:200px"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select
            v-model="nodeTypeFilter"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="节点类型"
            size="small"
            style="width:220px"
          >
            <el-option v-for="t in nodeTypeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
          <el-select
            v-model="relationFilter"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="关系类型"
            size="small"
            style="width:220px"
          >
            <el-option v-for="r in relationOptions" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
          <el-button size="small" @click="clearFilter">重置</el-button>
          <el-button size="small" @click="relayout" :disabled="!layoutFrozen">
            <el-icon><Refresh /></el-icon>{{ layoutFrozen ? '重新布局' : '布局中…' }}
          </el-button>
        </div>

        <!-- 力导向图 -->
        <div ref="chartRef" class="graph-chart" v-loading="loading"></div>
        <div v-if="!loading && filteredNodes.length === 0" class="graph-empty">暂无节点数据</div>

        <!-- 关联区域 -->
        <div class="graph-edges" v-if="filteredEdges.length > 0">
          <div
            v-for="edge in filteredEdges"
            :key="edge.id"
            class="graph-edge"
          >
            <span class="edge-node" :class="getEdgeNodeClass(edge.source_node_name)">{{ edge.source_node_name }}</span>
            <span class="edge-line"></span>
            <span class="edge-label">{{ getRelationLabel(edge.relation_type) }}</span>
            <span class="edge-line"></span>
            <span class="edge-node" :class="getEdgeNodeClass(edge.target_node_name)">{{ edge.target_node_name }}</span>
          </div>
        </div>
        <div v-else-if="!loading" class="graph-empty">暂无关联数据</div>

        <!-- 图谱统计 -->
        <div class="graph-stats">
          <div class="graph-stats-title">图谱统计</div>
          <div class="graph-stats-items">
            <div class="graph-stat-item">
              <span class="graph-stat-label">节点数</span>
              <span class="graph-stat-value">{{ graphData.node_count || 0 }}</span>
            </div>
            <div class="graph-stat-item">
              <span class="graph-stat-label">关联数</span>
              <span class="graph-stat-value">{{ graphData.edge_count || 0 }}</span>
            </div>
            <div class="graph-stat-item">
              <span class="graph-stat-label">文档覆盖</span>
              <span class="graph-stat-value">{{ docCoverage }}</span>
            </div>
            <div class="graph-stat-item">
              <span class="graph-stat-label">孤立节点</span>
              <span class="graph-stat-value" style="color: #E24B4A">{{ isolatedCount }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 节点详情抽屉 -->
    <el-drawer v-model="nodeDrawerVisible" :title="currentNode ? `${getNodeTypeLabel(currentNode.node_type)} 详情` : '节点详情'" size="380px">
      <div v-if="currentNode" class="node-detail">
        <div class="node-detail-name">{{ currentNode.name }}</div>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="节点类型">{{ getNodeTypeLabel(currentNode.node_type) }}</el-descriptions-item>
          <el-descriptions-item label="节点 ID">{{ currentNode.properties?.entity_id ?? currentNode.id }}</el-descriptions-item>
          <template v-for="(value, key) in nodePropertyRows" :key="key">
            <el-descriptions-item :label="getPropertyLabel(key)">{{ formatPropValue(value) }}</el-descriptions-item>
          </template>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import * as icons from '@element-plus/icons-vue'
import { ArrowLeft, Search, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { GraphChart } from 'echarts/charts'
import { TooltipComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getGraphDetail } from '../../api/graph'

echarts.use([GraphChart, TooltipComponent, TitleComponent, CanvasRenderer])

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const loading = ref(false)
const chartRef = ref(null)
let chartInstance = null
const nodes = ref([])
const edges = ref([])
const graphData = ref({})

// 筛选状态
const keyword = ref('')
const nodeTypeFilter = ref([])
const relationFilter = ref([])
const nodeDrawerVisible = ref(false)
const currentNode = ref(null)
const layoutFrozen = ref(false)  // 力导向收敛后是否冻结为静态布局
const FORCE_NODE_THRESHOLD = 150  // 超过此节点数降低排斥力，加速收敛

const nodeTypeOptions = [
  { label: '资产', value: 'asset' },
  { label: '文档', value: 'document' },
  { label: '功能点', value: 'feature' },
  { label: '测试用例', value: 'testcase' },
  { label: '接口', value: 'api' },
  { label: '模块', value: 'module' },
  { label: 'Sprint', value: 'sprint' },
  { label: '变更项', value: 'change' },
  { label: '脚本', value: 'script' },
  { label: '选择器', value: 'selector' },
  { label: '执行结果', value: 'execution' },
]

const relationOptions = [
  { value: 'contains', label: '包含' },
  { value: 'derived_from', label: '来源于' },
  { value: 'belongs_to', label: '属于' },
  { value: 'covers', label: '覆盖' },
  { value: 'tests_api', label: '测试接口' },
  { value: 'implements', label: '实现' },
  { value: 'changes', label: '变更' },
  { value: 'depends_on', label: '依赖' },
  { value: 'calls', label: '调用' },
  { value: 'uses_schema', label: '使用 Schema' },
  { value: 'generated_by', label: '生成自' },
  { value: 'verified_by', label: '验证于' },
  { value: 'mentions', label: '提及' },
]

const filteredNodes = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  const typeSet = nodeTypeFilter.value.length ? new Set(nodeTypeFilter.value) : null
  return nodes.value.filter(n => {
    if (typeSet && !typeSet.has(n.node_type)) return false
    if (kw && !(n.name || '').toLowerCase().includes(kw)) return false
    return true
  })
})

const filteredEdges = computed(() => {
  if (!relationFilter.value.length) return edges.value
  const relSet = new Set(relationFilter.value)
  return edges.value.filter(e => relSet.has(e.relation_type))
})

function clearFilter() {
  keyword.value = ''
  nodeTypeFilter.value = []
  relationFilter.value = []
}

const nodePropertyRows = computed(() => {
  if (!currentNode.value) return {}
  const props = currentNode.value.properties || {}
  // 过滤掉内部字段，只展示业务属性
  const { entity_type, entity_id, ...rest } = props
  return rest
})

function getNodeTypeLabel(type) {
  const item = nodeTypeOptions.find(t => t.value === type)
  return item ? item.label : (type || '节点')
}

const PROPERTY_LABELS = {
  asset_type: '资产类型', source_kind: '来源', sprint_id: 'Sprint ID', project_id: '项目 ID',
  module_id: '模块 ID', status: '状态', parse_status: '解析状态', file_type: '文件类型',
  file_size: '文件大小', document_id: '文档 ID', priority: '优先级', source_doc_id: '来源文档',
  source_asset_id: '来源资产', source_type: '来源类型', fingerprint: '指纹', case_no: '用例编号',
  exec_status: '执行状态', case_type: '用例类型', automation_status: '自动化状态', source: '来源标记',
  method: '方法', path: '路径', summary: '摘要', tag: '标签', auth_required: '需认证',
  change_type: '变更类型', target_type: '目标类型', target_id: '目标 ID', impact_level: '影响等级',
  ai_status: 'AI 状态', version: '版本', code: '模块代码', is_all: '是否汇总',
}

function getPropertyLabel(key) {
  return PROPERTY_LABELS[key] || key
}

function formatPropValue(value) {
  if (value === null || value === undefined || value === '') return '-'
  if (typeof value === 'boolean') return value ? '是' : '否'
  return value
}

function openNodeDrawer(node) {
  currentNode.value = node
  nodeDrawerVisible.value = true
}

// 计算文档覆盖：有至少一条关联的文档节点数 / 总文档节点数
const docCoverage = computed(() => {
  const docNodes = nodes.value.filter(n => n.node_type === 'document')
  if (docNodes.length === 0) return '0 / 0'
  const connectedNodeIds = new Set()
  edges.value.forEach(e => {
    connectedNodeIds.add(e.source_node_id)
    connectedNodeIds.add(e.target_node_id)
  })
  const connected = docNodes.filter(n => connectedNodeIds.has(n.id)).length
  return `${connected} / ${docNodes.length}`
})

// 计算孤立节点数
const isolatedCount = computed(() => {
  const connectedNodeIds = new Set()
  edges.value.forEach(e => {
    connectedNodeIds.add(e.source_node_id)
    connectedNodeIds.add(e.target_node_id)
  })
  return nodes.value.filter(n => !connectedNodeIds.has(n.id)).length
})

function getNodeColorClass(nodeType) {
  const map = {
    asset: 'gn-blue',
    document: 'gn-blue',
    module: 'gn-amber',
    testcase: 'gn-teal',
    feature: 'gn-purple',
    api: 'gn-teal',
    script: 'gn-coral',
    selector: 'gn-coral',
    execution: 'gn-amber',
    change: 'gn-coral',
  }
  return map[nodeType] || 'gn-blue'
}

function getNodeIcon(nodeType) {
  const map = {
    asset: 'Collection',
    document: 'Document',
    module: 'Box',
    testcase: 'List',
    feature: 'Star',
    api: 'Connection',
    script: 'Cpu',
    selector: 'Aim',
    execution: 'VideoPlay',
    change: 'Refresh',
  }
  return map[nodeType] || 'Document'
}

function getRelationLabel(relationType) {
  const map = {
    dependency: '依赖',
    include: '包含',
    call: '调用',
    dataflow: '数据流',
    contains: '包含',
    derived_from: '来源于',
    belongs_to: '属于',
    covers: '覆盖',
    tests_api: '测试接口',
    implements: '实现',
    changes: '变更',
    depends_on: '依赖',
    calls: '调用',
    uses_schema: '使用 Schema',
    generated_by: '生成自',
    verified_by: '验证于',
    mentions: '提及',
  }
  return map[relationType] || relationType
}

// 边节点的颜色（基于节点名称的简单哈希）
const COLOR_CLASSES = ['gn-blue', 'gn-purple', 'gn-teal', 'gn-amber', 'gn-coral']
function getEdgeNodeClass(name) {
  if (!name) return 'gn-blue'
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return COLOR_CLASSES[Math.abs(hash) % COLOR_CLASSES.length]
}

function goBack() {
  router.push('/graphs')
}

async function loadGraphDetail() {
  const graphId = route.params.id
  if (!graphId) return

  loading.value = true
  try {
    const res = await getGraphDetail(graphId)
    const data = res.data?.data || res.data || {}
    graphData.value = data
    nodes.value = data.nodes || []
    edges.value = data.edges || []
  } catch (e) {
    console.error('加载图谱详情失败', e)
  } finally {
    loading.value = false
  }
}

const NODE_CATEGORIES = nodeTypeOptions.map(t => ({ name: t.label }))
const NODE_TYPE_INDEX = {}
nodeTypeOptions.forEach((t, i) => { NODE_TYPE_INDEX[t.value] = i })

function initChart() {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  chartInstance.on('click', (params) => {
    if (params.dataType === 'node' && params.data?.raw) {
      openNodeDrawer(params.data.raw)
    }
  })
  // 力导向收敛后自动冻结：layoutAnimation:false 下首次 finished 即收敛态
  chartInstance.on('finished', () => {
    if (!layoutFrozen.value) freezeLayout()
  })
}

function renderChart(useForce = true) {
  if (!chartInstance) return
  const chartNodes = filteredNodes.value
  const chartEdges = filteredEdges.value
  if (chartNodes.length === 0) {
    chartInstance.clear()
    return
  }
  const nodeIds = new Set(chartNodes.map(n => n.id))
  const big = chartNodes.length > FORCE_NODE_THRESHOLD
  const series = {
    type: 'graph',
    layout: useForce ? 'force' : 'none',
    roam: true,
    draggable: true,
    categories: NODE_CATEGORIES,
    label: { show: true, position: 'right', fontSize: 11 },
    labelLayout: { hideOverlap: true },
    data: chartNodes.map(n => ({
      id: String(n.id),
      name: n.name,
      nodeType: n.node_type,
      category: NODE_TYPE_INDEX[n.node_type] ?? 0,
      symbolSize: 30,
      raw: n,
    })),
    links: chartEdges.filter(e => nodeIds.has(e.source_node_id) && nodeIds.has(e.target_node_id)).map(e => ({
      source: String(e.source_node_id),
      target: String(e.target_node_id),
      value: e.relation_type,
      sourceName: e.source_node_name,
      targetName: e.target_node_name,
      lineStyle: { width: 1.5, color: '#aaa', curveness: 0.1 },
    })),
    edgeLabel: { show: false, fontSize: 10, color: '#888', formatter: (p) => getRelationLabel(p.data.value) },
    emphasis: { focus: 'adjacency', lineStyle: { width: 3 }, edgeLabel: { show: true } },
    progressive: 300,
    progressiveThreshold: 1000,
  }
  if (useForce) {
    series.force = {
      layoutAnimation: false,  // 后台静默迭代到收敛再一次性渲染，避免中间帧卡顿
      repulsion: big ? 80 : 140,
      edgeLength: big ? 70 : 90,
      gravity: big ? 0.12 : 0.08,
      friction: 0.6,  // 提高摩擦力，加快收敛
    }
  }
  chartInstance.setOption({
    tooltip: {
      formatter: (p) => {
        if (p.dataType === 'node') return `${getNodeTypeLabel(p.data.nodeType)}：<br/>${p.data.name}`
        if (p.dataType === 'edge') return `${p.data.sourceName} → ${getRelationLabel(p.data.value)} → ${p.data.targetName}`
        return ''
      },
    },
    series: [series],
  }, true)
}

// 力导向收敛后冻结为静态布局：之后拖动/缩放只是视图变换，不再触发全图力学重算（根治拖动卡）
function freezeLayout() {
  if (!chartInstance || layoutFrozen.value) return
  const data = chartInstance.getOption()?.series?.[0]?.data
  if (!Array.isArray(data) || data.length === 0) return
  // 必须已有力导向计算出的坐标才冻结
  if (data.some(d => d.x == null || d.y == null)) return
  layoutFrozen.value = true
  chartInstance.setOption({
    series: [{
      layout: 'none',
      data: data.map(d => ({ ...d, fixed: true })),
    }],
  })
}

// 重新触发力导向布局（用户点「重新布局」，或筛选变化后节点集已变）
function relayout() {
  layoutFrozen.value = false
  renderChart(true)
}

watch([filteredNodes, filteredEdges], () => {
  layoutFrozen.value = false
  renderChart(true)
})

onMounted(async () => {
  appStore.setCurrentPage('knowledge-graph', '知识图谱')
  await loadGraphDetail()
  await nextTick()
  initChart()
  renderChart(true)
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.knowledge-graph {
  max-width: 1400px;
}

.graph-content {
  padding: 18px;
}

.graph-desc {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-bottom: 16px;
}

.graph-filter {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.graph-node.clickable {
  cursor: pointer;
  transition: transform 0.12s ease;
}

.graph-node.clickable:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.node-detail-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 14px;
  word-break: break-all;
}

.graph-empty {
  text-align: center;
  padding: 24px;
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.graph-chart {
  width: 100%;
  height: 520px;
  margin-bottom: 20px;
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-md);
  background: var(--color-background-primary);
}

/* 节点区域 */
.graph-nodes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.graph-node {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 11px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.graph-node .el-icon {
  font-size: 14px;
}

/* 节点颜色方案 */
.gn-blue {
  background: #E6F1FB;
  color: #042C53;
}

.gn-purple {
  background: #EEEDFE;
  color: #26215C;
}

.gn-teal {
  background: #E1F5EE;
  color: #085041;
}

.gn-amber {
  background: #FAEEDA;
  color: #633806;
}

.gn-coral {
  background: #FAECE7;
  color: #4A1B0C;
}

/* 关联区域 */
.graph-edges {
  border-top: 0.5px solid var(--color-border-tertiary);
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.graph-edge {
  display: flex;
  align-items: center;
  gap: 10px;
}

.edge-node {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.edge-line {
  flex: 0 0 40px;
  height: 1px;
  background: var(--color-border-secondary);
}

.edge-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 500;
  padding: 2px 8px;
  background: var(--color-background-secondary);
  border-radius: 4px;
}

/* 图谱统计 */
.graph-stats {
  background: var(--color-background-secondary);
  border-radius: var(--border-radius-md);
  padding: 14px 18px;
}

.graph-stats-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 10px;
}

.graph-stats-items {
  display: flex;
  gap: 32px;
}

.graph-stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.graph-stat-label {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.graph-stat-value {
  font-size: 18px;
  font-weight: 500;
  color: var(--color-text-primary);
}
</style>
