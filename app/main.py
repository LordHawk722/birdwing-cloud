"""
鸟趣 - 观鸟识别与分享平台后端
FastAPI + MySQL
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import init_db
from app.routers import users, posts, birds, upload, recognition


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    init_db()
    print(f"[INFO] API docs: http://localhost:{settings.PORT}/docs")
    print("[OK] 鸟趣后端启动成功!")
    yield


# 创建应用
app = FastAPI(
    title="鸟趣 API",
    description="鸟趣 - 观鸟识别与分享平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(birds.router)
app.include_router(upload.router)
app.include_router(recognition.router)

# 静态文件（上传的图片）
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    """根路径"""
    return {
        "name": "鸟趣 API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "message": "服务运行正常"}
