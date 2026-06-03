"""用户模块路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import (
    UserRegister, UserLogin, UserUpdate, UserInfo, UserToken, ResponseWrapper,
)
from app.services.auth import (
    hash_password, verify_password, create_access_token, get_current_user,
)

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.post("/register", response_model=ResponseWrapper)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    # 创建用户
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        nickname=data.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 生成 token
    token = create_access_token(user.id)

    return ResponseWrapper(data={
        "token": token,
        "user": UserInfo.model_validate(user),
    })


@router.post("/login", response_model=ResponseWrapper)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = create_access_token(user.id)

    return ResponseWrapper(data={
        "token": token,
        "user": UserInfo.model_validate(user),
    })


@router.get("/me", response_model=ResponseWrapper)
def get_my_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return ResponseWrapper(data=UserInfo.model_validate(current_user))


@router.put("/me", response_model=ResponseWrapper)
def update_my_info(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新当前用户信息"""
    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.bio is not None:
        current_user.bio = data.bio
    if data.avatar is not None:
        current_user.avatar = data.avatar

    db.commit()
    db.refresh(current_user)

    return ResponseWrapper(data=UserInfo.model_validate(current_user))


@router.get("/{user_id}", response_model=ResponseWrapper)
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return ResponseWrapper(data=UserInfo.model_validate(user))
