# 开发指南

本文档面向参与本项目的开发者，说明开发环境搭建、编码规范、提交规范和测试要求。

---

## 开发环境搭建

### 1. 克隆项目

```bash
git clone <repo-url>
cd bird-backend
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt

# 安装开发依赖
pip install pytest pytest-cov black isort ruff mypy
```

### 4. 启动开发服务器

```bash
# 使用 SQLite 快速启动（不需要 MySQL）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 项目架构

### 分层设计

```
请求 → 路由（routers/）→ 服务（services/）→ 模型（models/）→ 数据库
         │
         ├── 请求校验：schemas.py（Pydantic）
         ├── 认证：services/auth.py（JWT）
         └── 响应：统一 ResponseWrapper 格式
```

### 核心约定

- **路由层**（routers/）处理 HTTP 请求/响应，参数校验
- **服务层**（services/）封装业务逻辑
- **模型层**（models.py）定义数据库表结构
- **Schema 层**（schemas.py）定义请求/响应数据格式

---

## 编码规范

### Python 风格

- 遵循 PEP 8
- 使用类型注解（Type Hints）
- 优先使用不可变数据模式

### 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 类名 | PascalCase | `UserInfo`, `PostCreate` |
| 函数/方法 | snake_case | `get_current_user`, `hash_password` |
| 变量 | snake_case | `user_id`, `db_session` |
| 常量 | UPPER_SNAKE_CASE | `MAX_UPLOAD_SIZE` |
| 路由函数 | snake_case | `list_posts`, `get_bird_detail` |

### 代码风格

- 每行最多 100 字符
- 使用 4 空格缩进
- 导入顺序：标准库 → 第三方库 → 本地模块
- 函数尽量简短（建议 < 50 行）

### 路由命名规范

```
GET    /api/resource        # 列表/查询
POST   /api/resource        # 创建
GET    /api/resource/{id}   # 详情
PUT    /api/resource/{id}   # 更新
DELETE /api/resource/{id}   # 删除
POST   /api/resource/{id}/action  # 动作（如点赞）
```

---

## 如何添加新功能

### 1. 添加新表

在 `models.py` 中添加新模型类：

```python
class NewModel(Base):
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    # ... 其他字段
```

同步更新 `sql/schema.sql` 中的 DDL。

### 2. 添加 Schema

在 `schemas.py` 中添加请求/响应模型：

```python
class NewItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class NewItemInfo(BaseModel):
    id: int
    name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

### 3. 添加路由

在 `app/routers/` 下新建或扩展现有路由文件：

```python
router = APIRouter(prefix="/api/new-items", tags=["新功能"])

@router.get("", response_model=ResponseWrapper)
def list_items(db: Session = Depends(get_db)):
    """获取列表"""
    items = db.query(NewModel).all()
    return ResponseWrapper(data=[NewItemInfo.model_validate(i) for i in items])
```

### 4. 注册路由

在 `app/main.py` 中注册：

```python
app.include_router(new_items.router)
```

### 5. 编写测试

在 `tests/` 下添加测试文件，参考现有测试编写。

---

## 提交规范

### Commit Message 格式

```
<type>: <简短描述>

<可选详细说明>
```

### 类型说明

| 类型 | 使用场景 |
|------|----------|
| feat | 新功能 |
| fix | 修复 Bug |
| refactor | 重构（不改变外部行为） |
| docs | 文档更新 |
| test | 添加或修改测试 |
| chore | 构建/工具/配置变更 |
| perf | 性能优化 |
| ci | CI/CD 配置变更 |

### 提交前检查

- [ ] 代码格式规范（black + isort）
- [ ] 无 lint 错误（ruff）
- [ ] 类型检查通过（mypy）
- [ ] 所有测试通过（pytest）
- [ ] 无调试代码（print 语句等）
- [ ] 测试覆盖率达到 80%+

---

## 测试指南

### 测试运行

```bash
# 运行全部测试
python -m pytest tests/ -v

# 带覆盖率
python -m pytest tests/ --cov=app --cov-report=term-missing

# 按模块
python -m pytest tests/test_posts.py -v -k "test_create"

# 并行运行（需安装 pytest-xdist）
python -m pytest tests/ -n auto
```

### 测试约定

- 测试文件命名：`test_<module>.py`
- 测试函数命名：`test_<功能>_<场景>`
- 使用 AAA 模式：Arrange → Act → Assert
- 测试使用 SQLite 内存数据库，不依赖 MySQL

### 测试示例

```python
def test_register_success(client, db_session):
    """测试注册成功"""
    # Arrange
    data = {"username": "newuser", "password": "123456"}
    
    # Act
    response = client.post("/api/users/register", json=data)
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert "token" in result["data"]
```

---

## 数据库变更流程

### 方式一：开发阶段（推荐）

直接修改 `models.py`，删除 SQLite 数据库文件后重启服务即可重建。

```bash
rm bird_watching.db
uvicorn app.main:app --reload
```

### 方式二：生产环境

需要手动编写迁移 SQL 并更新 `sql/schema.sql`：

```sql
ALTER TABLE birds ADD COLUMN new_column VARCHAR(100) DEFAULT '';
```

---

## AI 识别服务扩展

如需接入真实 AI 识别服务，编辑 `app/services/bird_ai.py` 中的 `_baidu_ai_recognize()` 函数：

```python
async def _baidu_ai_recognize(image_path: str, db: Session) -> Optional[List[dict]]:
    """自定义 AI 识别实现"""
    # 1. 调用外部 API
    # 2. 解析返回结果
    # 3. 与数据库中的鸟类匹配
    # 4. 返回 [{"bird_id": 1, "name": "麻雀", "confidence": 0.95}, ...]
    pass
```

---

## 前端联调建议

1. 后端启动后先访问 `/docs` 确认接口正常
2. 使用 Swagger UI 测试各接口
3. 上传图片后使用返回的 URL 构造完整访问路径
4. 注意所有需登录接口都需要在请求头添加 `Authorization: Bearer <token>`

### 数据流示例：用户发帖

```
前端上传图片 → POST /api/upload/image → 得到图片 URL
前端发帖     → POST /api/posts          → 包含图片 URL 和文本内容
浏览首页     → GET  /api/posts          → 获取帖子列表
查看详情     → GET  /api/posts/{id}     → 获取完整帖子 + 作者信息
点赞         → POST /api/posts/{id}/like → toggle 点赞
```
