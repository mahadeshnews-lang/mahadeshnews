from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Article(BaseModel):
    """Article model for MongoDB"""
    articleId: int
    title: str
    summary: str
    content: str
    category: str
    district: Optional[str] = None
    image: str
    date: datetime = Field(default_factory=datetime.utcnow)
    author: str = "महादेश न्यूज़ डेस्क"
    views: int = 0
    sourceTitle: Optional[str] = None
    sourceUrl: Optional[str] = None
    sourcePublishedAt: Optional[datetime] = None
    isBreaking: bool = False
    priority: int = 5  # 1-10, based on category
    aiGenerated: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ArticleResponse(BaseModel):
    """Response model for frontend"""
    id: int
    title: str
    summary: str
    content: Optional[str] = None
    category: str
    district: Optional[str] = None
    image: str
    date: str
    author: str
    views: int
    sourceUrl: Optional[str] = None


class FetchJob(BaseModel):
    """Fetch job tracking model"""
    jobId: str
    status: str = "pending"  # pending, running, completed, failed
    articlesProcessed: int = 0
    startTime: datetime = Field(default_factory=datetime.utcnow)
    endTime: Optional[datetime] = None
    error: Optional[str] = None
