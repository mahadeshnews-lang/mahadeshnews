from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["news"])

# Database will be injected
db = None

def set_db(database):
    global db
    db = database


@router.get("/all")
async def get_all_news(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None
):
    """Get all news with pagination and optional category filter"""
    try:
        # Build query
        query = {}
        if category:
            query['category'] = category
        
        # Get total count
        total = await db.articles.count_documents(query)
        
        # Get articles
        skip = (page - 1) * limit
        articles = await db.articles.find(query).sort('date', -1).skip(skip).limit(limit).to_list(length=limit)
        
        # Format response
        formatted_articles = []
        for article in articles:
            formatted_articles.append({
                'id': article['articleId'],
                'title': article['title'],
                'summary': article['summary'],
                'category': article['category'],
                'district': article.get('district'),
                'image': article['image'],
                'date': article['date'].isoformat() if isinstance(article['date'], datetime) else article['date'],
                'author': article['author'],
                'views': article['views']
            })
        
        return {
            'success': True,
            'data': {
                'articles': formatted_articles,
                'total': total,
                'page': page,
                'pages': (total + limit - 1) // limit
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching all news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/breaking")
async def get_breaking_news():
    """Get breaking news ticker items"""
    try:
        # Get top 5 breaking news or high priority articles
        articles = await db.articles.find({
            '$or': [
                {'isBreaking': True},
                {'priority': {'$gte': 9}}
            ]
        }).sort('date', -1).limit(10).to_list(length=10)
        
        # Format as ticker items
        ticker_items = [article['title'] for article in articles]
        
        # If less than 5, add some regular high-priority news
        if len(ticker_items) < 5:
            additional = await db.articles.find().sort('date', -1).limit(10 - len(ticker_items)).to_list(length=10)
            ticker_items.extend([a['title'] for a in additional])
        
        return {
            'success': True,
            'data': ticker_items[:10]
        }
    
    except Exception as e:
        logger.error(f"Error fetching breaking news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{article_id}")
async def get_article(article_id: int):
    """Get single article by ID"""
    try:
        article = await db.articles.find_one({'articleId': article_id})
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {
            'success': True,
            'data': {
                'id': article['articleId'],
                'title': article['title'],
                'summary': article['summary'],
                'content': article['content'],
                'category': article['category'],
                'district': article.get('district'),
                'image': article['image'],
                'date': article['date'].isoformat() if isinstance(article['date'], datetime) else article['date'],
                'author': article['author'],
                'views': article['views'],
                'sourceUrl': article.get('sourceUrl')
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/increment-view/{article_id}")
async def increment_view(article_id: int):
    """Increment view count for an article"""
    try:
        result = await db.articles.update_one(
            {'articleId': article_id},
            {'$inc': {'views': 1}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get updated views
        article = await db.articles.find_one({'articleId': article_id})
        
        return {
            'success': True,
            'views': article['views']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error incrementing view for article {article_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category}")
async def get_news_by_category(
    category: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get news by category"""
    return await get_all_news(page=page, limit=limit, category=category)
