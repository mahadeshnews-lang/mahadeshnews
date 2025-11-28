import os
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from backend.services.news_fetcher import NewsFetcher # <--- सुधारित
from backend.services.ai_rewriter import AIRewriter   # <--- सुधारित
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

logger = logging.getLogger(__name__)


class NewsScheduler:
    """Scheduler for automatic news fetching and rewriting"""
    
    def __init__(self, db):
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.news_fetcher = NewsFetcher()
        self.ai_rewriter = AIRewriter()
        
        # Get interval from env (default 6 hours)
        self.interval_hours = int(os.environ.get('FETCH_INTERVAL_HOURS', 6))
    
    def start(self):
        """Start the scheduler"""
        # Run immediately on start
        asyncio.create_task(self.fetch_and_process_news())
        
        # Schedule periodic runs
        self.scheduler.add_job(
            self.fetch_and_process_news,
            trigger=IntervalTrigger(hours=self.interval_hours),
            id='news_fetch_job',
            name='Fetch and process news',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started with {self.interval_hours} hour interval")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def fetch_and_process_news(self):
        """Main job to fetch, rewrite, and store news"""
        job_id = str(uuid.uuid4())
        logger.info(f"Starting news fetch job: {job_id}")
        
        # Create job record
        job_data = {
            'jobId': job_id,
            'status': 'running',
            'articlesProcessed': 0,
            'startTime': datetime.utcnow()
        }
        await self.db.fetch_jobs.insert_one(job_data)
        
        try:
            # Fetch news from all categories
            all_news = await self.news_fetcher.fetch_all_news()
            
            total_processed = 0
            
            # Process each category
            for category, articles in all_news.items():
                logger.info(f"Processing {len(articles)} articles for category: {category}")
                
                for source_article in articles:
                    try:
                        # Rewrite using AI
                        rewritten = await self.ai_rewriter.rewrite_article(source_article)
                        
                        if not rewritten:
                            logger.warning(f"Failed to rewrite article: {source_article.get('sourceTitle', '')}")
                            continue
                        
                        # Check if article already exists
                        existing = await self.db.articles.find_one({
                            'sourceUrl': rewritten['sourceUrl']
                        })
                        
                        if existing:
                            logger.info(f"Article already exists: {rewritten['title'][:50]}...")
                            continue
                        
                        # Get next article ID
                        last_article = await self.db.articles.find_one(
                            sort=[('articleId', -1)]
                        )
                        next_id = (last_article['articleId'] + 1) if last_article else 1
                        
                        # Prepare article document
                        article_doc = {
                            'articleId': next_id,
                            'title': rewritten['title'],
                            'summary': rewritten['summary'],
                            'content': rewritten['content'],
                            'category': rewritten['category'],
                            'district': rewritten.get('district'),
                            'image': rewritten['image'] or 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800',
                            'date': datetime.utcnow(),
                            'author': 'महादेश न्यूज़ डेस्क',
                            'views': 0,
                            'sourceTitle': rewritten['sourceTitle'],
                            'sourceUrl': rewritten['sourceUrl'],
                            'sourcePublishedAt': rewritten.get('sourcePublishedAt'),
                            'isBreaking': rewritten.get('priority', 5) >= 9,
                            'priority': rewritten.get('priority', 5),
                            'aiGenerated': True,
                            'createdAt': datetime.utcnow(),
                            'updatedAt': datetime.utcnow()
                        }
                        
                        # Insert into database
                        await self.db.articles.insert_one(article_doc)
                        total_processed += 1
                        
                        logger.info(f"Processed article [{total_processed}]: {rewritten['title'][:50]}...")
                        
                        # Small delay to avoid rate limits
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Error processing individual article: {str(e)}")
                        continue
            
            # Update job status
            await self.db.fetch_jobs.update_one(
                {'jobId': job_id},
                {'$set': {
                    'status': 'completed',
                    'articlesProcessed': total_processed,
                    'endTime': datetime.utcnow()
                }}
            )
            
            logger.info(f"Job {job_id} completed. Processed {total_processed} articles.")
            
        except Exception as e:
            logger.error(f"Error in fetch job {job_id}: {str(e)}")
            
            # Update job with error
            await self.db.fetch_jobs.update_one(
                {'jobId': job_id},
                {'$set': {
                    'status': 'failed',
                    'error': str(e),
                    'endTime': datetime.utcnow()
                }}
            )
