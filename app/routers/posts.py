"""帖子模块路由"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import User, Post, PostLike, Comment
from app.schemas import (
    PostCreate, PostUpdate, PostInfo, PostListItem,
    CommentCreate, CommentInfo, UserInfo,
    ResponseWrapper, Pagination,
)
from app.services.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api/posts", tags=["帖子"])


@router.post("", response_model=ResponseWrapper)
def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建帖子"""
    post = Post(
        user_id=current_user.id,
        title=data.title,
        content=data.content,
        images=data.images,
        location=data.location,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return ResponseWrapper(data=_post_to_detail(post, current_user, db))


@router.get("", response_model=ResponseWrapper)
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """获取帖子列表（首页）"""
    query = db.query(Post).order_by(desc(Post.created_at))
    total = query.count()
    posts = query.offset((page - 1) * page_size).limit(page_size).all()

    # 构建列表数据
    user_ids = [p.user_id for p in posts]
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    items = []
    for post in posts:
        author = users.get(post.user_id)
        items.append(PostListItem(
            id=post.id,
            title=post.title,
            content=post.content[:200] if post.content else "",  # 截取摘要
            images=post.images or [],
            location=post.location or "",
            like_count=post.like_count or 0,
            comment_count=post.comment_count or 0,
            author_id=post.user_id,
            author_name=author.nickname if author else "未知",
            author_avatar=author.avatar if author else "",
            created_at=post.created_at,
        ))

    total_pages = (total + page_size - 1) // page_size

    return ResponseWrapper(data={
        "items": items,
        "pagination": Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    })


@router.get("/{post_id}", response_model=ResponseWrapper)
def get_post(
    post_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """获取帖子详情"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    return ResponseWrapper(data=_post_to_detail(post, current_user, db))


@router.put("/{post_id}", response_model=ResponseWrapper)
def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新帖子"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改")

    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content
    if data.images is not None:
        post.images = data.images
    if data.location is not None:
        post.location = data.location

    db.commit()
    db.refresh(post)

    return ResponseWrapper(data=_post_to_detail(post, current_user, db))


@router.delete("/{post_id}", response_model=ResponseWrapper)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除帖子"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除")

    db.delete(post)
    db.commit()

    return ResponseWrapper(message="删除成功")


@router.post("/{post_id}/like", response_model=ResponseWrapper)
def toggle_like(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """点赞/取消点赞"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    # 检查是否已点赞
    existing = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == current_user.id,
    ).first()

    if existing:
        # 取消点赞
        db.delete(existing)
        post.like_count = max(0, (post.like_count or 1) - 1)
        db.commit()
        return ResponseWrapper(data={"is_liked": False, "like_count": post.like_count})
    else:
        # 点赞
        like = PostLike(post_id=post_id, user_id=current_user.id)
        db.add(like)
        post.like_count = (post.like_count or 0) + 1
        db.commit()
        return ResponseWrapper(data={"is_liked": True, "like_count": post.like_count})


# ============================================
# 评论
# ============================================

@router.get("/{post_id}/comments", response_model=ResponseWrapper)
def list_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """获取帖子评论列表"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    query = db.query(Comment).filter(Comment.post_id == post_id).order_by(desc(Comment.created_at))
    total = query.count()
    comments = query.offset((page - 1) * page_size).limit(page_size).all()

    # 批量加载用户信息
    user_ids = [c.user_id for c in comments]
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    items = []
    for comment in comments:
        user = users.get(comment.user_id)
        items.append(CommentInfo(
            id=comment.id,
            post_id=comment.post_id,
            content=comment.content,
            user=UserInfo.model_validate(user) if user else UserInfo(
                id=0, username="[已删除]", nickname="[已删除]",
                avatar="", bio="", created_at=datetime.now(),
            ),
            created_at=comment.created_at,
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


@router.post("/{post_id}/comments", response_model=ResponseWrapper)
def create_comment(
    post_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发表评论"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=data.content,
    )
    db.add(comment)
    post.comment_count = (post.comment_count or 0) + 1
    db.commit()
    db.refresh(comment)

    return ResponseWrapper(data=CommentInfo(
        id=comment.id,
        post_id=comment.post_id,
        content=comment.content,
        user=current_user,
        created_at=comment.created_at,
    ))


def _post_to_detail(post: Post, current_user: Optional[User], db: Session) -> dict:
    """将 Post 对象转换为详情响应"""
    author = db.query(User).filter(User.id == post.user_id).first()
    if not author:
        # 作者已删除，返回默认值
        from app.schemas import UserInfo
        author = UserInfo(id=0, username="[已删除]", nickname="[已删除]", avatar="", bio="", created_at=datetime.now())

    is_liked = False
    if current_user:
        like = db.query(PostLike).filter(
            PostLike.post_id == post.id,
            PostLike.user_id == current_user.id,
        ).first()
        is_liked = like is not None

    return PostInfo(
        id=post.id,
        title=post.title,
        content=post.content or "",
        images=post.images or [],
        location=post.location or "",
        like_count=post.like_count or 0,
        comment_count=post.comment_count or 0,
        is_liked=is_liked,
        author=author,
        created_at=post.created_at,
        updated_at=post.updated_at,
    ).model_dump()
