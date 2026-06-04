<template>
  <div class="document-preview">
    <!-- 面包屑（3 层：项目 / Sprint / 文档预览） -->
    <div class="breadcrumb">
      <span class="breadcrumb-item" @click="goToKnowledge">
        <el-icon :size="13"><Folder /></el-icon>Sprint 列表
      </span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item" @click="goToSprint">{{ doc.sprintName || 'Sprint' }}</span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item current">文档预览</span>
    </div>

    <!-- 文档信息卡片 -->
    <div class="card" style="margin-bottom:16px">
      <div class="doc-info-bar">
        <div style="display:flex;align-items:center;gap:14px">
          <div class="doc-icon" :style="{ background: getFileIconBg(doc.file_type) }">
            <el-icon :size="22" :style="{ color: getFileIconColor(doc.file_type) }"><Document /></el-icon>
          </div>
          <div>
            <div class="doc-title">{{ doc.name }}</div>
            <div class="doc-details">
              <span><el-icon :size="13"><User /></el-icon> 上传人：<strong>{{ doc.uploader_name || '--' }}</strong></span>
              <span><el-icon :size="13"><Calendar /></el-icon> 上传时间：<strong>{{ formatDate(doc.created_at) }}</strong></span>
              <span><el-icon :size="13"><Document /></el-icon> 类型：<strong>{{ doc.file_type || '--' }}</strong></span>
              <span><el-icon :size="13"><Coin /></el-icon> 大小：<strong>{{ formatSize(doc.file_size) }}</strong></span>
            </div>
          </div>
        </div>
        <div class="doc-actions">
          <el-button size="small" @click="handleDownload">
            <el-icon><Download /></el-icon>下载
          </el-button>
          <el-button size="small" @click="handleShare">
            <el-icon><Share /></el-icon>分享
          </el-button>
        </div>
      </div>
    </div>

    <!-- 文档标签 -->
    <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap">
      <el-tag v-if="doc.file_type" :type="getTypeTagType(doc.file_type)" size="small" effect="plain">{{ doc.file_type }}</el-tag>
      <el-tag v-if="doc.version" size="small" effect="plain">{{ doc.version }}</el-tag>
      <el-tag v-for="m in doc.module_names" :key="m" type="info" size="small" effect="plain">{{ m }}</el-tag>
      <el-tag :type="getAiStatusType(doc.ai_status)" size="small" effect="plain" round>{{ doc.ai_status || '待分析' }}</el-tag>
    </div>

    <!-- 左右分栏 -->
    <div class="preview-layout">
      <!-- 左侧：文档预览 -->
      <div class="card preview-main">
        <div class="preview-toolbar">
          <div style="display:flex;align-items:center;gap:8px">
            <el-icon style="color:var(--accent);font-size:15px"><View /></el-icon>
            <span style="font-size:13px;font-weight:600">文档预览</span>
          </div>
          <div style="display:flex;gap:4px">
            <el-button :icon="ZoomIn" size="small" circle @click="zoomIn" title="放大" />
            <el-button :icon="ZoomOut" size="small" circle @click="zoomOut" title="缩小" />
            <el-button :icon="FullScreen" size="small" circle @click="fitPage" title="适配页面" />
          </div>
        </div>
        <div class="content-body" :style="{ fontSize: zoomLevel + 'px' }">
          <div v-if="doc.content_preview" v-html="doc.content_preview"></div>
          <div v-else class="empty-preview">
            <el-icon style="font-size:48px;color:var(--color-text-tertiary)"><Document /></el-icon>
            <div style="margin-top:12px;color:var(--color-text-tertiary)">暂无文档预览内容</div>
            <div style="font-size:12px;color:var(--color-text-tertiary);margin-top:4px">支持 Markdown 格式的文档预览</div>
          </div>
        </div>
      </div>

      <!-- 右侧：信息面板 -->
      <div class="side-panel">
        <!-- 版本信息 -->
        <div class="card">
          <div class="card-head">
            <div class="card-title" style="font-size:13px">
              <el-icon style="margin-right:6px;font-size:14px;color:var(--accent)"><Clock /></el-icon>版本信息
            </div>
          </div>
          <div style="padding:12px 16px;font-size:12px">
            <div style="display:flex;align-items:center;gap:8px">
              <span class="version-dot" style="background:var(--accent)"></span>
              <div>
                <div style="font-weight:500">{{ doc.version || 'v1.0' }}</div>
                <div style="color:var(--color-text-tertiary);margin-top:2px">{{ doc.uploader_name || '--' }} · {{ formatDate(doc.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 关联信息 -->
        <div class="card">
          <div class="card-head">
            <div class="card-title" style="font-size:13px">
              <el-icon style="margin-right:6px;font-size:14px;color:var(--accent)"><Link /></el-icon>关联信息
            </div>
          </div>
          <div class="related-list">
            <div class="related-item">
              <div class="related-label">所属 Sprint</div>
              <div class="related-link" @click="goToSprint">
                <el-icon :size="13"><Promotion /></el-icon>{{ doc.sprintName || 'Sprint' }}
              </div>
            </div>
            <div class="related-item">
              <div class="related-label">模块标签</div>
              <div style="display:flex;gap:4px;flex-wrap:wrap">
                <el-tag v-for="m in doc.module_names" :key="m" size="small" type="info" effect="plain">{{ m }}</el-tag>
                <span v-if="!doc.module_names?.length" style="font-size:12px;color:var(--color-text-tertiary)">无</span>
              </div>
            </div>
            <div class="related-item">
              <div class="related-label">关键词</div>
              <div style="display:flex;gap:4px;flex-wrap:wrap">
                <el-tag v-for="kw in (doc.keywords || [])" :key="kw" size="small" effect="plain">{{ kw }}</el-tag>
                <span v-if="!doc.keywords?.length" style="font-size:12px;color:var(--color-text-tertiary)">无</span>
              </div>
            </div>
          </div>
        </div>

        <!-- AI 分析摘要 -->
        <div class="card">
          <div class="card-head">
            <div class="card-title" style="font-size:13px">
              <el-icon style="margin-right:6px;font-size:14px;color:#8B5CF6"><MagicStick /></el-icon>AI 分析摘要
            </div>
          </div>
          <div class="ai-summary">
            <div v-if="doc.ai_summary">{{ doc.ai_summary }}</div>
            <div v-else style="color:var(--color-text-tertiary)">暂无 AI 分析结果</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, shallowRef } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Folder, Document, User, Calendar, Coin, Download, Share,
  View, ZoomIn, ZoomOut, FullScreen, Clock, Link, Promotion,
  MagicStick
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getSprint, getSprintDocuments } from '../../api/sprint'

const router = useRouter()
const route = useRoute()
const docId = route.params.id
const zoomLevel = ref(14)

const doc = ref({
  id: docId,
  name: '',
  file_type: '',
  file_size: 0,
  version: 'v1.0',
  uploader_name: '',
  created_at: null,
  sprintName: '',
  content_preview: '',
  ai_summary: '',
  keywords: [],
  module_names: [],
  ai_status: '待分析',
})

function formatDate(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function formatSize(bytes) {
  if (!bytes) return '--'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFileIconColor(type) {
  return { 'PDF': '#E24B4A', 'Word': '#16a34a', 'Markdown': '#8B5CF6', 'Excel': '#EF9F27' }[type] || 'var(--accent)'
}

function getFileIconBg(type) {
  return { 'PDF': '#FEF2F2', 'Word': '#F0FDF4', 'Markdown': '#F5F3FF', 'Excel': '#FFFBEB' }[type] || '#EBF5FF'
}

function getTypeTagType(t) {
  return { 'PDF': '', 'Word': 'success', 'Markdown': 'warning', 'Excel': 'danger' }[t] || 'info'
}

function getAiStatusType(status) {
  return { '已分析': 'success', '分析中': 'warning' }[status] || 'info'
}

function goToKnowledge() { router.push('/knowledge') }
function goToSprint() { router.back() }

function zoomIn() { zoomLevel.value = Math.min(zoomLevel.value + 2, 24) }
function zoomOut() { zoomLevel.value = Math.max(zoomLevel.value - 2, 10) }
function fitPage() { zoomLevel.value = 14 }

function handleDownload() { ElMessage.info('下载功能开发中...') }
function handleShare() { ElMessage.info('分享链接已复制到剪贴板') }

onMounted(async () => {
  // 从所有 Sprint 的文档中查找当前文档
  try {
    // 先获取所有 Sprint 列表，找到文档所在的 Sprint
    const { getSprints } = await import('../../api/sprint')
    const sprintsRes = await getSprints()
    const allSprints = sprintsRes.data || []

    for (const sp of allSprints) {
      const docsRes = await getSprintDocuments(sp.id)
      const found = (docsRes.data || []).find(d => String(d.id) === String(docId))
      if (found) {
        // 获取 Sprint 名称
        const sprintRes = await getSprint(sp.id)
        doc.value = {
          ...found,
          sprintName: sprintRes.data?.name || sp.name,
        }
        return
      }
    }
    // 未找到文档
    ElMessage.warning('未找到文档')
  } catch (e) {
    console.error(e)
    ElMessage.error('加载文档失败')
  }
})
</script>

<style scoped>
.document-preview { max-width: 1400px; }

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

.doc-info-bar {
  padding: 18px 20px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.doc-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.doc-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.doc-details {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 6px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.doc-details span {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.doc-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* 左右分栏布局 */
.preview-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 16px;
}

.preview-main {
  padding: 0;
  overflow: hidden;
}

.preview-toolbar {
  padding: 12px 18px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.content-body {
  padding: 32px 40px;
  min-height: 480px;
  background: #FAFBFC;
  line-height: 1.8;
  color: var(--color-text-primary);
}

.content-body h1,
.content-body h2,
.content-body h3 {
  color: var(--color-text-primary);
}

.content-body ul {
  padding-left: 20px;
}

.content-body li {
  margin-bottom: 8px;
}

.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

/* 右侧面板 */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.version-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 关联信息 */
.related-list {
  padding: 12px 16px;
  font-size: 12px;
}

.related-item {
  margin-bottom: 10px;
}

.related-item:last-child {
  margin-bottom: 0;
}

.related-label {
  color: var(--color-text-tertiary);
  margin-bottom: 4px;
}

.related-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--accent);
  cursor: pointer;
}

.related-link:hover {
  text-decoration: underline;
}

/* AI 摘要 */
.ai-summary {
  padding: 12px 16px;
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.7;
}
</style>
