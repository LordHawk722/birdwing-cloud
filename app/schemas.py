"""Pydantic 数据模型（请求/响应格式）"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


# ============================================
# 通用
# ============================================

class ResponseWrapper(BaseModel):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class Pagination(BaseModel):
    """分页信息"""
    page: int = 1
    page_size: int = 10
    total: int = 0
    total_pages: int = 0


# ============================================
# 用户
# ============================================

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户信息更新请求"""
    nickname: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = None


class UserInfo(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    nickname: str
    avatar: str
    bio: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserToken(BaseModel):
    """登录成功响应"""
    token: str
    user: UserInfo


# ============================================
# 帖子
# ============================================

class PostCreate(BaseModel):
    """创建帖子请求"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = ""
    images: List[str] = []
    location: str = ""


class PostUpdate(BaseModel):
    """更新帖子请求"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    images: Optional[List[str]] = None
    location: Optional[str] = None


class PostInfo(BaseModel):
    """帖子信息响应"""
    id: int
    title: str
    content: str
    images: list
    location: str
    like_count: int
    comment_count: int
    is_liked: bool = False
    author: UserInfo
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PostListItem(BaseModel):
    """帖子列表项（精简信息）"""
    id: int
    title: str
    content: str
    images: list
    location: str
    like_count: int
    comment_count: int
    author_id: int
    author_name: str
    author_avatar: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ============================================
# 评论
# ============================================

class CommentCreate(BaseModel):
    """创建评论请求"""
    content: str = Field(..., min_length=1, max_length=500)


class CommentInfo(BaseModel):
    """评论信息响应"""
    id: int
    post_id: int
    content: str
    user: UserInfo
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ============================================
# 鸟类
# ============================================

class BirdInfo(BaseModel):
    """鸟类信息响应"""
    id: int
    name: str
    latin_name: str
    region: str
    habits: str
    description: str
    image_url: str
    search_count: int
    model_config = ConfigDict(from_attributes=True)


class BirdRankItem(BaseModel):
    """排行榜单项"""
    rank: int
    id: int
    name: str
    latin_name: str
    region: str
    habits: str
    description: str
    image_url: str
    search_count: int


class BirdSearchResult(BaseModel):
    """鸟类搜索结果"""
    birds: List[BirdInfo]
    pagination: Pagination


# ============================================
# 识别
# ============================================

class RecognitionResultItem(BaseModel):
    """识别结果单项"""
    bird_id: int
    name: str
    confidence: float = Field(..., ge=0, le=1, description="置信度")


class RecognitionCreate(BaseModel):
    """创建识别记录请求"""
    image_url: str
    result: List[RecognitionResultItem]


class RecognitionRecordInfo(BaseModel):
    """识别记录响应"""
    id: int
    image_url: str
    result: List[RecognitionResultItem]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
