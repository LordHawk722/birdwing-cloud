# 众翼云鉴：智能鸟类摄享平台

> BirdWing Cloud — 智能鸟类识别与分享社区

## 项目结构

```
birdwing-cloud/
├── frontend/          # Vue 3 Web 前端
│   ├── src/
│   │   ├── pages/     # 8 个页面
│   │   ├── components/# 共享组件
│   │   ├── router/    # 路由配置
│   │   ├── api/       # API 服务层
│   │   ├── config/    # 配置文件
│   │   ├── utils/     # 工具函数
│   │   └── styles/    # 全局样式
│   └── ...
└── (后端待添加)
```

## 前端技术栈

- **Vue 3** (Composition API)
- **Vue Router 4**
- **Vite 5**
- **Axios**
- **SCSS**

## 快速开始

```bash
cd frontend
npm install
npm run dev
```

开发服务器默认运行在 `http://localhost:3000`。

## 页面路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | 首页 | Banner轮播 + 搜索 + 瀑布流 |
| `/upload` | 上传 | 图片上传与分析 |
| `/map` | 地图 | 鸟类观测点地图 |
| `/profile` | 我的 | 个人中心 |
| `/ranking` | 排行榜 | 热门鸟类排行 |
| `/guide` | 引导 | 新手指南 |
| `/ai-chat` | AI助理 | 鸟类知识问答 |
| `/encyclopedia` | 图鉴 | 鸟类卡片翻阅 |
