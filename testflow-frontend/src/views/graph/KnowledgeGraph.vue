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

        <!-- 节点区域 -->
        <div class="graph-nodes" v-if="nodes.length > 0">
          <div
            v-for="node in nodes"
            :key="node.id"
            class="graph-node"
            :class="getNodeColorClass(node.node_type)"
          >
            <el-icon><component :is="getNodeIcon(node.node_type)" /></el-icon>
            <span>{{ node.name }}</span>
          </div>
        </div>
        <div v-else class="graph-empty">暂无节点数据</div>

        <!-- 关联区域 -->
        <div class="graph-edges" v-if="edges.length > 0">
          <div
            v-for="edge in edges"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import * as icons from '@element-plus/icons-vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getGraphDetail } from '../../api/graph'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const loading = ref(false)
const nodes = ref([])
const edges = ref([])
const graphData = ref({})

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

onMounted(() => {
  appStore.setCurrentPage('knowledge-graph', '知识图谱', '查看详情')
  loadGraphDetail()
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

.graph-empty {
  text-align: center;
  padding: 24px;
  color: var(--color-text-tertiary);
  font-size: 13px;
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
