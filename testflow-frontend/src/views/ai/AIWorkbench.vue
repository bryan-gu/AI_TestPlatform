<template>
  <div class="ai-workbench">
    <!-- 模式选择 -->
    <div class="mode-cards">
      <div
        class="mode-card"
        :class="{ active: selectedMode === 'full' }"
        @click="selectedMode = 'full'"
      >
        <div class="mode-header">
          <el-icon :size="20" style="color:var(--accent)"><RefreshRight /></el-icon>
          <span class="mode-title">全量模式</span>
        </div>
        <div class="mode-desc">从零开始，完整执行 SKILL 全部 4 个阶段。适用于新项目或重大版本迭代。</div>
      </div>
      <div
        class="mode-card"
        :class="{ active: selectedMode === 'incremental' }"
        @click="selectedMode = 'incremental'"
      >
        <div class="mode-header">
          <el-icon :size="20" style="color:var(--color-text-secondary)"><Operation /></el-icon>
          <span class="mode-title">增量模式</span>
        </div>
        <div class="mode-desc">基于当前 Sprint 快照，仅分析变更部分并生成增量用例。适用于迭代回归。</div>
      </div>
    </div>

    <!-- Sprint 选择 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div class="card-title">Sprint 选择</div>
        <el-select v-model="selectedProject" size="small" style="width:160px">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>
      <div class="sprint-badges">
        <span
          v-for="s in sprints"
          :key="s.id"
          class="sprint-badge"
          :class="{ active: selectedSprint === s.id }"
          @click="selectedSprint = s.id"
        >{{ s.name }}</span>
      </div>
    </div>

    <!-- SKILL 4 阶段流水线 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div class="card-title">SKILL 流水线</div>
        <div style="display:flex;align-items:center;gap:8px">
          <el-tag type="success" size="small" effect="plain" round>运行中</el-tag>
          <span style="font-size:11px;color:var(--color-text-tertiary)">已运行 12 分 34 秒</span>
        </div>
      </div>
      <div class="pipeline">
        <!-- 阶段 1: 需求分析 -->
        <div class="pipeline-stage">
          <div class="stage-timeline">
            <div class="stage-dot completed">
              <el-icon :size="18"><Check /></el-icon>
            </div>
            <div class="stage-line completed"></div>
          </div>
          <div class="stage-content">
            <div class="stage-header">
              <div class="stage-name">阶段 1：需求分析</div>
              <el-tag type="success" size="small" effect="plain" round>已完成</el-tag>
            </div>
            <div class="stage-desc">AI 解析知识库中的需求文档，提取功能点、业务规则、接口定义，构建知识图谱关联。</div>
            <div class="stage-meta">
              <span>模型：<strong>GPT-4o</strong></span>
              <span>耗时：<strong>3m 12s</strong></span>
              <span>输入 Token：<strong class="mono">12,847</strong></span>
              <span>输出 Token：<strong class="mono">8,234</strong></span>
            </div>
            <!-- 展开的分析结果 -->
            <div class="stage-result">
              <div class="result-title">分析结果摘要</div>
              <div class="result-grid">
                <div class="result-item">
                  <div class="result-value" style="color:var(--accent)">23</div>
                  <div class="result-label">功能点</div>
                </div>
                <div class="result-item">
                  <div class="result-value" style="color:var(--accent)">15</div>
                  <div class="result-label">业务规则</div>
                </div>
                <div class="result-item">
                  <div class="result-value" style="color:var(--accent)">8</div>
                  <div class="result-label">API 端点</div>
                </div>
                <div class="result-item">
                  <div class="result-value" style="color:var(--accent)">12</div>
                  <div class="result-label">图谱关联</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 阶段 2: 测试用例生成 -->
        <div class="pipeline-stage">
          <div class="stage-timeline">
            <div class="stage-dot running">
              <div class="spinner"></div>
            </div>
            <div class="stage-line pending"></div>
          </div>
          <div class="stage-content">
            <div class="stage-header">
              <div class="stage-name">阶段 2：测试用例生成</div>
              <el-tag type="primary" size="small" effect="plain" round>执行中</el-tag>
            </div>
            <div class="stage-desc">基于需求分析结果，AI 自动生成测试用例，覆盖正向、异常、边界场景。</div>
            <div class="stage-meta" style="margin-bottom:10px">
              <span>模型：<strong>Claude 3.5 Sonnet</strong></span>
              <span>已生成：<strong>47 / ~80 条</strong></span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width:59%"></div>
            </div>
            <div style="font-size:11px;color:var(--color-text-tertiary);margin-top:6px">预计剩余 2 分钟</div>
          </div>
        </div>

        <!-- 阶段 3: E2E 脚本生成 -->
        <div class="pipeline-stage">
          <div class="stage-timeline">
            <div class="stage-dot waiting"><span>3</span></div>
            <div class="stage-line pending"></div>
          </div>
          <div class="stage-content">
            <div class="stage-header">
              <div class="stage-name waiting-text">阶段 3：E2E 脚本生成</div>
              <el-tag type="info" size="small" effect="plain" round>等待中</el-tag>
            </div>
            <div class="stage-desc waiting-text">将测试用例转化为可执行的 Playwright / Selenium 自动化脚本。</div>
          </div>
        </div>

        <!-- 阶段 4: 执行与自愈 -->
        <div class="pipeline-stage">
          <div class="stage-timeline">
            <div class="stage-dot waiting"><span>4</span></div>
          </div>
          <div class="stage-content">
            <div class="stage-header">
              <div class="stage-name waiting-text">阶段 4：执行与自愈</div>
              <el-tag type="info" size="small" effect="plain" round>等待中</el-tag>
            </div>
            <div class="stage-desc waiting-text">执行自动化脚本，失败时 AI 自动分析原因并尝试修复脚本。</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识图谱预处理 + 执行历史 -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <!-- 知识图谱预处理 -->
      <div class="card">
        <div class="card-head">
          <div class="card-title">知识图谱预处理</div>
          <el-tag type="success" size="small" effect="plain" round>已完成</el-tag>
        </div>
        <div class="preprocess-content">
          <div style="font-size:12px;color:var(--color-text-secondary);margin-bottom:12px">
            AI 在执行前自动解析知识库文档，构建跨模块关联图谱，供后续阶段使用。
          </div>
          <div class="preprocess-stats">
            <div class="preprocess-item">
              <div class="preprocess-value">29</div>
              <div class="preprocess-label">图谱节点</div>
            </div>
            <div class="preprocess-item">
              <div class="preprocess-value">47</div>
              <div class="preprocess-label">关联边</div>
            </div>
          </div>
          <div style="margin-top:12px">
            <span class="graph-link" @click="goToGraphList">查看知识图谱 →</span>
          </div>
        </div>
      </div>

      <!-- 执行历史 -->
      <div class="card">
        <div class="card-head">
          <div class="card-title">执行历史</div>
        </div>
        <div class="history-list">
          <div v-for="h in executionHistory" :key="h.name" class="history-item">
            <div class="history-info">
              <div class="history-name">{{ h.name }}</div>
              <div class="history-time">{{ h.time }}</div>
            </div>
            <el-tag :type="h.status === '运行中' ? 'success' : 'primary'" size="small" effect="plain" round>{{ h.status }}</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RefreshRight, Operation, Check } from '@element-plus/icons-vue'
import { useAppStore } from '../../stores/app'

const router = useRouter()
const appStore = useAppStore()

const selectedMode = ref('full')
const selectedProject = ref(1)
const selectedSprint = ref('sprint-2')

const projects = ref([
  { id: 1, name: '电商平台 v3.0' },
  { id: 2, name: '支付系统' },
  { id: 3, name: '用户中心重构' }
])

const sprints = ref([
  { id: 'sprint-0', name: 'Sprint 0' },
  { id: 'sprint-1', name: 'Sprint 1' },
  { id: 'sprint-2', name: 'Sprint 2' },
  { id: 'sprint-3', name: 'Sprint 3' },
  { id: 'sprint-all', name: 'sprint_all（最新汇总）' }
])

const executionHistory = ref([
  { name: 'Sprint 2 全量执行', time: '今天 14:20 · 运行中', status: '运行中' },
  { name: 'Sprint 1 增量执行', time: '昨天 16:45 · 18m 32s', status: '已完成' },
  { name: 'Sprint 0 全量执行', time: '3 天前 · 24m 10s', status: '已完成' }
])

function goToGraphList() {
  router.push('/graphs')
}

onMounted(() => {
  appStore.setCurrentPage('ai-workbench', 'AI 工作台')
})
</script>

<style scoped>
.ai-workbench { max-width: 1400px; }

/* 模式选择卡片 */
.mode-cards {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.mode-card {
  flex: 1;
  padding: 16px 20px;
  border-radius: var(--border-radius-lg, 10px);
  border: 1px solid var(--color-border-tertiary);
  background: var(--color-background-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.mode-card.active {
  border: 2px solid var(--accent);
  background: var(--accent-light, #EBF5FF);
}

.mode-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.mode-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.mode-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* Sprint 选择 */
.sprint-badges {
  padding: 14px 18px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.sprint-badge {
  padding: 6px 14px;
  border-radius: 14px;
  font-size: 12px;
  cursor: pointer;
  background: #E6F1FB;
  color: #378ADD;
  transition: all 0.15s;
}

.sprint-badge.active {
  background: var(--accent);
  color: #fff;
}

.sprint-badge:hover:not(.active) {
  opacity: 0.8;
}

/* 流水线 */
.pipeline {
  padding: 20px 18px;
}

.pipeline-stage {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  position: relative;
}

.pipeline-stage:last-child {
  margin-bottom: 0;
}

/* 时间线 */
.stage-timeline {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.stage-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stage-dot.completed {
  background: #dcfce7;
  color: #16a34a;
}

.stage-dot.running {
  background: var(--accent-light, #EBF5FF);
  border: 2px solid var(--accent);
}

.stage-dot.waiting {
  background: var(--color-background-secondary);
  color: var(--color-text-tertiary);
}

.stage-dot.waiting span {
  font-size: 14px;
  font-weight: 600;
}

.stage-line {
  width: 2px;
  flex: 1;
  margin-top: 4px;
}

.stage-line.completed { background: #dcfce7; }
.stage-line.pending { background: var(--color-border-tertiary); }

/* 阶段内容 */
.stage-content {
  flex: 1;
  padding-bottom: 16px;
}

.pipeline-stage:last-child .stage-content {
  padding-bottom: 0;
}

.stage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.stage-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.stage-name.waiting-text {
  color: var(--color-text-tertiary);
}

.stage-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 10px;
  line-height: 1.6;
}

.stage-desc.waiting-text {
  color: var(--color-text-tertiary);
}

.stage-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.stage-meta strong {
  color: var(--color-text-secondary);
}

.stage-meta .mono {
  font-family: var(--font-mono, monospace);
}

/* 分析结果 */
.stage-result {
  margin-top: 12px;
  padding: 12px;
  background: var(--color-background-secondary);
  border-radius: var(--border-radius-md, 6px);
  font-size: 12px;
}

.result-title {
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--color-text-primary);
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.result-item {
  text-align: center;
  padding: 8px;
  background: var(--color-background-primary);
  border-radius: var(--border-radius-sm, 4px);
}

.result-value {
  font-size: 18px;
  font-weight: 600;
}

.result-label {
  color: var(--color-text-tertiary);
  font-size: 11px;
}

/* 进度条 */
.progress-bar {
  height: 6px;
  background: var(--color-background-secondary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 0.3s;
}

/* 旋转动画 */
.spinner {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--accent);
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 预处理内容 */
.preprocess-content {
  padding: 14px 18px;
}

.preprocess-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.preprocess-item {
  padding: 10px;
  background: var(--color-background-secondary);
  border-radius: var(--border-radius-sm, 4px);
  text-align: center;
}

.preprocess-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--accent);
}

.preprocess-label {
  font-size: 10px;
  color: var(--color-text-tertiary);
}

.graph-link {
  font-size: 12px;
  color: var(--accent);
  cursor: pointer;
}

.graph-link:hover { text-decoration: underline; }

/* 执行历史 */
.history-list {
  padding: 4px 18px;
}

.history-item {
  padding: 10px 0;
  border-bottom: 0.5px solid var(--color-border-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-item:last-child {
  border-bottom: none;
}

.history-name {
  font-size: 13px;
  color: var(--color-text-primary);
}

.history-time {
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-top: 2px;
}
</style>
