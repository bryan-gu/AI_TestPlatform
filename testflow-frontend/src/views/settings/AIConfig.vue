<template>
  <div class="ai-config">
    <!-- LLM 模型配置 -->
    <div class="config-section card">
      <div class="card-head">
        <div class="card-title">
          <el-icon><ChatDotRound /></el-icon>
          LLM 模型配置
        </div>
      </div>
      <div class="card-body">
        <el-form :model="llmConfig" label-width="100px">
          <el-form-item label="模型提供商">
            <el-select v-model="llmConfig.provider" @change="handleProviderChange('llm')" style="width: 100%">
              <el-option label="OpenAI" value="openai" />
              <el-option label="Anthropic (Claude)" value="anthropic" />
              <el-option label="本地模型 (Ollama)" value="local" />
            </el-select>
          </el-form-item>

          <el-form-item label="使用模型">
            <el-select v-model="llmConfig.model" style="width: 100%">
              <el-option
                v-for="model in llmModels"
                :key="model.value"
                :label="model.label"
                :value="model.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="API Key">
            <div class="api-key-input">
              <el-input
                v-model="llmConfig.apiKey"
                :type="showLlmKey ? 'text' : 'password'"
                placeholder="请输入 API Key"
              >
                <template #append>
                  <el-button @click="showLlmKey = !showLlmKey">
                    <el-icon><View v-if="!showLlmKey" /><Hide v-else /></el-icon>
                  </el-button>
                </template>
              </el-input>
              <el-button @click="testConnection('llm')" :loading="testingLlm">
                测试连接
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="Base URL" v-if="llmConfig.provider === 'local'">
            <el-input
              v-model="llmConfig.baseUrl"
              placeholder="http://localhost:11434/v1"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- Embedding 模型配置 -->
    <div class="config-section card">
      <div class="card-head">
        <div class="card-title">
          <el-icon><Vector /></el-icon>
          Embedding 模型配置
        </div>
      </div>
      <div class="card-body">
        <el-form :model="embeddingConfig" label-width="100px">
          <el-form-item label="模型提供商">
            <el-select v-model="embeddingConfig.provider" @change="handleProviderChange('embedding')" style="width: 100%">
              <el-option label="OpenAI" value="openai" />
              <el-option label="HuggingFace" value="huggingface" />
              <el-option label="本地模型" value="local" />
            </el-select>
          </el-form-item>

          <el-form-item label="使用模型">
            <el-select v-model="embeddingConfig.model" style="width: 100%">
              <el-option
                v-for="model in embeddingModels"
                :key="model.value"
                :label="model.label"
                :value="model.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="API Key" v-if="embeddingConfig.provider !== 'local'">
            <div class="api-key-input">
              <el-input
                v-model="embeddingConfig.apiKey"
                :type="showEmbeddingKey ? 'text' : 'password'"
                placeholder="请输入 API Key"
              >
                <template #append>
                  <el-button @click="showEmbeddingKey = !showEmbeddingKey">
                    <el-icon><View v-if="!showEmbeddingKey" /><Hide v-else /></el-icon>
                  </el-button>
                </template>
              </el-input>
              <el-button @click="testConnection('embedding')" :loading="testingEmbedding">
                测试连接
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="向量维度">
            <el-input-number
              v-model="embeddingConfig.dimension"
              :min="128"
              :max="4096"
              :step="128"
              style="width: 200px"
            />
            <span class="form-tip">模型默认维度通常无需修改</span>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="save-section">
      <el-button type="primary" size="large" @click="handleSave" :loading="saving">
        <el-icon><Check /></el-icon>
        保存配置
      </el-button>
      <el-button size="large" @click="handleReset">
        <el-icon><RefreshRight /></el-icon>
        重置
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ChatDotRound, Vector, View, Hide, Check, RefreshRight
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 显示密码
const showLlmKey = ref(false)
const showEmbeddingKey = ref(false)

// 测试状态
const testingLlm = ref(false)
const testingEmbedding = ref(false)
const saving = ref(false)

// LLM 配置
const llmConfig = reactive({
  provider: 'openai',
  model: 'gpt-4o-mini',
  apiKey: '',
  baseUrl: ''
})

// Embedding 配置
const embeddingConfig = reactive({
  provider: 'openai',
  model: 'text-embedding-3-small',
  apiKey: '',
  dimension: 1536
})

// LLM 模型选项
const llmModels = computed(() => {
  const models = {
    openai: [
      { label: 'GPT-4o', value: 'gpt-4o' },
      { label: 'GPT-4o Mini', value: 'gpt-4o-mini' },
      { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
      { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' }
    ],
    anthropic: [
      { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' },
      { label: 'Claude 3 Opus', value: 'claude-3-opus-20240229' },
      { label: 'Claude 3 Haiku', value: 'claude-3-haiku-20240307' }
    ],
    local: [
      { label: 'Qwen2', value: 'qwen2' },
      { label: 'Llama3', value: 'llama3' },
      { label: 'ChatGLM', value: 'chatglm' },
      { label: '自定义模型', value: 'custom' }
    ]
  }
  return models[llmConfig.provider] || []
})

// Embedding 模型选项
const embeddingModels = computed(() => {
  const models = {
    openai: [
      { label: 'text-embedding-3-small', value: 'text-embedding-3-small' },
      { label: 'text-embedding-3-large', value: 'text-embedding-3-large' },
      { label: 'text-embedding-ada-002', value: 'text-embedding-ada-002' }
    ],
    huggingface: [
      { label: 'BGE-M3', value: 'BAAI/bge-m3' },
      { label: 'BGE-large-zh', value: 'BAAI/bge-large-zh-v1.5' },
      { label: 'M3E', value: 'moka-ai/m3e-base' }
    ],
    local: [
      { label: 'BGE-M3 (本地)', value: 'bge-m3-local' },
      { label: 'M3E (本地)', value: 'm3e-local' }
    ]
  }
  return models[embeddingConfig.provider] || []
})

// 提供商变更
function handleProviderChange(type) {
  if (type === 'llm') {
    llmConfig.model = llmModels.value[0]?.value || ''
    llmConfig.apiKey = ''
    llmConfig.baseUrl = ''
  } else {
    embeddingConfig.model = embeddingModels.value[0]?.value || ''
    embeddingConfig.apiKey = ''
    embeddingConfig.dimension = 1536
  }
}

// 测试连接
async function testConnection(type) {
  if (type === 'llm') {
    testingLlm.value = true
    try {
      // TODO: 调用API测试连接
      await new Promise(resolve => setTimeout(resolve, 1500))
      ElMessage.success('LLM 连接测试成功')
    } catch (error) {
      ElMessage.error('LLM 连接测试失败：' + error.message)
    } finally {
      testingLlm.value = false
    }
  } else {
    testingEmbedding.value = true
    try {
      // TODO: 调用API测试连接
      await new Promise(resolve => setTimeout(resolve, 1500))
      ElMessage.success('Embedding 连接测试成功')
    } catch (error) {
      ElMessage.error('Embedding 连接测试失败：' + error.message)
    } finally {
      testingEmbedding.value = false
    }
  }
}

// 保存配置
async function handleSave() {
  saving.value = true
  try {
    // 保存到 localStorage
    const config = {
      llm: { ...llmConfig },
      embedding: { ...embeddingConfig }
    }
    localStorage.setItem('ai_config', JSON.stringify(config))

    // TODO: 调用API保存到后端
    await new Promise(resolve => setTimeout(resolve, 500))

    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

// 重置配置
function handleReset() {
  Object.assign(llmConfig, {
    provider: 'openai',
    model: 'gpt-4o-mini',
    apiKey: '',
    baseUrl: ''
  })
  Object.assign(embeddingConfig, {
    provider: 'openai',
    model: 'text-embedding-3-small',
    apiKey: '',
    dimension: 1536
  })
  ElMessage.info('配置已重置')
}

// 加载配置
function loadConfig() {
  const saved = localStorage.getItem('ai_config')
  if (saved) {
    try {
      const config = JSON.parse(saved)
      Object.assign(llmConfig, config.llm)
      Object.assign(embeddingConfig, config.embedding)
    } catch (e) {
      console.error('加载配置失败:', e)
    }
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.ai-config {
  max-width: 800px;
}

.config-section {
  margin-bottom: 24px;
}

.card-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-head .card-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-body {
  padding: 20px;
}

.api-key-input {
  display: flex;
  gap: 8px;
  width: 100%;
}

.api-key-input .el-input {
  flex: 1;
}

.form-tip {
  margin-left: 12px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.save-section {
  display: flex;
  gap: 12px;
  padding: 20px 0;
}
</style>
