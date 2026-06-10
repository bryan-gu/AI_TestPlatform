<template>
  <div class="knowledge-detail">
    <!-- 面包屑 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item" @click="goToProject">
        <el-icon :size="13"><Folder /></el-icon>{{ sprint.projectName || '项目' }}
      </span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item" @click="goToKnowledge">Sprint 列表</span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item current">{{ sprint.name }}</span>
    </div>

    <!-- Sprint 信息卡片 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div style="display:flex;align-items:center;gap:8px">
          <el-icon :size="16" style="color:var(--accent)"><Promotion /></el-icon>
          <div>
            <div class="card-title">{{ sprint.name }}</div>
            <div style="font-size:11px;color:var(--color-text-tertiary);margin-top:2px">
              {{ sprint.projectName }} · {{ sprint.status }} · {{ sprint.moduleCount }} 个模块
            </div>
          </div>
        </div>
        <div style="display:flex;gap:10px">
          <el-tag :type="getSprintStatusType(sprint.status)" size="small" effect="plain" round>{{ sprint.status }}</el-tag>
        </div>
      </div>
      <div class="sprint-meta">
        <span>文档数：<strong>{{ documents.length }}</strong></span>
        <span>资产数：<strong>{{ assets.length }}</strong></span>
        <span>模块数：<strong>{{ sprint.moduleCount }}</strong></span>
        <span v-if="sprint.description" style="flex:1">描述：{{ sprint.description }}</span>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div class="card-title">文档列表</div>
        <div style="display:flex;gap:10px">
          <div class="card-action" @click="openUploadDialog">上传文档</div>
          <div class="card-action" @click="openModuleManager">管理模块标签</div>
        </div>
      </div>
      <el-table :data="documents" style="width:100%" @row-click="goToPreview" v-loading="loading" empty-text="暂无文档，点击「上传文档」添加">
        <el-table-column label="文档名称" min-width="240">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:8px">
              <el-icon :size="15" :style="{ color: getFileIconColor(row.file_type) }"><Document /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.file_type)" size="small" effect="plain" round>{{ row.file_type || '其他' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="模块标签" min-width="160">
          <template #default="{ row }">
            <div style="display:flex;gap:4px;flex-wrap:wrap">
              <el-tag v-for="m in row.module_names" :key="m" size="small" effect="plain" type="info">{{ m }}</el-tag>
              <span v-if="!row.module_names?.length" style="color:var(--color-text-tertiary);font-size:12px">待分析</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="解析状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getParseStatusType(row.parse_status)" size="small" effect="plain" round>{{ row.parse_status || '待解析' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="AI 状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getAiStatusType(row.ai_status)" size="small" effect="plain" round>{{ row.ai_status || '待分析' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploader_name" label="上传人" width="80" />
        <el-table-column label="上传时间" width="110">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns" @click.stop>
              <el-button type="primary" link size="small" @click="handleEditDoc(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button v-if="row.parse_status === '解析失败'" type="warning" link size="small" @click="handleReparseDoc(row)">
                <el-icon><Refresh /></el-icon>重新解析
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteDoc($index, row)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 上传文档对话框 -->
    <el-dialog v-model="uploadVisible" title="上传文档" width="500px" destroy-on-close>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        drag
      >
        <el-icon style="font-size:40px;color:var(--color-text-tertiary)"><Upload /></el-icon>
        <div style="margin-top:8px">拖拽文件到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div style="font-size:12px;color:var(--color-text-tertiary);margin-top:8px">
            支持 PDF、Word、Markdown、Excel 文件
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>

    <!-- 编辑文档对话框 -->
    <el-dialog v-model="editDocVisible" title="编辑文档" width="400px" destroy-on-close>
      <el-form :model="editDocForm" label-width="80px">
        <el-form-item label="文档名称"><el-input v-model="editDocForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDocVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDoc" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 资产列表 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div style="display:flex;align-items:center;gap:8px">
          <el-icon :size="16" style="color:#16a34a"><Collection /></el-icon>
          <div class="card-title">资产列表</div>
        </div>
        <div style="display:flex;gap:8px">
          <el-select v-model="assetTypeFilter" placeholder="全部类型" size="small" style="width:150px" clearable @change="loadAssets">
            <el-option v-for="item in assetTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>
      </div>
      <el-table :data="assets" style="width:100%" v-loading="assetLoading" empty-text="暂无资产，上传文档或运行 AI 流水线后自动生成">
        <el-table-column prop="name" label="资产名称" min-width="220" show-overflow-tooltip />
        <el-table-column label="资产类型" width="130">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :type="getAssetTagType(row.asset_type)">{{ getAssetTypeText(row.asset_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="90">
          <template #default="{ row }">{{ getAssetSourceText(row.source_kind) }}</template>
        </el-table-column>
        <el-table-column label="解析状态" width="90">
          <template #default="{ row }"><el-tag size="small" effect="plain" :type="getAssetParseType(row.parse_status)">{{ row.parse_status || 'pending' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="模块" width="120">
          <template #default="{ row }">{{ row.module_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="大小" width="90">
          <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column label="更新时间" width="120">
          <template #default="{ row }">{{ formatDate(row.updated_at || row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 功能点列表 -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-head">
        <div style="display:flex;align-items:center;gap:8px">
          <el-icon :size="16" style="color:#8B5CF6"><MagicStick /></el-icon>
          <div class="card-title">功能点</div>
          <span style="font-size:11px;color:var(--color-text-tertiary)">AI 从文档中提取</span>
        </div>
        <div class="card-action" @click="openCreateFpDialog">添加功能点</div>
      </div>
      <el-table :data="featurePoints" style="width:100%" v-loading="fpLoading" empty-text="暂无功能点，点击「添加功能点」手动添加">
        <el-table-column prop="name" label="功能点名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ row.description || '-' }}</template>
        </el-table-column>
        <el-table-column label="优先级" width="80">
          <template #default="{ row }"><span :class="getPriorityClass(row.priority)">{{ row.priority || '中' }}</span></template>
        </el-table-column>
        <el-table-column label="来源" width="90">
          <template #default="{ row }">{{ getSourceTypeText(row.source_type) }}</template>
        </el-table-column>
        <el-table-column label="来源文档" width="160">
          <template #default="{ row }">
            <span v-if="row.source_doc_name" style="color:var(--accent);cursor:pointer" @click="goToPreview({id: row.source_doc_id})">{{ row.source_doc_name }}</span>
            <span v-else style="color:var(--color-text-tertiary)">-</span>
          </template>
        </el-table-column>
        <el-table-column label="模块标签" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.module_name" size="small" effect="plain" type="info">{{ row.module_name }}</el-tag>
            <span v-else style="color:var(--color-text-tertiary)">-</span>
          </template>
        </el-table-column>
        <el-table-column label="覆盖用例" width="90">
          <template #default="{ row }">{{ row.coverage_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="110">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="{ row, $index }">
            <div class="action-btns">
              <el-button type="primary" link size="small" @click="openTraceDialog(row)">
                <el-icon><Connection /></el-icon>关系
              </el-button>
              <el-button type="primary" link size="small" @click="handleEditFp(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteFp($index, row)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建功能点对话框 -->
    <el-dialog v-model="createFpVisible" title="添加功能点" width="520px" destroy-on-close>
      <el-form :model="createFpForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="createFpForm.name" placeholder="请输入功能点名称" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="createFpForm.description" type="textarea" :rows="2" placeholder="请输入功能描述" /></el-form-item>
        <el-form-item label="操作入口"><el-input v-model="createFpForm.entry_path" placeholder="如 系统管理 → 用户管理" /></el-form-item>
        <el-form-item label="交互元素"><el-input v-model="createFpForm.interaction_elements" type="textarea" :rows="2" placeholder="表单字段、按钮、表格列等" /></el-form-item>
        <el-form-item label="业务规则"><el-input v-model="createFpForm.business_rules" type="textarea" :rows="2" placeholder="必填、长度、权限、状态流转等" /></el-form-item>
        <el-form-item label="来源文档">
          <el-select v-model="createFpForm.source_doc_id" style="width:100%" placeholder="选择文档（可选）" clearable>
            <el-option v-for="d in documents" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 16px">
          <el-form-item label="模块标签">
            <el-select v-model="createFpForm.module_id" style="width:100%" placeholder="选择模块" clearable>
              <el-option v-for="m in modules" :key="m.id" :label="m.name" :value="m.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="createFpForm.priority" style="width:100%">
              <el-option label="高" value="高" />
              <el-option label="中" value="中" />
              <el-option label="低" value="低" />
            </el-select>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="createFpVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateFp" :loading="fpSaving">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑功能点对话框 -->
    <el-dialog v-model="editFpVisible" title="编辑功能点" width="520px" destroy-on-close>
      <el-form :model="editFpForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="editFpForm.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="editFpForm.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="操作入口"><el-input v-model="editFpForm.entry_path" /></el-form-item>
        <el-form-item label="交互元素"><el-input v-model="editFpForm.interaction_elements" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="业务规则"><el-input v-model="editFpForm.business_rules" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="来源文档">
          <el-select v-model="editFpForm.source_doc_id" style="width:100%" placeholder="选择文档（可选）" clearable>
            <el-option v-for="d in documents" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 16px">
          <el-form-item label="模块标签">
            <el-select v-model="editFpForm.module_id" style="width:100%" placeholder="选择模块" clearable>
              <el-option v-for="m in modules" :key="m.id" :label="m.name" :value="m.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="editFpForm.priority" style="width:100%">
              <el-option label="高" value="高" />
              <el-option label="中" value="中" />
              <el-option label="低" value="低" />
            </el-select>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="editFpVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveFp" :loading="fpSaving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 关联关系对话框 -->
    <el-dialog v-model="traceVisible" :title="`${traceFeature?.name || '功能点'} - 关联关系`" width="760px" destroy-on-close>
      <div v-loading="traceLoading" class="trace-panel">
        <div class="trace-section">
          <div class="trace-title">一跳关系</div>
          <el-table :data="traceLinks" size="small" empty-text="暂无关联关系">
            <el-table-column label="方向" width="70">
              <template #default="{ row }">{{ row.source_type === 'feature' && row.source_id === traceFeature?.id ? '下游' : '上游' }}</template>
            </el-table-column>
            <el-table-column label="关系" width="90"><template #default="{ row }">{{ row.relation_label || getRelationText(row.relation_type) }}</template></el-table-column>
            <el-table-column label="来源" min-width="150"><template #default="{ row }">{{ formatEntity(row.source_type, row.source_name) }}</template></el-table-column>
            <el-table-column label="目标" min-width="150"><template #default="{ row }">{{ formatEntity(row.target_type, row.target_name) }}</template></el-table-column>
            <el-table-column label="置信度" width="80"><template #default="{ row }">{{ row.confidence || 0 }}%</template></el-table-column>
          </el-table>
        </div>
        <div class="trace-section">
          <div class="trace-title">影响范围</div>
          <div class="impact-groups" v-if="hasImpactData">
            <div v-for="group in impactGroups" :key="group.key" class="impact-group" v-show="group.items.length">
              <div class="impact-label">{{ group.label }} · {{ group.items.length }}</div>
              <div class="impact-tags">
                <el-tag v-for="item in group.items" :key="`${item.type}-${item.id}`" size="small" effect="plain">{{ item.name }}</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无影响数据" :image-size="72" />
        </div>
      </div>
    </el-dialog>

    <!-- 模块标签管理对话框 -->
    <el-dialog v-model="moduleManagerVisible" title="模块标签管理" width="560px" destroy-on-close>
      <div style="margin-bottom:12px;display:flex;gap:8px">
        <el-input v-model="newModuleName" placeholder="模块名称（中文）" style="flex:1" size="small" />
        <el-input v-model="newModuleCode" placeholder="英文缩写" style="width:120px" size="small" />
        <el-color-picker v-model="newModuleColor" size="small" />
        <el-button type="primary" size="small" @click="handleAddModule" :loading="saving">添加</el-button>
      </div>
      <el-table :data="modules" style="width:100%" size="small">
        <el-table-column label="模块名称" min-width="160">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px">
              <span :style="{ width: '10px', height: '10px', borderRadius: '50%', background: row.color || 'var(--accent)' }"></span>
              {{ row.name }}
              <span v-if="row.code" style="color:var(--color-text-tertiary);font-size:11px">({{ row.code }})</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="doc_count" label="关联文档" width="80" />
        <el-table-column label="操作" width="120">
          <template #default="{ row, $index }">
            <div class="action-btns">
              <el-button type="primary" link size="small" @click="handleEditModule(row)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDeleteModule($index, row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 编辑模块 -->
      <div v-if="editingModule" style="margin-top:12px;display:flex;gap:8px;align-items:center">
        <el-input v-model="editingModule.name" size="small" style="flex:1" placeholder="模块名称" />
        <el-input v-model="editingModule.code" size="small" style="width:120px" placeholder="英文缩写" />
        <el-color-picker v-model="editingModule.color" size="small" />
        <el-button type="primary" size="small" @click="handleSaveModule">保存</el-button>
        <el-button size="small" @click="editingModule = null">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Folder, Promotion, Document, Edit, Delete, Upload, MagicStick, Refresh, Collection, Connection } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getSprint, getSprintDocuments, uploadSprintDocument,
  updateSprintDocument, deleteSprintDocument, reparseSprintDocument,
  getModules, createModule, updateModule, deleteModule,
} from '../../api/sprint'
import {
  getFeaturePoints, createFeaturePoint, updateFeaturePoint, deleteFeaturePoint,
} from '../../api/featurePoint'
import { getKnowledgeAssets } from '../../api/knowledgeAsset'
import { getEntityTraceLinks, getEntityImpact } from '../../api/traceLink'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const fpLoading = ref(false)
const fpSaving = ref(false)
const assetLoading = ref(false)
const assetTypeFilter = ref('')
const traceVisible = ref(false)
const traceLoading = ref(false)
const traceFeature = ref(null)
const traceLinks = ref([])
const traceImpact = ref({})

// 解析状态轮询
let parsePollingTimer = null

function hasParsingDocs() {
  return documents.value.some(d => d.parse_status === '解析中')
}

function startParsePolling() {
  if (parsePollingTimer) return
  parsePollingTimer = setInterval(async () => {
    if (!hasParsingDocs()) {
      stopParsePolling()
      return
    }
    try {
      const docsRes = await getSprintDocuments(sprintId)
      documents.value = docsRes.data || []
    } catch (e) {
      console.error(e)
    }
  }, 5000)
}

function stopParsePolling() {
  if (parsePollingTimer) {
    clearInterval(parsePollingTimer)
    parsePollingTimer = null
  }
}

const sprintId = route.params.id

// Sprint 信息
const sprint = ref({
  id: sprintId,
  name: '',
  projectName: '',
  status: '',
  moduleCount: 0,
  description: '',
})

// 文档列表
const documents = ref([])

// 资产列表
const assets = ref([])
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

// 模块标签
const modules = ref([])
const moduleManagerVisible = ref(false)
const newModuleName = ref('')
const newModuleCode = ref('')
const newModuleColor = ref('#378ADD')
const editingModule = ref(null)

// 上传
const uploadVisible = ref(false)
const uploadRef = ref(null)
const selectedFile = ref(null)

// 编辑文档
const editDocVisible = ref(false)
const editDocId = ref(null)
const editDocForm = reactive({ name: '' })

// 功能点
const featurePoints = ref([])
const createFpVisible = ref(false)
const editFpVisible = ref(false)
const editFpId = ref(null)
const createFpForm = reactive({
  name: '',
  description: '',
  entry_path: '',
  interaction_elements: '',
  business_rules: '',
  priority: '中',
  source_doc_id: null,
  module_id: null,
  linked_cases: '',
  source_type: 'manual',
})
const editFpForm = reactive({
  name: '',
  description: '',
  entry_path: '',
  interaction_elements: '',
  business_rules: '',
  priority: '中',
  source_doc_id: null,
  module_id: null,
  linked_cases: '',
  source_type: 'manual',
})

const impactGroups = computed(() => [
  { key: 'testcases', label: '测试用例', items: traceImpact.value.testcases || [] },
  { key: 'assets', label: '知识资产', items: traceImpact.value.assets || [] },
  { key: 'features', label: '功能点', items: traceImpact.value.features || [] },
  { key: 'modules', label: '模块', items: traceImpact.value.modules || [] },
  { key: 'api_endpoints', label: '接口', items: traceImpact.value.api_endpoints || [] },
  { key: 'scripts', label: '脚本', items: traceImpact.value.scripts || [] },
  { key: 'changes', label: '变更', items: traceImpact.value.changes || [] },
])

const hasImpactData = computed(() => impactGroups.value.some(group => group.items.length > 0))

function formatDate(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function getSprintStatusType(status) {
  const map = { '基线': 'info', '已完成': 'success', '进行中': '', '最新汇总': 'warning', '待启动': 'info' }
  return map[status] || 'info'
}

function getTypeTagType(t) {
  return { 'PDF': '', 'Word': 'success', 'Markdown': 'warning', 'Excel': 'danger' }[t] || 'info'
}

function getAiStatusType(status) {
  return { '已分析': 'success', '分析中': 'warning' }[status] || 'info'
}

function getParseStatusType(status) {
  return { '已解析': 'success', '解析中': 'warning', '解析失败': 'danger' }[status] || 'info'
}

function getPriorityClass(p) {
  return { 高: 'badge badge-red', 中: 'badge badge-amber', 低: 'badge badge-blue' }[p] || 'badge badge-gray'
}

function getSourceTypeText(type) {
  return { requirement: '需求', ui_explore: 'UI探索', api_doc: '接口', manual: '手工', ai_generated: 'AI生成' }[type] || '手工'
}

function getAssetTypeText(type) {
  const item = assetTypeOptions.find(i => i.value === type)
  return item ? item.label : '其他'
}

function getAssetSourceText(source) {
  return { uploaded: '上传', ai_generated: 'AI生成', skill_generated: 'SKILL', imported: '导入', manual: '手工' }[source] || '上传'
}

function getAssetTagType(type) {
  return { requirement_doc: '', feature_spec: 'success', test_case_json: 'warning', test_case_excel: 'danger', api_doc_md: 'info', api_doc_openapi: 'info', test_script: 'warning', execution_report: 'success' }[type] || 'info'
}

function getAssetParseType(status) {
  return { pending: 'info', '待解析': 'info', '解析中': 'warning', '已解析': 'success', '解析失败': 'danger' }[status] || 'info'
}

function getRelationText(type) {
  return { contains: '包含', derived_from: '来源于', belongs_to: '属于', covers: '覆盖', generated_by: '生成自', depends_on: '依赖', verified_by: '验证于', tests_api: '测试接口', implements: '实现', changes: '变更', mentions: '提及' }[type] || type
}

function getEntityText(type) {
  return { asset: '资产', document: '文档', module: '模块', feature: '功能点', testcase: '用例', api: '接口', script: '脚本', selector: '选择器', execution: '执行', change: '变更' }[type] || type
}

function formatEntity(type, name) {
  return `${getEntityText(type)}：${name || '-'}`
}

function formatFileSize(size) {
  if (!size) return '-'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

function getFileIconColor(type) {
  return { 'PDF': '#E24B4A', 'Word': '#16a34a', 'Markdown': '#8B5CF6', 'Excel': '#EF9F27' }[type] || 'var(--accent)'
}

function goToProject() { router.push('/projects') }
function goToKnowledge() { router.push('/knowledge') }
function goToPreview(row) { router.push(`/knowledge/doc/${row.id}`) }

async function loadData() {
  loading.value = true
  try {
    const [sprintRes, docsRes] = await Promise.all([
      getSprint(sprintId),
      getSprintDocuments(sprintId),
    ])
    if (sprintRes.data) {
      sprint.value = {
        id: sprintRes.data.id,
        name: sprintRes.data.name,
        projectName: sprintRes.data.project_name || '',
        status: sprintRes.data.status,
        moduleCount: sprintRes.data.module_count || 0,
        description: sprintRes.data.description || '',
      }
    }
    documents.value = docsRes.data || []
    await loadAssets()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// ========== 资产操作 ==========

async function loadAssets() {
  assetLoading.value = true
  try {
    const params = { sprint_id: sprintId }
    if (assetTypeFilter.value) params.asset_type = assetTypeFilter.value
    const res = await getKnowledgeAssets(params)
    assets.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    assetLoading.value = false
  }
}

// ========== 文档操作 ==========

function openUploadDialog() {
  selectedFile.value = null
  uploadVisible.value = true
}

function handleFileChange(file) {
  selectedFile.value = file
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value.raw)
    await uploadSprintDocument(sprintId, formData)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    await loadData()
    startParsePolling()
  } catch (e) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

function handleEditDoc(row) {
  editDocId.value = row.id
  editDocForm.name = row.name
  editDocVisible.value = true
}

async function handleSaveDoc() {
  saving.value = true
  try {
    await updateSprintDocument(sprintId, editDocId.value, { name: editDocForm.name })
    ElMessage.success('保存成功')
    editDocVisible.value = false
    await loadData()
    await loadAssets()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleReparseDoc(row) {
  try {
    await reparseSprintDocument(sprintId, row.id)
    ElMessage.success('已触发重新解析')
    await loadData()
    startParsePolling()
  } catch (e) {
    ElMessage.error('重新解析失败')
  }
}

function handleDeleteDoc(index, row) {
  ElMessageBox.confirm(`确定要删除文档"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteSprintDocument(sprintId, row.id)
      ElMessage.success('删除成功')
      await loadData()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// ========== 功能点操作 ==========

async function loadFeaturePoints() {
  fpLoading.value = true
  try {
    const res = await getFeaturePoints({ sprint_id: sprintId })
    featurePoints.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    fpLoading.value = false
  }
}

async function openTraceDialog(row) {
  traceFeature.value = row
  traceLinks.value = []
  traceImpact.value = {}
  traceVisible.value = true
  traceLoading.value = true
  try {
    const [linksRes, impactRes] = await Promise.all([
      getEntityTraceLinks('feature', row.id),
      getEntityImpact('feature', row.id),
    ])
    traceLinks.value = linksRes.data || []
    traceImpact.value = impactRes.data || {}
  } catch (e) {
    ElMessage.error('加载关联关系失败')
  } finally {
    traceLoading.value = false
  }
}

function openCreateFpDialog() {
  Object.assign(createFpForm, {
    name: '',
    description: '',
    entry_path: '',
    interaction_elements: '',
    business_rules: '',
    priority: '中',
    source_doc_id: null,
    module_id: null,
    linked_cases: '',
    source_type: 'manual',
  })
  createFpVisible.value = true
}

async function handleCreateFp() {
  if (!createFpForm.name.trim()) {
    ElMessage.warning('请输入功能点名称')
    return
  }
  fpSaving.value = true
  try {
    await createFeaturePoint({
      ...createFpForm,
      sprint_id: parseInt(sprintId),
    })
    ElMessage.success('创建成功')
    createFpVisible.value = false
    await loadFeaturePoints()
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    fpSaving.value = false
  }
}

function handleEditFp(row) {
  editFpId.value = row.id
  Object.assign(editFpForm, {
    name: row.name,
    description: row.description || '',
    entry_path: row.entry_path || '',
    interaction_elements: row.interaction_elements || '',
    business_rules: row.business_rules || '',
    priority: row.priority || '中',
    source_doc_id: row.source_doc_id,
    module_id: row.module_id,
    linked_cases: row.linked_cases || '',
    source_type: row.source_type || 'manual',
  })
  editFpVisible.value = true
}

async function handleSaveFp() {
  fpSaving.value = true
  try {
    await updateFeaturePoint(editFpId.value, { ...editFpForm })
    ElMessage.success('保存成功')
    editFpVisible.value = false
    await loadFeaturePoints()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    fpSaving.value = false
  }
}

function handleDeleteFp(index, row) {
  ElMessageBox.confirm(`确定要删除功能点"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteFeaturePoint(row.id)
      ElMessage.success('删除成功')
      await loadFeaturePoints()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// ========== 模块标签管理 ==========

async function openModuleManager() {
  moduleManagerVisible.value = true
  editingModule.value = null
  await loadModules()
}

async function loadModules() {
  try {
    const res = await getModules({ project_id: sprint.value.projectId })
    modules.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

async function handleAddModule() {
  if (!newModuleName.value.trim()) {
    ElMessage.warning('请输入模块名称')
    return
  }
  saving.value = true
  try {
    await createModule({
      name: newModuleName.value,
      code: newModuleCode.value.trim().toUpperCase(),
      project_id: null, // TODO: 传入实际 project_id
      color: newModuleColor.value,
    })
    ElMessage.success('添加成功')
    newModuleName.value = ''
    newModuleCode.value = ''
    newModuleColor.value = '#378ADD'
    await loadModules()
  } catch (e) {
    ElMessage.error('添加失败')
  } finally {
    saving.value = false
  }
}

function handleEditModule(row) {
  editingModule.value = { ...row }
}

async function handleSaveModule() {
  if (!editingModule.value) return
  saving.value = true
  try {
    await updateModule(editingModule.value.id, {
      name: editingModule.value.name,
      code: editingModule.value.code ? editingModule.value.code.trim().toUpperCase() : '',
      color: editingModule.value.color,
    })
    ElMessage.success('保存成功')
    editingModule.value = null
    await loadModules()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function handleDeleteModule(index, row) {
  ElMessageBox.confirm(`确定要删除模块标签"${row.name}"吗？`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteModule(row.id)
      ElMessage.success('删除成功')
      await loadModules()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(async () => {
  appStore.setCurrentPage('knowledge', '文档列表', '上传文档', openUploadDialog)
  await loadData()
  if (hasParsingDocs()) startParsePolling()
  loadFeaturePoints()
})

onBeforeUnmount(() => {
  stopParsePolling()
})
</script>

<style scoped>
.knowledge-detail { max-width: 1400px; }

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 16px;
  font-size: 13px;
}

.breadcrumb-item {
  color: var(--accent);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.breadcrumb-item:hover { text-decoration: underline; }
.breadcrumb-item.current { color: var(--color-text-primary); cursor: default; font-weight: 500; }
.breadcrumb-item.current:hover { text-decoration: none; }

.breadcrumb-sep {
  margin: 0 8px;
  color: var(--color-text-tertiary);
}

.sprint-meta {
  padding: 14px 18px;
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.card-action {
  font-size: 12px;
  color: var(--accent);
  cursor: pointer;
  font-weight: 500;
}

.card-action:hover { text-decoration: underline; }

.action-btns { display: flex; gap: 4px; flex-wrap: wrap; }

.trace-panel {
  min-height: 220px;
}

.trace-section + .trace-section {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 0.5px solid var(--color-border-tertiary);
}

.trace-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 10px;
}

.impact-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.impact-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.impact-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.el-table { cursor: pointer; }
</style>
