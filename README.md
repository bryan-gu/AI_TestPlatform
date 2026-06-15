# TestFlow - 软件测试管理平台

TestFlow 是一个面向软件测试团队的综合管理平台，统一管理测试项目、测试用例、测试报告、需求文档等测试资产，通过 Sprint 组织知识快照，并以知识图谱实现需求与测试的可视化关联。

## 功能模块

| 模块 | 说明 |
|------|------|
| 项目总览 | 统计卡片 + 项目列表 + 近期动态 |
| 项目管理 | 项目 CRUD，进度跟踪，状态管理（待启动/进行中/测试中/已完成） |
| 测试用例 | 用例 CRUD，按项目筛选，优先级和执行状态管理，批量执行 |
| 测试报告 | 报告 CRUD，通过率统计，缺陷跟踪，审批流程，报告类型（回归/冒烟/迭代/全量） |
| 知识库 | Sprint 详情 Tabs（资产/功能点/测试用例/接口/变更影响/关系图谱），KnowledgeAsset 资产层，TraceLink 追踪关系，AI 功能点提取，文档上传与预览 |
| 知识图谱 | ECharts 力导向图可视化（资产/文档/功能点/用例/接口/模块/脚本/变更全实体），subgraph/邻居/搜索查询，影响范围分析 |
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

默认账号：`admin@test.com` / `Aa123456`

## 项目结构

```
├── CLAUDE.md                           # 项目说明（Claude Code 指令）
├── 知识库与知识图谱增强项开发计划.md      # 增强项 8 批次开发计划（已全部完成）
├── RAG知识库与知识图谱技术方案.md         # RAG/图谱远期技术愿景（未实现）
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
└── deploy.ps1                          # 部署脚本（Git push + Docker 重建）
```

## 开发进度

### 已完成
- [x] 前端全部页面 + 后端核心 API + Docker Compose 部署 + deploy.ps1 部署脚本（Phase 0~7）
- [x] 知识库结构重构（阶段 1~8）：KnowledgeAsset 资产层、TraceLink 追踪关系、ApiEndpoint、ChangeItem、sprint_all 基线快照、图谱从 TraceLink 重建、本地项目导入、Sprint 详情 Tabs
- [x] 增强项 8 批次（详见 `知识库与知识图谱增强项开发计划.md`）：
  - 功能点矩阵/接口清单关联统计列；Sprint 聚合接口 + 统一覆盖率口径（4 类）
  - 脚本/selector 精确映射（用例→脚本自动化闭环）；ImportJob 异步导入 + 进度轮询
  - 图谱 subgraph/neighbors/search 查询 + ECharts 力导向图可视化
  - 流水线智能化（PRD LLM 变更识别 + 按模块 prepare + 接口-用例智能覆盖映射）
  - sprint_all 脚本合并 + Sprint sequence_no 排序；数据库 active 唯一约束

### 后续方向
- RAG 语义检索（文档向量化 + ChromaDB，远期愿景，见 `RAG知识库与知识图谱技术方案.md`）
- 用户权限与角色完善（RBAC 细化、项目成员级）
- 性能优化与全量测试
