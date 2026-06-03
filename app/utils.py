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
    保存上传文件，返回相对路径
    """
    # 生成唯一文件名
    ext = get_file_extension(file.filename)
    filename = f"{generate_uuid()}.{ext}"

    # 创建目录
    save_dir = Path(settings.UPLOAD_DIR) / sub_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    # 读取并检查大小
    content = await file.read()
    check_file_size(content)

    # 保存文件
    save_path = save_dir / filename
    with open(save_path, "wb") as f:
        f.write(content)

    # 返回相对路径（用于构建URL）
    return f"uploads/{sub_dir}/{filename}"
