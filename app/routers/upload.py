"""文件上传路由"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.config import settings
from app.utils import is_allowed_file, save_upload_file
from app.schemas import ResponseWrapper

router = APIRouter(prefix="/api/upload", tags=["上传"])

# 允许的扩展名（用于错误提示）
ALLOWED_EXT_NAMES = ["jpg", "jpeg", "png", "gif", "webp"]


@router.post("/image", response_model=ResponseWrapper)
async def upload_image(file: UploadFile = File(...)):
    """上传图片"""
    # 检查文件类型
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXT_NAMES)}",
        )

    # 检查文件大小
    contents = await file.read()
    file_size = len(contents)
    if file_size > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE / 1024 / 1024
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大，最大支持 {max_mb:.0f}MB",
        )

    try:
        # 将文件指针重置到开头
        await file.seek(0)
        file_path = await save_upload_file(file, sub_dir="images")
        return ResponseWrapper(data={
            "url": file_path,
            "filename": file.filename,
            "size": file_size,
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}",
        )
