// SVG图标映射
const iconSvgs = {
  'ti-test-pipe': '<svg viewBox="0 0 24 24"><path d="M6 2v6a3 3 0 0 0 3 3h.5a5.5 5.5 0 0 1 5.5 5.5c0 2.5-2 4.5-4.5 4.5S6 19 6 16.5V12"/><path d="M18 2v6a3 3 0 0 1-3 3h-.5"/><circle cx="12" cy="16.5" r="1.5"/></svg>',
  'ti-layout-dashboard': '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>',
  'ti-list-check': '<svg viewBox="0 0 24 24"><path d="M3 5h2"/><path d="M3 12h2"/><path d="M3 19h2"/><path d="M6 5l1.5 1.5L10 4"/><path d="M6 12l1.5 1.5L10 11"/><path d="M6 19l1.5 1.5L10 18"/><path d="M13 5h8"/><path d="M13 12h8"/><path d="M13 19h8"/></svg>',
  'ti-chart-bar': '<svg viewBox="0 0 24 24"><path d="M3 12h4v8H3z"/><path d="M10 8h4v12h-4z"/><path d="M17 4h4v16h-4z"/></svg>',
  'ti-books': '<svg viewBox="0 0 24 24"><path d="M6 4v16"/><path d="M18 4v16"/><path d="M6 4h12v16H6z"/><path d="M6 12h12"/></svg>',
  'ti-atom': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="2"/><ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/></svg>',
  'ti-shield-half': '<svg viewBox="0 0 24 24"><path d="M12 2l8 4v6c0 5.5-3.8 10-8 11-4.2-1-8-5.5-8-11V6z"/><path d="M12 2v20"/></svg>',
  'ti-users': '<svg viewBox="0 0 24 24"><circle cx="9" cy="7" r="3"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><circle cx="17" cy="8" r="2.5"/><path d="M21 21v-1.5a3 3 0 0 0-2-2.8"/></svg>',
  'ti-chevrons-left': '<svg viewBox="0 0 24 24"><path d="M11 7l-5 5 5 5"/><path d="M17 7l-5 5 5 5"/></svg>',
  'ti-chevrons-right': '<svg viewBox="0 0 24 24"><path d="M13 7l5 5-5 5"/><path d="M7 7l5 5-5 5"/></svg>',
  'ti-settings': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="2.5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
  'ti-search': '<svg viewBox="0 0 24 24"><circle cx="10" cy="10" r="6"/><path d="M21 21l-4.35-4.35"/></svg>',
  'ti-plus': '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
  'ti-check': '<svg viewBox="0 0 24 24"><path d="M5 12l5 5L20 7"/></svg>',
  'ti-bug': '<svg viewBox="0 0 24 24"><path d="M8 2l1.5 2M16 2l-1.5 2"/><rect x="5" y="6" width="14" height="12" rx="4"/><path d="M5 10H3M21 10h-2M5 14H2M22 14h-3M5 18l-2 2M19 18l2 2"/><path d="M9 10v4M15 10v4"/></svg>',
  'ti-file-text': '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h6"/></svg>',
  'ti-user-plus': '<svg viewBox="0 0 24 24"><circle cx="9" cy="7" r="3"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M19 8v6M16 11h6"/></svg>',
  'ti-crown': '<svg viewBox="0 0 24 24"><path d="M2 20h20"/><path d="M4 20l1.5-11 5.5 4 3-6 3 6 5.5-4L20 20"/></svg>',
  'ti-shield': '<svg viewBox="0 0 24 24"><path d="M12 2l8 4v6c0 5.5-3.8 10-8 11-4.2-1-8-5.5-8-11V6z"/></svg>',
  'ti-user': '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M6 21v-2a6 6 0 0 1 12 0v2"/></svg>',
  'ti-eye': '<svg viewBox="0 0 24 24"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
  'ti-cube': '<svg viewBox="0 0 24 24"><path d="M12 2l9 4.5v11L12 22l-9-4.5v-11z"/><path d="M12 22V11"/><path d="M21 6.5l-9 4.5-9-4.5"/></svg>',
  'ti-database': '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.66 3.58 3 8 3s8-1.34 8-3V5"/><path d="M4 11v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6"/></svg>',
  'ti-folder': '<svg viewBox="0 0 24 24"><path d="M5 4h4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/></svg>',
  'ti-arrow-left': '<svg viewBox="0 0 24 24"><path d="M5 12h14M5 12l6-6M5 12l6 6"/></svg>',
  'ti-edit': '<svg viewBox="0 0 24 24"><path d="M4 20h4L18.5 9.5a2.83 2.83 0 0 0-4-4L4 16v4"/><path d="M13.5 6.5l4 4"/></svg>',
  'ti-trash': '<svg viewBox="0 0 24 24"><path d="M4 7h16M10 11v6M14 11v6M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-12M9 7V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"/></svg>',
  'ti-x': '<svg viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>',
  'ti-settings-cog': '<svg viewBox="0 0 24 24"><path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
  'ti-plug-connected': '<svg viewBox="0 0 24 24"><path d="M7 12h10"/><path d="M12 7v10"/><path d="M4 4l4 4"/><path d="M20 4l-4 4"/><path d="M4 20l4-4"/><path d="M20 20l-4-4"/></svg>',
  'ti-player-play': '<svg viewBox="0 0 24 24"><polygon points="6,3 20,12 6,21"/></svg>',
  'ti-sparkles': '<svg viewBox="0 0 24 24"><path d="M12 2l2 7h7l-5.5 4 2 7L12 16l-5.5 4 2-7L3 9h7z"/></svg>'
};

// 检测字体是否加载
function isIconFontLoaded() {
  const testEl = document.createElement('span');
  testEl.className = 'ti ti-test-pipe';
  testEl.style.position = 'absolute';
  testEl.style.left = '-9999px';
  testEl.style.fontSize = '24px';
  document.body.appendChild(testEl);
  const width = testEl.offsetWidth;
  document.body.removeChild(testEl);
  return width > 10;
}

// 替换图标为SVG
function replaceIconsWithSvg() {
  document.querySelectorAll('.ti').forEach(el => {
    const classes = el.className.split(' ');
    const iconClass = classes.find(c => c.startsWith('ti-') && c !== 'ti');
    if (iconClass && iconSvgs[iconClass]) {
      el.innerHTML = iconSvgs[iconClass];
      el.classList.add('icon-svg');
      el.classList.remove('ti');
    }
  });
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
  // 延迟检测字体加载
  setTimeout(() => {
    if (!isIconFontLoaded()) {
      console.log('Tabler Icons字体未加载，使用SVG备用方案');
      replaceIconsWithSvg();
    } else {
      console.log('Tabler Icons字体已加载');
    }
  }, 500);

  // 恢复侧边栏折叠状态
  const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
  if (isCollapsed) {
    document.getElementById('sidebar').classList.add('collapsed');
  }

  console.log('TestFlow 测试管理平台已加载');

  // 项目总览页隐藏操作按钮
  document.getElementById('main-btn').style.display = 'none';
});

const pages = ['project','project-list','testcase','knowledge','knowledge-detail','knowledge-docs','doc-preview','graph-list','graph','report','role','user','ai-config','ai-workbench'];
const titles = {
  project:'项目总览',
  'project-list':'项目管理',
  testcase:'测试用例',
  knowledge:'知识库',
  'knowledge-detail':'Sprint 文档',
  'knowledge-docs':'文档列表',
  'doc-preview':'文档预览',
  'graph-list':'知识图谱',
  graph:'图谱详情',
  report:'测试报告',
  role:'角色管理',
  user:'用户管理',
  'ai-config':'AI 配置',
  'ai-workbench':'AI 工作台'
};
const btnText = {
  project:'新建项目',
  'project-list':'新建项目',
  testcase:'新建用例',
  knowledge:'创建知识库',
  'knowledge-detail':'上传文档',
  'knowledge-docs':'上传文档',
  'doc-preview':'下载文档',
  'graph-list':'创建图谱',
  graph:'编辑关联',
  report:'生成报告',
  role:'新建角色',
  user:'邀请用户',
  'ai-config':'添加服务商',
  'ai-workbench':'执行 SKILL'
};

// 知识库子页面映射到侧边栏"知识库"菜单项
const knowledgeSubPages = ['knowledge', 'knowledge-detail', 'knowledge-docs', 'doc-preview'];
// 知识图谱子页面映射到侧边栏"知识图谱"菜单项
const graphSubPages = ['graph-list', 'graph'];

// 切换页面
function switchPage(id) {
  currentPage = id;
  pages.forEach(p => {
    const el = document.getElementById('page-' + p);
    if (el) el.style.display = p === id ? '' : 'none';
  });

  document.getElementById('page-title').textContent = titles[id] || id;
  // 项目总览页隐藏操作按钮
  const mainBtn = document.getElementById('main-btn');
  if (id === 'project') {
    mainBtn.style.display = 'none';
  } else {
    mainBtn.style.display = '';
    if (id === 'ai-workbench') {
      updateMainBtn();
    } else {
      mainBtn.style.background = '';
      document.getElementById('main-btn-text').textContent = btnText[id] || '新建';
    }
  }

  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const navMap = {project:0, 'project-list':1, testcase:2, report:3, knowledge:4, 'graph-list':5, graph:5, role:6, user:7, 'ai-config':8, 'ai-workbench':9};
  const items = document.querySelectorAll('.nav-item');

  // 知识库子页面高亮"知识库"菜单项
  if (knowledgeSubPages.includes(id)) {
    if (items[navMap['knowledge']]) items[navMap['knowledge']].classList.add('active');
  } else if (graphSubPages.includes(id)) {
    // 知识图谱子页面高亮"知识图谱"菜单项
    if (items[navMap['graph-list']]) items[navMap['graph-list']].classList.add('active');
  } else {
    if (items[navMap[id]]) items[navMap[id]].classList.add('active');
  }
}

// 文档预览数据
const docData = [
  {
    title: '用户登录注册需求说明.pdf',
    author: '李明',
    date: '2026-03-28',
    type: 'PDF',
    size: '2.4 MB',
    iconColor: '#378ADD',
    iconBg: '#EBF5FF',
    tags: ['需求文档', 'Sprint 1', 'v1.2'],
    relatedCases: 'TC-001 ~ TC-023（23 条）',
    content: `<div style="max-width:680px;margin:0 auto">
      <h1 style="font-size:22px;font-weight:700;margin-bottom:8px;color:var(--color-text-primary)">用户登录注册需求说明书</h1>
      <div style="font-size:12px;color:var(--color-text-tertiary);margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--color-border-tertiary)">
        文档编号：REQ-AUTH-001 &nbsp;|&nbsp; 版本：v1.2 &nbsp;|&nbsp; 作者：李明 &nbsp;|&nbsp; 最后更新：2026-03-28
      </div>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">1. 概述</h2>
      <p style="margin-bottom:12px">本文档定义了电商平台用户登录注册模块的功能需求，包括手机号注册、邮箱注册、第三方登录（微信/支付宝）以及密码找回等功能。</p>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">2. 功能需求</h2>
      <h3 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:var(--color-text-primary)">2.1 手机号注册</h3>
      <p style="margin-bottom:8px">用户输入手机号 → 发送短信验证码（60s 有效期）→ 输入验证码 → 设置密码（8-20位，需含大小写字母+数字）→ 注册成功。</p>
      <div style="background:var(--color-background-secondary);border-left:3px solid var(--accent);padding:12px 16px;border-radius:0 6px 6px 0;margin:12px 0;font-size:13px">
        <strong>业务规则：</strong>同一手机号不可重复注册；验证码错误超过 5 次锁定 30 分钟；密码不可与手机号后 6 位相同。
      </div>
      <h3 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:var(--color-text-primary)">2.2 第三方登录</h3>
      <p style="margin-bottom:8px">支持微信 OAuth 2.0 和支付宝授权登录。首次第三方登录需绑定手机号。</p>
      <ul style="margin:8px 0 12px 20px;font-size:13px">
        <li style="margin-bottom:4px">微信登录：调用微信开放平台 API，获取 openid 和 unionid</li>
        <li style="margin-bottom:4px">支付宝登录：调用支付宝 auth 接口，获取 user_id</li>
        <li style="margin-bottom:4px">绑定流程：第三方授权 → 跳转绑定手机号页面 → 短信验证 → 绑定完成</li>
      </ul>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">3. 非功能需求</h2>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin:8px 0">
        <thead><tr style="background:var(--color-background-secondary)"><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">指标</th><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">要求</th></tr></thead>
        <tbody>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">接口响应时间</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">&le; 500ms (P95)</td></tr>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">并发支持</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">&ge; 1000 QPS</td></tr>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">短信到达率</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">&ge; 99.5%</td></tr>
        </tbody>
      </table>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">4. 接口定义</h2>
      <div style="background:#1E293B;border-radius:8px;padding:16px;font-family:var(--font-mono);font-size:12px;color:#E2E8F0;line-height:1.7;overflow-x:auto">
        <div style="color:#94A3B8">// POST /api/v1/auth/register</div>
        <div>{ <span style="color:#7DD3FC">"phone"</span>: <span style="color:#86EFAC">"string"</span>, <span style="color:#7DD3FC">"code"</span>: <span style="color:#86EFAC">"string"</span>, <span style="color:#7DD3FC">"password"</span>: <span style="color:#86EFAC">"string"</span> }</div>
      </div>
    </div>`,
    versions: [
      { ver: 'v1.2', current: true, author: '李明', date: '2026-03-28 14:30', desc: '补充第三方登录绑定流程' },
      { ver: 'v1.1', author: '李明', date: '2026-03-25 10:15', desc: '增加接口定义章节' },
      { ver: 'v1.0', author: '李明', date: '2026-03-20 09:00', desc: '初始版本' }
    ],
    aiSummary: '关键实体：用户、手机号、验证码、密码、微信 openid、支付宝 user_id<br>业务规则：5 条校验规则，2 条安全约束<br>接口数量：6 个 API 端点<br>建议测试点：注册流程、验证码边界、第三方授权回调、密码强度校验、并发注册'
  },
  {
    title: '购物车模块 PRD v1.2.docx',
    author: '王芳',
    date: '2026-03-30',
    type: 'Word',
    size: '1.8 MB',
    iconColor: '#1D9E75',
    iconBg: '#E1F5EE',
    tags: ['PRD', 'Sprint 1', 'v1.2'],
    relatedCases: 'TC-024 ~ TC-047（24 条）',
    content: `<div style="max-width:680px;margin:0 auto">
      <h1 style="font-size:22px;font-weight:700;margin-bottom:8px;color:var(--color-text-primary)">购物车模块产品需求文档</h1>
      <div style="font-size:12px;color:var(--color-text-tertiary);margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--color-border-tertiary)">
        文档编号：REQ-CART-001 &nbsp;|&nbsp; 版本：v1.2 &nbsp;|&nbsp; 作者：王芳 &nbsp;|&nbsp; 最后更新：2026-03-30
      </div>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">1. 产品概述</h2>
      <p style="margin-bottom:12px">购物车模块是电商平台的核心交易链路，承载商品加入、数量修改、规格切换、优惠计算、结算跳转等关键功能。</p>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">2. 核心功能</h2>
      <h3 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:var(--color-text-primary)">2.1 加入购物车</h3>
      <p style="margin-bottom:8px">商品详情页点击"加入购物车" → 选择 SKU 规格（颜色/尺码）→ 确认数量 → 调用 AddCart API → 顶部购物车图标数字 +1 动画反馈。</p>
      <div style="background:var(--color-background-secondary);border-left:3px solid var(--accent);padding:12px 16px;border-radius:0 6px 6px 0;margin:12px 0;font-size:13px">
        <strong>业务规则：</strong>单个 SKU 库存不足时提示"库存仅剩 N 件"；同一 SKU 重复添加合并数量；购物车上限 200 件。
      </div>
      <h3 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:var(--color-text-primary)">2.2 优惠计算引擎</h3>
      <p style="margin-bottom:8px">实时计算满减、优惠券、会员折扣。优先级：优惠券 > 满减 > 会员折扣。价格变动时底部浮层提示。</p>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin:8px 0">
        <thead><tr style="background:var(--color-background-secondary)"><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">优惠类型</th><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">规则</th><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">示例</th></tr></thead>
        <tbody>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">满减</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">满 200 减 30</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">购物车合计 ¥258 → ¥228</td></tr>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">优惠券</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">指定品类 8 折</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">服饰类商品自动打 8 折</td></tr>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">会员折扣</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">VIP 95 折</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">VIP 用户额外 95 折</td></tr>
        </tbody>
      </table>
    </div>`,
    versions: [
      { ver: 'v1.2', current: true, author: '王芳', date: '2026-03-30 16:00', desc: '增加优惠计算引擎说明' },
      { ver: 'v1.1', author: '王芳', date: '2026-03-26 11:20', desc: '补充 SKU 规格选择交互' },
      { ver: 'v1.0', author: '王芳', date: '2026-03-22 09:30', desc: '初始版本' }
    ],
    aiSummary: '关键实体：购物车、SKU、商品、优惠券、满减规则、会员等级<br>业务规则：8 条计算规则，3 条库存校验<br>接口数量：5 个 API 端点<br>建议测试点：SKU 合并逻辑、优惠叠加边界、库存不足提示、200 件上限、价格变动实时刷新'
  },
  {
    title: '订单流程评审会议纪要.md',
    author: '陈刚',
    date: '2026-04-02',
    type: 'Markdown',
    size: '320 KB',
    iconColor: '#534AB7',
    iconBg: '#F3F0FF',
    tags: ['会议纪要', 'Sprint 2'],
    relatedCases: 'TC-048 ~ TC-065（18 条）',
    content: `<div style="max-width:680px;margin:0 auto">
      <h1 style="font-size:22px;font-weight:700;margin-bottom:8px;color:var(--color-text-primary)">订单流程评审会议纪要</h1>
      <div style="font-size:12px;color:var(--color-text-tertiary);margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--color-border-tertiary)">
        会议时间：2026-04-02 14:00-15:30 &nbsp;|&nbsp; 参会人：陈刚、李明、王芳、赵强 &nbsp;|&nbsp; 记录人：陈刚
      </div>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">议题一：订单状态机设计</h2>
      <p style="margin-bottom:12px">讨论了订单从创建到完成的完整状态流转。确认状态包括：待支付 → 已支付 → 待发货 → 已发货 → 已签收 → 已完成。取消可在待支付和已支付两个状态下触发。</p>
      <div style="background:#FEF3C7;border-left:3px solid #F59E0B;padding:12px 16px;border-radius:0 6px 6px 0;margin:12px 0;font-size:13px">
        <strong>待确认：</strong>已支付状态取消订单的退款流程需与财务确认 T+1 还是实时退款。下次会议给出结论。
      </div>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">议题二：超时自动取消</h2>
      <p style="margin-bottom:8px">待支付订单 30 分钟未支付自动取消。技术方案：Redis 延迟队列 + 定时任务兜底。赵强负责技术方案细化。</p>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">议题三：测试覆盖计划</h2>
      <ul style="margin:8px 0 12px 20px;font-size:13px">
        <li style="margin-bottom:4px">正向流程：创建→支付→发货→签收→完成（5 条用例）</li>
        <li style="margin-bottom:4px">取消流程：待支付取消、已支付取消（4 条用例）</li>
        <li style="margin-bottom:4px">异常流程：超时取消、支付回调失败、重复支付（6 条用例）</li>
        <li style="margin-bottom:4px">边界测试：库存为 0 时下单、优惠券过期（3 条用例）</li>
      </ul>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">Action Items</h2>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin:8px 0">
        <thead><tr style="background:var(--color-background-secondary)"><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">事项</th><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">负责人</th><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">截止日期</th></tr></thead>
        <tbody>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">退款流程确认</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">陈刚</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">2026-04-05</td></tr>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">超时取消技术方案</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">赵强</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">2026-04-08</td></tr>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">订单测试用例编写</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">李明</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">2026-04-10</td></tr>
        </tbody>
      </table>
    </div>`,
    versions: [
      { ver: 'v1.0', current: true, author: '陈刚', date: '2026-04-02 16:00', desc: '会议记录定稿' }
    ],
    aiSummary: '关键实体：订单、状态机、支付、退款、Redis 队列<br>决策点：2 个待确认事项<br>Action Items：3 项，截止 4 月 10 日<br>建议测试点：状态流转完整性、超时取消边界、退款异常处理、重复支付防护'
  },
  {
    title: '支付接口对接方案.xlsx',
    author: '李明',
    date: '2026-04-05',
    type: 'Excel',
    size: '890 KB',
    iconColor: '#EF9F27',
    iconBg: '#FEF3C7',
    tags: ['接口文档', 'Sprint 2', 'v2.0'],
    relatedCases: 'TC-066 ~ TC-091（26 条）',
    content: `<div style="max-width:680px;margin:0 auto">
      <h1 style="font-size:22px;font-weight:700;margin-bottom:8px;color:var(--color-text-primary)">支付接口对接方案</h1>
      <div style="font-size:12px;color:var(--color-text-tertiary);margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--color-border-tertiary)">
        文档编号：REQ-PAY-001 &nbsp;|&nbsp; 版本：v2.0 &nbsp;|&nbsp; 作者：李明 &nbsp;|&nbsp; 最后更新：2026-04-05
      </div>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">1. 支付渠道</h2>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin:8px 0">
        <thead><tr style="background:var(--color-background-secondary)"><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">渠道</th><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">接口协议</th><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">手续费</th><th style="padding:8px 12px;text-align:left;border:1px solid var(--color-border-tertiary)">到账时间</th></tr></thead>
        <tbody>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">微信支付</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">V3 API</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">0.6%</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">T+1</td></tr>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">支付宝</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">SDK 2.0</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">0.55%</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">T+1</td></tr>
          <tr><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">银联云闪付</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">UnionPay API</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">0.5%</td><td style="padding:8px 12px;border:1px solid var(--color-border-tertiary)">T+1</td></tr>
        </tbody>
      </table>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">2. 支付流程</h2>
      <p style="margin-bottom:8px">统一下单 → 获取支付参数 → 前端调起支付 → 异步回调通知 → 更新订单状态 → 退款（原路退回）。</p>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">3. 安全要求</h2>
      <ul style="margin:8px 0 12px 20px;font-size:13px">
        <li style="margin-bottom:4px">所有支付请求必须携带签名（RSA2 / HMAC-SHA256）</li>
        <li style="margin-bottom:4px">回调通知需验签，防止伪造</li>
        <li style="margin-bottom:4px">金额单位统一为分，避免浮点精度问题</li>
        <li style="margin-bottom:4px">幂等处理：同一订单号不可重复扣款</li>
      </ul>
      <h2 style="font-size:16px;font-weight:600;margin:24px 0 10px;color:var(--color-text-primary)">4. 接口清单</h2>
      <div style="background:#1E293B;border-radius:8px;padding:16px;font-family:var(--font-mono);font-size:12px;color:#E2E8F0;line-height:1.7;overflow-x:auto">
        <div style="color:#94A3B8">// 统一下单</div>
        <div>POST /api/v1/pay/create</div>
        <div style="color:#94A3B8;margin-top:6px">// 支付回调</div>
        <div>POST /api/v1/pay/notify/{channel}</div>
        <div style="color:#94A3B8;margin-top:6px">// 退款</div>
        <div>POST /api/v1/pay/refund</div>
        <div style="color:#94A3B8;margin-top:6px">// 查询</div>
        <div>GET /api/v1/pay/query/{orderId}</div>
      </div>
    </div>`,
    versions: [
      { ver: 'v2.0', current: true, author: '李明', date: '2026-04-05 10:00', desc: '增加银联云闪付渠道' },
      { ver: 'v1.1', author: '李明', date: '2026-03-28 15:30', desc: '补充安全要求章节' },
      { ver: 'v1.0', author: '李明', date: '2026-03-18 09:00', desc: '初始版本' }
    ],
    aiSummary: '关键实体：支付渠道、订单、回调、退款、签名<br>安全规则：4 条强制约束<br>接口数量：4 个 API 端点<br>建议测试点：多渠道支付、回调验签、幂等扣款、退款原路返回、金额精度、超时处理'
  }
];

// 文档预览
function previewDoc(idx) {
  const doc = docData[idx];
  if (!doc) return;

  // 更新顶部信息
  document.getElementById('doc-preview-title').textContent = doc.title;
  document.getElementById('doc-preview-author').textContent = doc.author;
  document.getElementById('doc-preview-date').textContent = doc.date;
  document.getElementById('doc-preview-type').textContent = doc.type;
  document.getElementById('doc-preview-size').textContent = doc.size;

  // 更新图标
  const iconEl = document.getElementById('doc-preview-icon');
  iconEl.style.background = doc.iconBg;
  iconEl.querySelector('i').style.color = doc.iconColor;

  // 更新标签
  const tagContainer = iconEl.parentElement.parentElement.parentElement.nextElementSibling;
  tagContainer.innerHTML = doc.tags.map(t => {
    const cls = t === '需求文档' || t === 'PRD' ? 'badge-blue' : t === '会议纪要' ? 'badge-purple' : t === '接口文档' ? 'badge-amber' : t.includes('Sprint') ? 'badge-green' : '';
    const style = t === '会议纪要' ? 'background:#EEEDFE;color:#26215C' : t.includes('v') ? 'background:#F3F4F6;color:#4B5563' : '';
    return `<span class="badge ${cls}" style="${style}">${t}</span>`;
  }).join('');

  // 更新文档内容
  document.getElementById('doc-preview-content').innerHTML = doc.content;

  // 更新版本历史
  const versionCard = document.querySelectorAll('#page-doc-preview .card')[2];
  const versionHTML = doc.versions.map((v, i) => `
    <div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;${i < doc.versions.length - 1 ? 'border-bottom:1px dashed var(--color-border-tertiary)' : ''}">
      <div style="width:8px;height:8px;border-radius:50%;background:${v.current ? 'var(--accent)' : '#9CA3AF'};margin-top:5px;flex-shrink:0"></div>
      <div>
        <div style="font-weight:500">${v.ver} ${v.current ? '<span class="badge badge-green" style="font-size:10px;padding:1px 6px">当前</span>' : ''}</div>
        <div style="color:var(--color-text-tertiary);margin-top:2px">${v.author} · ${v.date}</div>
        <div style="color:var(--color-text-secondary);margin-top:4px">${v.desc}</div>
      </div>
    </div>
  `).join('');
  versionCard.querySelector('.card-head').nextElementSibling.innerHTML = versionHTML;

  // 更新关联测试用例
  const relatedCard = document.querySelectorAll('#page-doc-preview .card')[3];
  const relatedLink = relatedCard.querySelector('[onclick*="testcase"]');
  if (relatedLink) relatedLink.innerHTML = `<i class="ti ti-list-check" style="font-size:13px" aria-hidden="true"></i>${doc.relatedCases}`;

  // 更新AI摘要
  const aiCard = document.querySelectorAll('#page-doc-preview .card')[4];
  aiCard.querySelector('.card-head').nextElementSibling.innerHTML = doc.aiSummary;

  switchPage('doc-preview');
}

// 切换侧边栏折叠状态
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const isCollapsed = sidebar.classList.toggle('collapsed');

  // 保存折叠状态到localStorage
  localStorage.setItem('sidebarCollapsed', isCollapsed ? 'true' : 'false');
}

// 切换 AI 服务商时更新模型列表
function onProviderChange() {
  const provider = document.getElementById('ai-provider-select').value;
  const modelSelect = document.getElementById('ai-model-select');
  const endpoint = document.getElementById('ai-endpoint');
  const models = {
    openai: ['GPT-4o', 'GPT-4o-mini', 'GPT-4-turbo', 'o1-preview', 'o1-mini'],
    anthropic: ['Claude 3.5 Sonnet', 'Claude 3.5 Haiku', 'Claude 3 Opus'],
    deepseek: ['DeepSeek-V3', 'DeepSeek-Coder-V2', 'DeepSeek-R1'],
    custom: ['自定义模型...']
  };
  const endpoints = {
    openai: 'https://api.openai.com/v1',
    anthropic: 'https://api.anthropic.com',
    deepseek: 'https://api.deepseek.com/v1',
    custom: ''
  };
  modelSelect.innerHTML = (models[provider] || []).map(m => '<option>' + m + '</option>').join('');
  endpoint.value = endpoints[provider] || '';
  endpoint.placeholder = provider === 'custom' ? '输入自定义 API 端点' : '';
}

// ========== 当前页面追踪 ==========
let currentPage = 'project';

// ========== 对话框管理 ==========
// 所有删除操作共用一个确认对话框
const deleteDialogs = [
  'project-delete', 'testcase-delete', 'kb-delete',
  'folder-delete', 'doc-delete', 'report-delete',
  'role-delete', 'user-delete', 'graph-delete'
];

// 主按钮 → 根据当前页面打开对应的创建对话框
const mainBtnDialogMap = {
  'project': 'project-create',
  'project-list': 'project-create',
  'testcase': 'testcase-create',
  'knowledge': 'kb-create',
  'knowledge-detail': 'folder-create',
  'knowledge-docs': 'doc-upload',
  'graph-list': 'graph-create',
  'graph': null, // 编辑关联用交互式操作
  'report': 'report-generate',
  'role': 'role-create',
  'user': 'user-invite',
  'ai-config': 'ai-provider-add',
  'ai-workbench': null // SKILL 执行用独立交互
};

document.getElementById('main-btn').addEventListener('click', function() {
  if (currentPage === 'ai-workbench') {
    toggleSkill();
    return;
  }
  const dialogId = mainBtnDialogMap[currentPage];
  if (dialogId) {
    openDialog(dialogId);
  } else if (currentPage === 'graph') {
    showToast('info', '请在图谱中点击节点进行编辑关联');
  }
});

function openDialog(id) {
  // 删除类操作统一打开确认对话框
  if (deleteDialogs.includes(id)) {
    document.getElementById('dialog-delete-confirm').classList.add('active');
    return;
  }
  const el = document.getElementById('dialog-' + id);
  if (el) el.classList.add('active');
}

function closeDialog(id) {
  const el = document.getElementById('dialog-' + id);
  if (el) el.classList.remove('active');
}

// 保存并关闭 + 显示 toast
function saveAndClose(dialogId) {
  closeDialog(dialogId);
  showToast('success', '操作成功');
}

// Toast 通知
function showToast(type, message) {
  const toast = document.getElementById('toast');
  const toastIcon = document.getElementById('toast-icon');
  const toastText = document.getElementById('toast-text');
  toastIcon.textContent = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  toastText.textContent = message;
  toast.style.display = 'block';
  requestAnimationFrame(() => {
    toast.style.transform = 'translateX(0)';
  });
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.style.transform = 'translateX(120%)';
    setTimeout(() => { toast.style.display = 'none'; }, 300);
  }, 2500);
}

// 全局搜索
function handleSearch(query) {
  const results = document.getElementById('search-results');
  if (!query.trim()) {
    results.innerHTML = '<div style="font-size:12px;color:var(--color-text-tertiary);margin-bottom:8px">最近访问</div>' +
      '<div class="search-result-item" onclick="closeDialog(\'search\');switchPage(\'project\')"><i class="ti ti-layout-dashboard" style="color:var(--accent);margin-right:8px"></i>项目总览</div>' +
      '<div class="search-result-item" onclick="closeDialog(\'search\');switchPage(\'testcase\')"><i class="ti ti-list-check" style="color:#378ADD;margin-right:8px"></i>测试用例</div>' +
      '<div class="search-result-item" onclick="closeDialog(\'search\');switchPage(\'knowledge\')"><i class="ti ti-books" style="color:#534AB7;margin-right:8px"></i>知识库</div>' +
      '<div class="search-result-item" onclick="closeDialog(\'search\');switchPage(\'ai-config\')"><i class="ti ti-settings-cog" style="color:#EF9F27;margin-right:8px"></i>AI 配置</div>';
    return;
  }
  const q = query.toLowerCase();
  const searchData = [
    { name: '电商平台 v3.0', page: 'project-list', icon: 'ti-folder', color: '#378ADD' },
    { name: 'TC-001 用户登录 - 正常账号密码', page: 'testcase', icon: 'ti-list-check', color: '#1D9E75' },
    { name: 'TC-047 订单结算 - 优惠券叠加', page: 'testcase', icon: 'ti-list-check', color: '#E24B4A' },
    { name: '电商平台知识库', page: 'knowledge', icon: 'ti-books', color: '#534AB7' },
    { name: '支付系统接口图谱', page: 'graph-list', icon: 'ti-atom', color: '#378ADD' },
    { name: '张测试 (管理员)', page: 'user', icon: 'ti-user', color: '#1D9E75' },
    { name: 'OpenAI GPT-4o', page: 'ai-config', icon: 'ti-settings-cog', color: '#10A37F' },
  ];
  const filtered = searchData.filter(item => item.name.toLowerCase().includes(q));
  if (filtered.length === 0) {
    results.innerHTML = '<div style="text-align:center;padding:20px;color:var(--color-text-tertiary);font-size:13px">未找到匹配结果</div>';
    return;
  }
  results.innerHTML = filtered.map(item =>
    `<div class="search-result-item" onclick="closeDialog('search');switchPage('${item.page}')"><i class="ti ${item.icon}" style="color:${item.color};margin-right:8px"></i>${item.name}</div>`
  ).join('');
}

// 知识图谱筛选标签交互
function initGraphFilterTabs() {
  document.querySelectorAll('.graph-filter-tab').forEach(tab => {
    tab.addEventListener('click', function() {
      const parent = this.parentElement;
      parent.querySelectorAll('.graph-filter-tab').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
    });
  });
}

// 知识图谱 — 筛选边
function filterGraphEdges(type) {
  const svg = document.querySelector('#page-graph svg');
  if (!svg) return;
  const lines = svg.querySelectorAll('line');
  const texts = svg.querySelectorAll('text');
  const typeMap = {
    'dep': ['#1D9E75', '#085041'],
    'ref': ['#888', '#9CA3AF'],
    'cover': ['#EF9F27', '#633806'],
    'all': null
  };
  const colors = typeMap[type];
  lines.forEach(line => {
    if (!colors) {
      line.style.opacity = '';
    } else {
      const stroke = line.getAttribute('stroke');
      line.style.opacity = (colors.includes(stroke)) ? '' : '0.08';
    }
  });
  // Also dim/restore edge labels
  texts.forEach(t => {
    if (!colors) {
      t.style.opacity = '';
    } else {
      const fill = t.getAttribute('fill');
      const isLegend = t.parentElement && t.parentElement.querySelector('circle, line');
      if (isLegend) return; // skip legend
      t.style.opacity = (colors.includes(fill)) ? '' : '0.08';
    }
  });
}

// 知识图谱 — 节点数据
const graphNodes = {
  'REQ-EC-001': {
    name: '电商平台需求 v3.2', id: 'REQ-EC-001', icon: 'ti-file-text', color: '#1D9E75', bg: '#E1F5EE',
    upstream: [
      { name: '支付系统接口文档', color: '#378ADD', rel: '依赖' },
      { name: '推荐算法文档', color: '#888', rel: '引用' }
    ],
    downstream: [
      { name: '购物车模块', color: '#EF9F27', rel: '包含' },
      { name: '订单模块', color: '#E24B4A', rel: '包含' }
    ],
    stats: { related: 6, strong: 2 }
  },
  'REQ-PAY-001': {
    name: '支付系统接口文档', id: 'REQ-PAY-001', icon: 'ti-file-text', color: '#378ADD', bg: '#E6F1FB',
    upstream: [
      { name: '电商平台需求', color: '#1D9E75', rel: '被依赖' }
    ],
    downstream: [
      { name: '支付模块', color: '#378ADD', rel: '包含' }
    ],
    stats: { related: 3, strong: 1 }
  },
  'REQ-UC-001': {
    name: '用户中心 PRD', id: 'REQ-UC-001', icon: 'ti-file-text', color: '#534AB7', bg: '#EEEDFE',
    upstream: [
      { name: '电商平台需求', color: '#1D9E75', rel: '被依赖' }
    ],
    downstream: [
      { name: '登录鉴权', color: '#1D9E75', rel: '包含' }
    ],
    stats: { related: 2, strong: 0 }
  },
  'REQ-REC-001': {
    name: '推荐算法文档', id: 'REQ-REC-001', icon: 'ti-file-text', color: '#888', bg: '#F1EFE8',
    upstream: [],
    downstream: [
      { name: '电商平台需求', color: '#1D9E75', rel: '引用' }
    ],
    stats: { related: 1, strong: 0 }
  },
  'MOD-CART': {
    name: '购物车模块', id: 'MOD-CART', icon: 'ti-cube', color: '#EF9F27', bg: '#FAEEDA',
    upstream: [
      { name: '电商平台需求', color: '#1D9E75', rel: '被包含' }
    ],
    downstream: [
      { name: '订单模块', color: '#E24B4A', rel: '依赖' }
    ],
    stats: { related: 3, strong: 1 }
  },
  'MOD-ORD': {
    name: '订单模块', id: 'MOD-ORD', icon: 'ti-cube', color: '#E24B4A', bg: '#FAECE7',
    upstream: [
      { name: '电商平台需求', color: '#1D9E75', rel: '被包含' },
      { name: '购物车模块', color: '#EF9F27', rel: '被依赖' }
    ],
    downstream: [
      { name: '支付模块', color: '#378ADD', rel: '强依赖' }
    ],
    stats: { related: 4, strong: 2 }
  },
  'MOD-PAY': {
    name: '支付模块', id: 'MOD-PAY', icon: 'ti-cube', color: '#378ADD', bg: '#E6F1FB',
    upstream: [
      { name: '支付系统接口文档', color: '#378ADD', rel: '被包含' },
      { name: '订单模块', color: '#E24B4A', rel: '强依赖' }
    ],
    downstream: [],
    stats: { related: 3, strong: 1 }
  },
  'MOD-AUTH': {
    name: '登录鉴权', id: 'MOD-AUTH', icon: 'ti-cube', color: '#1D9E75', bg: '#E1F5EE',
    upstream: [
      { name: '用户中心 PRD', color: '#534AB7', rel: '被包含' }
    ],
    downstream: [],
    stats: { related: 2, strong: 0 }
  },
  'TC-GROUP-1': {
    name: 'TC-001~TC-047', id: 'TC-GROUP-1', icon: 'ti-list-check', color: '#1D9E75', bg: '#E1F5EE',
    upstream: [],
    downstream: [
      { name: '购物车模块', color: '#EF9F27', rel: '覆盖' },
      { name: '登录鉴权', color: '#1D9E75', rel: '覆盖' }
    ],
    stats: { related: 2, strong: 0 }
  },
  'TC-GROUP-2': {
    name: 'TC-048~TC-091', id: 'TC-GROUP-2', icon: 'ti-list-check', color: '#378ADD', bg: '#E6F1FB',
    upstream: [],
    downstream: [
      { name: '订单模块', color: '#E24B4A', rel: '覆盖' },
      { name: '支付模块', color: '#378ADD', rel: '覆盖' }
    ],
    stats: { related: 2, strong: 0 }
  }
};

// 知识图谱 — 点击节点更新详情面板
function selectNode(nodeId) {
  const node = graphNodes[nodeId];
  if (!node) return;
  const detailCard = document.querySelector('#page-graph .card:last-of-type');
  if (!detailCard) return;

  // Update node detail header
  const headerDiv = detailCard.querySelector('[style*="display:flex"][style*="align-items:center"][style*="gap:8px"][style*="margin-bottom:12px"]');
  if (headerDiv) {
    const iconDiv = headerDiv.querySelector('div');
    if (iconDiv) {
      iconDiv.style.background = node.bg;
      iconDiv.querySelector('i').style.color = node.color;
    }
    const nameEl = headerDiv.querySelector('div > div:first-child');
    const idEl = headerDiv.querySelector('div > div:last-child');
    if (nameEl) nameEl.textContent = node.name;
    if (idEl) idEl.textContent = node.id;
  }

  // Update stats
  const statDivs = detailCard.querySelectorAll('[style*="text-align:center"][style*="padding:10px"]');
  if (statDivs[0]) statDivs[0].querySelector('div:first-child').textContent = node.stats.related;
  if (statDivs[1]) statDivs[1].querySelector('div:first-child').textContent = node.stats.strong;

  // Update upstream/downstream lists
  const listsContainer = detailCard.querySelector('[style*="padding:16px 18px"]');
  if (listsContainer) {
    let html = '';

    // Header
    html += `<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
      <div style="width:32px;height:32px;border-radius:50%;background:${node.bg};display:flex;align-items:center;justify-content:center"><i class="ti ${node.icon}" style="color:${node.color};font-size:15px"></i></div>
      <div><div style="font-size:14px;font-weight:500;color:var(--color-text-primary)">${node.name}</div><div style="font-size:11px;color:var(--color-text-tertiary);font-family:var(--font-mono)">${node.id}</div></div>
    </div>`;

    // Stats grid
    html += `<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">
      <div style="text-align:center;padding:10px;background:var(--color-background-secondary);border-radius:var(--border-radius-md)"><div style="font-size:18px;font-weight:500;color:var(--accent)">${node.stats.related}</div><div style="font-size:10px;color:var(--color-text-tertiary);margin-top:2px">关联文档</div></div>
      <div style="text-align:center;padding:10px;background:var(--color-background-secondary);border-radius:var(--border-radius-md)"><div style="font-size:18px;font-weight:500;color:#E24B4A">${node.stats.strong}</div><div style="font-size:10px;color:var(--color-text-tertiary);margin-top:2px">强依赖</div></div>
    </div>`;

    // Upstream
    if (node.upstream.length) {
      html += `<div style="font-size:11px;font-weight:500;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">上游依赖</div>`;
      node.upstream.forEach((u, i) => {
        html += `<div style="display:flex;align-items:center;gap:8px;padding:7px 0;${i < node.upstream.length - 1 ? 'border-bottom:0.5px solid var(--color-border-tertiary);' : ''}font-size:12.5px"><span style="width:7px;height:7px;border-radius:50%;background:${u.color};flex-shrink:0"></span><span>${u.name}</span><span style="margin-left:auto;font-size:10.5px;color:var(--color-text-tertiary);font-family:var(--font-mono)">${u.rel}</span></div>`;
      });
    }

    // Downstream
    if (node.downstream.length) {
      html += `<div style="font-size:11px;font-weight:500;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:0.05em;margin:12px 0 8px">下游影响</div>`;
      node.downstream.forEach((d, i) => {
        html += `<div style="display:flex;align-items:center;gap:8px;padding:7px 0;${i < node.downstream.length - 1 ? 'border-bottom:0.5px solid var(--color-border-tertiary);' : ''}font-size:12.5px"><span style="width:7px;height:7px;border-radius:50%;background:${d.color};flex-shrink:0"></span><span>${d.name}</span><span style="margin-left:auto;font-size:10.5px;color:var(--color-text-tertiary);font-family:var(--font-mono)">${d.rel}</span></div>`;
      });
    }

    listsContainer.innerHTML = html;
  }

  // Highlight selected node in SVG
  document.querySelectorAll('#page-graph svg g[filter]').forEach(g => {
    const rect = g.querySelector('rect');
    if (rect) rect.setAttribute('stroke-width', rect.parentElement.dataset.nodeId === nodeId ? '3' : '2');
  });
}

// 仪表盘统计卡片点击导航
function initDashboardStatClicks() {
  const statLinks = [
    { selector: '#page-project .stat-card:nth-child(1)', page: 'project-list' },
    { selector: '#page-project .stat-card:nth-child(2)', page: 'testcase' },
    { selector: '#page-project .stat-card:nth-child(3)', page: 'report' },
    { selector: '#page-project .stat-card:nth-child(4)', page: 'testcase' }
  ];
  statLinks.forEach(({ selector, page }) => {
    const el = document.querySelector(selector);
    if (el) {
      el.style.cursor = 'pointer';
      el.addEventListener('click', () => switchPage(page));
    }
  });
}

// 仪表盘动态点击导航
function initDashboardActivityClicks() {
  const activityPages = ['report', 'testcase', 'knowledge', 'user', 'graph-list'];
  document.querySelectorAll('#page-project .activity-item').forEach((item, i) => {
    item.style.cursor = 'pointer';
    item.addEventListener('click', () => {
      if (activityPages[i]) switchPage(activityPages[i]);
    });
  });
}

// 测试用例项目筛选
function initTestCaseFilter() {
  const select = document.querySelector('#page-testcase select');
  if (!select) return;
  select.addEventListener('change', function() {
    const val = this.value;
    const rows = document.querySelectorAll('#page-testcase .table tbody tr');
    // Simulated filter — in real app would filter by project
    if (val === '全部项目') {
      rows.forEach(r => r.style.display = '');
    } else {
      // For demo, alternate visibility
      rows.forEach((r, i) => {
        r.style.display = (val === '电商平台' && i % 2 === 0) || (val === '支付系统' && i % 2 === 1) ? '' : 'none';
      });
    }
  });
}

// 测试报告审批
function approveReport(btn) {
  const row = btn.closest('tr');
  if (!row) return;
  const statusBadge = row.querySelector('td:nth-child(5) .badge');
  if (statusBadge) {
    statusBadge.className = 'badge badge-green';
    statusBadge.textContent = '已审批';
  }
  btn.remove();
  showToast('success', '报告已审批');
}

// 初始化报告审批按钮
function initReportApprove() {
  document.querySelectorAll('#page-report .table tbody tr').forEach(row => {
    const statusBadge = row.querySelector('td:nth-child(5) .badge');
    if (statusBadge && statusBadge.textContent === '待审批') {
      const actionDiv = row.querySelector('.action-btns');
      if (actionDiv && !actionDiv.querySelector('.btn-approve')) {
        const approveBtn = document.createElement('button');
        approveBtn.className = 'btn-edit btn-approve';
        approveBtn.style.cssText = 'background:#E1F5EE;color:#1D9E75';
        approveBtn.innerHTML = '<i class="ti ti-check"></i>审批';
        approveBtn.addEventListener('click', function() { approveReport(this); });
        actionDiv.insertBefore(approveBtn, actionDiv.firstChild);
      }
    }
  });
}

// 角色权限矩阵切换
function togglePermission(el) {
  const states = ['✓', '◐', '✕'];
  const colors = ['#1D9E75', '#EF9F27', '#E24B4A'];
  let idx = states.indexOf(el.textContent);
  idx = (idx + 1) % states.length;
  el.textContent = states[idx];
  el.style.color = colors[idx];
}

// 用户状态切换
function toggleUserStatus(btn) {
  const row = btn.closest('tr');
  if (!row) return;
  const statusDot = row.querySelector('.status-dot');
  const statusText = row.querySelector('.status-text');
  if (!statusDot) return;
  const isActive = statusDot.classList.contains('dot-green');
  if (isActive) {
    statusDot.className = 'status-dot dot-red';
    if (statusText) statusText.textContent = '禁用';
    btn.textContent = '启用';
    btn.style.background = '#E1F5EE';
    btn.style.color = '#1D9E75';
    showToast('success', '用户已禁用');
  } else {
    statusDot.className = 'status-dot dot-green';
    if (statusText) statusText.textContent = '活跃';
    btn.textContent = '禁用';
    btn.style.background = '#FCEBEB';
    btn.style.color = '#E24B4A';
    showToast('success', '用户已启用');
  }
}

// AI 模型分配策略编辑
function saveAiStrategy() {
  closeDialog('ai-strategy-edit');
  showToast('success', '模型分配策略已保存');
}

// AI 全局参数编辑
function saveAiGlobal() {
  closeDialog('ai-global-edit');
  showToast('success', '全局参数已保存');
}

// 点击遮罩层关闭对话框
document.querySelectorAll('.dialog-overlay').forEach(overlay => {
  overlay.addEventListener('click', function(e) {
    if (e.target === this) {
      this.classList.remove('active');
    }
  });
});

// 搜索框点击打开搜索对话框
document.querySelector('.header-search').addEventListener('click', function() {
  openDialog('search');
  setTimeout(() => {
    const input = document.getElementById('search-input');
    if (input) input.focus();
  }, 100);
});

// Page init functions — called by loadPage() after content is injected
function initProjectPage() {
  initDashboardStatClicks();
  initDashboardActivityClicks();
  initProjectRowClick();
}

function initTestCasePage() {
  initTestCaseFilter();
  initTestCaseRowExpand();
  initDeleteConfirm();
}

function initKnowledgePage() {
  initKbProjectSelector();
  initDeleteConfirm();
}

function initGraphListPage() {
  initGraphFilterTabs();
  initDeleteConfirm();
}

function initGraphPage() {
  initGraphFilterTabs();
}

function initReportPage() {
  initReportApprove();
  initDeleteConfirm();
}

function initRolePage() {
  initDeleteConfirm();
}

function initUserPage() {
  initDeleteConfirm();
}

function initAiWorkbenchPage() {
  initSkillModeToggle();
  initSprintSelection();
  initStageToggle();
}

function initAiConfigPage() {
  initDeleteConfirm();
}

function initDocPreviewPage() {
  // Doc preview has its own inline interactions
}

// 用户设置入口
document.querySelector('.user-row').addEventListener('click', function(e) {
  if (e.target.closest('.ti-settings') || e.target.classList.contains('ti-settings')) {
    showToast('info', '个人设置功能开发中');
  }
});

// ========== AI 工作台交互 ==========

// SKILL 模式切换（全量/增量）
function initSkillModeToggle() {
  const cards = document.querySelectorAll('.skill-mode-card');
  if (cards.length < 2) return;
  cards.forEach((card, i) => {
    card.addEventListener('click', function() {
      cards.forEach(c => {
        c.style.border = '1px solid var(--color-border-tertiary)';
        c.style.background = 'var(--color-background-primary)';
        c.querySelector('i').style.color = 'var(--color-text-secondary)';
      });
      this.style.border = '2px solid var(--accent)';
      this.style.background = 'var(--accent-light)';
      this.querySelector('i').style.color = 'var(--accent)';
      showToast('info', i === 0 ? '已切换到全量模式' : '已切换到增量模式');
    });
  });
}

// Sprint 选择高亮
function initSprintSelection() {
  const container = document.querySelector('#page-ai-workbench .card:nth-child(2) > div:last-child');
  if (!container) return;
  container.addEventListener('click', function(e) {
    const badge = e.target.closest('.badge');
    if (!badge) return;
    container.querySelectorAll('.badge').forEach(b => {
      b.style.background = '';
      b.style.color = '';
      b.className = 'badge badge-blue';
      b.style.padding = '6px 14px';
      b.style.cursor = 'pointer';
      b.style.fontSize = '12px';
    });
    badge.style.background = 'var(--accent)';
    badge.style.color = '#fff';
    badge.className = 'badge';
    showToast('info', '已选择 ' + badge.textContent.trim());
  });
}

// 执行 SKILL 状态机
let skillState = 'idle'; // idle | running | paused | done
let skillTimer = null;
let skillSeconds = 0;

function updateMainBtn() {
  const btn = document.getElementById('main-btn');
  const btnText = document.getElementById('main-btn-text');
  if (currentPage !== 'ai-workbench') return;
  btn.style.display = '';
  if (skillState === 'idle') {
    btnText.textContent = '执行 SKILL';
    btn.style.background = '';
  } else if (skillState === 'running') {
    btnText.textContent = '暂停执行';
    btn.style.background = '#EF9F27';
  } else if (skillState === 'paused') {
    btnText.textContent = '继续执行';
    btn.style.background = '';
  } else {
    btnText.textContent = '重新执行';
    btn.style.background = '#1D9E75';
  }
}

function tickSkill() {
  skillSeconds++;
  const m = Math.floor(skillSeconds / 60);
  const s = skillSeconds % 60;
  const timerEl = document.querySelector('#page-ai-workbench .card:nth-child(3) .card-head span:last-child');
  if (timerEl) timerEl.textContent = '已运行 ' + m + ' 分 ' + (s < 10 ? '0' : '') + s + ' 秒';
}

function toggleSkill() {
  if (skillState === 'idle' || skillState === 'paused') {
    skillState = 'running';
    skillTimer = setInterval(tickSkill, 1000);
    showToast('success', 'SKILL 流水线已启动');
  } else if (skillState === 'running') {
    skillState = 'paused';
    clearInterval(skillTimer);
    showToast('info', 'SKILL 流水线已暂停');
  } else {
    skillState = 'idle';
    skillSeconds = 0;
    clearInterval(skillTimer);
    showToast('info', 'SKILL 流水线已重置');
  }
  updateMainBtn();
}

// 阶段展开/收起
function initStageToggle() {
  const stages = document.querySelectorAll('#page-ai-workbench .card:nth-child(3) > div > div > div:first-child');
  stages.forEach(stage => {
    const header = stage.querySelector('div:nth-child(2) > div:first-child');
    if (!header) return;
    header.style.cursor = 'pointer';
    header.addEventListener('click', function() {
      const detail = stage.querySelector('div:nth-child(2) > div:not(:first-child):not(:nth-child(2))');
      if (!detail) return;
      const isHidden = detail.style.display === 'none';
      detail.style.display = isHidden ? '' : 'none';
    });
  });
}

// ========== 测试用例行展开 ==========

function initTestCaseRowExpand() {
  document.querySelectorAll('#page-testcase .table tbody tr').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function(e) {
      if (e.target.closest('.action-btns')) return;
      const existing = this.nextElementSibling;
      if (existing && existing.classList.contains('row-detail')) {
        existing.remove();
        return;
      }
      document.querySelectorAll('.row-detail').forEach(r => r.remove());
      const cells = this.querySelectorAll('td');
      const detail = document.createElement('tr');
      detail.className = 'row-detail';
      detail.innerHTML = `<td colspan="7" style="padding:0">
        <div style="padding:16px 20px;background:var(--color-background-secondary);border-top:0.5px solid var(--color-border-tertiary);display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;font-size:12px">
          <div><div style="color:var(--color-text-tertiary);margin-bottom:4px">前置条件</div><div style="color:var(--color-text-secondary)">用户已注册且账号状态正常</div></div>
          <div><div style="color:var(--color-text-tertiary);margin-bottom:4px">测试步骤</div><div style="color:var(--color-text-secondary)">1. 打开登录页面<br>2. 输入账号密码<br>3. 点击登录</div></div>
          <div><div style="color:var(--color-text-tertiary);margin-bottom:4px">预期结果</div><div style="color:var(--color-text-secondary)">登录成功，跳转首页</div></div>
        </div>
      </td>`;
      this.after(detail);
    });
  });
}

// ========== 项目列表行点击进入详情 ==========
function initProjectRowClick() {
  document.querySelectorAll('#page-project-list .table tbody tr').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function(e) {
      if (e.target.closest('.action-btns')) return;
      switchPage('knowledge');
    });
  });
}

// ========== 删除确认 — 实际移除行 ==========
function initDeleteConfirm() {
  let pendingDeleteRow = null;
  document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', function(e) {
      pendingDeleteRow = this.closest('tr');
    });
  });
  const confirmBtn = document.querySelector('#dialog-delete-confirm .btn-danger');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', function() {
      if (pendingDeleteRow) {
        pendingDeleteRow.style.transition = 'opacity 0.3s, transform 0.3s';
        pendingDeleteRow.style.opacity = '0';
        pendingDeleteRow.style.transform = 'translateX(20px)';
        setTimeout(() => pendingDeleteRow.remove(), 300);
        pendingDeleteRow = null;
      }
    });
  }
}

// ========== 文档预览缩放 ==========
let docZoom = 100;
function zoomDocPreview(delta) {
  docZoom = Math.max(50, Math.min(200, docZoom + delta));
  const content = document.getElementById('doc-preview-content');
  if (content) {
    content.style.transform = 'scale(' + (docZoom / 100) + ')';
    content.style.transformOrigin = 'top left';
    showToast('info', '缩放: ' + docZoom + '%');
  }
}
function fitDocPreview() {
  docZoom = 100;
  const content = document.getElementById('doc-preview-content');
  if (content) {
    content.style.transform = '';
    showToast('info', '已适配页面');
  }
}

// ========== AI 连接测试动画 ==========
function testAiConnection() {
  openDialog('ai-test');
  const icon = document.getElementById('ai-test-icon');
  const title = document.getElementById('ai-test-title');
  const msg = document.getElementById('ai-test-msg');
  icon.style.background = '#E6F1FB';
  icon.innerHTML = '<div style="width:24px;height:24px;border:3px solid #378ADD;border-top-color:transparent;border-radius:50%;animation:spin 1s linear infinite"></div>';
  title.textContent = '正在测试连接...';
  msg.textContent = '正在验证 API Key 和模型可用性';
  setTimeout(() => {
    icon.style.background = '#E1F5EE';
    icon.innerHTML = '<i class="ti ti-check" style="font-size:28px;color:#1D9E75"></i>';
    title.textContent = '连接成功';
    msg.innerHTML = '已成功连接到 AI 服务<br>模型响应正常，延迟 230ms';
  }, 1500);
}

// ========== 分享按钮 — 复制链接 ==========
function copyShareLink() {
  const title = document.getElementById('doc-preview-title');
  const text = title ? title.textContent : '文档链接';
  if (navigator.clipboard) {
    navigator.clipboard.writeText('https://testflow.example.com/docs/' + encodeURIComponent(text));
  }
  showToast('success', '链接已复制到剪贴板');
}

// ========== 下载文档 ==========
function downloadDoc() {
  const title = document.getElementById('doc-preview-title');
  const name = title ? title.textContent : '文档';
  showToast('success', name + ' 下载开始…');
}

// ========== 测试用例批量执行 ==========
function batchExecuteTestCases() {
  const rows = document.querySelectorAll('#page-testcase .table tbody tr');
  let count = 0;
  rows.forEach(row => {
    const statusBadge = row.querySelector('td:nth-child(4) .badge');
    if (statusBadge && statusBadge.textContent === '待执行') {
      statusBadge.className = 'badge badge-green';
      statusBadge.textContent = '通过';
      count++;
    }
  });
  if (count > 0) {
    showToast('success', '已批量执行 ' + count + ' 条用例');
  } else {
    showToast('info', '没有待执行的用例');
  }
}

// ========== 知识库项目筛选 ==========
function initKbProjectSelector() {
  const select = document.getElementById('kb-project-selector');
  if (!select) return;
  select.addEventListener('change', function() {
    showToast('info', '已切换到项目: ' + this.value);
  });
}

// ========== 知识图谱重新生成 ==========
function regenerateGraph(btn) {
  const icon = btn.querySelector('i');
  icon.style.animation = 'spin 1s linear infinite';
  btn.disabled = true;
  btn.style.opacity = '0.7';
  showToast('info', '正在重新生成图谱...');
  setTimeout(() => {
    icon.style.animation = '';
    btn.disabled = false;
    btn.style.opacity = '';
    showToast('success', '图谱重新生成完成');
  }, 2000);
}



// Note: init functions are now called per-page by loadPage() in index.html