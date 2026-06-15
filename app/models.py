"""数据库模型定义"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(100), default="", comment="昵称")
    avatar = Column(String(255), default="", comment="头像URL")
    bio = Column(Text, default="", comment="个人简介")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("PostLike", back_populates="user")
    recognition_records = relationship("RecognitionRecord", back_populates="user")


class Post(Base):
    """帖子表"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="作者ID")
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, default="", comment="内容")
    images = Column(JSON, default=list, comment="图片URL列表")
    location = Column(String(255), default="", comment="位置")
    like_count = Column(Integer, default=0, comment="点赞数")
    comment_count = Column(Integer, default=0, comment="评论数")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联
    author = relationship("User", back_populates="posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class PostLike(Base):
    """点赞表"""
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, comment="帖子ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    created_at = Column(DateTime, default=datetime.now, comment="点赞时间")

    # 关联
    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")

    # 联合唯一约束（一个用户只能点赞一次）
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uk_post_user"),
    )


class Comment(Base):
    """评论表"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, comment="帖子ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评论者ID")
    content = Column(Text, nullable=False, comment="评论内容")
    created_at = Column(DateTime, default=datetime.now, comment="评论时间")

    # 关联
    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Bird(Base):
    """鸟类百科表"""
    __tablename__ = "birds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="中文名")
    latin_name = Column(String(200), default="", comment="学名")
    region = Column(String(100), default="", comment="主要分布地区")
    habits = Column(Text, default="", comment="生活习性")
    description = Column(Text, default="", comment="简介")
    image_url = Column(String(255), default="", comment="代表图片URL")
    search_count = Column(BigInteger, default=0, comment="搜索次数")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class RecognitionRecord(Base):
    """识别记录表"""
    __tablename__ = "recognition_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    image_url = Column(String(255), nullable=False, comment="上传图片URL")
    result = Column(JSON, nullable=False, comment="识别结果（Top3鸟类列表）")
    created_at = Column(DateTime, default=datetime.now, comment="识别时间")

    # 关联
    user = relationship("User", back_populates="recognition_records")
