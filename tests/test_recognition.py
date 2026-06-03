"""AI 识别模块接口测试"""
import pytest


class TestRecognition:
    """识别功能测试"""

    def test_analyze(self, client, auth_headers, seed_birds):
        """AI 分析（模拟模式）"""
        resp = client.post("/api/recognition/analyze", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "record_id" in data
        assert "results" in data
        assert len(data["results"]) == 3  # 返回 Top3
        for r in data["results"]:
            assert "bird_id" in r
            assert "name" in r
            assert "confidence" in r
            assert 0 <= r["confidence"] <= 1

    def test_analyze_requires_auth(self, client):
        """未登录不能使用识别"""
        resp = client.post("/api/recognition/analyze")
        assert resp.status_code == 401

    def test_create_record(self, client, auth_headers, seed_birds):
        """手动保存识别记录"""
        resp = client.post("/api/recognition/records", headers=auth_headers, json={
            "image_url": "uploads/test.jpg",
            "result": [
                {"bird_id": 1, "name": "麻雀", "confidence": 0.85},
                {"bird_id": 2, "name": "喜鹊", "confidence": 0.62},
                {"bird_id": 3, "name": "燕子", "confidence": 0.31},
            ],
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "record_id" in data

    def test_get_records(self, client, auth_headers, seed_birds):
        """获取识别记录列表"""
        # 先创建两条记录
        client.post("/api/recognition/records", headers=auth_headers, json={
            "image_url": "uploads/test1.jpg",
            "result": [{"bird_id": 1, "name": "麻雀", "confidence": 0.85}],
        })
        client.post("/api/recognition/records", headers=auth_headers, json={
            "image_url": "uploads/test2.jpg",
            "result": [{"bird_id": 2, "name": "喜鹊", "confidence": 0.72}],
        })

        resp = client.get("/api/recognition/records", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["items"]) >= 2

    def test_get_record_detail(self, client, auth_headers, seed_birds):
        """获取识别记录详情"""
        # 创建记录
        create_resp = client.post("/api/recognition/records", headers=auth_headers, json={
            "image_url": "uploads/test.jpg",
            "result": [{"bird_id": 1, "name": "麻雀", "confidence": 0.85}],
        })
        record_id = create_resp.json()["data"]["record_id"]

        # 获取详情
        resp = client.get(f"/api/recognition/records/{record_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == record_id
        assert len(data["result"]) == 1
        assert data["result"][0]["name"] == "麻雀"

    def test_get_others_record(self, client, auth_headers, second_auth_headers, seed_birds):
        """不能查看别人的识别记录"""
        create_resp = client.post("/api/recognition/records", headers=auth_headers, json={
            "image_url": "uploads/test.jpg",
            "result": [{"bird_id": 1, "name": "麻雀", "confidence": 0.85}],
        })
        record_id = create_resp.json()["data"]["record_id"]

        resp = client.get(f"/api/recognition/records/{record_id}", headers=second_auth_headers)
        assert resp.status_code == 404  # 别人的记录看不到

    def test_records_pagination(self, client, auth_headers, seed_birds):
        """识别记录分页"""
        for i in range(3):
            client.post("/api/recognition/records", headers=auth_headers, json={
                "image_url": f"uploads/test{i}.jpg",
                "result": [{"bird_id": 1, "name": "麻雀", "confidence": 0.85}],
            })

        resp = client.get("/api/recognition/records?page=1&page_size=2", headers=auth_headers)
        data = resp.json()["data"]
        assert len(data["items"]) == 2
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["total_pages"] == 2


class TestAuthGuard:
    """认证守卫测试"""

    def test_register_no_auth_needed(self, client):
        """注册不需要登录"""
        resp = client.post("/api/users/register", json={
            "username": "public_user",
            "password": "password123",
        })
        assert resp.status_code == 200

    @pytest.mark.parametrize("endpoint,method,body", [
        ("/api/posts", "post", {"title": "test", "content": "test"}),
        ("/api/recognition/analyze", "post", None),
        ("/api/recognition/records", "get", None),
        ("/api/users/me", "get", None),
        ("/api/users/me", "put", {"nickname": "test"}),
    ])
    def test_guarded_endpoints(self, client, endpoint, method, body):
        """需要登录的接口返回 401"""
        if method == "post":
            resp = client.post(endpoint, json=body or {})
        elif method == "put":
            resp = client.put(endpoint, json=body or {})
        else:
            resp = client.get(endpoint)
        assert resp.status_code == 401

    def test_public_endpoints(self, client, seed_birds):
        """不需要登录的接口可以访问"""
        # 帖子列表
        assert client.get("/api/posts").status_code == 200
        # 鸟类排行榜
        assert client.get("/api/birds/rankings").status_code == 200
        # 鸟类搜索
        assert client.get("/api/birds/search?keyword=麻雀").status_code == 200
        # 健康检查
        assert client.get("/api/health").status_code == 200
