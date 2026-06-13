<template>
  <div class="local-import">
    <div class="card">
      <div class="card-head">
        <div class="card-title">本地项目资料导入</div>
      </div>

      <div class="import-form">
        <div class="form-row">
          <label>项目</label>
          <el-select v-model="form.project_id" placeholder="选择目标项目" style="width:260px" filterable>
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
        <div class="form-row">
          <label>本地目录</label>
          <el-input v-model="form.root_path" placeholder="服务器可访问的绝对路径，如 /data/projects/xxx" style="width:520px" />
        </div>
        <div class="form-row">
          <label>预览模式</label>
          <el-switch v-model="form.dry_run" active-text="仅扫描（dry_run）" inactive-text="直接正式导入" />
        </div>
        <div class="form-actions">
          <el-button type="primary" :loading="running" @click="handleRun">
            <el-icon><Search /></el-icon>{{ form.dry_run ? '扫描预览' : '开始导入' }}
          </el-button>
        </div>
        <div class="tip">
          约定目录结构：需求文档/sprintN/、测试用例/sprintN/、接口文档/。未归属 sprintN 的资料归入 sprint_all。
        </div>
      </div>
    </div>

    <!-- 扫描/导入结果 -->
    <div class="card" v-if="result">
      <div class="card-head">
        <div class="card-title">{{ result.dry_run ? '扫描结果（dry_run）' : '导入结果' }}</div>
      </div>

      <div class="result-summary">
        <div class="summary-item"><span class="sl">扫描文件</span><strong>{{ (result.assets || []).length }}</strong></div>
        <div class="summary-item" v-for="(v, k) in result.counts" :key="k">
          <span class="sl">{{ assetTypeText(k) }}</span><strong>{{ v }}</strong>
        </div>
        <template v-if="!result.dry_run && result.imported">
          <div class="summary-item"><span class="sl">导入文档</span><strong>{{ result.imported.documents || 0 }}</strong></div>
          <div class="summary-item"><span class="sl">导入资产</span><strong>{{ result.imported.assets || 0 }}</strong></div>
          <div class="summary-item"><span class="sl">导入用例</span><strong>{{ result.imported.testcases || 0 }}</strong></div>
          <div class="summary-item"><span class="sl">导入接口</span><strong>{{ result.imported.api_endpoints || 0 }}</strong></div>
        </template>
      </div>

      <div v-if="(result.sprints || []).length" class="sub-title">识别 Sprint</div>
      <div class="sprint-tags" v-if="(result.sprints || []).length">
        <el-tag v-for="s in result.sprints" :key="s.name" size="small" effect="plain">{{ s.name }} · {{ s.asset_count }}</el-tag>
      </div>

      <div class="sub-title">资产清单</div>
      <el-table :data="result.assets || []" size="small" style="width:100%" empty-text="未识别到资产">
        <el-table-column prop="rel_path" label="相对路径" min-width="260" show-overflow-tooltip />
        <el-table-column label="类型" width="130">
          <template #default="{ row }">{{ assetTypeText(row.asset_type) }}</template>
        </el-table-column>
        <el-table-column prop="sprint_name" label="归属 Sprint" width="130" />
        <el-table-column prop="file_type" label="文件类型" width="100" />
        <el-table-column label="大小" width="80">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
      </el-table>

      <div class="sub-title" v-if="(result.warnings || []).length">告警 ({{ (result.warnings || []).length }})</div>
      <div class="warnings" v-if="(result.warnings || []).length">
        <div v-for="(w, i) in result.warnings" :key="i" class="warning-item">• {{ w }}</div>
      </div>

      <div class="confirm-actions" v-if="result.dry_run && (result.assets || []).length">
        <el-button type="primary" :loading="running" @click="handleConfirmImport">确认正式导入</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { importLocalProject } from '../../api/knowledgeAsset'
import { getProjects } from '../../api/project'

const projects = ref([])
const running = ref(false)
const result = ref(null)

const form = reactive({
  project_id: null,
  root_path: '',
  dry_run: true,
})

const ASSET_TYPE_TEXT = {
  requirement_doc: '需求文档', feature_spec: '功能点规格', test_case_json: '用例 JSON',
  test_case_excel: '用例 Excel', api_doc_md: '接口文档', api_doc_openapi: 'OpenAPI',
  test_script: '脚本', selector_map: '选择器', execution_report: '执行报告', other: '其他',
}
function assetTypeText(t) { return ASSET_TYPE_TEXT[t] || t }
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

async function handleRun() {
  if (!form.project_id) { ElMessage.warning('请选择目标项目'); return }
  if (!form.root_path.trim()) { ElMessage.warning('请输入本地目录路径'); return }
  running.value = true
  try {
    const res = await importLocalProject({
      project_id: form.project_id,
      root_path: form.root_path.trim(),
      dry_run: form.dry_run,
    })
    result.value = res.data || null
    ElMessage.success(res.message || (form.dry_run ? '扫描完成' : '导入完成'))
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    running.value = false
  }
}

async function handleConfirmImport() {
  form.dry_run = false
  await handleRun()
  form.dry_run = true
}

onMounted(async () => {
  await loadProjects()
})
</script>

<style scoped>
.local-import { max-width: 1100px; }

.card { margin-bottom: 16px; }

.card-head {
  padding: 16px 18px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.import-form {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-row label {
  width: 70px;
  font-size: 13px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.form-actions {
  margin-top: 4px;
}

.tip {
  font-size: 12px;
  color: var(--color-text-tertiary);
  background: var(--color-background-secondary);
  border-radius: var(--border-radius-md);
  padding: 10px 12px;
  line-height: 1.6;
}

.result-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  padding: 16px 18px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-item .sl {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.summary-item strong {
  font-size: 18px;
  color: var(--color-text-primary);
}

.sub-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  padding: 0 18px 8px;
}

.sprint-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 0 18px 14px;
}

.sub-title + .el-table {
  margin: 0 18px 14px;
  width: calc(100% - 36px) !important;
}

.warnings {
  padding: 0 18px 14px;
  max-height: 160px;
  overflow-y: auto;
}

.warning-item {
  font-size: 12px;
  color: #B45309;
  line-height: 1.7;
}

.confirm-actions {
  padding: 0 18px 18px;
}
</style>
