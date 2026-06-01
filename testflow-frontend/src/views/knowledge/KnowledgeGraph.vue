<template>
  <div class="knowledge-graph">
    <div class="card">
      <div class="card-head">
        <div class="card-title">知识图谱 — 需求关联可视化</div>
        <div class="card-action">编辑关联</div>
      </div>

      <div class="graph-content">
        <div class="graph-desc">
          节点代表需求文档或功能模块，连线代表关联关系
        </div>

        <!-- 节点区域 -->
        <div class="graph-nodes">
          <div
            v-for="node in nodes"
            :key="node.id"
            class="graph-node"
            :class="node.colorClass"
          >
            <el-icon><component :is="icons[node.icon]" /></el-icon>
            <span>{{ node.label }}</span>
          </div>
        </div>

        <!-- 关联区域 -->
        <div class="graph-edges">
          <div
            v-for="edge in edges"
            :key="edge.id"
            class="graph-edge"
          >
            <span class="edge-node" :class="edge.fromClass">{{ edge.from }}</span>
            <span class="edge-line"></span>
            <span class="edge-label">{{ edge.relation }}</span>
            <span class="edge-line"></span>
            <span class="edge-node" :class="edge.toClass">{{ edge.to }}</span>
          </div>
        </div>

        <!-- 图谱统计 -->
        <div class="graph-stats">
          <div class="graph-stats-title">图谱统计</div>
          <div class="graph-stats-items">
            <div class="graph-stat-item">
              <span class="graph-stat-label">节点数</span>
              <span class="graph-stat-value">{{ graphStats.nodeCount }}</span>
            </div>
            <div class="graph-stat-item">
              <span class="graph-stat-label">关联数</span>
              <span class="graph-stat-value">{{ graphStats.edgeCount }}</span>
            </div>
            <div class="graph-stat-item">
              <span class="graph-stat-label">文档覆盖</span>
              <span class="graph-stat-value">{{ graphStats.docCoverage }}</span>
            </div>
            <div class="graph-stat-item">
              <span class="graph-stat-label">孤立节点</span>
              <span class="graph-stat-value" style="color: #E24B4A">{{ graphStats.isolatedNodes }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import * as icons from '@element-plus/icons-vue'

const appStore = useAppStore()

const nodes = ref([
  { id: 1, label: '电商平台需求 v3.2', icon: 'Document', colorClass: 'gn-blue' },
  { id: 2, label: '支付系统接口文档', icon: 'Document', colorClass: 'gn-purple' },
  { id: 3, label: '用户中心 PRD', icon: 'Document', colorClass: 'gn-teal' },
  { id: 4, label: '购物车模块', icon: 'Box', colorClass: 'gn-amber' },
  { id: 5, label: '订单模块', icon: 'Box', colorClass: 'gn-coral' },
  { id: 6, label: '登录鉴权', icon: 'Box', colorClass: 'gn-blue' },
  { id: 7, label: 'TC-001 ~ TC-047', icon: 'List', colorClass: 'gn-teal' },
  { id: 8, label: 'TC-048 ~ TC-091', icon: 'List', colorClass: 'gn-purple' }
])

const edges = ref([
  { id: 1, from: '电商平台需求', fromClass: 'gn-blue', relation: '依赖', to: '支付系统接口', toClass: 'gn-purple' },
  { id: 2, from: '用户中心 PRD', fromClass: 'gn-teal', relation: '包含', to: '登录鉴权', toClass: 'gn-blue' },
  { id: 3, from: '购物车模块', fromClass: 'gn-amber', relation: '覆盖', to: 'TC-001 ~ TC-047', toClass: 'gn-teal' }
])

const graphStats = ref({
  nodeCount: 8,
  edgeCount: 12,
  docCoverage: '4 / 4',
  isolatedNodes: 0
})

onMounted(() => {
  appStore.setCurrentPage('knowledge-graph', '知识图谱', '编辑关联')
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
