<template>
  <div class="asset-center">
    <div class="card">
      <div class="card-head">
        <div class="card-title">资产中心</div>
        <div class="filter-bar">
          <el-select v-model="filter.project_id" placeholder="项目" size="small" style="width:150px" clearable filterable @change="onProjectChange">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-select v-model="filter.sprint_id" placeholder="Sprint" size="small" style="width:150px" clearable filterable @change="loadAssets">
            <el-option v-for="s in sprints" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
          <el-select v-model="filter.asset_type" placeholder="资产类型" size="small" style="width:140px" clearable @change="loadAssets">
            <el-option v-for="t in assetTypeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
          <el-select v-model="filter.status" placeholder="状态" size="small" style="width:110px" clearable @change="loadAssets">
            <el-option label="有效" value="active" />
            <el-option label="已删除" value="deleted" />
          </el-select>
          <el-input v-model="filter.keyword" placeholder="搜索名称" size="small" style="width:170px" clearable @change="loadAssets">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
      </div>

      <el-table :data="assets" style="width:100%" v-loading="loading" empty-text="暂无资产" @row-click="openDetail">
        <el-table-column prop="name" label="资产名称" min-width="220" show-overflow-tooltip />
        <el-table-column label="类型" width="130">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :type="getAssetTagType(row.asset_type)">{{ getAssetTypeText(row.asset_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="90">
          <template #default="{ row }">{{ getSourceText(row.source_kind) }}</template>
        </el-table-column>
        <el-table-column prop="sprint_name" label="Sprint" width="130" show-overflow-tooltip />
        <el-table-column prop="module_name" label="模块" width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ row.module_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="解析状态" width="90">
          <template #default="{ row }"><el-tag size="small" effect="plain" :type="getParseType(row.parse_status)">{{ row.parse_status || 'pending' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="大小" width="80">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="action-btns" v-if="row.asset_type === 'api_doc_openapi' || row.asset_type === 'api_doc_md'">
              <el-button type="primary" link size="small" @click.stop="handleParseApi(row)" :loading="parsingId === row.id">
                <el-icon><Connection /></el-icon>解析接口
              </el-button>
            </div>
            <span v-else style="color:var(--color-text-tertiary);font-size:12px">-</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 资产详情抽屉 -->
    <el-drawer v-model="detailVisible" title="资产详情" size="420px">
      <div v-if="current" class="detail-panel">
        <div class="detail-name">{{ current.name }}</div>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="资产类型">{{ getAssetTypeText(current.asset_type) }}</el-descriptions-item>
          <el-descriptions-item label="来源">{{ getSourceText(current.source_kind) }}</el-descriptions-item>
          <el-descriptions-item label="项目">{{ current.project_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Sprint">{{ current.sprint_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="模块">{{ current.module_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="文档">{{ current.document_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">{{ current.file_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatSize(current.file_size) }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ current.status }}</el-descriptions-item>
          <el-descriptions-item label="解析状态">{{ current.parse_status }}</el-descriptions-item>
          <el-descriptions-item label="内容哈希">{{ current.content_hash ? current.content_hash.slice(0, 16) + '…' : '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Connection } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getKnowledgeAssets } from '../../api/knowledgeAsset'
import { getProjects } from '../../api/project'
import { getSprints } from '../../api/sprint'
import { importOpenApi, importMarkdownApi } from '../../api/apiEndpoint'

const loading = ref(false)
const assets = ref([])
const projects = ref([])
const sprints = ref([])
const parsingId = ref(null)
const detailVisible = ref(false)
const current = ref(null)

const filter = reactive({
  project_id: null,
  sprint_id: null,
  asset_type: '',
  status: 'active',
  keyword: '',
})

const assetTypeOptions = [
  { label: '需求文档', value: 'requirement_doc' },
  { label: '功能点规格', value: 'feature_spec' },
  { label: '用例 JSON', value: 'test_case_json' },
  { label: '用例 Excel', value: 'test_case_excel' },
  { label: '接口文档', value: 'api_doc_md' },
  { label: 'OpenAPI', value: 'api_doc_openapi' },
  { label: '自动化脚本', value: 'test_script' },
  { label: '执行报告', value: 'execution_report' },
  { label: '其他', value: 'other' },
]

function getAssetTypeText(t) {
  return assetTypeOptions.find(i => i.value === t)?.label || '其他'
}
function getSourceText(s) {
  return { uploaded: '上传', ai_generated: 'AI生成', skill_generated: 'SKILL', imported: '导入', manual: '手工' }[s] || '上传'
}
function getAssetTagType(t) {
  return { requirement_doc: '', feature_spec: 'success', test_case_json: 'warning', test_case_excel: 'danger', api_doc_md: 'info', api_doc_openapi: 'info', test_script: 'warning' }[t] || 'info'
}
function getParseType(s) {
  return { pending: 'info', '待解析': 'info', '解析中': 'warning', '已解析': 'success', '解析失败': 'danger' }[s] || 'info'
}
function formatSize(size) {
  if (!size) return '-'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

async function loadProjects() {
  const res = await getProjects()
  projects.value = res.data || []
}

async function onProjectChange() {
  filter.sprint_id = null
  if (filter.project_id) {
    const res = await getSprints({ project_id: filter.project_id })
    sprints.value = res.data || []
  } else {
    sprints.value = []
  }
  await loadAssets()
}

async function loadAssets() {
  loading.value = true
  try {
    const params = {}
    if (filter.project_id) params.project_id = filter.project_id
    if (filter.sprint_id) params.sprint_id = filter.sprint_id
    if (filter.asset_type) params.asset_type = filter.asset_type
    if (filter.status) params.status = filter.status
    if (filter.keyword) params.keyword = filter.keyword
    const res = await getKnowledgeAssets(params)
    assets.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openDetail(row) {
  current.value = row
  detailVisible.value = true
}

async function handleParseApi(row) {
  parsingId.value = row.id
  try {
    const fn = row.asset_type === 'api_doc_openapi' ? importOpenApi : importMarkdownApi
    const res = await fn({ asset_id: row.id })
    const r = res.data || {}
    if (r.total === 0) {
      ElMessage.warning('未解析出接口')
    } else {
      ElMessage.success(`解析完成：共 ${r.total} 个，新建 ${r.created || 0}，更新 ${r.updated || 0}`)
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '解析失败')
  } finally {
    parsingId.value = null
  }
}

onMounted(async () => {
  await loadProjects()
  await loadAssets()
})
</script>

<style scoped>
.asset-center { max-width: 1400px; }

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.filter-bar {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.action-btns { display: flex; gap: 4px; }

.detail-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 14px;
  word-break: break-all;
}

.el-table { cursor: pointer; }
</style>
