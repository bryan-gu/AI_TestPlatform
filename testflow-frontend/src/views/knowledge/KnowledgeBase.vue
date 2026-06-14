<template>
  <div class="knowledge-base">
    <!-- 项目上下文栏 -->
    <div class="project-context-bar">
      <div class="project-icon">
        <el-icon :size="16" style="color: var(--accent)"><Folder /></el-icon>
      </div>
      <div style="flex:1">
        <div style="display:flex;align-items:center;gap:8px">
          <el-select
            v-model="selectedProject"
            style="width:200px"
            size="small"
            @change="handleProjectChange"
          >
            <el-option
              v-for="p in projectOptions"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
          <span class="badge badge-blue" style="font-size:10px">{{ currentProjectStatus }}</span>
        </div>
        <div style="font-size:12px;color:var(--color-text-secondary);margin-top:2px">
          知识库按 Sprint 组织 · 每个 Sprint 是独立快照 · 共 {{ stats.sprintCount }} 个 Sprint、{{ stats.totalDocs }} 篇文档
        </div>
      </div>
      <div style="display:flex;gap:8px">
        <el-button size="small" @click="handleEnsureSprintAll" :loading="ensuringAll">
          <el-icon><CopyDocument /></el-icon>确保 sprint_all
        </el-button>
        <el-button type="primary" size="small" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>新建 Sprint
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="stat-card">
        <div class="stat-label">Sprint 数</div>
        <div class="stat-value">{{ stats.sprintCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-blue"></span>含 sprint_all</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">模块数</div>
        <div class="stat-value">{{ stats.moduleCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>全部已关联</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">文档总数</div>
        <div class="stat-value">{{ stats.totalDocs }}</div>
        <div class="stat-sub"><span class="stat-dot dot-amber"></span>项目级汇总</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">功能点</div>
        <div class="stat-value">{{ stats.featurePointCount }}</div>
        <div class="stat-sub"><span class="stat-dot dot-green"></span>AI 提取</div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-entries">
      <div class="quick-entry" @click="router.push('/knowledge-assets')">
        <el-icon :size="18" style="color:#16a34a"><Files /></el-icon>
        <div class="qe-text"><div class="qe-title">资产中心</div><div class="qe-sub">知识资产统一检索</div></div>
      </div>
      <div class="quick-entry" @click="router.push('/feature-matrix')">
        <el-icon :size="18" style="color:#8B5CF6"><Grid /></el-icon>
        <div class="qe-text"><div class="qe-title">功能点矩阵</div><div class="qe-sub">功能点与覆盖用例</div></div>
      </div>
      <div class="quick-entry" @click="router.push('/api-endpoints')">
        <el-icon :size="18" style="color:var(--accent)"><Connection /></el-icon>
        <div class="qe-text"><div class="qe-title">接口清单</div><div class="qe-sub">接口与用例关联</div></div>
      </div>
      <div class="quick-entry" @click="router.push('/coverage-analysis')">
        <el-icon :size="18" style="color:#EF9F27"><DataAnalysis /></el-icon>
        <div class="qe-text"><div class="qe-title">覆盖分析</div><div class="qe-sub">覆盖率统计</div></div>
      </div>
      <div class="quick-entry" @click="router.push('/graphs')">
        <el-icon :size="18" style="color:#378ADD"><Share /></el-icon>
        <div class="qe-text"><div class="qe-title">知识图谱</div><div class="qe-sub">关联可视化</div></div>
      </div>
      <div class="quick-entry" @click="router.push('/local-import')">
        <el-icon :size="18" style="color:#085041"><Upload /></el-icon>
        <div class="qe-text"><div class="qe-title">本地导入</div><div class="qe-sub">批量导入项目资料</div></div>
      </div>
    </div>

    <!-- Sprint 知识快照表格 -->
    <div class="card">
      <div class="card-head">
        <div class="card-title">Sprint 知识快照</div>
      </div>
      <el-table :data="sprints" style="width:100%" @row-click="goToDetail" v-loading="loading">
        <el-table-column label="Sprint" min-width="180">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;gap:6px">
              <el-icon :size="15" :style="{ color: row.isAll ? '#8B5CF6' : 'var(--accent)' }">
                <component :is="row.isAll ? 'CopyDocument' : 'Promotion'" />
              </el-icon>
              <strong>{{ row.name }}</strong>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getSprintStatusType(row.status)" size="small" effect="plain" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="moduleCount" label="模块数" width="80" />
        <el-table-column prop="docCount" label="文档数" width="80" />
        <el-table-column label="更新时间" width="120">
          <template #default="{ row }">{{ formatDate(row.updatedAt || row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="450" fixed="right">
          <template #default="{ row }">
            <div class="action-btns" @click.stop>
              <el-button v-if="row.isAll" type="primary" link size="small" @click="goToGraphList">
                <el-icon><Share /></el-icon>图谱
              </el-button>
              <template v-else>
                <el-button type="warning" link size="small" @click="handleMarkBaseline(row)">
                  设为基线
                </el-button>
                <el-button type="success" link size="small" @click="handleMarkSprintAll(row)">
                  设为最新汇总
                </el-button>
                <el-button type="primary" link size="small" @click="handlePrepareFromAll(row)">
                  准备增量底稿
                </el-button>
                <el-button type="primary" link size="small" @click="handleSyncToAll(row)">
                  同步到最新汇总
                </el-button>
                <el-button type="success" link size="small" @click="handleMergeToAll(row)">
                  合并确认变更
                </el-button>
                <el-button type="primary" link size="small" @click="handleEdit(row)">
                  <el-icon><Edit /></el-icon>编辑
                </el-button>
                <el-button type="danger" link size="small" @click="handleDelete(row)">
                  <el-icon><Delete /></el-icon>删除
                </el-button>
              </template>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建 Sprint 对话框 -->
    <el-dialog v-model="createVisible" title="新建 Sprint" width="520px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="createForm.name" placeholder="例如：Sprint 3" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑 Sprint 对话框 -->
    <el-dialog v-model="editVisible" title="编辑 Sprint" width="520px" destroy-on-close>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 准备增量底稿对话框（按模块） -->
    <el-dialog v-model="prepareVisible" title="准备增量底稿（按模块）" width="520px" destroy-on-close>
      <div style="font-size:13px;color:var(--color-text-secondary);margin-bottom:10px">
        从 sprint_all 克隆底稿到 <strong>{{ prepareRow?.name }}</strong>。勾选要克隆的模块，不勾选则克隆全部。
      </div>
      <el-checkbox-group v-model="prepareSelectedModules" v-loading="prepareLoading">
        <div style="display:flex;flex-direction:column;gap:8px">
          <el-checkbox v-for="m in prepareModuleOptions" :key="m.id" :label="m.id">
            {{ m.name }}<span v-if="m.code" style="color:var(--color-text-tertiary);font-size:12px;margin-left:6px">{{ m.code }}</span>
          </el-checkbox>
          <el-empty v-if="!prepareModuleOptions.length" description="项目暂无模块，将克隆全部" :image-size="60" />
        </div>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="prepareVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmPrepare" :loading="preparing">确认准备</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { Folder, Plus, Edit, Delete, Promotion, CopyDocument, Share, Files, Grid, Connection, DataAnalysis, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjects } from '../../api/project'
import { getSprints, getSprintStats, createSprint, updateSprint, deleteSprint, ensureSprintAll, markSprintAsBaseline, markSprintAsSprintAll, syncSprintToAll, prepareSprintFromAll, mergeSprintToAll, getModules } from '../../api/sprint'

const router = useRouter()
const appStore = useAppStore()
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)
const ensuringAll = ref(false)

// 准备增量底稿（按模块）
const prepareVisible = ref(false)
const prepareRow = ref(null)
const prepareModuleOptions = ref([])
const prepareSelectedModules = ref([])
const prepareLoading = ref(false)
const preparing = ref(false)

const selectedProject = ref(null)
const currentProjectStatus = ref('')
const projectOptions = ref([])

const stats = ref({
  sprintCount: 0,
  moduleCount: 0,
  totalDocs: 0,
  featurePointCount: 0,
})

const sprints = ref([])

const createVisible = ref(false)
const createForm = reactive({ name: '', description: '' })
const editVisible = ref(false)
const editId = ref(null)
const editForm = reactive({ name: '', description: '' })

function formatDate(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function getProjectStatusText(s) {
  // 后端已返回中文状态，直接使用
  return s || '进行中'
}

function getSprintStatusType(status) {
  const map = { '基线': 'info', '已完成': 'success', '进行中': '', '最新汇总': 'warning', '待启动': 'info' }
  return map[status] || 'info'
}

function normalizeSprint(row) {
  return {
    ...row,
    isAll: row.is_all ?? row.isAll ?? false,
    moduleCount: row.module_count ?? row.moduleCount ?? 0,
    docCount: row.doc_count ?? row.docCount ?? 0,
    updatedAt: row.updated_at ?? row.updatedAt,
  }
}

function formatSyncStats(data) {
  const features = data?.features || {}
  const apis = data?.api_endpoints || {}
  const cases = data?.testcases || {}
  const links = data?.trace_links || {}
  return `功能点：新增 ${features.created || 0}，更新 ${features.updated || 0}；接口：新增 ${apis.created || 0}，更新 ${apis.updated || 0}；用例：新增 ${cases.created || 0}，更新 ${cases.updated || 0}；关系：新增 ${links.created || 0}，更新 ${links.updated || 0}`
}

function formatPrepareStats(data) {
  const features = data?.features || {}
  const apis = data?.api_endpoints || {}
  const cases = data?.testcases || {}
  const coverages = data?.coverages || {}
  const apiLinks = data?.testcase_api_endpoints || {}
  const links = data?.trace_links || {}
  return `功能点：新增 ${features.created || 0}，跳过 ${features.skipped || 0}；接口：新增 ${apis.created || 0}，跳过 ${apis.skipped || 0}；用例：新增 ${cases.created || 0}，跳过 ${cases.skipped || 0}；覆盖：新增 ${coverages.created || 0}，更新 ${coverages.updated || 0}；接口用例：新增 ${apiLinks.created || 0}，更新 ${apiLinks.updated || 0}；追踪：新增 ${links.created || 0}，更新 ${links.updated || 0}`
}

function goToDetail(row) {
  if (row.isAll) {
    router.push('/graphs')
  } else {
    router.push(`/knowledge/${row.id}`)
  }
}

function goToGraphList() {
  router.push('/graphs')
}

function openCreateDialog() {
  Object.assign(createForm, { name: '', description: '' })
  createVisible.value = true
}

async function loadData() {
  if (!selectedProject.value) return
  loading.value = true
  try {
    const [sprintRes, statsRes] = await Promise.all([
      getSprints({ project_id: selectedProject.value }),
      getSprintStats(selectedProject.value),
    ])
    sprints.value = (sprintRes.data || []).map(normalizeSprint)
    stats.value = statsRes.data || { sprintCount: 0, moduleCount: 0, totalDocs: 0, featurePointCount: 0 }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleEnsureSprintAll() {
  if (!selectedProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  ElMessageBox.confirm('将为当前项目创建或修正唯一的 sprint_all 最新汇总基线，不会同步或复制实体数据。是否继续？', '确保 sprint_all', {
    confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    ensuringAll.value = true
    try {
      await ensureSprintAll(selectedProject.value)
      ElMessage.success('已确保 sprint_all')
      await loadData()
    } catch (e) {
      ElMessage.error('操作失败')
    } finally {
      ensuringAll.value = false
    }
  }).catch(() => {})
}

async function handleCreate() {
  if (!createForm.name.trim()) {
    ElMessage.warning('请输入 Sprint 名称')
    return
  }
  creating.value = true
  try {
    await createSprint({
      name: createForm.name,
      description: createForm.description,
      project_id: selectedProject.value,
    })
    ElMessage.success('创建成功')
    createVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

function handleEdit(row) {
  editId.value = row.id
  Object.assign(editForm, { name: row.name, description: row.description || '' })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    await updateSprint(editId.value, { name: editForm.name, description: editForm.description })
    ElMessage.success('保存成功')
    editVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除 Sprint"${row.name}"吗？关联的文档也将被删除。`, '确认删除', {
    confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteSprint(row.id)
      ElMessage.success('删除成功')
      await loadData()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

function handleMarkBaseline(row) {
  ElMessageBox.confirm(`确定将 Sprint"${row.name}" 标记为基线吗？该操作只修改 Sprint 状态，不会同步实体数据。`, '设为基线', {
    confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await markSprintAsBaseline(row.id)
      ElMessage.success('已标记为基线')
      await loadData()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

function handleMarkSprintAll(row) {
  ElMessageBox.confirm(`确定将 Sprint"${row.name}" 设为最新汇总基线吗？该操作会取消同项目其他 sprint_all 标记，但不会同步或复制实体数据。`, '设为最新汇总', {
    confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await markSprintAsSprintAll(row.id)
      ElMessage.success('已标记为最新汇总')
      await loadData()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

function handleSyncToAll(row) {
  ElMessageBox.confirm(`确定将 Sprint"${row.name}" 的结构化实体同步到 sprint_all 吗？该操作会新增或更新功能点、接口、用例和关系，不会清空 sprint_all，也不会删除 sprint_all 中已有接口/功能点/用例。`, '同步到最新汇总', {
    confirmButtonText: '确认同步', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      const res = await syncSprintToAll(row.id)
      ElMessage.success(formatSyncStats(res.data))
      await loadData()
    } catch (e) {
      ElMessage.error('同步失败')
    }
  }).catch(() => {})
}

async function handlePrepareFromAll(row) {
  prepareRow.value = row
  prepareSelectedModules.value = []
  prepareModuleOptions.value = []
  prepareVisible.value = true
  prepareLoading.value = true
  try {
    const res = await getModules({ project_id: row.project_id })
    prepareModuleOptions.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    prepareLoading.value = false
  }
}

async function confirmPrepare() {
  if (!prepareRow.value) return
  preparing.value = true
  try {
    const res = await prepareSprintFromAll(prepareRow.value.id, {
      update_existing: false,
      module_ids: prepareSelectedModules.value,
    })
    ElMessage.success(formatPrepareStats(res.data))
    prepareVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('准备失败')
  } finally {
    preparing.value = false
  }
}

function handleMergeToAll(row) {
  ElMessageBox.confirm(
    `确定将 Sprint"${row.name}" 中已确认/已解决的变更项合并到 sprint_all 最新汇总吗？只会应用状态为"已确认"或"已解决"的变更项（功能点和接口），成功应用后变更项将标记为"已应用"。`,
    '合并确认变更',
    { confirmButtonText: '确认合并', cancelButtonText: '取消', type: 'warning' },
  ).then(async () => {
    try {
      const res = await mergeSprintToAll(row.id, {
        statuses: ['confirmed', 'resolved'],
        target_types: ['feature', 'api'],
      })
      const data = res.data || {}
      const features = data.features || {}
      const apis = data.api_endpoints || {}
      ElMessage.success(
        `已应用 ${data.applied || 0} 个变更（功能点：新增 ${features.created || 0}、更新 ${features.updated || 0}；接口：新增 ${apis.created || 0}、更新 ${apis.updated || 0}）`,
      )
      await loadData()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '合并失败')
    }
  }).catch(() => {})
}

function handleProjectChange(id) {
  const proj = projectOptions.value.find(p => p.id === id)
  if (proj) currentProjectStatus.value = proj.status || '进行中'
  loadData()
}

// 监听搜索关键词
let loadTimer = null
watch(() => appStore.searchKeyword, (kw) => {
  if (loadTimer) clearTimeout(loadTimer)
  loadTimer = setTimeout(async () => {
    if (!selectedProject.value) return
    loading.value = true
    try {
      const res = await getSprints({ project_id: selectedProject.value, keyword: kw || undefined })
      sprints.value = (res.data || []).map(normalizeSprint)
    } catch (e) { console.error(e) } finally { loading.value = false }
  }, 300)
})

onMounted(async () => {
  appStore.setCurrentPage('knowledge', '知识库')
  try {
    const projRes = await getProjects()
    if (projRes.data?.length) {
      projectOptions.value = projRes.data.map(p => ({
        id: p.id, name: p.name, status: p.status || '进行中',
      }))
      selectedProject.value = projectOptions.value[0].id
      currentProjectStatus.value = projectOptions.value[0].status || '进行中'
      await loadData()
    }
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.knowledge-base { max-width: 1400px; }

.project-context-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-lg);
  margin-bottom: 16px;
}

.project-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.badge-blue {
  background: #E6F1FB;
  color: #378ADD;
}

.action-btns { display: flex; gap: 4px; }
.el-table { cursor: pointer; }

.quick-entries {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.quick-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 14px;
  background: var(--color-background-primary);
  border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.quick-entry:hover {
  border-color: var(--accent);
  box-shadow: var(--shadow-sm);
}

.qe-text { min-width: 0; }

.qe-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.qe-sub {
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-top: 1px;
}
</style>
