"""鸟类百科模块接口测试"""
import pytest


class TestBirdRankings:
    """排行榜测试"""

    def test_rankings_default_top10(self, client, seed_birds):
        """默认返回前10名"""
        resp = client.get("/api/birds/rankings")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) == 5  # 种子数据有5种鸟
        # 按 search_count 降序
        assert data[0]["name"] == "麻雀"  # search_count=100
        assert data[0]["rank"] == 1
        assert data[-1]["name"] == "丹顶鹤"  # search_count=20
        assert data[-1]["rank"] == 5

    def test_rankings_limit(self, client, seed_birds):
        """限制返回数量"""
        resp = client.get("/api/birds/rankings?top_n=3")
        data = resp.json()["data"]
        assert len(data) == 3

    def test_rankings_structure(self, client, seed_birds):
        """排行榜数据字段完整"""
        resp = client.get("/api/birds/rankings")
        item = resp.json()["data"][0]
        assert "rank" in item
        assert "name" in item
        assert "search_count" in item
        assert "region" in item
        assert "habits" in item
        assert "description" in item
        assert "image_url" in item


class TestBirdSearch:
    """搜索测试"""

    def test_search_by_name(self, client, seed_birds):
        """按中文名搜索"""
        resp = client.get("/api/birds/search?keyword=麻雀")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["birds"]) >= 1
        assert data["birds"][0]["name"] == "麻雀"

    def test_search_by_latin_name(self, client, seed_birds):
        """按学名搜索"""
        resp = client.get("/api/birds/search?keyword=Pica")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["birds"]) >= 1
        assert data["birds"][0]["name"] == "喜鹊"

    def test_search_partial(self, client, seed_birds):
        """部分匹配"""
        resp = client.get("/api/birds/search?keyword=雀")
        assert resp.status_code == 200
        data = resp.json()["data"]
        names = [b["name"] for b in data["birds"]]
        assert "麻雀" in names

    def test_search_no_result(self, client, seed_birds):
        """无匹配结果"""
        resp = client.get("/api/birds/search?keyword=霸王龙")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["birds"]) == 0
        assert data["pagination"]["total"] == 0

    def test_search_empty_keyword(self, client, seed_birds):
        """空关键词返回空"""
        resp = client.get("/api/birds/search?keyword=")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["birds"]) == 0

    def test_search_increases_count(self, client, seed_birds):
        """搜索增加计数"""
        # 先查当前计数
        resp = client.get("/api/birds/search?keyword=麻雀")
        count_before = resp.json()["data"]["birds"][0]["search_count"]

        # 再搜一次
        resp = client.get("/api/birds/search?keyword=麻雀")
        count_after = resp.json()["data"]["birds"][0]["search_count"]

        assert count_after > count_before


class TestBirdDetail:
    """鸟类详情测试"""

    def test_get_bird_detail(self, client, seed_birds):
        """获取鸟类详情"""
        # 先搜索拿到 ID
        resp = client.get("/api/birds/search?keyword=翠鸟")
        bird_id = resp.json()["data"]["birds"][0]["id"]

        resp = client.get(f"/api/birds/{bird_id}")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["name"] == "翠鸟"
        assert data["latin_name"] == "Alcedo atthis"
        assert data["region"] == "南方"

    def test_get_bird_detail_increases_count(self, client, seed_birds):
        """查看详情也增加搜索次数"""
        resp = client.get("/api/birds/search?keyword=翠鸟")
        bird_id = resp.json()["data"]["birds"][0]["id"]
        count_before = resp.json()["data"]["birds"][0]["search_count"]

        client.get(f"/api/birds/{bird_id}")

        resp = client.get(f"/api/birds/{bird_id}")
        count_after = resp.json()["data"]["search_count"]
        assert count_after > count_before

    def test_get_nonexistent_bird(self, client):
        """不存在的鸟类"""
        resp = client.get("/api/birds/99999")
        assert resp.status_code == 404
