import os
import logging
from typing import Dict, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AIRewriter:
    """Service to rewrite news articles using AI in Aaj Tak style"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        self.model = os.environ.get('AI_MODEL', 'gpt-5.1')
        
        # System message for Aaj Tak style rewriting
        self.system_message = """तुम एक प्रोफेशनल हिंदी न्यूज़ राइटर हो जो आज तक न्यूज़ चैनल की स्टाइल में न्यूज़ लिखता है।
तुम्हारी राइटिंग स्टाइल:
- बोल्ड, तेज़, और इम्पैक्ट वाले छोटे वाक्य
- सीधी और स्पष्ट भाषा
- फैक्ट्स पर फोकस
- ड्रामाटिक लेकिन सच्चाई पर आधारित
- शुद्ध हिंदी भाषा का उपयोग

तुम्हें न्यूज़ को रीराइट करना है ताकि:
1. कोई भी प्लेजियरिज्म न हो
2. फैक्ट्स वही रहें लेकिन शब्द और स्ट्रक्चर बिल्कुल नया हो
3. आज तक की स्टाइल में लिखा जाए
4. हिंदी भाषा में ही आउटपुट दो
5. केवल न्यूज़ कंटेंट दो, कोई extra comments नहीं"""
    
    async def rewrite_article(self, source_article: Dict) -> Dict:
        """Rewrite article in Aaj Tak style"""
        try:
            # Extract source content
            source_title = source_article.get('sourceTitle', '')
            source_desc = source_article.get('sourceDescription', '')
            source_content = source_article.get('sourceContent', '')
            category = source_article.get('category', '')
            
            # Create prompt
            prompt = f"""नीचे दी गई न्यूज़ को आज तक स्टाइल में रीराइट करो:

Original Title: {source_title}
Description: {source_desc}
Content: {source_content}

Category: {category}

रीराइट करते समय:
1. एक नया, कैची हेडलाइन बनाओ (1 लाइन)
2. एक छोटी सारांश लिखो (2 लाइन)
3. पूरा आर्टिकल लिखो (300-500 शब्द)

Format:
HEADLINE: [headline यहाँ]
SUMMARY: [summary यहाँ]
CONTENT: [full article यहाँ]"""
            
            # Initialize chat
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"rewrite_{source_article.get('sourceUrl', 'default')}",
                system_message=self.system_message
            )
            
            # Use OpenAI GPT-5.1
            chat.with_model("openai", self.model)
            
            # Send message
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse response
            parsed = self._parse_response(response)
            
            if not parsed:
                logger.error("Failed to parse AI response")
                return None
            
            # Detect district if local news
            district = None
            if category == 'स्थानीय':
                district = self._detect_district(parsed['headline'], parsed['summary'])
            
            return {
                'title': parsed['headline'],
                'summary': parsed['summary'],
                'content': parsed['content'],
                'category': category,
                'district': district,
                'image': source_article.get('sourceImage', ''),
                'sourceTitle': source_title,
                'sourceUrl': source_article.get('sourceUrl', ''),
                'sourcePublishedAt': source_article.get('sourcePublishedAt', ''),
                'priority': source_article.get('priority', 5)
            }
            
        except Exception as e:
            logger.error(f"Error rewriting article: {str(e)}")
            return None
    
    def _parse_response(self, response: str) -> Optional[Dict]:
        """Parse AI response into structured format"""
        try:
            lines = response.strip().split('\n')
            
            headline = ""
            summary = ""
            content = ""
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('HEADLINE:'):
                    headline = line.replace('HEADLINE:', '').strip()
                    current_section = 'headline'
                elif line.startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '').strip()
                    current_section = 'summary'
                elif line.startswith('CONTENT:'):
                    content = line.replace('CONTENT:', '').strip()
                    current_section = 'content'
                elif line and current_section:
                    if current_section == 'headline':
                        headline += ' ' + line
                    elif current_section == 'summary':
                        summary += ' ' + line
                    elif current_section == 'content':
                        content += ' ' + line
            
            if not headline or not summary or not content:
                # Fallback parsing
                parts = response.split('\n\n')
                if len(parts) >= 3:
                    headline = parts[0].strip()
                    summary = parts[1].strip()
                    content = ' '.join(parts[2:]).strip()
                else:
                    return None
            
            return {
                'headline': headline.strip(),
                'summary': summary.strip(),
                'content': content.strip()
            }
            
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return None
    
    def _detect_district(self, title: str, summary: str) -> Optional[str]:
        """Detect district from rewritten content"""
        content = f"{title} {summary}".lower()
        
        districts = {
            'जलना': ['jalna', 'जलना'],
            'औरंगाबाद': ['aurangabad', 'औरंगाबाद', 'sambhajinagar', 'संभाजीनगर'],
            'मराठवाड़ा': ['marathwada', 'मराठवाड़ा'],
            'परभणी': ['parbhani', 'परभणी']
        }
        
        for district, keywords in districts.items():
            if any(keyword in content for keyword in keywords):
                return district
        
        return None
