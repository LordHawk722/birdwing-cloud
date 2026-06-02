"""AI 识别记录路由"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import User, RecognitionRecord
from app.schemas import (
    RecognitionCreate, RecognitionRecordInfo,
    ResponseWrapper, Pagination,
)
from app.services.auth import get_current_user
from app.services.bird_ai import recognize_bird
from app.utils import is_allowed_file, save_upload_file
from app.routers.upload import ALLOWED_EXT_NAMES

router = APIRouter(prefix="/api/recognition", tags=["识别"])


@router.post("/analyze", response_model=ResponseWrapper)
async def analyze_image(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    AI 分析图片中的鸟类
    注意：前端需要先调用上传接口获取图片URL，然后将URL传入此接口
    或者直接上传图片到此接口（TODO：支持直接上传）
    当前实现：从数据库中随机返回3种鸟作为识别结果（模拟模式）
    """
    # 调用 AI 识别服务
    result = await recognize_bird("", db)

    # 保存识别记录
    record = RecognitionRecord(
        user_id=current_user.id,
        image_url="",  # 前端上传后再关联
        result=result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ResponseWrapper(data={
        "record_id": record.id,
        "results": result,
    })


@router.post("/analyze-with-image", response_model=ResponseWrapper)
async def analyze_with_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传图片并识别（一步完成）"""
    # 检查文件类型
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXT_NAMES)}",
        )

    # 保存图片
    file_path = await save_upload_file(file, sub_dir="recognition")

    # 调用 AI 识别
    result = await recognize_bird(file_path, db)

    # 保存识别记录
    record = RecognitionRecord(
        user_id=current_user.id,
        image_url=file_path,
        result=result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ResponseWrapper(data={
        "record_id": record.id,
        "image_url": file_path,
        "results": result,
    })


@router.post("/records", response_model=ResponseWrapper)
def create_record(
    data: RecognitionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    记录识别结果（前端分析完成后调用此接口保存）
    """
    record = RecognitionRecord(
        user_id=current_user.id,
        image_url=data.image_url,
        result=[r.model_dump() for r in data.result],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 增加对应鸟类的搜索次数
    for item in data.result:
        from app.models import Bird
        bird = db.query(Bird).filter(Bird.id == item.bird_id).first()
        if bird:
            bird.search_count = (bird.search_count or 0) + 1
    db.commit()

    return ResponseWrapper(data={
        "record_id": record.id,
    })


@router.get("/records", response_model=ResponseWrapper)
def get_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的识别记录"""
    query = db.query(RecognitionRecord).filter(
        RecognitionRecord.user_id == current_user.id
    ).order_by(desc(RecognitionRecord.created_at))

    total = query.count()
    records = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for record in records:
        items.append(RecognitionRecordInfo(
            id=record.id,
            image_url=record.image_url or "",
            result=record.result,
            created_at=record.created_at,
        ))

    return ResponseWrapper(data={
        "items": items,
        "pagination": Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    })


@router.get("/records/{record_id}", response_model=ResponseWrapper)
def get_record_detail(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取识别记录详情"""
    record = db.query(RecognitionRecord).filter(
        RecognitionRecord.id == record_id,
        RecognitionRecord.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    return ResponseWrapper(data=RecognitionRecordInfo(
        id=record.id,
        image_url=record.image_url or "",
        result=record.result,
        created_at=record.created_at,
    ).model_dump())
