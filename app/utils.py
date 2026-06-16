"""工具函数"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import settings


def generate_uuid() -> str:
    """生成唯一ID"""
    return uuid.uuid4().hex


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    ext = get_file_extension(filename)
    return ext in settings.ALLOWED_EXTENSIONS


def check_file_size(content: bytes) -> None:
    """检查文件大小是否超过限制"""
    if len(content) > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE / 1024 / 1024
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大，最大支持 {max_mb:.0f}MB",
        )


async def save_upload_file(file: UploadFile, sub_dir: str = "images") -> str:
    """
    保存上传文件到 OSS，返回完整 URL
    未配置 OSS 时降级为本地存储
    """
    ext = get_file_extension(file.filename)
    filename = f"{generate_uuid()}.{ext}"

    content = await file.read()
    check_file_size(content)

    # 优先使用 OSS
    if settings.OSS_ACCESS_KEY_ID:
        return await _upload_to_oss(content, filename, sub_dir)

    # 降级为本地存储
    return await _save_to_local(content, filename, sub_dir)


async def _upload_to_oss(content: bytes, filename: str, sub_dir: str) -> str:
    """上传到阿里云 OSS，返回完整 URL"""
    import oss2

    auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET)

    object_key = f"uploads/{sub_dir}/{filename}"
    try:
        result = bucket.put_object(object_key, content)
        print(f"[OSS] 上传成功: {object_key}, status={result.status}")
    except Exception as e:
        print(f"[OSS] 上传失败: {e}")
        raise

    return f"https://{settings.OSS_BUCKET}.{settings.OSS_ENDPOINT}/{object_key}"


async def _save_to_local(content: bytes, filename: str, sub_dir: str) -> str:
    """降级为本地存储，返回相对路径"""
    save_dir = Path(settings.UPLOAD_DIR) / sub_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    save_path = save_dir / filename
    with open(save_path, "wb") as f:
        f.write(content)

    return f"uploads/{sub_dir}/{filename}"
