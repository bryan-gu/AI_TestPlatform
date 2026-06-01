# TestFlow 后端开发计划

## Context

前端页面已全部完成（10个路由页面，含编辑/删除功能），当前使用Mock数据。需要搭建Python后端，提供真实API替换Mock数据。

**技术栈**：Python + FastAPI + PostgreSQL + SQLAlchemy + Alembic + JWT + Docker Compose

**开发策略**：分两阶段
- **第一阶段**：核心业务API（认证、项目、用例、报告、知识库基础CRUD、角色、用户），PostgreSQL单库
- **第二阶段**：RAG知识库 + 知识图谱，引入Neo4j/ChromaDB/MinIO

---

## 第一阶段：核心业务API

### 1. 项目初始化与基础设施

**新建目录**：`testflow-backend/`

```
testflow-backend/
├── docker-compose.yml              # PostgreSQL + 后端服务
├── Dockerfile                      # 后端镜像
├── requirements.txt                # Python依赖
├── alembic.ini                     # 数据库迁移配置
├── alembic/
│   ├── env.py
│   └── versions/                   # 迁移版本文件
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI入口
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # 配置（数据库URL、JWT密钥等）
│   │   ├── database.py             # 数据库连接和Session管理
│   │   ├── security.py             # JWT生成/验证、密码哈希
│   │   └── deps.py                 # 依赖注入（获取当前用户、数据库Session）
│   ├── models/                     # SQLAlchemy数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── project.py
│   │   ├── testcase.py
│   │   ├── report.py
│   │   ├── knowledge.py            # KnowledgeBase + Folder + Document
│   │   └── activity.py             # 操作动态记录
│   ├── schemas/                    # Pydantic请求/响应模型
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── project.py
│   │   ├── testcase.py
│   │   ├── report.py
│   │   ├── knowledge.py
│   │   ├── dashboard.py
│   │   └── common.py               # 统一响应格式
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py           # 汇总所有路由
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── roles.py
│   │       ├── projects.py
│   │       ├── testcases.py
│   │       ├── reports.py
│   │       ├── knowledge.py
│   │       └── dashboard.py
│   ├── services/                   # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── project_service.py
│   │   └── ...
│   └── crud/                       # 数据库操作层
│       ├── __init__.py
│       ├── crud_user.py
│       ├── crud_role.py
│       ├── crud_project.py
│       ├── crud_testcase.py
│       ├── crud_report.py
│       └── crud_knowledge.py
└── README.md
```

### 2. 数据库模型设计

#### 2.1 Role（角色）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| name | String(50) | 角色名称（唯一） |
| type | Enum('内置','自定义') | 角色类型 |
| permissions | JSON | 权限列表，如 ["project.view","case.edit"] 或 ["*"] |
| is_editable | Boolean | 是否可编辑（内置角色为False） |
| created_at | DateTime | 创建时间 |

**初始数据**：
- 超级管理员（内置，permissions: ["*"]）
- 项目管理员（自定义）
- 测试工程师（自定义）
- 只读观察员（自定义）

#### 2.2 User（用户）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| name | String(50) | 姓名 |
| email | String(100) | 邮箱（唯一） |
| password_hash | String(128) | 密码哈希 |
| role_id | Integer FK | 关联角色 |
| project | String(100) | 所属项目（简单文本，可为"全部"或空） |
| status | Enum('活跃','离线','待激活','禁用') | 用户状态 |
| last_login | DateTime | 最近登录时间 |
| created_at | DateTime | 创建时间 |

#### 2.3 Project（项目）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| name | String(100) | 项目名称 |
| description | Text | 项目描述 |
| status | Enum('pending','active','testing','completed') | 项目状态 |
| progress | Integer | 进度百分比 0-100 |
| owner_id | Integer FK | 负责人（关联User） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 2.4 TestCase（测试用例）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| case_no | String(20) | 用例编号（自动生成，如TC-001） |
| title | String(200) | 用例标题 |
| priority | Enum('高','中','低') | 优先级 |
| exec_status | Enum('通过','失败','执行中','待执行') | 执行状态 |
| executor_id | Integer FK | 执行人（关联User，可为空） |
| project_id | Integer FK | 所属项目 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 2.5 Report（测试报告）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| name | String(200) | 报告名称 |
| project_id | Integer FK | 所属项目 |
| pass_rate | Float | 通过率 |
| defect_count | Integer | 缺陷数 |
| status | Enum('已审批','待审批') | 审批状态 |
| created_at | DateTime | 创建时间 |

#### 2.6 KnowledgeBase（知识库）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| name | String(100) | 知识库名称 |
| description | Text | 描述 |
| project_id | Integer FK | 所属项目 |
| creator_id | Integer FK | 创建人 |
| created_at | DateTime | 创建时间 |

#### 2.7 Folder（文件夹）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| name | String(100) | 文件夹名称 |
| knowledge_base_id | Integer FK | 所属知识库 |
| created_at | DateTime | 创建时间 |

#### 2.8 Document（文档）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| name | String(200) | 文档名称 |
| file_path | String(500) | 文件存储路径 |
| file_type | String(20) | 文件类型（PDF/Word/Markdown/Excel） |
| file_size | Integer | 文件大小（字节） |
| folder_id | Integer FK | 所属文件夹 |
| uploader_id | Integer FK | 上传人 |
| created_at | DateTime | 创建时间 |

#### 2.9 Activity（操作动态）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| icon | String(50) | 图标名称 |
| text | String(200) | 动态描述 |
| user_id | Integer FK | 操作人 |
| created_at | DateTime | 创建时间 |

### 3. API接口清单（第一阶段）

#### 3.1 认证模块 `/api/v1/auth`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | /auth/login | 登录 | {email, password} | {token} |
| POST | /auth/register | 注册 | {name, email, password} | {token} |
| POST | /auth/logout | 登出 | - | {code:200} |
| GET | /auth/me | 获取当前用户 | - | {id, name, email, role:{name,permissions}} |
| POST | /auth/change-password | 修改密码 | {old_password, new_password} | {code:200} |

#### 3.2 仪表盘 `/api/v1/dashboard`

| 方法 | 路径 | 说明 | 响应 |
|------|------|------|------|
| GET | /dashboard/stats | 统计数据 | {activeProjects, totalCases, newCases, passRate, passRateChange, pendingBugs, severeBugs, normalBugs} |
| GET | /dashboard/activities | 近期动态 | [{icon, text, time, user}] |

#### 3.3 项目管理 `/api/v1/projects`

| 方法 | 路径 | 说明 | 请求体/参数 | 响应 |
|------|------|------|------------|------|
| GET | /projects | 项目列表 | ?page=&page_size= | [Project] |
| GET | /projects/{id} | 项目详情 | - | Project |
| POST | /projects | 创建项目 | {name, description, status, progress, owner_id} | Project |
| PUT | /projects/{id} | 更新项目 | {name, description, status, progress, owner_id} | Project |
| DELETE | /projects/{id} | 删除项目 | - | {code:200} |
| GET | /projects/{id}/testcases | 项目关联用例 | - | [TestCase] |
| GET | /projects/{id}/reports | 项目关联报告 | - | [Report] |

#### 3.4 测试用例 `/api/v1/testcases`

| 方法 | 路径 | 说明 | 请求体/参数 | 响应 |
|------|------|------|------------|------|
| GET | /testcases | 用例列表 | ?project= (项目名称筛选) | [TestCase] |
| GET | /testcases/stats | 用例统计 | - | {total, projectCount, passed, passRate, failed, pending} |
| POST | /testcases | 创建用例 | {title, priority, execStatus, executor_id, project_id} | TestCase |
| PUT | /testcases/{id} | 更新用例 | {title, priority, execStatus, executor_id} | TestCase |
| DELETE | /testcases/{id} | 删除用例 | - | {code:200} |

#### 3.5 测试报告 `/api/v1/reports`

| 方法 | 路径 | 说明 | 请求体/参数 | 响应 |
|------|------|------|------------|------|
| GET | /reports | 报告列表 | - | [Report] |
| GET | /reports/stats | 报告统计 | - | {monthlyReports, monthlyChange, avgPassRate, totalDefects, fixedDefects, pendingApproval} |
| POST | /reports | 创建报告 | {name, project_id} | Report |
| PUT | /reports/{id} | 更新报告 | {name, status} | Report |
| DELETE | /reports/{id} | 删除报告 | - | {code:200} |

#### 3.6 知识库 `/api/v1/knowledge`

| 方法 | 路径 | 说明 | 请求体/参数 | 响应 |
|------|------|------|------------|------|
| GET | /knowledge | 知识库列表 | - | [KnowledgeBase] |
| GET | /knowledge/stats | 知识库统计 | - | {totalBases, totalDocs, newDocs} |
| GET | /knowledge/{id} | 知识库详情 | - | KnowledgeBase |
| POST | /knowledge | 创建知识库 | {name, description, project_id} | KnowledgeBase |
| PUT | /knowledge/{id} | 更新知识库 | {name, description, project_id} | KnowledgeBase |
| DELETE | /knowledge/{id} | 删除知识库 | - | {code:200} |

#### 3.7 文件夹 `/api/v1/knowledge/{id}/folders`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /knowledge/{id}/folders | 文件夹列表 | - | [Folder] |
| POST | /knowledge/{id}/folders | 创建文件夹 | {name} | Folder |
| PUT | /knowledge/{id}/folders/{folderId} | 更新文件夹 | {name} | Folder |
| DELETE | /knowledge/{id}/folders/{folderId} | 删除文件夹 | - | {code:200} |

#### 3.8 文档 `/api/v1/knowledge/{id}/folders/{folderId}/documents`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | .../documents | 文档列表 | - | [Document] |
| POST | .../documents | 上传文档 | multipart/form-data {file} | Document |
| PUT | .../documents/{docId} | 更新文档 | {name} | Document |
| DELETE | .../documents/{docId} | 删除文档 | - | {code:200} |

#### 3.9 角色管理 `/api/v1/roles`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /roles | 角色列表 | - | [Role] |
| GET | /roles/stats | 角色统计 | - | {totalRoles, builtInRoles, totalPermissions} |
| POST | /roles | 创建角色 | {name, permissions} | Role |
| PUT | /roles/{id} | 更新角色 | {name, permissions} | Role |
| DELETE | /roles/{id} | 删除角色 | - | {code:200} |

#### 3.10 用户管理 `/api/v1/users`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /users | 用户列表 | - | [User] |
| GET | /users/stats | 用户统计 | - | {totalUsers, newUsers, activeUsers, onlineToday, disabledUsers, pendingUsers} |
| POST | /users | 创建/邀请用户 | {name, email, role_id, project, status} | User |
| PUT | /users/{id} | 更新用户 | {name, role_id, project, status} | User |
| DELETE | /users/{id} | 删除用户 | - | {code:200} |

**第一阶段接口总计：48个**

### 4. 开发顺序

```
第1步：项目骨架 + Docker Compose + PostgreSQL
  ├── docker-compose.yml（PostgreSQL服务）
  ├── FastAPI项目结构
  ├── 数据库连接和Session管理
  └── Alembic迁移配置

第2步：数据模型 + 迁移
  ├── 所有SQLAlchemy模型
  ├── Alembic初始迁移
  └── 初始数据种子（默认角色）

第3步：认证API
  ├── JWT工具函数
  ├── 密码哈希（bcrypt）
  ├── /auth/login
  ├── /auth/register
  ├── /auth/me
  ├── /auth/logout
  └── /auth/change-password

第4步：核心CRUD API（按依赖顺序）
  ├── 角色管理（用户依赖角色）
  ├── 用户管理（项目依赖用户）
  ├── 项目管理（用例/报告依赖项目）
  ├── 测试用例
  ├── 测试报告
  └── 仪表盘统计

第5步：知识库API
  ├── 知识库CRUD
  ├── 文件夹CRUD
  └── 文档CRUD（含文件上传）

第6步：前后端对接
  ├── 前端API层替换Mock数据
  ├── 统一响应格式验证
  └── 跨域配置（CORS）
```

### 5. Docker Compose 配置

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: testflow
      POSTGRES_USER: testflow
      POSTGRES_PASSWORD: testflow123
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://testflow:testflow123@db:5432/testflow
      JWT_SECRET_KEY: your-secret-key-here
    depends_on:
      - db
    volumes:
      - ./app:/code/app
      - uploads:/code/uploads

volumes:
  pgdata:
  uploads:
```

### 6. Python依赖

```
# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
alembic==1.13.0
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
pydantic==2.9.0
pydantic-settings==2.5.0
```

---

## 第二阶段：RAG + 知识图谱（后续规划）

### 涉及组件
- **Neo4j**：模块关联关系存储
- **ChromaDB**：文档向量存储
- **MinIO**：文件对象存储
- **Embedding模型**：文档向量化

### 第二阶段接口（暂不实现）

| 模块 | 接口 | 说明 |
|------|------|------|
| 文档处理 | POST /documents/{id}/parse | 触发文档解析和向量化 |
| 文档处理 | GET /documents/{id}/chunks | 查看文档分块 |
| 文档处理 | GET /documents/{id}/status | 向量化状态 |
| 知识图谱 | GET /graph/{project_id} | 获取项目图谱 |
| 知识图谱 | GET /graph/{project_id}/stats | 图谱统计 |
| 知识图谱 | GET /graph/{project_id}/modules/{name}/related | 影响范围分析 |
| 知识图谱 | POST/PUT/DELETE /graph/nodes | 节点CRUD |
| 知识图谱 | POST/DELETE /graph/edges | 关联CRUD |
| AI用例生成 | POST /testcases/generate | RAG增强用例生成 |
| 全局搜索 | GET /search?q= | 跨模块搜索 |

---

## 验证方式

1. **Docker启动**：`docker-compose up -d`，确认PostgreSQL和API服务正常运行
2. **Swagger文档**：访问 http://localhost:8000/docs 查看自动生成的API文档
3. **认证流程**：通过Swagger UI测试注册→登录→获取用户信息
4. **CRUD测试**：通过Swagger UI测试各模块的增删改查
5. **前端对接**：关闭Mock数据，前端连接真实API，验证所有页面功能

---

## 预估工作量

| 步骤 | 内容 | 预估 |
|------|------|------|
| 第1步 | 项目骨架 + Docker | 1天 |
| 第2步 | 数据模型 + 迁移 | 1天 |
| 第3步 | 认证API | 1天 |
| 第4步 | 核心CRUD API | 2-3天 |
| 第5步 | 知识库API | 1天 |
| 第6步 | 前后端对接 | 1天 |
| **合计** | | **7-8天** |
