# 鸟趣 · 观鸟 Web 后端

基于 **FastAPI + MySQL** 构建的观鸟识别与分享平台 Web API，提供鸟类识别、社交分享、百科查询等功能。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 框架 | **FastAPI** (Python 3.10+) | 高性能异步框架，自动生成 OpenAPI 文档 |
| 数据库 | **MySQL 8.0+**（主）/ **SQLite**（回退） | PyMySQL 驱动，SQLAlchemy 2.0 ORM |
| 认证 | **JWT** (python-jose) | Bearer Token，24 小时过期 |
| 密码 | **PBKDF2\_SHA256** (passlib) | 无需编译 C 扩展，兼容性好 |
| AI 识别 | **模拟模式**（内置）/ **百度 AI**（可选） | 加权随机返回鸟类预测结果 |
| 测试 | **pytest** + SQLite 内存数据库 | 60 个测试用例，覆盖全部接口 |

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+（可选 — 无 MySQL 时自动降级为 SQLite）

### 安装

```bash
pip install -r requirements.txt
```

### 配置

编辑 `.env` 文件配置数据库连接（可选 — 不配置则使用 SQLite）：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=bird_watching
```

> 提示：不配置 MySQL 时系统自动使用 `bird_watching.db`（SQLite）运行，适合本地开发测试。

### 启动

```bash
# 开发模式（热重载）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 或直接运行
python -m app.main
```

启动后访问：
- **Swagger 文档**：http://localhost:8000/docs
- **ReDoc 文档**：http://localhost:8000/redoc
- **健康检查**：http://localhost:8000/api/health

### 初始化数据

项目启动时自动建表。如需填充测试数据，手动执行：

```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p < sql/seed.sql
```

## 项目结构

```
bird-backend/
├── app/
│   ├── main.py                 # 应用入口、CORS、路由注册
│   ├── config.py               # 环境配置
│   ├── database.py             # 数据库引擎（自动降级）
│   ├── models.py               # 数据模型（6 张表）
│   ├── schemas.py              # Pydantic 请求/响应模型
│   ├── utils.py                # 文件上传工具函数
│   ├── routers/
│   │   ├── users.py            # 用户模块路由
│   │   ├── posts.py            # 帖子模块路由
│   │   ├── birds.py            # 鸟类百科路由
│   │   ├── upload.py           # 文件上传路由
│   │   └── recognition.py      # AI 识别路由
│   └── services/
│       ├── auth.py             # JWT 认证服务
│       └── bird_ai.py          # AI 识别服务
├── sql/
│   ├── schema.sql              # 数据库 DDL
│   └── seed.sql                # 种子数据
├── tests/
│   ├── conftest.py             # 测试基础设施
│   ├── test_users.py           # 用户模块测试
│   ├── test_posts.py           # 帖子模块测试
│   ├── test_birds.py           # 鸟类百科测试
│   ├── test_upload.py          # 上传模块测试
│   └── test_recognition.py     # 识别模块测试
├── docs/
│   ├── API.md                  # API 文档
│   ├── DEPLOY.md               # 部署指南
│   └── DEV.md                  # 开发指南
├── uploads/images/             # 上传图片存储
├── requirements.txt
├── pyproject.toml
└── .env                        # 环境变量（不入库）
```

## 数据库设计

6 张表，完整外键约束与索引：

| 表 | 说明 | 核心字段 |
|----|------|----------|
| `users` | 用户 | username, password\_hash, nickname, avatar, bio |
| `posts` | 帖子 | user\_id(FK), title, content, images(JSON), location |
| `post\_likes` | 点赞记录 | user\_id(FK), post\_id(FK), UNIQUE(user\_id, post\_id) |
| `comments` | 评论 | user\_id(FK), post\_id(FK), content |
| `birds` | 鸟类百科 | name, latin\_name, region, habits, description, image\_url |
| `recognition\_records` | 识别记录 | user\_id(FK), image\_url, result(JSON) |

DDL 详见 [sql/schema.sql](sql/schema.sql)。

## API 概览

详细文档（含请求/响应示例）见 [docs/API.md](docs/API.md)。

### 用户 `/api/users`
| 方法 | 路径 | 说明 | 需登录 |
|------|------|------|--------|
| POST | `/api/users/register` | 注册 | ❌ |
| POST | `/api/users/login` | 登录 | ❌ |
| GET | `/api/users/me` | 获取当前用户信息 | ✅ |
| PUT | `/api/users/me` | 更新个人信息 | ✅ |
| GET | `/api/users/{id}` | 获取指定用户信息 | ❌ |

### 帖子 `/api/posts`
| 方法 | 路径 | 说明 | 需登录 |
|------|------|------|--------|
| POST | `/api/posts` | 创建帖子 | ✅ |
| GET | `/api/posts` | 帖子列表（分页） | ❌ |
| GET | `/api/posts/{id}` | 帖子详情 | ❌ |
| PUT | `/api/posts/{id}` | 更新帖子 | ✅（本人） |
| DELETE | `/api/posts/{id}` | 删除帖子 | ✅（本人） |
| POST | `/api/posts/{id}/like` | 点赞/取消点赞 | ✅ |
| GET | `/api/posts/{id}/comments` | 评论列表（分页） | ❌ |
| POST | `/api/posts/{id}/comments` | 发表评论 | ✅ |

### 鸟类百科 `/api/birds`
| 方法 | 路径 | 说明 | 需登录 |
|------|------|------|--------|
| GET | `/api/birds/rankings` | 搜索排行榜 | ❌ |
| GET | `/api/birds/search` | 搜索鸟类（模糊匹配） | ❌ |
| GET | `/api/birds/{id}` | 鸟类详情 | ❌ |

### 上传 `/api/upload`
| 方法 | 路径 | 说明 | 需登录 |
|------|------|------|--------|
| POST | `/api/upload/image` | 上传图片（jpg/png/gif/webp） | ❌ |

### AI 识别 `/api/recognition`
| 方法 | 路径 | 说明 | 需登录 |
|------|------|------|--------|
| POST | `/api/recognition/analyze` | AI 分析图片（模拟识别） | ✅ |
| POST | `/api/recognition/analyze-with-image` | 上传图片并识别（一步完成） | ✅ |
| POST | `/api/recognition/records` | 保存识别结果 | ✅ |
| GET | `/api/recognition/records` | 识别记录列表 | ✅ |
| GET | `/api/recognition/records/{id}` | 识别记录详情 | ✅ |

## AI 识别

当前提供**模拟识别模式**，随机从数据库中选取鸟类作为识别结果。若需对接真实 AI：

1. 注册[百度 AI 开放平台](https://ai.baidu.com/)
2. 创建「动物识别」应用，获取密钥
3. 填入 `.env`：
   ```env
   BAIDU_APP_ID=your_app_id
   BAIDU_API_KEY=your_api_key
   BAIDU_SECRET_KEY=your_secret_key
   ```
4. 重启服务即可

## 测试

```bash
# 运行全部测试
python -m pytest tests/ -v

# 按模块
python -m pytest tests/test_users.py -v
python -m pytest tests/test_posts.py -v

# 带覆盖率
python -m pytest tests/ --cov=app
```

> 测试使用 SQLite 内存数据库，无需安装 MySQL。

## 部署

完整部署指南见 [docs/DEPLOY.md](docs/DEPLOY.md)。

```bash
# 生产环境快速启动
pip install gunicorn
nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 > app.log 2>&1 &
```

## 开发指南

参见 [docs/DEV.md](docs/DEV.md) 了解编码规范、提交规范和开发工作流。

## 许可证

本项目为课程项目，仅供学习交流使用。
