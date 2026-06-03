"""
测试基础设施
- 使用 SQLite 内存数据库（无需真实 MySQL）
- 自动创建和清理测试数据
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import User, Bird
from app.services.auth import hash_password

# ============================================
# SQLite 内存数据库（替代 MySQL）
# ============================================

@pytest.fixture(scope="session")
def test_engine():
    """创建 SQLite 内存引擎"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # 启用 WAL 模式和外键约束
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    """每个测试独立的事务"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI 测试客户端（使用 lifespan=off 跳过 MySQL 连接检查）"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ============================================
# 测试数据
# ============================================

@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "username": "testuser",
        "password": "password123",
    }


@pytest.fixture
def second_user_data():
    """第二个测试用户数据"""
    return {
        "username": "user2",
        "password": "password456",
    }


@pytest.fixture
def auth_headers(client, test_user_data):
    """注册并登录，返回认证头"""
    client.post("/api/users/register", json=test_user_data)
    resp = client.post("/api/users/login", json=test_user_data)
    token = resp.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(client, second_user_data):
    """第二个用户的认证头"""
    client.post("/api/users/register", json=second_user_data)
    resp = client.post("/api/users/login", json=second_user_data)
    token = resp.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_birds(db_session):
    """预置鸟类测试数据"""
    birds = [
        Bird(name="麻雀", latin_name="Passer montanus", region="全国",
             habits="群居", description="最常见鸟类", image_url="sparrow.jpg",
             search_count=100),
        Bird(name="喜鹊", latin_name="Pica pica", region="全国",
             habits="成对活动", description="吉祥鸟", image_url="magpie.jpg",
             search_count=80),
        Bird(name="燕子", latin_name="Hirundo rustica", region="全国",
             habits="候鸟", description="捕食昆虫", image_url="swallow.jpg",
             search_count=60),
        Bird(name="翠鸟", latin_name="Alcedo atthis", region="南方",
             habits="俯冲捕鱼", description="羽毛翠蓝", image_url="kingfisher.jpg",
             search_count=40),
        Bird(name="丹顶鹤", latin_name="Grus japonensis", region="东北",
             habits="湿地栖息", description="传统文化吉祥鸟", image_url="crane.jpg",
             search_count=20),
    ]
    for bird in birds:
        db_session.add(bird)
    db_session.commit()
    return birds
