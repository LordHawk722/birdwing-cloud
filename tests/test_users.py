"""用户模块接口测试"""
import pytest


class TestUserRegister:
    """用户注册测试"""

    def test_register_success(self, client):
        """注册成功"""
        resp = client.post("/api/users/register", json={
            "username": "newuser",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert "token" in data["data"]
        assert data["data"]["user"]["username"] == "newuser"

    def test_register_duplicate_username(self, client, test_user_data):
        """重复用户名注册失败"""
        client.post("/api/users/register", json=test_user_data)
        resp = client.post("/api/users/register", json=test_user_data)
        assert resp.status_code == 400
        assert "已存在" in resp.json()["detail"]

    def test_register_short_username(self, client):
        """用户名太短"""
        resp = client.post("/api/users/register", json={
            "username": "ab",
            "password": "password123",
        })
        assert resp.status_code == 422  # Pydantic 校验错误

    def test_register_short_password(self, client):
        """密码太短"""
        resp = client.post("/api/users/register", json={
            "username": "validuser",
            "password": "12345",
        })
        assert resp.status_code == 422


class TestUserLogin:
    """用户登录测试"""

    def test_login_success(self, client, test_user_data):
        """登录成功"""
        client.post("/api/users/register", json=test_user_data)
        resp = client.post("/api/users/login", json=test_user_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert "token" in data["data"]

    def test_login_wrong_password(self, client, test_user_data):
        """密码错误"""
        client.post("/api/users/register", json=test_user_data)
        resp = client.post("/api/users/login", json={
            "username": test_user_data["username"],
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        """用户不存在"""
        resp = client.post("/api/users/login", json={
            "username": "nobody",
            "password": "password123",
        })
        assert resp.status_code == 401


class TestUserProfile:
    """用户信息测试"""

    def test_get_my_info(self, client, auth_headers, test_user_data):
        """获取当前用户信息"""
        resp = client.get("/api/users/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data
        assert "created_at" in data

    def test_get_my_info_unauthorized(self, client):
        """未登录无法获取信息"""
        resp = client.get("/api/users/me")
        assert resp.status_code == 401  # 无 Bearer token

    def test_update_profile(self, client, auth_headers):
        """更新个人信息"""
        resp = client.put("/api/users/me", headers=auth_headers, json={
            "nickname": "新昵称",
            "bio": "新的个人简介",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["nickname"] == "新昵称"
        assert data["bio"] == "新的个人简介"

    def test_update_profile_partial(self, client, auth_headers):
        """部分更新"""
        resp = client.put("/api/users/me", headers=auth_headers, json={
            "nickname": "仅改昵称",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["nickname"] == "仅改昵称"
        # 其他字段不应变化
        assert "bio" in data

    def test_get_user_by_id(self, client, auth_headers):
        """获取指定用户信息"""
        # 先获取自己的ID
        me = client.get("/api/users/me", headers=auth_headers).json()["data"]
        user_id = me["id"]

        resp = client.get(f"/api/users/{user_id}")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["username"] == me["username"]

    def test_get_nonexistent_user(self, client):
        """获取不存在的用户"""
        resp = client.get("/api/users/99999")
        assert resp.status_code == 404
