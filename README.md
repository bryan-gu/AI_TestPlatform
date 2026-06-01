# TestFlow - 软件测试管理平台

TestFlow 是一个面向软件测试团队的综合管理平台，统一管理测试项目、测试用例、测试报告、需求文档等测试资产，并通过知识图谱实现需求与测试的可视化关联。

## 功能模块

| 模块 | 说明 |
|------|------|
| 项目总览 | 统计卡片（进行中项目、用例总数、通过率、待修复缺陷）+ 项目列表 + 近期动态 |
| 项目管理 | 项目 CRUD，进度跟踪，状态管理（待启动/进行中/测试中/已完成） |
| 测试用例 | 用例 CRUD，按项目筛选，优先级（高/中/低）和执行状态管理 |
| 测试报告 | 报告 CRUD，通过率统计，缺陷跟踪，审批流程 |
| 知识库 | 三层结构：知识库 → 文件夹（Sprint） → 文档，支持文件上传 |
| 知识图谱 | 模块关联可视化，支持依赖/包含/调用/数据流关系 |
| 角色管理 | RBAC 权限控制，内置角色 + 自定义角色 |
| 用户管理 | 用户 CRUD，角色分配，状态管理（活跃/离线/待激活/禁用） |

## 技术栈

### 前端
- Vue 3 + Composition API
- Element Plus
- Vue Router 4 + Pinia
- Axios
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
├── testflow-frontend/          # 前端 Vue3 项目
│   └── src/
│       ├── api/                # API 接口定义
│       ├── components/         # 公共组件（布局）
│       ├── router/             # 路由配置
│       ├── stores/             # Pinia 状态管理
│       ├── views/              # 页面组件
│       │   ├── auth/           # 登录/注册
│       │   ├── dashboard/      # 项目总览
│       │   ├── project/        # 项目管理
│       │   ├── testcase/       # 测试用例
│       │   ├── report/         # 测试报告
│       │   ├── knowledge/      # 知识库 + 知识图谱
│       │   ├── role/           # 角色管理
│       │   └── user/           # 用户管理
│       └── utils/              # 工具函数
│
├── testflow-backend/           # 后端 FastAPI 项目
│   └── app/
│       ├── api/v1/             # API 路由（48个接口）
│       ├── core/               # 配置、数据库、安全
│       ├── crud/               # 数据库操作层
│       ├── models/             # SQLAlchemy 数据模型
│       └── schemas/            # Pydantic 请求/响应模型
│
└── software_test_platform.html # HTML 静态原型
```

## 开发进度

- [x] 前端全部页面（10个路由，含编辑/删除功能）
- [x] 后端骨架搭建（48个API接口）
- [ ] Docker 部署验证
- [ ] 前后端对接（替换 Mock 数据）
- [ ] 知识图谱 ECharts 可视化
- [ ] RAG 知识库（文档解析、向量化、语义检索）
