"""帖子模块接口测试"""
import pytest


class TestPostCRUD:
    """帖子增删改查测试"""

    def test_create_post(self, client, auth_headers):
        """创建帖子"""
        resp = client.post("/api/posts", headers=auth_headers, json={
            "title": "今天看到一只翠鸟",
            "content": "在公园里发现了一只漂亮的翠鸟！",
            "location": "莲花山公园",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["title"] == "今天看到一只翠鸟"
        assert data["content"] == "在公园里发现了一只漂亮的翠鸟！"
        assert data["location"] == "莲花山公园"
        assert data["like_count"] == 0
        assert data["comment_count"] == 0
        assert data["author"]["username"] == "testuser"

    def test_create_post_empty_title(self, client, auth_headers):
        """标题不能为空"""
        resp = client.post("/api/posts", headers=auth_headers, json={
            "title": "",
            "content": "内容",
        })
        assert resp.status_code == 422

    def test_list_posts(self, client, auth_headers):
        """获取帖子列表"""
        # 创建2篇帖子
        client.post("/api/posts", headers=auth_headers, json={"title": "帖子1", "content": "内容1"})
        client.post("/api/posts", headers=auth_headers, json={"title": "帖子2", "content": "内容2"})

        resp = client.get("/api/posts")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["items"]) == 2
        assert data["pagination"]["total"] == 2

    def test_list_posts_pagination(self, client, auth_headers):
        """帖子列表分页"""
        for i in range(5):
            client.post("/api/posts", headers=auth_headers, json={"title": f"帖子{i}", "content": "内容"})

        # 第一页，每页2条
        resp = client.get("/api/posts?page=1&page_size=2")
        data = resp.json()["data"]
        assert len(data["items"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["total_pages"] == 3

        # 第三页
        resp = client.get("/api/posts?page=3&page_size=2")
        data = resp.json()["data"]
        assert len(data["items"]) == 1

    def test_get_post_detail(self, client, auth_headers):
        """获取帖子详情"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={
            "title": "测试帖子",
            "content": "测试内容",
        })
        post_id = create_resp.json()["data"]["id"]

        resp = client.get(f"/api/posts/{post_id}")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["title"] == "测试帖子"
        assert data["author"]["username"] == "testuser"

    def test_get_nonexistent_post(self, client):
        """获取不存在的帖子"""
        resp = client.get("/api/posts/99999")
        assert resp.status_code == 404

    def test_update_post(self, client, auth_headers):
        """更新帖子"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={
            "title": "原标题",
            "content": "原内容",
        })
        post_id = create_resp.json()["data"]["id"]

        resp = client.put(f"/api/posts/{post_id}", headers=auth_headers, json={
            "title": "新标题",
            "content": "新内容",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["title"] == "新标题"
        assert data["content"] == "新内容"

    def test_update_others_post(self, client, auth_headers, second_auth_headers):
        """不能修改别人的帖子"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={
            "title": "别人的帖子",
        })
        post_id = create_resp.json()["data"]["id"]

        resp = client.put(f"/api/posts/{post_id}", headers=second_auth_headers, json={
            "title": "想修改",
        })
        assert resp.status_code == 403

    def test_delete_post(self, client, auth_headers):
        """删除帖子"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={"title": "待删除"})
        post_id = create_resp.json()["data"]["id"]

        resp = client.delete(f"/api/posts/{post_id}", headers=auth_headers)
        assert resp.status_code == 200

        # 确认已删除
        resp = client.get(f"/api/posts/{post_id}")
        assert resp.status_code == 404

    def test_delete_others_post(self, client, auth_headers, second_auth_headers):
        """不能删除别人的帖子"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={"title": "别人的帖子"})
        post_id = create_resp.json()["data"]["id"]

        resp = client.delete(f"/api/posts/{post_id}", headers=second_auth_headers)
        assert resp.status_code == 403


class TestPostLike:
    """点赞测试"""

    def test_like_post(self, client, auth_headers):
        """点赞帖子"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={"title": "点赞测试"})
        post_id = create_resp.json()["data"]["id"]

        resp = client.post(f"/api/posts/{post_id}/like", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["is_liked"] is True
        assert data["like_count"] == 1

    def test_unlike_post(self, client, auth_headers):
        """取消点赞"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={"title": "取消点赞"})
        post_id = create_resp.json()["data"]["id"]

        # 点赞
        client.post(f"/api/posts/{post_id}/like", headers=auth_headers)
        # 取消点赞
        resp = client.post(f"/api/posts/{post_id}/like", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["is_liked"] is False
        assert data["like_count"] == 0

    def test_multiple_users_like(self, client, auth_headers, second_auth_headers):
        """多个用户点赞同一帖子"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={"title": "多人点赞"})
        post_id = create_resp.json()["data"]["id"]

        # 用户1点赞
        client.post(f"/api/posts/{post_id}/like", headers=auth_headers)
        # 用户2点赞
        client.post(f"/api/posts/{post_id}/like", headers=second_auth_headers)

        # 查看帖子详情，is_liked 基于当前用户
        resp = client.get(f"/api/posts/{post_id}", headers=auth_headers)
        assert resp.json()["data"]["is_liked"] is True
        assert resp.json()["data"]["like_count"] == 2

    def test_like_nonexistent_post(self, client, auth_headers):
        """点赞不存在的帖子"""
        resp = client.post("/api/posts/99999/like", headers=auth_headers)
        assert resp.status_code == 404


class TestComment:
    """评论测试"""

    def test_create_comment(self, client, auth_headers):
        """发表评论"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={"title": "评论测试"})
        post_id = create_resp.json()["data"]["id"]

        resp = client.post(f"/api/posts/{post_id}/comments", headers=auth_headers, json={
            "content": "好棒的观鸟记录！",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["content"] == "好棒的观鸟记录！"
        assert data["user"]["username"] == "testuser"

    def test_list_comments(self, client, auth_headers, second_auth_headers):
        """获取评论列表"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={"title": "多评论测试"})
        post_id = create_resp.json()["data"]["id"]

        # 两个用户各发一条评论
        client.post(f"/api/posts/{post_id}/comments", headers=auth_headers, json={"content": "评论1"})
        client.post(f"/api/posts/{post_id}/comments", headers=second_auth_headers, json={"content": "评论2"})

        resp = client.get(f"/api/posts/{post_id}/comments")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["items"]) == 2

    def test_comment_updates_count(self, client, auth_headers):
        """评论后帖子评论数增加"""
        create_resp = client.post("/api/posts", headers=auth_headers, json={"title": "计数测试"})
        post_id = create_resp.json()["data"]["id"]
        assert create_resp.json()["data"]["comment_count"] == 0

        client.post(f"/api/posts/{post_id}/comments", headers=auth_headers, json={"content": "一条评论"})

        resp = client.get(f"/api/posts/{post_id}")
        assert resp.json()["data"]["comment_count"] == 1
