<template>
  <div class="document-preview">
    <!-- 面包屑 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item" @click="goToProject">
        <el-icon :size="13"><Folder /></el-icon>电商平台 v3.0
      </span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item" @click="goToSprint">Sprint 2</span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item" @click="goToModule">用户登录注册</span>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-item current">文档预览</span>
    </div>

    <!-- 文档信息卡片 -->
    <div class="card" style="margin-bottom:16px">
      <div class="doc-info-bar">
        <div style="display:flex;align-items:center;gap:14px">
          <div class="doc-icon" style="background:#EBF5FF">
            <el-icon :size="22" style="color:#378ADD"><Document /></el-icon>
          </div>
          <div>
            <div class="doc-title">{{ doc.title }}</div>
            <div class="doc-details">
              <span><el-icon :size="13"><User /></el-icon> 上传人：<strong>{{ doc.author }}</strong></span>
              <span><el-icon :size="13"><Calendar /></el-icon> 上传时间：<strong>{{ doc.date }}</strong></span>
              <span><el-icon :size="13"><Document /></el-icon> 类型：<strong>{{ doc.type }}</strong></span>
              <span><el-icon :size="13"><Coin /></el-icon> 大小：<strong>{{ doc.size }}</strong></span>
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
          <el-button size="small" @click="handleEdit">
            <el-icon><Edit /></el-icon>编辑
          </el-button>
        </div>
      </div>
    </div>

    <!-- 文档标签 -->
    <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap">
      <el-tag type="primary" size="small" effect="plain">需求文档</el-tag>
      <el-tag type="success" size="small" effect="plain">Sprint 1</el-tag>
      <el-tag size="small" effect="plain">v1.2</el-tag>
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
        <div class="content-body" :style="{ fontSize: zoomLevel + 'px' }" v-html="doc.content"></div>
      </div>

      <!-- 右侧：信息面板 -->
      <div class="side-panel">
        <!-- 版本历史 -->
        <div class="card">
          <div class="card-head">
            <div class="card-title" style="font-size:13px">
              <el-icon style="margin-right:6px;font-size:14px;color:var(--accent)"><Clock /></el-icon>版本历史
            </div>
          </div>
          <div class="version-list">
            <div v-for="ver in doc.versions" :key="ver.version" class="version-item">
              <div class="version-dot" :style="{ background: ver.isCurrent ? 'var(--accent)' : '#9CA3AF' }"></div>
              <div class="version-info">
                <div style="font-weight:500">
                  {{ ver.version }}
                  <el-tag v-if="ver.isCurrent" type="success" size="small" effect="plain" style="font-size:10px;padding:0 6px;margin-left:4px">当前</el-tag>
                </div>
                <div style="color:var(--color-text-tertiary);margin-top:2px">{{ ver.author }} · {{ ver.date }}</div>
                <div style="color:var(--color-text-secondary);margin-top:4px">{{ ver.desc }}</div>
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
              <div class="related-label">所属知识库</div>
              <div class="related-link" @click="goToSprint">
                <el-icon :size="13"><Collection /></el-icon>电商平台知识库
              </div>
            </div>
            <div class="related-item">
              <div class="related-label">所属文件夹</div>
              <div style="display:flex;align-items:center;gap:6px">
                <el-icon :size="13" style="color:#EF9F27"><Folder /></el-icon>Sprint 1
              </div>
            </div>
            <div class="related-item">
              <div class="related-label">关联测试用例</div>
              <div class="related-link" @click="goToTestCases">
                <el-icon :size="13"><List /></el-icon>TC-001 ~ TC-023（23 条）
              </div>
            </div>
            <div class="related-item">
              <div class="related-label">知识图谱节点</div>
              <div class="related-link" @click="goToGraphs">
                <el-icon :size="13"><Share /></el-icon>电商平台需求图谱
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
            <div style="margin-bottom:8px"><strong>关键实体：</strong>用户、手机号、验证码、密码、微信 openid、支付宝 user_id</div>
            <div style="margin-bottom:8px"><strong>业务规则：</strong>5 条校验规则，2 条安全约束</div>
            <div style="margin-bottom:8px"><strong>接口数量：</strong>6 个 API 端点</div>
            <div><strong>建议测试点：</strong>注册流程、验证码边界、第三方授权回调、密码强度校验、并发注册</div>
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
  Folder, Document, User, Calendar, Coin, List, Download, Share,
  Edit, View, ZoomIn, ZoomOut, FullScreen, Clock, Link, Collection,
  MagicStick
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const docId = route.params.id
const zoomLevel = ref(14)

const doc = ref({
  id: docId,
  title: '用户登录注册需求说明.pdf',
  author: '李明',
  date: '2026-03-28',
  type: 'PDF',
  size: '2.4 MB',
  versions: [
    { version: 'v1.2', isCurrent: true, author: '李明', date: '2026-03-28 14:30', desc: '补充第三方登录绑定流程' },
    { version: 'v1.1', isCurrent: false, author: '李明', date: '2026-03-25 10:15', desc: '增加接口定义章节' },
    { version: 'v1.0', isCurrent: false, author: '李明', date: '2026-03-20 09:00', desc: '初始版本' }
  ],
  content: `
    <div style="max-width:680px;margin:0 auto">
      <h1 style="font-size:22px;font-weight:700;margin-bottom:8px;color:var(--color-text-primary)">用户登录注册需求说明书</h1>
      <div style="font-size:12px;color:var(--color-text-tertiary);margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--color-border-tertiary)">
        文档编号：REQ-AUTH-001 &nbsp;|&nbsp; 版本：v1.2 &nbsp;|&nbsp; 作者：李明 &nbsp;|&nbsp; 最后更新：2026-03-28
      </div>

      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">1. 概述</h2>
      <p style="margin-bottom:12px;line-height:1.8">本文档定义了电商平台用户登录注册模块的功能需求，包括手机号注册、邮箱注册、第三方登录（微信/支付宝）以及密码找回等功能。</p>

      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">2. 功能需求</h2>
      <h3 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:var(--color-text-primary)">2.1 手机号注册</h3>
      <p style="margin-bottom:8px;line-height:1.8">用户输入手机号 → 发送短信验证码（60s 有效期）→ 输入验证码 → 设置密码（8-20位，需含大小写字母+数字）→ 注册成功。</p>
      <div style="background:var(--color-background-secondary);border-left:3px solid var(--accent);padding:12px 16px;border-radius:0 6px 6px 0;margin:12px 0;font-size:13px;line-height:1.7">
        <strong>业务规则：</strong>同一手机号不可重复注册；验证码错误超过 5 次锁定 30 分钟；密码不可与手机号后 6 位相同。
      </div>

      <h3 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:var(--color-text-primary)">2.2 第三方登录</h3>
      <p style="margin-bottom:8px;line-height:1.8">支持微信 OAuth 2.0 和支付宝授权登录。首次第三方登录需绑定手机号。</p>
      <ul style="margin:8px 0 12px 20px;font-size:13px;line-height:1.8">
        <li style="margin-bottom:4px">微信登录：调用微信开放平台 API，获取 openid 和 unionid</li>
        <li style="margin-bottom:4px">支付宝登录：调用支付宝 auth 接口，获取 user_id</li>
        <li style="margin-bottom:4px">绑定流程：第三方授权 → 跳转绑定手机号页面 → 短信验证 → 绑定完成</li>
      </ul>

      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">3. 非功能需求</h2>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin:8px 0">
        <thead>
          <tr style="background:var(--color-background-secondary)">
            <th style="padding:8px 12px;text-align:left;border:0.5px solid var(--color-border-tertiary)">指标</th>
            <th style="padding:8px 12px;text-align:left;border:0.5px solid var(--color-border-tertiary)">要求</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary)">接口响应时间</td><td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary)">≤ 500ms (P95)</td></tr>
          <tr><td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary)">并发支持</td><td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary)">≥ 1000 QPS</td></tr>
          <tr><td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary)">短信到达率</td><td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary)">≥ 99.5%</td></tr>
          <tr><td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary)">密码加密</td><td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary)">bcrypt, salt rounds ≥ 12</td></tr>
        </tbody>
      </table>

      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">4. 接口定义</h2>
      <div style="background:#1E293B;border-radius:8px;padding:16px;font-family:monospace;font-size:12px;color:#E2E8F0;line-height:1.7;overflow-x:auto">
        <div style="color:#94A3B8">// POST /api/v1/auth/register</div>
        <div>{</div>
        <div>&nbsp;&nbsp;<span style="color:#7DD3FC">"phone"</span>: <span style="color:#86EFAC">"string"</span>,</div>
        <div>&nbsp;&nbsp;<span style="color:#7DD3FC">"code"</span>: <span style="color:#86EFAC">"string"</span>,</div>
        <div>&nbsp;&nbsp;<span style="color:#7DD3FC">"password"</span>: <span style="color:#86EFAC">"string"</span></div>
        <div>}</div>
        <div style="margin-top:8px;color:#94A3B8">// Response: 200 OK</div>
        <div>{</div>
        <div>&nbsp;&nbsp;<span style="color:#7DD3FC">"code"</span>: <span style="color:#FDE68A">0</span>,</div>
        <div>&nbsp;&nbsp;<span style="color:#7DD3FC">"data"</span>: { <span style="color:#7DD3FC">"token"</span>: <span style="color:#86EFAC">"jwt..."</span>, <span style="color:#7DD3FC">"userId"</span>: <span style="color:#86EFAC">"10001"</span> }</div>
        <div>}</div>
      </div>
    </div>
  `
})

function goToProject() { router.push('/projects') }
function goToSprint() { router.back() }
function goToModule() { router.back() }
function goToTestCases() { router.push('/testcases') }
function goToGraphs() { router.push('/graphs') }

function zoomIn() { zoomLevel.value = Math.min(zoomLevel.value + 2, 24) }
function zoomOut() { zoomLevel.value = Math.max(zoomLevel.value - 2, 10) }
function fitPage() { zoomLevel.value = 14 }

function handleDownload() { ElMessage.info('下载功能开发中...') }
function handleShare() { ElMessage.info('分享链接已复制到剪贴板') }
function handleEdit() { ElMessage.info('编辑功能开发中...') }

onMounted(() => {
  // TODO: 从API获取文档详情
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

/* 右侧面板 */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 版本历史 */
.version-list {
  padding: 12px 16px;
  font-size: 12px;
}

.version-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--color-border-tertiary);
}

.version-item:last-child {
  border-bottom: none;
}

.version-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.version-info {
  flex: 1;
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
