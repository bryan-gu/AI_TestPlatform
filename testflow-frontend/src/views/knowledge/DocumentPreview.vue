<template>
  <div class="document-preview">
    <!-- 面包屑导航 -->
    <div class="breadcrumb-nav">
      <span class="back-link" @click="goBack">
        <el-icon><ArrowLeft /></el-icon> 返回文档列表
      </span>
    </div>

    <!-- 文档信息卡片 -->
    <div class="doc-info card">
      <div class="doc-header">
        <div class="doc-icon" :style="{ background: doc.iconBg, color: doc.iconColor }">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div class="doc-meta">
          <h1 class="doc-title">{{ doc.title }}</h1>
          <div class="doc-details">
            <span><el-icon><User /></el-icon> {{ doc.author }}</span>
            <span><el-icon><Calendar /></el-icon> {{ doc.date }}</span>
            <span><el-icon><Document /></el-icon> {{ doc.type }}</span>
            <span><el-icon><Coin /></el-icon> {{ doc.size }}</span>
          </div>
        </div>
      </div>

      <!-- 标签 -->
      <div class="doc-tags">
        <el-tag
          v-for="tag in doc.tags"
          :key="tag"
          size="small"
          type="info"
        >
          {{ tag }}
        </el-tag>
      </div>

      <!-- 关联用例 -->
      <div class="doc-related">
        <span class="related-label">关联测试用例：</span>
        <span class="related-link" @click="goToTestCases">
          <el-icon><List /></el-icon>
          {{ doc.relatedCases }}
        </span>
      </div>
    </div>

    <!-- 文档内容 -->
    <div class="doc-content card">
      <div class="card-head">
        <div class="card-title">文档内容</div>
        <div class="card-actions">
          <el-button size="small" @click="handleDownload">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
          <el-button size="small" @click="handleGenerateCases">
            <el-icon><MagicStick /></el-icon>
            生成测试用例
          </el-button>
        </div>
      </div>
      <div class="content-body" v-html="doc.content"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  ArrowLeft, Document, User, Calendar, Coin, List,
  Download, MagicStick
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const docId = route.params.id

// 文档数据
const doc = ref({
  id: docId,
  title: '用户登录注册需求说明书',
  author: '李明',
  date: '2026-03-28',
  type: 'PDF',
  size: '2.4 MB',
  iconColor: '#378ADD',
  iconBg: '#EBF5FF',
  tags: ['需求文档', 'Sprint 1', 'v1.2'],
  relatedCases: 'TC-001 ~ TC-023（23 条）',
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
      <ul style="margin-bottom:12px;padding-left:20px;line-height:1.8">
        <li>用户输入手机号，点击"获取验证码"按钮</li>
        <li>系统发送6位数字验证码到用户手机</li>
        <li>验证码有效期为5分钟</li>
        <li>用户输入验证码和密码（8-20位，需包含字母和数字）完成注册</li>
        <li>同一手机号不可重复注册</li>
      </ul>

      <h3 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:var(--color-text-primary)">2.2 邮箱注册</h3>
      <ul style="margin-bottom:12px;padding-left:20px;line-height:1.8">
        <li>用户输入邮箱地址，点击"发送验证邮件"</li>
        <li>系统发送验证链接到用户邮箱</li>
        <li>验证链接有效期为24小时</li>
        <li>用户点击链接后设置密码完成注册</li>
      </ul>

      <h3 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:var(--color-text-primary)">2.3 第三方登录</h3>
      <ul style="margin-bottom:12px;padding-left:20px;line-height:1.8">
        <li>支持微信登录和支付宝登录</li>
        <li>首次第三方登录需绑定手机号</li>
        <li>已绑定用户可直接登录</li>
      </ul>

      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">3. 业务规则</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:16px">
        <thead>
          <tr style="background:var(--color-background-secondary)">
            <th style="padding:8px 12px;text-align:left;border:0.5px solid var(--color-border-tertiary);font-size:12px">规则编号</th>
            <th style="padding:8px 12px;text-align:left;border:0.5px solid var(--color-border-tertiary);font-size:12px">规则描述</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary);font-size:13px">BR-001</td>
            <td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary);font-size:13px">密码必须为8-20位，包含至少一个字母和一个数字</td>
          </tr>
          <tr>
            <td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary);font-size:13px">BR-002</td>
            <td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary);font-size:13px">验证码5分钟内有效，超时需重新获取</td>
          </tr>
          <tr>
            <td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary);font-size:13px">BR-003</td>
            <td style="padding:8px 12px;border:0.5px solid var(--color-border-tertiary);font-size:13px">同一手机号每天最多发送10次验证码</td>
          </tr>
        </tbody>
      </table>
    </div>
  `
})

// 返回
function goBack() {
  router.back()
}

// 跳转到测试用例
function goToTestCases() {
  router.push('/testcases')
}

// 下载文档
function handleDownload() {
  ElMessage.info('下载功能开发中...')
}

// 生成测试用例
function handleGenerateCases() {
  ElMessage.info('AI生成功能开发中...')
}

onMounted(() => {
  // TODO: 从API获取文档详情
})
</script>

<style scoped>
.document-preview {
  max-width: 1000px;
}

.breadcrumb-nav {
  margin-bottom: 16px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--accent);
  cursor: pointer;
}

.back-link:hover {
  text-decoration: underline;
}

.doc-info {
  margin-bottom: 16px;
}

.doc-header {
  display: flex;
  gap: 16px;
  padding: 18px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}

.doc-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.doc-meta {
  flex: 1;
}

.doc-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.doc-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.doc-details span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.doc-tags {
  display: flex;
  gap: 8px;
  padding: 12px 18px;
  border-bottom: 0.5px solid var(--color-border-tertiary);
}

.doc-related {
  padding: 12px 18px;
  font-size: 13px;
}

.related-label {
  color: var(--color-text-secondary);
}

.related-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--accent);
  cursor: pointer;
}

.related-link:hover {
  text-decoration: underline;
}

.doc-content {
  margin-bottom: 24px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.content-body {
  padding: 20px;
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
</style>
