# TestFlow - 知识库与知识图谱技术方案

## 文档说明

> **⚠️ 状态：远期技术愿景，尚未实现。** 本文档描述的 ChromaDB 向量库、Neo4j 图数据库、RAG 语义检索均未落地。当前知识图谱实现为 PostgreSQL 的 GraphNode/GraphEdge + TraceLink 追踪关系（详见 `知识库与知识图谱增强项开发计划.md`）。本文档作为远期 RAG 演进方向的参考保留。

本文档详细说明TestFlow平台中知识库和知识图谱的技术架构、数据处理流程、技术选型和实现方案。

**核心价值**：为AI生成测试用例提供上下文支持，实现跨模块测试覆盖

参考来源：项目组内《知识图谱数据处理流程说明》

---

## 一、整体架构

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TestFlow 平台                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│   │   前端       │    │   API网关    │    │   认证服务   │                 │
│   │   Vue3       │───▶│   FastAPI    │───▶│   JWT        │                 │
│   └──────────────┘    └──────┬───────┘    └──────────────┘                 │
│                              │                                              │
│        ┌─────────────────────┼─────────────────────┐                       │
│        ▼                     ▼                     ▼                       │
│   ┌──────────┐        ┌──────────┐          ┌──────────┐                  │
│   │ 业务服务 │        │ 知识库   │          │ 图谱服务 │                  │
│   │ 项目/用例│        │ 文档/向量│          │ 模块/关联│                  │
│   └────┬─────┘        └────┬─────┘          └────┬─────┘                  │
│        │                   │                     │                         │
│        ▼                   ▼                     ▼                         │
│   ┌──────────┐        ┌──────────┐          ┌──────────┐                  │
│   │PostgreSQL│        │ ChromaDB │          │  Neo4j   │                  │
│   │ 结构化   │        │ 向量     │          │ 图数据   │                  │
│   └──────────┘        └──────────┘          └──────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           知识库构建流程                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   需求文档 ──▶ 文档解析 ──▶ 文本分块 ──▶ 向量化 ──▶ ChromaDB              │
│   (PDF/Word)    (纯文本)    (Chunk)    (Embedding)   (存储)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           测试用例生成流程                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   点击"生成测试用例"                                                         │
│         │                                                                   │
│         ▼                                                                   │
│   ┌─────────────────┐                                                       │
│   │ 知识图谱查询    │ ──▶ 获取关联模块                                      │
│   └────────┬────────┘                                                       │
│            ▼                                                                │
│   ┌─────────────────┐                                                       │
│   │ RAG语义检索     │ ──▶ 检索相关文档片段                                  │
│   └────────┬────────┘                                                       │
│            ▼                                                                │
│   ┌─────────────────┐                                                       │
│   │ 组装Prompt      │ ──▶ 功能点 + 关联模块 + 文档片段                      │
│   └────────┬────────┘                                                       │
│            ▼                                                                │
│   ┌─────────────────┐                                                       │
│   │ LLM生成用例     │ ──▶ 输出测试用例                                      │
│   └─────────────────┘                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、技术选型

### 2.1 存储层

| 组件 | 用途 | 选型理由 |
|------|------|----------|
| **PostgreSQL** | 结构化数据存储 | 成熟稳定、支持全文搜索 |
| **Neo4j** | 图数据库 | 业界标准、Cypher查询强大 |
| **ChromaDB** | 向量数据库 | 轻量级、Python原生、易部署 |
| **MinIO** | 文件存储 | 兼容S3协议、可本地部署 |

### 2.2 AI层（可配置）

AI模型采用**适配器模式**，支持通过配置切换不同模型。

```python
# 配置示例
AI_CONFIG = {
    "llm": {
        "provider": "openai",  # 可选: openai / anthropic / local
        "model": "gpt-4o-mini",
        "api_key": "sk-xxx"
    },
    "embedding": {
        "provider": "openai",  # 可选: openai / huggingface
        "model": "text-embedding-3-small",
        "dimension": 1536
    }
}
```

**支持的LLM选项**：

| 提供商 | 模型 | 适用场景 |
|--------|------|----------|
| OpenAI | GPT-4o / GPT-4o-mini | 通用场景，效果好 |
| Anthropic | Claude 3.5 Sonnet / Haiku | 长文本处理 |
| 本地 | Qwen / Llama / ChatGLM | 数据安全要求高 |

**支持的Embedding选项**：

| 提供商 | 模型 | 维度 | 特点 |
|--------|------|------|------|
| OpenAI | text-embedding-3-small | 1536 | 简单易用 |
| HuggingFace | BGE-M3 | 1024 | 中文优化，可本地部署 |

---

## 三、数据模型设计

### 3.1 PostgreSQL表结构

```sql
-- =====================================================
-- 文档管理相关表
-- =====================================================

-- 需求文档表
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,              -- 文档名称
    project_id UUID REFERENCES projects(id), -- 所属项目
    category VARCHAR(50),                    -- 分类: functional/interface/product/nonfunctional
    version VARCHAR(50),                     -- 版本号
    file_url VARCHAR(500),                   -- 文件存储路径
    file_size INTEGER,                       -- 文件大小(bytes)
    file_type VARCHAR(20),                   -- 文件类型: pdf/docx/md/txt
    chunk_count INTEGER DEFAULT 0,           -- 分块数量
    vector_status VARCHAR(20) DEFAULT 'pending', -- 向量化状态: pending/processing/completed/failed
    uploader_id UUID REFERENCES users(id),   -- 上传人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文档分块表
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,            -- 分块序号
    content TEXT NOT NULL,                   -- 分块内容
    summary VARCHAR(500),                    -- 摘要
    metadata JSONB,                          -- 元数据 {page, section, ...}
    vector_id VARCHAR(100),                  -- ChromaDB中的向量ID
    token_count INTEGER,                     -- Token数量
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 索引
-- =====================================================

CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_documents_status ON documents(vector_status);
CREATE INDEX idx_chunks_document ON document_chunks(document_id);
```

### 3.2 Neo4j图模型

```cypher
// =====================================================
// 节点类型
// =====================================================

// 模块节点
CREATE (m:Module {
    id: 'uuid',
    name: '订单模块',
    project_id: 'project_uuid',
    description: '处理用户订单的创建、支付、取消等流程',
    risk_level: 'high'           // 风险等级: high/medium/low
})

// 功能节点
CREATE (f:Feature {
    id: 'uuid',
    name: '创建订单',
    module_id: 'module_uuid',
    description: '用户下单后创建订单记录',
    priority: 'high'
})

// 接口节点
CREATE (a:API {
    id: 'uuid',
    name: '/api/orders/create',
    method: 'POST',
    module_id: 'module_uuid',
    description: '创建订单接口'
})

// =====================================================
// 关系类型
// =====================================================

// 依赖关系: 模块A依赖模块B
CREATE (m1:Module)-[:DEPENDS_ON {description: '订单依赖购物车数据'}]->(m2:Module)

// 调用关系: 模块A调用模块B的接口
CREATE (m1:Module)-[:CALLS {api: '/api/payment/create', description: '创建支付'}]->(m2:Module)

// 包含关系: 模块包含功能
CREATE (m:Module)-[:CONTAINS]->(f:Feature)

// 数据流关系: 数据从A流向B
CREATE (m1:Module)-[:DATA_FLOW {data: '订单数据', description: '订单创建后流向库存模块'}]->(m2:Module)
```

### 3.3 ChromaDB集合设计

```python
# 集合: 文档chunk向量
collection = {
    "name": "document_chunks_{project_id}",
    "metadata": {"hnsw:space": "cosine"}
}

# 每条记录
record = {
    "id": "chunk_uuid",
    "embedding": [0.1, 0.2, ...],          # 向量
    "document": "chunk文本内容",
    "metadata": {
        "document_id": "文档ID",
        "document_name": "文档名称",
        "project_id": "项目ID",
        "module_name": "模块名称",
        "chunk_index": 0,
        "page_number": 1,
        "category": "functional"
    }
}
```

---

## 四、数据处理流程

### 4.1 文档上传处理流程

```
用户上传需求文档
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 文档解析                                                 │
├─────────────────────────────────────────────────────────────────┤
│ - PDF: 使用 pdfplumber 提取文本                                  │
│ - Word: 使用 python-docx 提取段落                                │
│ - Excel: 使用 openpyxl 提取表格数据                              │
│ - Markdown: 直接读取                                              │
│                                                                 │
│ 输出: 纯文本 + 结构信息（页码、章节）                             │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Chunk分块                                                │
├─────────────────────────────────────────────────────────────────┤
│ 分块策略：                                                        │
│ - 按段落切分，每块 500-1000 tokens                                │
│ - 相邻chunk重叠 10%，保持上下文连贯                               │
│ - 保留元数据：chunk_id, doc_id, page, section, module_name       │
│                                                                 │
│ 输出: 多个chunk，每个带元数据                                     │
└─────────────────────────────────────────────────────────────────┘
    │
    ├────────────────────┬────────────────────┐
    ▼                    ▼                    ▼
┌────────────┐    ┌────────────┐    ┌────────────┐
│ Step 3a    │    │ Step 3b    │    │ Step 3c    │
│ 写入PG     │    │ 向量化     │    │ 提取模块   │
│ 存储原文   │    │ 存储ChromaDB│   │ 存入图谱   │
└────────────┘    └────────────┘    └────────────┘
```

### 4.2 测试用例生成流程

```python
async def generate_test_cases(
    project_id: str,
    module_name: str,
    feature_doc: str  # 功能点.md内容
) -> List[Dict]:
    """
    生成测试用例
    
    流程：
    1. 从知识图谱获取关联模块
    2. 从ChromaDB检索相关文档片段
    3. 组装Prompt
    4. 调用LLM生成用例
    """
    
    # Step 1: 从知识图谱获取关联模块
    related_modules = await graph_service.get_related_modules(
        project_id, module_name
    )
    
    # Step 2: 从ChromaDB检索相关文档片段
    # 检索当前模块的相关内容
    module_chunks = await vector_store.search(
        query=f"{module_name} 功能需求 业务规则",
        project_id=project_id,
        filter={"module": module_name},
        top_k=5
    )
    
    # 检索关联模块的相关内容
    related_chunks = []
    for related_module in related_modules:
        chunks = await vector_store.search(
            query=f"{related_module['name']} 与 {module_name} 的关系",
            project_id=project_id,
            filter={"module": related_module['name']},
            top_k=3
        )
        related_chunks.extend(chunks)
    
    # Step 3: 组装Prompt
    prompt = f"""
## 当前模块功能点
{feature_doc}

## 模块关联关系（来自知识图谱）
{format_related_modules(related_modules)}

## 相关文档片段（RAG检索）
### 当前模块相关
{format_chunks(module_chunks)}

### 关联模块相关
{format_chunks(related_chunks)}

## 要求
1. 生成覆盖当前模块所有功能的测试用例
2. 生成与关联模块交互的集成测试用例
3. 包含边界条件和异常场景
4. 输出JSON格式
"""
    
    # Step 4: 调用LLM生成
    result = await llm.extract_json(prompt)
    
    return result["test_cases"]
```

---

## 五、与bf-test-workflow集成

### 5.1 bf-case-generator增强流程

```
原流程：
    功能点.md → bf-case-generator → cases.json

增强流程：
    功能点.md ─────────────────────────────────────────┐
        │                                              │
        ▼                                              ▼
  ┌─────────────┐                              ┌─────────────┐
  │ RAG检索     │                              │ 知识图谱    │
  │ 相关文档    │                              │ 关联模块    │
  └──────┬──────┘                              └──────┬──────┘
         │                                            │
         └────────────────┬───────────────────────────┘
                          ▼
                ┌─────────────────┐
                │ bf-case-        │
                │ generator       │
                │ (增强版Prompt)  │
                └────────┬────────┘
                         ▼
                   cases.json
                   (包含关联模块用例)
```

### 5.2 增强版Prompt模板

```python
def build_enhanced_prompt(feature_doc, rag_chunks, related_modules):
    prompt = f"""
## 功能点信息
{feature_doc}

## 模块关联关系（来自知识图谱）
{format_related_modules(related_modules)}

## 相关文档片段（RAG检索）
{format_chunks(rag_chunks)}

## 测试用例生成要求

1. **当前模块用例**：覆盖功能点中的所有场景
2. **集成测试用例**：覆盖与关联模块的交互场景
3. **边界case**：包含异常场景和边界条件
4. **回归范围**：基于模块关联关系，标注需要回归测试的模块

请生成测试用例JSON。
"""
    return prompt
```

### 5.3 影响范围分析API

```python
async def get_related_modules(project_id: str, module_name: str) -> List[Dict]:
    """
    获取关联模块
    
    返回：
    [
        {"name": "购物车模块", "relation": "depends_on", "description": "..."},
        {"name": "支付模块", "relation": "calls", "description": "..."},
        ...
    ]
    """
    # Neo4j查询
    query = """
    MATCH (m:Module {name: $module_name, project_id: $project_id})-[r]-(related:Module)
    RETURN related.name AS name, type(r) AS relation_type, r.description AS description
    """
    
    results = await neo4j.execute(query, {
        "module_name": module_name,
        "project_id": project_id
    })
    
    return [
        {
            "name": r["name"],
            "relation": r["relation_type"],
            "description": r["description"]
        }
        for r in results
    ]
```

---

## 六、API接口设计

### 6.1 文档管理API

```python
# 文档上传
POST /api/v1/documents/upload
Content-Type: multipart/form-data

# 请求
{
    "file": <file>,
    "project_id": "uuid",
    "category": "functional"
}

# 响应
{
    "code": 200,
    "data": {
        "document_id": "uuid",
        "name": "需求文档v1.0.pdf",
        "chunk_count": 45,
        "vector_status": "processing"
    }
}

# =====================================================

# 获取文档列表
GET /api/v1/documents?project_id=xxx

# 响应
{
    "code": 200,
    "data": [
        {
            "id": "uuid",
            "name": "需求文档v1.0.pdf",
            "category": "functional",
            "chunk_count": 45,
            "vector_status": "completed",
            "created_at": "2024-01-01T00:00:00"
        }
    ]
}

# =====================================================

# 触发文档解析
POST /api/v1/documents/{id}/parse

# 响应
{
    "code": 200,
    "message": "文档解析已启动"
}
```

### 6.2 知识图谱API

```python
# 获取项目图谱
GET /api/v1/graph/{project_id}

# 响应
{
    "code": 200,
    "data": {
        "nodes": [
            {
                "id": "uuid",
                "name": "订单模块",
                "type": "module",
                "risk_level": "high"
            }
        ],
        "edges": [
            {
                "source": "订单模块",
                "target": "购物车模块",
                "type": "depends_on",
                "description": "订单依赖购物车数据"
            }
        ]
    }
}

# =====================================================

# 获取关联模块
GET /api/v1/graph/{project_id}/modules/{module_name}/related

# 响应
{
    "code": 200,
    "data": [
        {
            "name": "购物车模块",
            "relation": "depends_on",
            "description": "订单依赖购物车数据"
        },
        {
            "name": "支付模块",
            "relation": "calls",
            "description": "订单调用支付接口"
        }
    ]
}

# =====================================================

# 添加模块节点
POST /api/v1/graph/nodes

# 请求
{
    "project_id": "uuid",
    "name": "订单模块",
    "type": "module",
    "description": "处理用户订单",
    "risk_level": "high"
}

# =====================================================

# 添加关联关系
POST /api/v1/graph/edges

# 请求
{
    "project_id": "uuid",
    "source": "订单模块",
    "target": "购物车模块",
    "type": "depends_on",
    "description": "订单依赖购物车数据"
}
```

### 6.3 测试用例生成API

```python
# 生成测试用例
POST /api/v1/testcases/generate

# 请求
{
    "project_id": "uuid",
    "module_name": "订单模块",
    "feature_doc": "功能点.md的内容..."
}

# 响应
{
    "code": 200,
    "data": {
        "test_cases": [
            {
                "case_no": "TC-001",
                "title": "正常创建订单",
                "priority": "high",
                "steps": [...],
                "expected": "..."
            }
        ],
        "related_modules": ["购物车模块", "支付模块"],
        "sources": ["需求文档v1.0.pdf - 第3页"]
    }
}
```

---

## 七、部署架构

### 7.1 开发环境

```yaml
# docker-compose.dev.yml

version: '3.8'

services:
  # 主数据库
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: testflow
      POSTGRES_USER: testflow
      POSTGRES_PASSWORD: testflow123
    volumes:
      - pgdata:/var/lib/postgresql/data

  # 图数据库
  neo4j:
    image: neo4j:5.0
    ports:
      - "7474:7474"  # Web UI
      - "7687:7687"  # Bolt协议
    environment:
      NEO4J_AUTH: neo4j/testflow123
    volumes:
      - neo4jdata:/data

  # 向量数据库
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chromadata:/chroma/chroma

  # 对象存储
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data

volumes:
  pgdata:
  neo4jdata:
  chromadata:
  miniodata:
```

---

## 八、开发计划

### 阶段1：知识库基础（2周）

| 任务 | 时间 | 说明 |
|------|------|------|
| 文档解析服务 | 3天 | PDF/Word/Excel解析 |
| Chunk分块服务 | 2天 | 分块策略、元数据生成 |
| 向量化服务 | 2天 | Embedding适配器 |
| ChromaDB集成 | 2天 | 存储和检索 |
| 文档管理API | 3天 | 上传、解析、列表 |

### 阶段2：知识图谱（1.5周）

| 任务 | 时间 | 说明 |
|------|------|------|
| Neo4j集成 | 2天 | 连接、基础操作 |
| 模块关联管理 | 2天 | 节点和边的CRUD |
| 影响范围查询 | 2天 | 关联模块查询 |
| 图谱可视化API | 2天 | 前端数据接口 |

### 阶段3：测试用例生成（1.5周）

| 任务 | 时间 | 说明 |
|------|------|------|
| RAG检索服务 | 2天 | 语义检索相关文档 |
| Prompt组装 | 2天 | 整合图谱和RAG结果 |
| LLM调用适配器 | 2天 | 支持多模型切换 |
| 生成API | 2天 | 生成测试用例接口 |

**总计：约5周**

---

## 九、注意事项

### 9.1 性能优化

- **异步处理**：文档解析和向量化异步执行，避免阻塞
- **批量向量化**：Chunk批量处理，减少API调用
- **连接池**：Neo4j、ChromaDB使用连接池

### 9.2 数据安全

- **权限控制**：按项目隔离数据
- **文档加密**：敏感文档加密存储

### 9.3 监控告警

- **向量化状态**：监控失败任务
- **检索延迟**：P99延迟 < 2s
- **存储容量**：监控各存储组件容量

---

## 十、总结

本方案的核心思想：**RAG + 知识图谱 协同工作，为AI生成测试用例提供全面上下文**

- **知识图谱**：提供模块间的关联关系（依赖、调用、数据流）
- **RAG检索**：提供关联模块的详细文档内容
- **LLM生成**：基于完整上下文生成覆盖全面的测试用例

**不提供用户直接问答界面**，RAG和知识图谱仅作为AI生成用例的底层能力。

这样既能保证测试用例的质量，又降低了系统复杂度。
