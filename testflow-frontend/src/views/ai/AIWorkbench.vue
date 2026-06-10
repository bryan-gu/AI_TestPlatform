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

    <!-- Sprint 选择 + 启动按钮 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div class="card-title">Sprint 选择</div>
        <div style="display:flex;gap:8px;align-items:center">
          <el-select v-model="selectedProject" size="small" style="width:160px" @change="onProjectChange">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-button
            type="primary"
            size="small"
            :disabled="!selectedProject || !selectedSprint"
            :loading="starting"
            @click="handleStart"
          >
            <el-icon><VideoPlay /></el-icon>
            {{ currentExecution && currentExecution.status === 'running' ? '执行中...' : '启动执行' }}
          </el-button>
        </div>
      </div>
      <div class="sprint-badges">
        <span
          v-for="s in sprints"
          :key="s.id"
          class="sprint-badge"
          :class="{ active: selectedSprint === s.id }"
          @click="selectedSprint = s.id"
        >{{ s.name }}</span>
        <div v-if="sprints.length === 0" style="font-size:12px;color:var(--color-text-tertiary);padding:10px">
          请先选择一个项目
        </div>
      </div>
    </div>

    <!-- SKILL 4 阶段流水线 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div class="card-title">SKILL 流水线</div>
        <div style="display:flex;align-items:center;gap:8px" v-if="currentExecution">
          <el-tag
            :type="statusTagType(currentExecution.status)"
            size="small"
            effect="plain"
            round
          >{{ statusLabel(currentExecution.status) }}</el-tag>
          <span v-if="currentExecution.duration_display" style="font-size:11px;color:var(--color-text-tertiary)">
            总耗时 {{ currentExecution.duration_display }}
          </span>
          <el-button
            v-if="currentExecution.status === 'running'"
            type="warning"
            size="small"
            @click="handlePause"
          >
            <el-icon><VideoPause /></el-icon>暂停
          </el-button>
          <el-button
            v-if="currentExecution.status === 'paused'"
            type="success"
            size="small"
            @click="handleResume"
          >
            <el-icon><VideoPlay /></el-icon>继续
          </el-button>
        </div>
      </div>

      <div class="pipeline" v-if="currentStages.length > 0">
        <div
          v-for="stage in currentStages"
          :key="stage.stage_no"
          class="pipeline-stage"
        >
          <div class="stage-timeline">
            <div
              class="stage-dot"
              :class="{
                completed: stage.status === 'completed',
                running: stage.status === 'running',
                failed: stage.status === 'failed',
                waiting: stage.status === 'waiting',
              }"
            >
              <el-icon v-if="stage.status === 'completed'" :size="18"><Check /></el-icon>
              <el-icon v-else-if="stage.status === 'failed'" :size="18"><Close /></el-icon>
              <div v-else-if="stage.status === 'running'" class="spinner"></div>
              <span v-else>{{ stage.stage_no }}</span>
            </div>
            <div
              class="stage-line"
              :class="stage.status === 'completed' ? 'completed' : 'pending'"
            ></div>
          </div>
          <div class="stage-content">
            <div class="stage-header">
              <div
                class="stage-name"
                :class="{ 'waiting-text': stage.status === 'waiting' }"
              >
                阶段 {{ stage.stage_no }}：{{ stage.stage_name }}
              </div>
              <el-tag
                :type="stageStatusTagType(stage.status)"
                size="small"
                effect="plain"
                round
              >{{ stageStatusLabel(stage.status) }}</el-tag>
            </div>
            <div
              class="stage-desc"
              :class="{ 'waiting-text': stage.status === 'waiting' }"
            >
              {{ stageDescription(stage.stage_no) }}
            </div>

            <!-- 已完成：展示结果 -->
            <template v-if="stage.status === 'completed'">
              <div class="stage-meta">
                <span>模型：<strong>{{ stage.model || '-' }}</strong></span>
                <span>耗时：<strong>{{ stage.duration_display || '-' }}</strong></span>
                <span>输入 Token：<strong class="mono">{{ formatNumber(stage.input_tokens) }}</strong></span>
                <span>输出 Token：<strong class="mono">{{ formatNumber(stage.output_tokens) }}</strong></span>
              </div>
              <div class="stage-result" v-if="stage.result_summary && Object.keys(stage.result_summary).length > 0">
                <div class="result-title">分析结果摘要</div>
                <div class="result-grid">
                  <div
                    v-for="(val, key) in stage.result_summary"
                    :key="key"
                    class="result-item"
                  >
                    <div class="result-value" style="color:var(--accent)">{{ val }}</div>
                    <div class="result-label">{{ key }}</div>
                  </div>
                </div>
              </div>
            </template>

            <!-- 运行中 -->
            <template v-else-if="stage.status === 'running'">
              <div class="stage-meta">
                <span>模型：<strong>{{ stage.model || '-' }}</strong></span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill indeterminate"></div>
              </div>
              <div style="font-size:11px;color:var(--color-text-tertiary);margin-top:6px">正在执行中...</div>
            </template>

            <!-- 失败 -->
            <template v-else-if="stage.status === 'failed'">
              <div style="font-size:12px;color:#E24B4A">执行失败，请检查 AI 配置或重试</div>
            </template>
          </div>
        </div>
      </div>

      <div v-else class="pipeline-empty">
        <div style="text-align:center;padding:40px 0;color:var(--color-text-tertiary)">
          <el-icon :size="32" style="margin-bottom:8px;color:var(--color-border-secondary)"><Cpu /></el-icon>
          <div style="font-size:13px">选择项目与 Sprint，点击「启动执行」开始 SKILL 流水线</div>
        </div>
      </div>
    </div>

    <!-- 产物展示：功能点 + 测试用例 -->
    <template v-if="showArtifacts">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
        <!-- 功能点 -->
        <div class="card">
          <div class="card-head">
            <div class="card-title">AI 提取的功能点</div>
            <el-tag size="small" effect="plain" round>{{ artifactFeaturePoints.length }} 个功能点</el-tag>
          </div>
          <div class="artifact-content" v-if="artifactFeaturePoints.length > 0">
            <div v-for="fp in artifactFeaturePoints" :key="fp.id" class="artifact-item">
              <div class="artifact-name">{{ fp.name }}</div>
              <div class="artifact-meta">
                <el-tag size="small" type="info" effect="plain">{{ fp.module_name }}</el-tag>
              </div>
            </div>
          </div>
          <div v-else style="padding:16px;text-align:center;color:var(--color-text-tertiary);font-size:12px">
            暂无功能点数据
          </div>
        </div>

        <!-- 测试用例 -->
        <div class="card">
          <div class="card-head">
            <div class="card-title">AI 生成的测试用例</div>
            <div style="display:flex;align-items:center;gap:8px">
              <el-tag size="small" effect="plain" round>{{ artifactTestCases.length }} 条用例</el-tag>
              <el-button
                v-if="showTestCases"
                type="primary"
                size="small"
                :loading="downloadingExcel"
                @click="handleDownloadExcel"
              >
                <el-icon><Download /></el-icon>下载 Excel
              </el-button>
            </div>
          </div>
          <div class="artifact-content" v-if="artifactTestCases.length > 0">
            <div v-for="tc in artifactTestCases.slice(0, 20)" :key="tc.id" class="artifact-item">
              <div class="artifact-name">
                <code class="case-no">{{ tc.case_no }}</code>
                {{ tc.title }}
              </div>
              <div class="artifact-meta">
                <el-tag size="small" type="info" effect="plain">{{ tc.module }}</el-tag>
                <el-tag :type="tc.priority === '高' ? 'danger' : tc.priority === '低' ? 'info' : 'warning'" size="small" effect="plain">
                  {{ tc.priority }}
                </el-tag>
              </div>
            </div>
            <div v-if="artifactTestCases.length > 20" style="text-align:center;padding:8px;font-size:11px;color:var(--color-text-tertiary)">
              显示前 20 条，共 {{ artifactTestCases.length }} 条用例
            </div>
          </div>
          <div v-else-if="!showTestCases" style="padding:16px;text-align:center;color:var(--color-text-tertiary);font-size:12px">
            等待 Stage 2 完成后展示
          </div>
          <div v-else style="padding:16px;text-align:center;color:var(--color-text-tertiary);font-size:12px">
            暂无用例数据
          </div>
        </div>
      </div>
    </template>

    <!-- 知识图谱预处理 + 执行历史 -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <!-- 知识图谱预处理 -->
      <div class="card">
        <div class="card-head">
          <div class="card-title">知识图谱预处理</div>
        </div>
        <div class="preprocess-content">
          <div style="font-size:12px;color:var(--color-text-secondary);margin-bottom:12px">
            AI 在执行前自动解析知识库文档，构建跨模块关联图谱，供后续阶段使用。
          </div>
          <div class="preprocess-stats">
            <div class="preprocess-item">
              <div class="preprocess-value">{{ graphStats.totalNodes }}</div>
              <div class="preprocess-label">图谱节点</div>
            </div>
            <div class="preprocess-item">
              <div class="preprocess-value">{{ graphStats.totalEdges }}</div>
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
        <div class="history-list" v-if="executionHistory.length > 0">
          <div v-for="h in executionHistory" :key="h.id" class="history-item" @click="loadExecution(h)">
            <div class="history-info">
              <div class="history-name">
                {{ h.sprint_name || h.project_name || '未指定' }}
                <el-tag size="small" style="margin-left:4px">{{ h.mode === 'incremental' ? '增量' : '全量' }}</el-tag>
                <el-tag v-if="h.sprint_deleted || h.project_deleted" type="info" size="small" effect="plain" style="margin-left:4px">已删除</el-tag>
              </div>
              <div class="history-time">
                {{ formatTime(h.created_at) }}
                <template v-if="h.duration_display"> · {{ h.duration_display }}</template>
              </div>
            </div>
            <el-tag
              :type="statusTagType(h.status)"
              size="small"
              effect="plain"
              round
            >{{ statusLabel(h.status) }}</el-tag>
          </div>
        </div>
        <div v-else style="padding:20px;text-align:center;color:var(--color-text-tertiary);font-size:12px">
          暂无执行记录
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { RefreshRight, Operation, Check, Close, VideoPlay, VideoPause, Cpu, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '../../stores/app'
import { getProjects } from '../../api/project'
import { getSprints } from '../../api/sprint'
import { getGraphStats } from '../../api/graph'
import { getExecutions, createExecution, pauseExecution, resumeExecution, getExecution, getExecutionFeaturePoints, getExecutionTestCases, downloadExecutionExcel } from '../../api/pipeline'

const router = useRouter()
const appStore = useAppStore()

// ── 选择状态 ──
const selectedMode = ref('full')
const selectedProject = ref(null)
const selectedSprint = ref(null)
const starting = ref(false)

// ── 数据 ──
const projects = ref([])
const sprints = ref([])
const executionHistory = ref([])
const currentExecution = ref(null)

const graphStats = reactive({ totalNodes: 0, totalEdges: 0 })

// ── 产物数据 ──
const artifactFeaturePoints = ref([])
const artifactTestCases = ref([])
const downloadingExcel = ref(false)

// 判断是否显示产物区域
const showArtifacts = computed(() => {
  if (!currentExecution.value) return false
  const stages = currentExecution.value.stages || []
  const stage1 = stages.find(s => s.stage_no === 1)
  return stage1 && stage1.status === 'completed'
})

const showTestCases = computed(() => {
  if (!currentExecution.value) return false
  const stages = currentExecution.value.stages || []
  const stage2 = stages.find(s => s.stage_no === 2)
  return stage2 && stage2.status === 'completed'
})

// ── 轮询 ──
let pollingTimer = null

function startPolling(executionId) {
  stopPolling()
  pollingTimer = setInterval(async () => {
    try {
      const res = await getExecution(executionId)
      const data = res.data?.data || res.data || {}
      currentExecution.value = data
      // 终态时停止轮询
      if (['completed', 'failed'].includes(data.status)) {
        stopPolling()
        await loadExecutionHistory()
        appStore.refreshSidebarBadges()
        // 加载产物数据并刷新图谱统计
        await loadArtifacts(executionId)
        await loadGraphStats()
      }
    } catch (e) {
      console.error('轮询执行状态失败', e)
      stopPolling()
    }
  }, 3000)
}

function stopPolling() {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

const currentStages = computed(() => {
  if (!currentExecution.value || !currentExecution.value.stages) return []
  return currentExecution.value.stages
})

// ── 工具函数 ──

function statusTagType(status) {
  const map = {
    completed: 'success',
    running: 'primary',
    paused: 'warning',
    waiting: 'info',
    failed: 'danger',
  }
  return map[status] || 'info'
}

function statusLabel(status) {
  const map = {
    completed: '已完成',
    running: '运行中',
    paused: '已暂停',
    waiting: '等待中',
    failed: '失败',
  }
  return map[status] || status
}

function stageStatusTagType(status) {
  return statusTagType(status)
}

function stageStatusLabel(status) {
  return statusLabel(status)
}

function stageDescription(stageNo) {
  const map = {
    1: 'AI 解析知识库中的需求文档，提取功能点、业务规则、接口定义，构建知识图谱关联。',
    2: '基于需求分析结果，AI 自动生成测试用例，覆盖正向、异常、边界场景。',
    3: '将测试用例转化为可执行的 Playwright / Selenium 自动化脚本。',
    4: '执行自动化脚本，失败时 AI 自动分析原因并尝试修复脚本。',
  }
  return map[stageNo] || ''
}

function formatNumber(n) {
  if (!n) return '0'
  return n.toLocaleString()
}

function formatTime(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} 天前`
  return `${d.getMonth() + 1}/${d.getDate()}`
}

// ── 数据加载 ──

async function loadProjects() {
  try {
    const res = await getProjects()
    projects.value = res.data?.data || res.data || []
    if (projects.value.length > 0 && !selectedProject.value) {
      selectedProject.value = projects.value[0].id
      await loadSprints()
    }
  } catch (e) {
    console.error('加载项目失败', e)
  }
}

async function loadSprints() {
  if (!selectedProject.value) {
    sprints.value = []
    return
  }
  try {
    const res = await getSprints({ project_id: selectedProject.value })
    sprints.value = res.data?.data || res.data || []
    if (sprints.value.length > 0 && !selectedSprint.value) {
      selectedSprint.value = sprints.value[0].id
    }
  } catch (e) {
    console.error('加载 Sprint 失败', e)
  }
}

async function loadExecutionHistory() {
  try {
    const params = {}
    if (selectedProject.value) params.project_id = selectedProject.value
    const res = await getExecutions(params)
    executionHistory.value = res.data?.data || res.data || []
    // 如果有执行记录，默认加载最近一条
    if (executionHistory.value.length > 0 && !currentExecution.value) {
      currentExecution.value = executionHistory.value[0]
      // 获取完整详情（含 stages）
      await loadExecution(executionHistory.value[0])
    }
  } catch (e) {
    console.error('加载执行历史失败', e)
  }
}

async function loadGraphStats() {
  try {
    const res = await getGraphStats()
    const s = res.data?.data || res.data || {}
    graphStats.totalNodes = s.total_nodes ?? 0
    graphStats.totalEdges = s.total_edges ?? 0
  } catch (e) {
    console.error('加载图谱统计失败', e)
  }
}

async function loadExecution(h) {
  try {
    const res = await getExecution(h.id)
    currentExecution.value = res.data?.data || res.data || {}
    // 加载产物数据
    await loadArtifacts(h.id)
  } catch (e) {
    console.error('加载执行详情失败', e)
  }
}

async function loadArtifacts(executionId) {
  if (!executionId) return
  try {
    const [fpRes, tcRes] = await Promise.all([
      getExecutionFeaturePoints(executionId).catch(() => ({ data: { data: [] } })),
      getExecutionTestCases(executionId).catch(() => ({ data: { data: [] } })),
    ])
    artifactFeaturePoints.value = fpRes.data?.data || []
    artifactTestCases.value = tcRes.data?.data || []
  } catch (e) {
    console.error('加载产物数据失败', e)
  }
}

async function handleDownloadExcel() {
  if (!currentExecution.value) return
  downloadingExcel.value = true
  try {
    const res = await downloadExecutionExcel(currentExecution.value.id)
    // Blob 下载
    const blob = res.data instanceof Blob ? res.data : new Blob([res.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `测试用例-${currentExecution.value.sprint_name || 'export'}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('Excel 下载成功')
  } catch (e) {
    ElMessage.error('下载失败，可能尚未生成 Excel')
  } finally {
    downloadingExcel.value = false
  }
}

async function onProjectChange() {
  selectedSprint.value = null
  currentExecution.value = null
  await Promise.all([loadSprints(), loadExecutionHistory()])
}

// ── 操作 ──

async function handleStart() {
  if (!selectedProject.value || !selectedSprint.value) {
    ElMessage.warning('请先选择项目和 Sprint')
    return
  }
  starting.value = true
  try {
    const res = await createExecution({
      project_id: selectedProject.value,
      sprint_id: selectedSprint.value,
      mode: selectedMode.value,
    })
    const execution = res.data?.data || res.data || {}
    currentExecution.value = execution
    ElMessage.success('流水线已启动')
    appStore.refreshSidebarBadges()
    await loadExecutionHistory()
    // 启动轮询跟踪执行进度
    if (execution.id && ['running', 'waiting'].includes(execution.status)) {
      startPolling(execution.id)
    }
  } catch (e) {
    ElMessage.error('启动执行失败')
    console.error(e)
  } finally {
    starting.value = false
  }
}

async function handlePause() {
  if (!currentExecution.value) return
  try {
    const res = await pauseExecution(currentExecution.value.id)
    currentExecution.value = res.data?.data || res.data || {}
    stopPolling()
    appStore.refreshSidebarBadges()
    ElMessage.info('已暂停')
  } catch (e) {
    ElMessage.error('暂停失败')
  }
}

async function handleResume() {
  if (!currentExecution.value) return
  try {
    const res = await resumeExecution(currentExecution.value.id)
    const execution = res.data?.data || res.data || {}
    currentExecution.value = execution
    ElMessage.success('流水线已恢复执行')
    appStore.refreshSidebarBadges()
    // 启动轮询跟踪执行进度
    if (execution.id && ['running', 'waiting'].includes(execution.status)) {
      startPolling(execution.id)
    }
  } catch (e) {
    ElMessage.error('继续执行失败')
  }
}

function goToGraphList() {
  router.push('/graphs')
}

// ── 初始化 ──

onMounted(async () => {
  appStore.setCurrentPage('ai-workbench', 'AI 工作台')
  await loadProjects()
  await Promise.all([loadExecutionHistory(), loadGraphStats()])
})

onUnmounted(() => {
  stopPolling()
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

.pipeline-empty {
  padding: 10px;
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

.stage-dot.failed {
  background: #fee2e2;
  color: #dc2626;
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
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
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

.progress-fill.indeterminate {
  width: 30%;
  animation: indeterminate 1.5s ease-in-out infinite;
}

@keyframes indeterminate {
  0% { margin-left: 0; width: 30%; }
  50% { margin-left: 40%; width: 30%; }
  100% { margin-left: 0; width: 30%; }
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
  cursor: pointer;
}

.history-item:hover {
  background: var(--color-background-secondary);
  margin: 0 -18px;
  padding: 10px 18px;
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

/* 产物展示 */
.artifact-content {
  padding: 4px 18px;
  max-height: 320px;
  overflow-y: auto;
}

.artifact-item {
  padding: 10px 0;
  border-bottom: 0.5px solid var(--color-border-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.artifact-item:last-child {
  border-bottom: none;
}

.artifact-name {
  font-size: 12px;
  color: var(--color-text-primary);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artifact-meta {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.case-no {
  font-family: var(--font-mono, monospace);
  font-size: 11px;
  background: var(--color-background-secondary);
  padding: 1px 6px;
  border-radius: 3px;
  color: var(--accent);
  margin-right: 6px;
}
</style>
