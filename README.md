# TestFlow - 软件测试管理平台

TestFlow 是一个面向软件测试团队的综合管理平台，统一管理测试项目、测试用例、测试报告、需求文档等测试资产，通过 Sprint 组织知识快照，并以知识图谱实现需求与测试的可视化关联。

## 功能模块

| 模块 | 说明 |
|------|------|
| 项目总览 | 统计卡片 + 项目列表 + 近期动态 |
| 项目管理 | 项目 CRUD，进度跟踪，状态管理（待启动/进行中/测试中/已完成） |
| 测试用例 | 用例 CRUD，按项目筛选，优先级和执行状态管理，批量执行 |
| 测试报告 | 报告 CRUD，通过率统计，缺陷跟踪，审批流程，报告类型（回归/冒烟/迭代/全量） |
| 知识库 | Sprint 知识快照 → 文档列表，Module 为 AI 自动识别的标签字典，AI 功能点提取，支持文件上传和文档预览 |
| 知识图谱 | 模块关联可视化（依赖/包含/调用/数据流），AI 自动生成，影响范围分析 |
| AI 工作台 | 4 阶段 SKILL 流水线（需求分析 → 用例生成 → 脚本生成 → 执行自愈），支持全量/增量模式 |
| AI 配置 | 多服务商管理（OpenAI/Anthropic/DeepSeek），模型分配策略，全局参数，调用日志 |
| 角色管理 | RBAC 权限控制，内置角色 + 自定义角色 |
| 用户管理 | 用户 CRUD，角色分配，邀请功能，状态管理 |

## 技术栈

### 前端
- Vue 3 + Composition API + `<script setup>`
- Element Plus
- Vue Router 4 + Pinia
- Axios
- ECharts（知识图谱可视化）
- Vite

### 后端
- Python + FastAPI
- PostgreSQL + SQLAlchemy + Alembic
- JWT 认证
- Docker Compose 部署

## 快速开始

### 前端

```bash
cd testflow-frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 后端

```bash
cd testflow-backend
docker-compose up -d
```

API 文档：http://localhost:8000/docs

默认账号：`zhang@test.com` / `123456`

## 项目结构

```
├── CLAUDE.md                           # 项目说明（Claude Code 指令）
├── 全栈开发方案.md                      # 前后端全栈开发方案
├── RAG知识库与知识图谱技术方案.md         # RAG/图谱技术架构文档
│
├── Prototype/TestFlow/                 # 原型设计（HTML + 功能描述）
│
├── testflow-frontend/                  # 前端 Vue3 项目
│   └── src/
│       ├── api/                        # API 接口定义
│       ├── components/layout/          # 布局组件（侧边栏/顶栏）
│       ├── router/                     # 路由配置
│       ├── stores/                     # Pinia 状态管理
│       ├── views/
│       │   ├── auth/                   # 登录/注册
│       │   ├── dashboard/              # 项目总览
│       │   ├── project/               # 项目管理
│       │   ├── testcase/              # 测试用例
│       │   ├── report/                # 测试报告
│       │   ├── knowledge/             # 知识库（Sprint/文档/预览，Module为AI标签）
│       │   ├── graph/                 # 知识图谱
│       │   ├── ai/                    # AI 工作台
│       │   ├── settings/              # AI 配置
│       │   ├── role/                  # 角色管理
│       │   └── user/                  # 用户管理
│       └── utils/                     # 工具函数
│
├── testflow-backend/                   # 后端 FastAPI 项目
│   └── app/
│       ├── api/v1/                     # API 路由
│       ├── core/                       # 配置、数据库、安全
│       ├── crud/                       # 数据库操作层
│       ├── models/                     # SQLAlchemy 数据模型
│       └── schemas/                    # Pydantic 请求/响应模型
│
├── deploy.ps1                          # 部署脚本（Git push + Docker 重建）
└── software_test_platform.html         # HTML 静态原型（早期）
```

## 开发进度

### 已完成
- [x] 原型设计（`Prototype/TestFlow/` 含功能描述文档）
- [x] 前端全部页面（14 个路由，含 Sprint 知识快照、AI 工作台、AI 配置）
- [x] 后端核心 API（认证、项目、用例、报告、角色、用户、仪表盘）
- [x] Docker Compose 部署（前端 + 后端 + PostgreSQL）
- [x] 部署脚本（`deploy.ps1` 自动 Git push + 服务器 Docker 重建）
- [x] Alembic 数据库迁移基础设施（Phase 0）
- [x] 知识库模型重构：KnowledgeBase/Folder → Sprint + Module(AI标签字典) + Document（Phase 1）
- [x] Sprint/Doc/Module CRUD API + 前端对接（Phase 2A）
- [x] TestCase 字段补充（前置条件/测试步骤/预期结果）
- [x] Report 字段补充（报告类型/审批流程）
- [x] TestCase + Report Schema/CRUD/API 暴露新字段 + 批量执行 + 审批接口（Phase 2B）
- [x] FeaturePoint 功能点模型 + API + 前端功能点管理（Phase 3）
- [x] AI 配置模块（Provider/Strategy/Config/CallLog）+ 前端对接（Phase 4）
- [x] 知识图谱模块（Graph/Node/Edge）+ 前端对接（Phase 5）
- [x] AI 流水线/工作台（PipelineExecution/Stage）+ 前端对接（Phase 6）
- [x] 全局搜索 + Dashboard 增强（Phase 7）

### 进行中（参见 全栈开发方案.md）
- 无
