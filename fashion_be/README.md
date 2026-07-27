# Fashion Evaluation Backend API

基于 FastAPI 的时尚设计评估数据管理系统后端服务。

## 功能特性

- ✅ 自动解析评估文档（txt格式）
- ✅ 增量同步数据到 SQLite 数据库
- ✅ RESTful API 接口
- ✅ 启动时自动同步数据
- ✅ 支持手动触发同步
- ✅ 完整的 CRUD 操作

## 技术栈

- **FastAPI**: 现代高性能 Web 框架
- **SQLAlchemy**: ORM 数据库工具
- **SQLite**: 轻量级数据库
- **Pydantic**: 数据验证
- **Uvicorn**: ASGI 服务器

## 项目结构

```
fashion_be/
├── main.py              # FastAPI 主应用
├── models.py            # 数据库模型
├── schemas.py           # Pydantic 模型
├── database.py          # 数据库配置
├── crud.py              # 数据库操作
├── parser.py            # 评估文档解析器
├── requirements.txt     # 依赖包
├── .env.example         # 环境变量示例
└── README.md           # 项目文档
```

## 安装和运行

### 1. 安装依赖

```bash
cd fashion_be
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

复制 `.env.example` 为 `.env` 并根据需要修改配置。

### 3. 启动服务

```bash
python main.py
```

或使用 uvicorn 命令：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 基础端点

- `GET /` - 根路径，返回 API 信息
- `GET /health` - 健康检查

### 数据同步

- `POST /api/sync` - 手动触发数据同步

### 评估记录管理

- `GET /api/evaluations` - 获取所有评估记录（支持分页）
- `GET /api/evaluations/{look_name}` - 获取单个评估记录
- `DELETE /api/evaluations/{look_name}` - 删除评估记录

## 数据模型

### LookEvaluation（评估记录）

```python
{
    "id": 1,
    "look_name": "look_1",
    "brand": "Givenchy",
    "theme": "I Am Your Mirror",
    
    # Criteria 评分（6个维度）
    "theme_relevance_score": 7.0,
    "theme_relevance_justification": "...",
    "brand_dna_score": 8.0,
    "brand_dna_justification": "...",
    "innovation_score": 5.0,
    "innovation_justification": "...",
    "aesthetics_score": 7.0,
    "aesthetics_justification": "...",
    "structural_logic_score": 8.0,
    "structural_logic_justification": "...",
    "functionality_score": 7.0,
    "functionality_justification": "...",
    
    # Overall Assessment
    "strengths": "...",
    "weaknesses": "...",
    "improvement_suggestions": "...",
    
    # 图片路径
    "image_path": "E:\\fashion_agents_project\\...\\look_1.png",
    
    # 时间戳
    "created_at": "2026-01-18T15:00:00",
    "updated_at": "2026-01-18T15:00:00"
}
```

## 数据同步机制

### 启动时自动同步

服务启动时会自动：
1. 从 `fashion_config.yaml` 读取 brand 和 theme
2. 扫描评估文件目录
3. 解析所有 `*_evaluation.txt` 文件
4. 增量同步到数据库（已存在则更新，不存在则创建）

### 手动同步

可通过 API 手动触发同步：

```bash
curl -X POST http://localhost:8000/api/sync
```

## 解析器说明

### 评估文档格式要求

评估文档应包含以下部分：

1. **Criteria 表格**: 包含 6 个评估维度
   - Theme Relevance（主题相关性）
   - Brand DNA Alignment（品牌DNA契合度）
   - Innovation & Originality（创新与原创性）
   - Aesthetics & Visual Impact（美学与视觉冲击力）
   - Structural Logic & Material Expression（结构逻辑与材料表达）
   - Anticipated Functionality（预期功能性）

2. **Overall Assessment**: 包含三部分
   - Strengths（优点）
   - Weaknesses（弱点）
   - Improvement Suggestions（改进建议）

### 文件命名规范

- 评估文件: `look_{n}_evaluation.txt`
- 图片文件: `look_{n}.png`

其中 `{n}` 为数字编号。

## 示例请求

### 获取所有评估记录

```bash
curl http://localhost:8000/api/evaluations
```

### 获取单个评估记录

```bash
curl http://localhost:8000/api/evaluations/look_1
```

### 手动同步数据

```bash
curl -X POST http://localhost:8000/api/sync
```

### 删除评估记录

```bash
curl -X DELETE http://localhost:8000/api/evaluations/look_1
```

## 开发说明

### 添加新的 API 端点

在 `main.py` 中添加新的路由函数。

### 修改数据模型

1. 修改 `models.py` 中的数据库模型
2. 修改 `schemas.py` 中的 Pydantic 模型
3. 相应地修改 `parser.py` 中的解析逻辑
4. 删除旧的数据库文件 `fashion_evaluation.db`
5. 重启服务，数据库表会自动重建

### 调试

启动时会打印详细的同步信息，包括：
- 解析的文件数量
- 新增/更新的记录数
- 任何错误或警告信息

## 注意事项

1. **数据库文件**: SQLite 数据库文件 `fashion_evaluation.db` 会在首次运行时自动创建
2. **图片路径**: 确保评估文件对应的 PNG 图片存在
3. **配置文件**: 确保 `fashion_config.yaml` 存在且包含 `brand` 和 `theme` 字段
4. **增量同步**: 相同 `look_name` 的记录会被更新而不是重复创建

## License

MIT License
