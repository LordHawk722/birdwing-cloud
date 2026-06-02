# API 文档

> 本文档详细描述所有 API 接口的请求格式、响应格式和示例。

**基础路径**：`http://localhost:8000`

**内容类型**：`application/json`（上传接口使用 `multipart/form-data`）

## 认证方式

除特别标注"无需登录"的接口外，均需在请求头中携带 JWT Token：

```
Authorization: Bearer <token>
```

Token 在登录/注册时获取，默认有效期为 24 小时。

---

## 通用响应格式

所有接口统一使用以下响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误响应**：

```json
{
  "detail": "错误描述信息"
}
```

HTTP 状态码说明：

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或 token 无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 422 | 请求数据校验失败 |
| 500 | 服务器内部错误 |

---

## 1. 用户模块 `/api/users`

### 1.1 注册

```
POST /api/users/register
```

**无需登录**

**请求体**：

```json
{
  "username": "birdfan",
  "password": "123456"
}
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| username | string | 3-50 字符 | 用户名 |
| password | string | 6-50 字符 | 密码 |

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": 1,
      "username": "birdfan",
      "nickname": "birdfan",
      "avatar": "",
      "bio": "",
      "created_at": "2026-06-03T12:00:00"
    }
  }
}
```

**错误**：400 — 用户名已存在

---

### 1.2 登录

```
POST /api/users/login
```

**无需登录**

**请求体**：

```json
{
  "username": "birdfan",
  "password": "123456"
}
```

**响应**：同注册响应

**错误**：401 — 用户名或密码错误

---

### 1.3 获取当前用户信息

```
GET /api/users/me
```

**需登录**

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "birdfan",
    "nickname": "birdfan",
    "avatar": "",
    "bio": "",
    "created_at": "2026-06-03T12:00:00"
  }
}
```

---

### 1.4 更新个人信息

```
PUT /api/users/me
```

**需登录**

**请求体**（全部可选）：

```json
{
  "nickname": "观鸟达人小王",
  "bio": "热爱自然，热爱鸟类",
  "avatar": "uploads/images/avatar.jpg"
}
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| nickname | string | 最多 100 字符 | 可选 |
| bio | string | 最多 500 字符 | 可选 |
| avatar | string | — | 可选 |

**响应**：返回更新后的用户信息

---

### 1.5 获取指定用户信息

```
GET /api/users/{user_id}
```

**无需登录**

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | int | 用户 ID |

**响应**：返回用户信息对象（同 `GET /me`）

**错误**：404 — 用户不存在

---

## 2. 帖子模块 `/api/posts`

### 2.1 创建帖子

```
POST /api/posts
```

**需登录**

**请求体**：

```json
{
  "title": "今天在公园拍到一只翠鸟",
  "content": "在莲花山公园蹲守了一上午，终于拍到翠鸟捕鱼的精彩瞬间！",
  "images": ["uploads/images/post1.jpg"],
  "location": "深圳莲花山公园"
}
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| title | string | 1-200 字符，必填 | 帖子标题 |
| content | string | — | 帖子内容 |
| images | string[] | — | 图片 URL 列表 |
| location | string | — | 位置信息 |

**响应**：返回完整帖子详情对象

---

### 2.2 帖子列表

```
GET /api/posts?page=1&page_size=10
```

**无需登录**

**查询参数**：

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| page | int | 1 | 页码 |
| page_size | int | 10 | 每页数量（最多 50） |

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "今天在公园拍到一只翠鸟",
        "content": "在莲花山公园蹲守了一上午...",
        "images": ["uploads/images/post1.jpg"],
        "location": "深圳莲花山公园",
        "like_count": 5,
        "comment_count": 3,
        "author_id": 1,
        "author_name": "birdfan",
        "author_avatar": "",
        "created_at": "2026-06-03T12:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

> 列表项中的 content 截取前 200 字符作为摘要。

---

### 2.3 帖子详情

```
GET /api/posts/{post_id}
```

**无需登录**

**路径参数**：`post_id` (int)

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "今天在公园拍到一只翠鸟",
    "content": "在莲花山公园蹲守了一上午，终于拍到翠鸟捕鱼的精彩瞬间！",
    "images": ["uploads/images/post1.jpg"],
    "location": "深圳莲花山公园",
    "like_count": 5,
    "comment_count": 3,
    "is_liked": true,
    "author": {
      "id": 1,
      "username": "birdfan",
      "nickname": "birdfan",
      "avatar": "",
      "bio": "",
      "created_at": "2026-06-03T12:00:00"
    },
    "created_at": "2026-06-03T12:00:00",
    "updated_at": "2026-06-03T14:00:00"
  }
}
```

> `is_liked` 仅在登录用户访问时有效，未登录默认为 false。

**错误**：404 — 帖子不存在

---

### 2.4 更新帖子

```
PUT /api/posts/{post_id}
```

**需登录（仅本人）**

**请求体**（全部可选）：

```json
{
  "title": "更新后的标题",
  "content": "更新后的内容",
  "images": ["uploads/images/new.jpg"],
  "location": "新位置"
}
```

**错误**：
- 404 — 帖子不存在
- 403 — 无权修改（非本人）

---

### 2.5 删除帖子

```
DELETE /api/posts/{post_id}
```

**需登录（仅本人）**

**错误**：
- 404 — 帖子不存在
- 403 — 无权删除（非本人）

---

### 2.6 点赞/取消点赞

```
POST /api/posts/{post_id}/like
```

**需登录**

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "is_liked": true,
    "like_count": 6
  }
}
```

> 已点赞时调用取消点赞，未点赞时调用进行点赞（toggle 模式）。

**错误**：404 — 帖子不存在

---

### 2.7 评论列表

```
GET /api/posts/{post_id}/comments?page=1&page_size=20
```

**无需登录**

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "post_id": 1,
        "content": "翠鸟拍得真清楚！用的什么镜头？",
        "user": {
          "id": 2,
          "username": "birdwatcher",
          "nickname": "观鸟爱好者",
          "avatar": "",
          "bio": "",
          "created_at": "2026-06-03T12:00:00"
        },
        "created_at": "2026-06-03T13:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

**错误**：404 — 帖子不存在

---

### 2.8 发表评论

```
POST /api/posts/{post_id}/comments
```

**需登录**

**请求体**：

```json
{
  "content": "拍得太好了！"
}
```

| 字段 | 类型 | 约束 |
|------|------|------|
| content | string | 1-500 字符，必填 |

**响应**：返回评论详情对象

**错误**：404 — 帖子不存在

---

## 3. 鸟类百科 `/api/birds`

### 3.1 搜索排行榜

```
GET /api/birds/rankings?top_n=10
```

**无需登录**

**查询参数**：

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| top_n | int | 10 | 返回数量（最多 50） |

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "rank": 1,
      "id": 1,
      "name": "麻雀",
      "latin_name": "Passer montanus",
      "region": "全国广泛分布",
      "habits": "群居，适应力强...",
      "description": "最常见的城市鸟类之一",
      "image_url": "https://example.com/images/sparrow.jpg",
      "search_count": 1520
    }
  ]
}
```

> 按 search_count 降序排列。

---

### 3.2 搜索鸟类

```
GET /api/birds/search?keyword=麻雀&page=1&page_size=10
```

**无需登录**

**查询参数**：

| 参数 | 类型 | 默认 | 约束 | 说明 |
|------|------|------|------|------|
| keyword | string | "" | 最多 100 字符 | 搜索关键词（中文名/学名） |
| page | int | 1 | ≥1 | 页码 |
| page_size | int | 10 | 1-50 | 每页数量 |

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "birds": [
      {
        "id": 1,
        "name": "麻雀",
        "latin_name": "Passer montanus",
        "region": "全国广泛分布",
        "habits": "群居，适应力强...",
        "description": "最常见的城市鸟类之一",
        "image_url": "https://example.com/images/sparrow.jpg",
        "search_count": 1521
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

> 匹配成功的鸟类 `search_count` 会自动 +1。支持按中文名和学名模糊搜索。

---

### 3.3 鸟类详情

```
GET /api/birds/{bird_id}
```

**无需登录**

**响应**：返回 `BirdInfo` 对象（同搜索项结构）

> 查看详情也会增加 `search_count`。

**错误**：404 — 鸟类不存在

---

## 4. 文件上传 `/api/upload`

### 4.1 上传图片

```
POST /api/upload/image
```

**无需登录**

**请求体**：`multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| file | File | 图片文件 |

**支持格式**：jpg, jpeg, png, gif, webp

**大小限制**：10MB

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "url": "uploads/images/abc123.jpg",
    "filename": "photo.jpg",
    "size": 24576
  }
}
```

> 返回的 `url` 可直接用于帖子图片和识别记录的 `image_url` 字段。

**错误**：
- 400 — 不支持的文件格式
- 413 — 文件过大

---

## 5. AI 识别 `/api/recognition`

### 5.1 AI 分析图片（模拟）

```
POST /api/recognition/analyze
```

**需登录**

**说明**：当前实现为模拟模式，从数据库中随机返回 3 种鸟类 作为识别结果。配置百度 AI 密钥后自动切换为真实识别。

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "record_id": 1,
    "results": [
      { "bird_id": 1, "name": "麻雀", "confidence": 0.85 },
      { "bird_id": 5, "name": "翠鸟", "confidence": 0.62 },
      { "bird_id": 3, "name": "燕子", "confidence": 0.38 }
    ]
  }
}
```

---

### 5.2 上传并识别

```
POST /api/recognition/analyze-with-image
```

**需登录**

**请求体**：`multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| file | File | 图片文件 |

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "record_id": 1,
    "image_url": "uploads/images/recognition/abc123.jpg",
    "results": [
      { "bird_id": 1, "name": "麻雀", "confidence": 0.85 },
      { "bird_id": 5, "name": "翠鸟", "confidence": 0.62 },
      { "bird_id": 3, "name": "燕子", "confidence": 0.38 }
    ]
  }
}
```

---

### 5.3 保存识别结果

```
POST /api/recognition/records
```

**需登录**

**请求体**：

```json
{
  "image_url": "uploads/images/abc123.jpg",
  "result": [
    { "bird_id": 1, "name": "麻雀", "confidence": 0.85 },
    { "bird_id": 5, "name": "翠鸟", "confidence": 0.62 }
  ]
}
```

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "record_id": 1
  }
}
```

> 保存记录时会增加对应鸟类的搜索次数。

---

### 5.4 识别记录列表

```
GET /api/recognition/records?page=1&page_size=20
```

**需登录**（仅查看自己的记录）

**响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "image_url": "uploads/images/recognition/abc123.jpg",
        "result": [
          { "bird_id": 1, "name": "麻雀", "confidence": 0.85 },
          { "bird_id": 5, "name": "翠鸟", "confidence": 0.62 }
        ],
        "created_at": "2026-06-03T12:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

---

### 5.5 识别记录详情

```
GET /api/recognition/records/{record_id}
```

**需登录**（仅查看自己的记录）

**响应**：返回单个 `RecognitionRecordInfo` 对象

**错误**：404 — 记录不存在

---

## 6. 系统接口

### 6.1 根路径

```
GET /
```

```json
{
  "name": "观鸟小程序 API",
  "version": "1.0.0",
  "docs": "/docs",
  "status": "running"
}
```

### 6.2 健康检查

```
GET /api/health
```

```json
{
  "status": "ok",
  "message": "服务运行正常"
}
```
