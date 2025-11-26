import os
import logging
from typing import List, Dict, Optional
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Service to fetch news from NewsAPI"""
    
    def __init__(self):
        self.api_key = os.environ.get('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("NEWS_API_KEY not found in environment")
        
        self.newsapi = NewsApiClient(api_key=self.api_key)
        
        # Category mappings with priorities
        self.category_config = {
            'सरकारी योजना': {
                'keywords': 'सरकारी योजना OR government scheme OR महाराष्ट्र सरकार OR central scheme',
                'priority': 10,
                'limit': 15
            },
            'अपराध': {
                'keywords': 'crime OR murder OR अपराध OR हत्या OR गिरफ्तार',
                'priority': 10,
                'limit': 15
            },
            'सड़क हादसा': {
                'keywords': 'road accident OR दुर्घटना OR हादसा OR accident',
                'priority': 10,
                'limit': 10
            },
            'राजनीति': {
                'keywords': 'maharashtra politics OR महाराष्ट्र राजनीति OR विधानसभा',
                'priority': 7,
                'limit': 8
            },
            'मनोरंजन': {
                'keywords': 'bollywood OR entertainment OR मनोरंजन OR फिल्म',
                'priority': 5,
                'limit': 5
            },
            'खेल': {
                'keywords': 'sports OR cricket OR खेल OR भारतीय टीम',
                'priority': 5,
                'limit': 5
            },
            'स्थानीय': {
                'keywords': 'jalna OR aurangabad OR marathwada OR जालना OR औरंगाबाद OR मराठवाड़ा',
                'priority': 10,
                'limit': 20
            }
        }
    
    async def fetch_news_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Fetch news for a specific category"""
        try:
            config = self.category_config.get(category, {})
            keywords = config.get('keywords', category)
            
            # Fetch from NewsAPI
            from_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
            
            response = self.newsapi.get_everything(
                q=keywords,
                from_param=from_date,
                language='en',
                sort_by='publishedAt',
                page_size=limit
            )
            
            articles = response.get('articles', [])
            logger.info(f"Fetched {len(articles)} articles for category: {category}")
            
            return self._format_articles(articles, category, config.get('priority', 5))
            
        except Exception as e:
            logger.error(f"Error fetching news for category {category}: {str(e)}")
            return []
    
    async def fetch_maharashtra_news(self) -> List[Dict]:
        """Fetch Maharashtra-specific news with 3X priority"""
        try:
            districts = ['jalna', 'aurangabad', 'marathwada', 'जालना', 'औरंगाबाद', 'मराठवाड़ा']
            
            articles = []
            for district in districts[:3]:  # Focus on main districts
                from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                
                response = self.newsapi.get_everything(
                    q=district,
                    from_param=from_date,
                    language='en',
                    sort_by='publishedAt',
                    page_size=10
                )
                
                articles.extend(response.get('articles', []))
            
            logger.info(f"Fetched {len(articles)} Maharashtra-specific articles")
        
            return self._format_articles(articles, 'स्थानीय', 10)
            
        except Exception as e:
            logger.error(f"Error fetching Maharashtra news: {str(e)}")
            return []
    
    async def fetch_all_news(self) -> Dict[str, List[Dict]]:
        """Fetch news for all categories"""
        all_news = {}
        
        # Fetch Maharashtra news first (3X priority)
        maharashtra_news = await self.fetch_maharashtra_news()
        all_news['स्थानीय'] = maharashtra_news
        
        # Fetch other categories
        for category, config in self.category_config.items():
            if category != 'स्थानीय':
                articles = await self.fetch_news_by_category(category, config.get('limit', 10))
                all_news[category] = articles
        
        logger.info(f"Total categories fetched: {len(all_news)}")
        return all_news
    
    def _format_articles(self, articles: List[Dict], category: str, priority: int) -> List[Dict]:
        """Format articles from NewsAPI response"""
        formatted = []
        
        for article in articles:
            try:
                formatted_article = {
                    'sourceTitle': article.get('title', ''),
                    'sourceUrl': article.get('url', ''),
                    'sourceDescription': article.get('description', ''),
                    'sourceContent': article.get('content', ''),
                    'sourceImage': article.get('urlToImage', ''),
                    'sourcePublishedAt': article.get('publishedAt', ''),
                    'category': category,
                    'priority': priority,
                    'source': article.get('source', {}).get('name', '')
                }
                formatted.append(formatted_article)
            except Exception as e:
                logger.error(f"Error formatting article: {str(e)}")
                continue
        
        return formatted
    
    def _detect_district(self, title: str, description: str) -> Optional[str]:
        """Detect district from article content"""
        content = f"{title} {description}".lower()
        
        districts = {
            'जालना': ['jalna', 'जालना'],
            'औरंगाबाद': ['aurangabad', 'औरंगाबाद', 'sambhajinagar', 'संभाजीनगर'],
            'मराठवाड़ा': ['marathwada', 'मराठवाड़ा'],
            'परभणी': ['parbhani', 'परभणी']
        }
        
        for district, keywords in districts.items():
            if any(keyword in content for keyword in keywords):
                return district
        
        return None
