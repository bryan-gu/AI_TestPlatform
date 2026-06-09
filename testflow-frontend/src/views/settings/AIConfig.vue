<template>
  <div class="ai-config">
    <!-- 统计卡片 -->
    <div class="stats-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="stat-card">
        <div class="stat-label">已配置模型</div>
        <div class="stat-value">{{ stats.configured_models }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>全部可用</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">本月调用次数</div>
        <div class="stat-value">{{ stats.monthly_calls }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>AI 调用统计</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Token 消耗</div>
        <div class="stat-value">{{ formatTokens(stats.total_input_tokens + stats.total_output_tokens) }}</div>
        <div class="stat-sub"><span class="stat-dot dot-amber"></span>输入 + 输出</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">平均响应</div>
        <div class="stat-value">{{ stats.avg_duration_ms ? (stats.avg_duration_ms / 1000).toFixed(1) + 's' : '--' }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>正常范围</div>
      </div>
    </div>

    <!-- AI 服务商配置 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">AI 服务商配置</div>
        <div class="card-action" @click="handleAddProvider">添加服务商</div>
      </div>
      <el-table :data="providers" style="width:100%" v-loading="providerLoading">
        <el-table-column label="服务商" min-width="180">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:8px">
              <div class="provider-logo" :style="{ background: getProviderBg(row.provider_type) }">
                <span :style="{ color: getProviderColor(row.provider_type), fontSize: '13px', fontWeight: 700 }">{{ getProviderLetter(row.provider_type) }}</span>
              </div>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="模型" width="160" />
        <el-table-column label="API Key" width="150">
          <template #default="{ row }">
            <code class="api-key-masked">{{ row.api_key_masked }}</code>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '正常' ? 'success' : 'warning'" size="small" effect="plain" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最近调用" width="120">
          <template #default="{ row }">{{ formatTimeAgo(row.last_call_at) }}</template>
        </el-table-column>
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

    <!-- 模型分配策略 + 全局参数 + 被测系统配置 -->
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px">
      <!-- 模型分配策略 -->
      <div class="card">
        <div class="card-head">
          <div class="card-title">模型分配策略</div>
          <div class="card-action" @click="openStrategyEdit">编辑</div>
        </div>
        <el-table :data="strategies" style="width:100%">
          <el-table-column prop="task_type" label="任务类型" min-width="120" />
          <el-table-column label="分配模型" width="160">
            <template #default="{ row }">
              <el-tag type="primary" size="small" effect="plain">{{ row.model_name }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 全局参数 -->
      <div class="card">
        <div class="card-head">
          <div class="card-title">全局参数</div>
          <div class="card-action" @click="openGlobalParamsEdit('system')">编辑</div>
        </div>
        <div class="param-list">
          <div v-for="param in systemParams" :key="param.key" class="param-item">
            <span class="param-label">{{ param.label || param.key }}</span>
            <span v-if="param.key === 'log_level'" class="param-badge">
              <el-tag type="primary" size="small" effect="plain">{{ param.value }}</el-tag>
            </span>
            <span v-else class="param-value">{{ param.value }}</span>
          </div>
        </div>
      </div>

      <!-- 被测系统配置 -->
      <div class="card">
        <div class="card-head">
          <div class="card-title">被测系统配置</div>
          <div class="card-action" @click="openGlobalParamsEdit('target')">编辑</div>
        </div>
        <div class="param-list">
          <div v-for="param in targetParams" :key="param.key" class="param-item">
            <span class="param-label">{{ param.label || param.key }}</span>
            <span v-if="isSecretKey(param.key)" class="param-value">{{ param.value ? '••••••' : '未配置' }}</span>
            <span v-else class="param-value">{{ param.value || '未配置' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 调用日志 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">最近调用日志</div>
        <div style="display:flex;gap:8px">
          <el-select v-model="logFilterProvider" size="small" style="width:120px" placeholder="全部服务商" clearable @change="loadCallLogs">
            <el-option v-for="p in providers" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-select v-model="logFilterStatus" size="small" style="width:120px" placeholder="全部状态" clearable @change="loadCallLogs">
            <el-option label="成功" value="成功" />
            <el-option label="失败" value="失败" />
            <el-option label="超时" value="超时" />
          </el-select>
        </div>
      </div>
      <el-table :data="callLogs" style="width:100%" v-loading="logLoading">
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            <span class="mono-text">{{ formatDateTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="task_type" label="任务类型" width="140" />
        <el-table-column prop="model" label="模型" width="150" />
        <el-table-column label="输入 Token" width="100">
          <template #default="{ row }"><span class="mono-text">{{ row.input_tokens?.toLocaleString() }}</span></template>
        </el-table-column>
        <el-table-column label="输出 Token" width="100">
          <template #default="{ row }"><span class="mono-text">{{ row.output_tokens?.toLocaleString() }}</span></template>
        </el-table-column>
        <el-table-column label="耗时" width="80">
          <template #default="{ row }"><span class="mono-text">{{ row.duration_ms ? (row.duration_ms / 1000).toFixed(1) + 's' : '--' }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="logStatusType(row.status)" size="small" effect="plain" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑服务商对话框 -->
    <el-dialog v-model="providerEditVisible" :title="isEditProvider ? '编辑服务商' : '添加服务商'" width="500px" destroy-on-close>
      <el-form :model="providerForm" label-width="100px">
        <el-form-item label="服务商类型">
          <el-select v-model="providerForm.provider_type" placeholder="选择服务商类型" style="width:100%">
            <el-option label="OpenAI" value="OpenAI" />
            <el-option label="Anthropic" value="Anthropic" />
            <el-option label="DeepSeek" value="DeepSeek" />
            <el-option label="Custom" value="Custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input v-model="providerForm.name" placeholder="例如：OpenAI GPT-4o" />
        </el-form-item>
        <el-form-item label="模型">
          <el-input v-model="providerForm.model" placeholder="例如：gpt-4o" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input
            v-model="providerForm.api_key"
            :placeholder="apiKeyPlaceholder"
            @focus="handleApiKeyFocus"
            @blur="handleApiKeyBlur"
          />
        </el-form-item>
        <el-form-item label="自定义端点">
          <el-input v-model="providerForm.endpoint_url" placeholder="可选，留空使用默认端点" />
        </el-form-item>
        <el-form-item label="最大Token">
          <el-input-number v-model="providerForm.max_tokens" :min="256" :max="128000" :step="256" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="providerEditVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveProvider" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑策略对话框 -->
    <el-dialog v-model="strategyEditVisible" title="编辑模型分配策略" width="650px" destroy-on-close>
      <el-table :data="strategyEditForm" style="width:100%">
        <el-table-column prop="task_type" label="任务类型" min-width="120" />
        <el-table-column label="分配模型" min-width="250">
          <template #default="{ row }">
            <el-select
              v-model="row.provider_id"
              size="small"
              filterable
              placeholder="选择已配置的模型"
              style="width:100%"
              @change="(val) => onStrategyProviderChange(row, val)"
            >
              <el-option
                v-for="p in providers"
                :key="p.id"
                :label="`${p.name}（${p.model}）`"
                :value="p.id"
              />
            </el-select>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="strategyEditVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveStrategies" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑全局参数对话框 -->
    <el-dialog v-model="globalParamsEditVisible" :title="globalParamsEditTitle" width="500px" destroy-on-close>
      <el-form label-width="120px">
        <el-form-item v-for="item in globalParamsEditForm" :key="item.key" :label="item.label">
          <el-input
            v-model="item.value"
            :type="isSecretKey(item.key) ? 'password' : 'text'"
            :show-password="isSecretKey(item.key)"
            :placeholder="getParamPlaceholder(item.key)"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="globalParamsEditVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveGlobalParams" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Edit, Delete, Connection } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '../../stores/app'
import {
  getProviders, createProvider, updateProvider, deleteProvider, testProvider,
  getStrategies, batchUpdateStrategies,
  getGlobalConfig, batchUpdateGlobalConfig,
  getCallLogs, getAIStats,
} from '../../api/aiConfig'

const appStore = useAppStore()
const saving = ref(false)
const providerLoading = ref(false)
const logLoading = ref(false)

// 统计
const stats = ref({
  configured_models: 0,
  monthly_calls: 0,
  total_input_tokens: 0,
  total_output_tokens: 0,
  avg_duration_ms: 0,
})

// 服务商
const providers = ref([])
const providerEditVisible = ref(false)
const isEditProvider = ref(false)
const editProviderId = ref(null)
const providerForm = reactive({
  provider_type: 'OpenAI',
  name: '',
  model: '',
  api_key: '',
  endpoint_url: '',
  max_tokens: 4096,
})

// 策略
const strategies = ref([])
const strategyEditVisible = ref(false)
const strategyEditForm = ref([])

// 全局参数
const globalParams = ref([])
const globalParamsEditVisible = ref(false)
const globalParamsEditForm = ref([])
const globalParamsEditGroup = ref('system')

// 按分组过滤参数
const systemParams = computed(() => globalParams.value.filter(p => (p.group || 'system') === 'system'))
const targetParams = computed(() => globalParams.value.filter(p => p.group === 'target'))
const globalParamsEditTitle = computed(() => globalParamsEditGroup.value === 'target' ? '编辑被测系统配置' : '编辑全局参数')

// 调用日志
const callLogs = ref([])
const logFilterProvider = ref('')
const logFilterStatus = ref('')

// API Key 编辑状态
const editProviderMaskedKey = ref('')  // 记住脱敏值，用于 blur 恢复
const apiKeyFocused = ref(false)
const apiKeyPlaceholder = computed(() => {
  if (!isEditProvider.value) return '请输入 API Key'
  return apiKeyFocused.value ? '输入新 Key 覆盖原值' : ''
})

function handleApiKeyFocus() {
  if (!isEditProvider.value) return
  apiKeyFocused.value = true
  // 聚焦时清空脱敏值，让用户输入新 Key
  providerForm.api_key = ''
}

function handleApiKeyBlur() {
  if (!isEditProvider.value) return
  apiKeyFocused.value = false
  // 如果用户没输入任何内容，恢复脱敏值
  if (!providerForm.api_key.trim()) {
    providerForm.api_key = editProviderMaskedKey.value
  }
}

// ============ 格式化工具 ============

function formatTokens(count) {
  if (!count) return '0'
  if (count >= 1000000) return (count / 1000000).toFixed(1) + 'M'
  if (count >= 1000) return (count / 1000).toFixed(1) + 'K'
  return String(count)
}

function formatDateTime(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function formatTimeAgo(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour} 小时前`
  const diffDay = Math.floor(diffHour / 24)
  return `${diffDay} 天前`
}

function logStatusType(status) {
  return { '成功': 'success', '失败': 'danger', '超时': 'warning' }[status] || 'info'
}

function getProviderBg(type) {
  const map = { 'OpenAI': '#10A37F1A', 'Anthropic': '#D4A5741A', 'DeepSeek': '#4D6BFE1A' }
  return map[type] || '#8B5CF61A'
}

function getProviderColor(type) {
  const map = { 'OpenAI': '#10A37F', 'Anthropic': '#D4A574', 'DeepSeek': '#4D6BFE' }
  return map[type] || '#8B5CF6'
}

function getProviderLetter(type) {
  const map = { 'OpenAI': 'O', 'Anthropic': 'A', 'DeepSeek': 'D' }
  return map[type] || 'C'
}

// ============ 数据加载 ============

async function loadStats() {
  try {
    const res = await getAIStats()
    stats.value = res.data || stats.value
  } catch (e) { console.error(e) }
}

async function loadProviders() {
  providerLoading.value = true
  try {
    const res = await getProviders()
    providers.value = (res.data || []).map(p => ({ ...p, testing: false }))
  } catch (e) { console.error(e) }
  finally { providerLoading.value = false }
}

async function loadStrategies() {
  try {
    const res = await getStrategies()
    strategies.value = res.data || []
  } catch (e) { console.error(e) }
}

async function loadGlobalParams() {
  try {
    const res = await getGlobalConfig()
    globalParams.value = res.data || []
  } catch (e) { console.error(e) }
}

async function loadCallLogs() {
  logLoading.value = true
  try {
    const params = {}
    if (logFilterProvider.value) params.provider_id = logFilterProvider.value
    if (logFilterStatus.value) params.status = logFilterStatus.value
    const res = await getCallLogs(params)
    callLogs.value = res.data || []
  } catch (e) { console.error(e) }
  finally { logLoading.value = false }
}

// ============ 服务商操作 ============

function handleAddProvider() {
  isEditProvider.value = false
  editProviderId.value = null
  Object.assign(providerForm, {
    provider_type: 'OpenAI', name: '', model: '', api_key: '',
    endpoint_url: '', max_tokens: 4096,
  })
  providerEditVisible.value = true
}

function handleEditProvider(row) {
  isEditProvider.value = true
  editProviderId.value = row.id
  editProviderMaskedKey.value = row.api_key_masked || ''
  apiKeyFocused.value = false
  Object.assign(providerForm, {
    provider_type: row.provider_type,
    name: row.name,
    model: row.model,
    api_key: row.api_key_masked,  // 显示脱敏值
    endpoint_url: row.endpoint_url || '',
    max_tokens: row.max_tokens ?? 4096,
  })
  providerEditVisible.value = true
}

async function handleSaveProvider() {
  if (!providerForm.name.trim() || !providerForm.model.trim()) {
    ElMessage.warning('请填写服务商名称和模型')
    return
  }
  if (!isEditProvider.value && !providerForm.api_key.trim()) {
    ElMessage.warning('请填写 API Key')
    return
  }
  saving.value = true
  try {
    if (isEditProvider.value) {
      const data = {
        provider_type: providerForm.provider_type,
        name: providerForm.name,
        model: providerForm.model,
        endpoint_url: providerForm.endpoint_url || null,
        max_tokens: providerForm.max_tokens,
      }
      // 只有用户输入了新 Key（与脱敏值不同）才提交
      if (providerForm.api_key.trim() && providerForm.api_key !== editProviderMaskedKey.value) {
        data.api_key = providerForm.api_key
      }
      await updateProvider(editProviderId.value, data)
    } else {
      await createProvider({
        provider_type: providerForm.provider_type,
        name: providerForm.name,
        model: providerForm.model,
        api_key: providerForm.api_key,
        endpoint_url: providerForm.endpoint_url || null,
        max_tokens: providerForm.max_tokens,
      })
    }
    ElMessage.success('保存成功')
    providerEditVisible.value = false
    await loadProviders()
    await loadStats()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally { saving.value = false }
}

async function handleTestProvider(row) {
  row.testing = true
  try {
    const res = await testProvider(row.id)
    const result = res.data || {}
    if (result.success) {
      ElMessage.success({
        message: `${row.name} 连接测试成功（模型: ${result.model || row.model}）`,
        duration: 3000,
      })
    } else {
      ElMessage.error({
        message: result.message || '连接测试失败',
        duration: 5000,
      })
    }
    await loadProviders()
    await loadCallLogs()
  } catch (e) {
    ElMessage.error('连接测试失败: ' + (e.message || '未知错误'))
  } finally { row.testing = false }
}

function handleDeleteProvider(row) {
  ElMessageBox.confirm(`确定要删除服务商"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    try {
      await deleteProvider(row.id)
      ElMessage.success('删除成功')
      await loadProviders()
      await loadStats()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// ============ 策略操作 ============

function openStrategyEdit() {
  strategyEditForm.value = strategies.value.map(s => ({
    task_type: s.task_type,
    model_name: s.model_name,
    provider_id: s.provider_id,
  }))
  strategyEditVisible.value = true
}

function onStrategyProviderChange(row, providerId) {
  const p = providers.value.find(item => item.id === providerId)
  if (p) {
    row.provider_id = p.id
    row.model_name = p.model
  }
}

async function handleSaveStrategies() {
  saving.value = true
  try {
    await batchUpdateStrategies(strategyEditForm.value)
    ElMessage.success('策略更新成功')
    strategyEditVisible.value = false
    await loadStrategies()
  } catch (e) {
    ElMessage.error('策略更新失败')
  } finally { saving.value = false }
}

// ============ 全局参数操作 ============

function openGlobalParamsEdit(group = 'system') {
  globalParamsEditGroup.value = group
  const source = group === 'target' ? targetParams.value : systemParams.value
  globalParamsEditForm.value = source.map(p => ({
    key: p.key,
    value: p.value,
    label: p.label || p.key,
  }))
  globalParamsEditVisible.value = true
}

function getParamPlaceholder(key) {
  const map = {
    target_url: '例如：https://demo.example.com',
    test_username: '测试账号',
    test_password: '测试密码',
    project_prefix: '例如：SPD（用于生成用例编号 SPD_TC_XX_001）',
    mineru_api_token: 'MinerU 文档解析 API Token',
  }
  return map[key] || ''
}

function isSecretKey(key) {
  return ['test_password', 'mineru_api_token'].includes(key)
}

async function handleSaveGlobalParams() {
  saving.value = true
  try {
    await batchUpdateGlobalConfig(globalParamsEditForm.value)
    ElMessage.success('全局参数更新成功')
    globalParamsEditVisible.value = false
    await loadGlobalParams()
  } catch (e) {
    ElMessage.error('全局参数更新失败')
  } finally { saving.value = false }
}

// ============ 初始化 ============

onMounted(async () => {
  appStore.setCurrentPage('ai-config', 'AI 配置')
  await Promise.all([
    loadStats(),
    loadProviders(),
    loadStrategies(),
    loadGlobalParams(),
    loadCallLogs(),
  ])
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
