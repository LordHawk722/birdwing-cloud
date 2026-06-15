"""数据库连接"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
    connect_args={"connect_timeout": 10, "read_timeout": 30, "write_timeout": 30},
)

try:
    with engine.connect() as conn:
        conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    print("[OK] MySQL 数据库连接成功")
except Exception as e:
    print(f"[FATAL] MySQL 连接失败: {e}", file=sys.stderr)
    raise

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
Base = declarative_base()


def get_db():
    """获取数据库会话（用于 FastAPI 依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    import app.models  # noqa: F401 - 注册模型
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] 数据库表已创建")
    except Exception as e:
        print(f"[WARN] 数据库表创建失败: {e}", file=sys.stderr)
