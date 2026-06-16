"""鸟类百科 + 排行榜 + 搜索路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import Bird, User
from app.schemas import (
    BirdInfo, BirdRankItem, BirdSearchResult,
    ResponseWrapper, Pagination,
)
from app.services.auth import get_optional_user

router = APIRouter(prefix="/api/birds", tags=["鸟类"])


@router.get("/rankings", response_model=ResponseWrapper)
def get_rankings(
    top_n: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    鸟类搜索排行榜
    按 search_count 降序排列
    """
    birds = db.query(Bird).order_by(desc(Bird.search_count)).limit(top_n).all()

    items = []
    for i, bird in enumerate(birds):
        items.append(BirdRankItem(
            rank=i + 1,
            id=bird.id,
            name=bird.name,
            latin_name=bird.latin_name or "",
            region=bird.region or "",
            habits=bird.habits or "",
            description=bird.description or "",
            image_url=bird.image_url or "",
            search_count=bird.search_count or 0,
        ))

    return ResponseWrapper(data=items)


@router.get("/search", response_model=ResponseWrapper)
def search_birds(
    keyword: str = Query("", max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    搜索鸟类
    按名称（中文名、学名）模糊搜索，匹配后增加 search_count
    """
    keyword = keyword.strip()
    query = db.query(Bird)
    if keyword:
        query = query.filter(
            Bird.name.contains(keyword) | Bird.latin_name.contains(keyword)
        )
    query = query.order_by(desc(Bird.search_count))

    total = query.count()
    birds = query.offset((page - 1) * page_size).limit(page_size).all()

    # 增加搜索次数
    if keyword:
        for bird in birds:
            bird.search_count = (bird.search_count or 0) + 1
        db.commit()

    items = [BirdInfo.model_validate(bird) for bird in birds]

    return ResponseWrapper(data={
        "birds": [item.model_dump() for item in items],
        "pagination": Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    })


@router.get("/{bird_id}", response_model=ResponseWrapper)
def get_bird_detail(
    bird_id: int,
    db: Session = Depends(get_db),
):
    """获取鸟类详情"""
    bird = db.query(Bird).filter(Bird.id == bird_id).first()
    if not bird:
        raise HTTPException(status_code=404, detail="鸟类不存在")

    # 查看也算一次搜索
    bird.search_count = (bird.search_count or 0) + 1
    db.commit()

    return ResponseWrapper(data=BirdInfo.model_validate(bird).model_dump())
