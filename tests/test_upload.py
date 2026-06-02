"""上传模块接口测试"""
import io
import pytest
from PIL import Image


def _create_test_image(width=100, height=100, format="JPEG"):
    """创建测试图片"""
    img = Image.new("RGB", (width, height), color="red")
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf


class TestUpload:
    """上传测试"""

    def test_upload_image_success(self, client):
        """上传图片成功"""
        buf = _create_test_image()
        resp = client.post(
            "/api/upload/image",
            files={"file": ("test.jpg", buf, "image/jpeg")},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "url" in data
        assert data["url"].startswith("uploads/")

    def test_upload_invalid_extension(self, client):
        """不支持的文件格式"""
        resp = client.post(
            "/api/upload/image",
            files={"file": ("test.exe", io.BytesIO(b"fake content"), "application/x-msdownload")},
        )
        assert resp.status_code == 400
        assert "不支持" in resp.json()["detail"]

    def test_upload_png_success(self, client):
        """PNG格式也可以"""
        buf = _create_test_image(format="PNG")
        resp = client.post(
            "/api/upload/image",
            files={"file": ("test.png", buf, "image/png")},
        )
        assert resp.status_code == 200

    def test_upload_no_file(self, client):
        """没传文件"""
        resp = client.post("/api/upload/image")
        assert resp.status_code == 422  # FastAPI 校验错误
