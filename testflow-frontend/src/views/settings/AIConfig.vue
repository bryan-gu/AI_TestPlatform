<template>
  <div class="ai-config">
    <!-- 统计卡片 -->
    <div class="stats-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="stat-card">
        <div class="stat-label">已配置模型</div>
        <div class="stat-value">{{ stats.configuredModels }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>全部可用</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">本月调用次数</div>
        <div class="stat-value">{{ stats.monthlyCalls }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>较上月 +18%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Token 消耗</div>
        <div class="stat-value">{{ stats.tokenUsage }}</div>
        <div class="stat-sub"><span class="stat-dot dot-amber"></span>剩余额度 68%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">平均响应</div>
        <div class="stat-value">{{ stats.avgResponse }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>正常范围</div>
      </div>
    </div>

    <!-- AI 服务商配置 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">AI 服务商配置</div>
        <div class="card-action" @click="handleAddProvider">添加服务商</div>
      </div>
      <el-table :data="providers" style="width:100%">
        <el-table-column label="服务商" min-width="180">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:8px">
              <div class="provider-logo" :style="{ background: row.logoBg }">
                <span :style="{ color: row.logoColor, fontSize: '13px', fontWeight: 700 }">{{ row.logoLetter }}</span>
              </div>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="模型" width="160" />
        <el-table-column label="API Key" width="150">
          <template #default="{ row }">
            <code class="api-key-masked">{{ row.apiKeyMasked }}</code>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '正常' ? 'success' : 'warning'" size="small" effect="plain" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastCall" label="最近调用" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-btns">
              <el-button type="primary" link size="small" @click="handleEditProvider(row)"><el-icon><Edit /></el-icon>编辑</el-button>
              <el-button type="primary" link size="small" @click="handleTestProvider(row)" :loading="row.testing"><el-icon><Connection /></el-icon>测试</el-button>
              <el-button type="danger" link size="small" @click="handleDeleteProvider(row)"><el-icon><Delete /></el-icon>删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 模型分配策略 + 全局参数 -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <!-- 模型分配策略 -->
      <div class="card">
        <div class="card-head">
          <div class="card-title">模型分配策略</div>
          <div class="card-action" @click="handleEditStrategy">编辑</div>
        </div>
        <el-table :data="strategies" style="width:100%">
          <el-table-column prop="taskType" label="任务类型" min-width="120" />
          <el-table-column label="分配模型" width="160">
            <template #default="{ row }">
              <el-tag type="primary" size="small" effect="plain">{{ row.model }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="temperature" label="温度" width="80" />
        </el-table>
      </div>

      <!-- 全局参数 -->
      <div class="card">
        <div class="card-head">
          <div class="card-title">全局参数</div>
          <div class="card-action" @click="handleEditGlobalParams">编辑</div>
        </div>
        <div class="param-list">
          <div v-for="param in globalParams" :key="param.label" class="param-item">
            <span class="param-label">{{ param.label }}</span>
            <span v-if="param.isBadge" class="param-badge">
              <el-tag type="primary" size="small" effect="plain">{{ param.value }}</el-tag>
            </span>
            <span v-else class="param-value">{{ param.value }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 调用日志 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">最近调用日志</div>
        <div style="display:flex;gap:8px">
          <el-select v-model="logFilterProvider" size="small" style="width:120px" placeholder="全部服务商">
            <el-option label="全部服务商" value="" />
            <el-option v-for="p in providers" :key="p.name" :label="p.name" :value="p.name" />
          </el-select>
          <el-select v-model="logFilterStatus" size="small" style="width:120px" placeholder="全部状态">
            <el-option label="全部状态" value="" />
            <el-option label="成功" value="成功" />
            <el-option label="失败" value="失败" />
            <el-option label="超时" value="超时" />
          </el-select>
        </div>
      </div>
      <el-table :data="filteredLogs" style="width:100%">
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            <span class="mono-text">{{ row.time }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="taskType" label="任务类型" width="140" />
        <el-table-column prop="model" label="模型" width="150" />
        <el-table-column label="输入 Token" width="100">
          <template #default="{ row }"><span class="mono-text">{{ row.inputTokens }}</span></template>
        </el-table-column>
        <el-table-column label="输出 Token" width="100">
          <template #default="{ row }"><span class="mono-text">{{ row.outputTokens }}</span></template>
        </el-table-column>
        <el-table-column label="耗时" width="80">
          <template #default="{ row }"><span class="mono-text">{{ row.duration }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="logStatusType(row.status)" size="small" effect="plain" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑服务商对话框 -->
    <el-dialog v-model="providerEditVisible" title="编辑服务商" width="500px" destroy-on-close>
      <el-form :model="providerForm" label-width="80px">
        <el-form-item label="服务商"><el-input v-model="providerForm.name" /></el-form-item>
        <el-form-item label="模型"><el-input v-model="providerForm.model" /></el-form-item>
        <el-form-item label="API Key"><el-input v-model="providerForm.apiKey" placeholder="请输入 API Key" show-password /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="providerEditVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveProvider" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Edit, Delete, Connection } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '../../stores/app'

const appStore = useAppStore()
const saving = ref(false)

const stats = reactive({
  configuredModels: 3,
  monthlyCalls: '1,247',
  tokenUsage: '3.2M',
  avgResponse: '2.4s'
})

// 服务商数据
const providers = ref([
  { id: 1, name: 'OpenAI', model: 'GPT-4o', apiKeyMasked: 'sk-****...a8Bf', status: '正常', lastCall: '2 分钟前', logoLetter: 'O', logoBg: '#10A37F1A', logoColor: '#10A37F', testing: false },
  { id: 2, name: 'Anthropic', model: 'Claude 3.5 Sonnet', apiKeyMasked: 'sk-ant-****...x9K2', status: '正常', lastCall: '15 分钟前', logoLetter: 'A', logoBg: '#D4A5741A', logoColor: '#D4A574', testing: false },
  { id: 3, name: 'DeepSeek', model: 'DeepSeek-V3', apiKeyMasked: 'sk-****...m3Pq', status: '限流', lastCall: '1 小时前', logoLetter: 'D', logoBg: '#4D6BFE1A', logoColor: '#4D6BFE', testing: false }
])

// 模型分配策略
const strategies = ref([
  { taskType: '需求文档分析', model: 'GPT-4o', temperature: 0.1 },
  { taskType: '测试用例生成', model: 'Claude 3.5 Sonnet', temperature: 0.3 },
  { taskType: '自动化脚本生成', model: 'GPT-4o', temperature: 0.2 },
  { taskType: '知识图谱关联', model: 'DeepSeek-V3', temperature: 0.4 },
  { taskType: '测试报告摘要', model: 'Claude 3.5 Sonnet', temperature: 0.5 }
])

// 全局参数
const globalParams = ref([
  { label: '最大 Token 数', value: '4096', isBadge: false },
  { label: '超时时间', value: '60s', isBadge: false },
  { label: '重试次数', value: '3', isBadge: false },
  { label: '请求并发数', value: '5', isBadge: false },
  { label: '日志级别', value: 'INFO', isBadge: true }
])

// 调用日志
const logs = ref([
  { time: '2026-01-15 14:32:18', taskType: '需求文档分析', model: 'GPT-4o', inputTokens: '1,247', outputTokens: '3,891', duration: '3.2s', status: '成功' },
  { time: '2026-01-15 14:28:05', taskType: '测试用例生成', model: 'Claude 3.5 Sonnet', inputTokens: '2,103', outputTokens: '5,672', duration: '4.8s', status: '成功' },
  { time: '2026-01-15 14:15:42', taskType: '自动化脚本生成', model: 'GPT-4o', inputTokens: '3,421', outputTokens: '8,102', duration: '6.1s', status: '成功' },
  { time: '2026-01-15 13:58:11', taskType: '知识图谱关联', model: 'DeepSeek-V3', inputTokens: '1,856', outputTokens: '-', duration: '60.0s', status: '超时' },
  { time: '2026-01-15 13:45:30', taskType: '测试报告摘要', model: 'Claude 3.5 Sonnet', inputTokens: '892', outputTokens: '1,245', duration: '2.1s', status: '成功' }
])

const logFilterProvider = ref('')
const logFilterStatus = ref('')

const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    const matchProvider = !logFilterProvider.value || log.model.includes(logFilterProvider.value) || log.model === logFilterProvider.value
    const matchStatus = !logFilterStatus.value || log.status === logFilterStatus.value
    return matchProvider && matchStatus
  })
})

function logStatusType(status) {
  return { '成功': 'success', '失败': 'danger', '超时': 'warning' }[status] || 'info'
}

const providerEditVisible = ref(false)
const providerForm = reactive({ name: '', model: '', apiKey: '' })

function handleAddProvider() {
  Object.assign(providerForm, { name: '', model: '', apiKey: '' })
  providerEditVisible.value = true
}

function handleEditProvider(row) {
  Object.assign(providerForm, { name: row.name, model: row.model, apiKey: '' })
  providerEditVisible.value = true
}

async function handleSaveProvider() {
  saving.value = true
  try {
    await new Promise(r => setTimeout(r, 500))
    ElMessage.success('保存成功')
    providerEditVisible.value = false
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}

async function handleTestProvider(row) {
  row.testing = true
  try {
    await new Promise(r => setTimeout(r, 1500))
    ElMessage.success(`${row.name} 连接测试成功`)
  } catch (e) { ElMessage.error('连接测试失败') } finally { row.testing = false }
}

function handleDeleteProvider(row) {
  ElMessageBox.confirm(`确定要删除服务商"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    providers.value = providers.value.filter(p => p.id !== row.id)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function handleEditStrategy() {
  ElMessage.info('模型分配策略编辑功能开发中...')
}

function handleEditGlobalParams() {
  ElMessage.info('全局参数编辑功能开发中...')
}

onMounted(() => {
  appStore.setCurrentPage('ai-config', 'AI 配置')
})
</script>

<style scoped>
.ai-config { max-width: 1400px; }

.provider-logo {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.api-key-masked {
  font-family: var(--font-mono, monospace);
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.card-action {
  font-size: 12px;
  color: var(--accent);
  cursor: pointer;
  font-weight: 500;
}

.card-action:hover { text-decoration: underline; }

.action-btns { display: flex; gap: 4px; }

.mono-text {
  font-family: var(--font-mono, monospace);
  font-size: 12px;
}

/* 参数列表 */
.param-list {
  padding: 16px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}

.param-item:last-child {
  border-bottom: none;
}

.param-label {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.param-value {
  font-family: var(--font-mono, monospace);
  font-size: 13px;
  font-weight: 500;
}
</style>
