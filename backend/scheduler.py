import os
import requests
import datetime
from pymongo import MongoClient

# --- 1. Vercel Variables से डेटा प्राप्त करना ---
MONGO_URI = os.environ.get("MONGO_URI")
LLM_API_KEY = os.environ.get("EMERGENT_LLM_KEY") 
DB_NAME = os.environ.get("DB_NAME") or "MahadeshNewsDB"

# --- 2. MongoDB कनेक्शन और सेव फ़ंक्शन ---
def save_news_to_db(news_data):
    if not MONGO_URI:
        print("❌ Error: MONGO_URI not found.")
        return

    try:
        client = MongoClient(MONGO_URI)
        db = client.get_database(DB_NAME)
        news_collection = db.articles 
        
        news_data['timestamp'] = datetime.datetime.utcnow()
        result = news_collection.insert_one(news_data)
        
        print(f"✅ News successfully inserted into MongoDB. ID: {result.inserted_id}")
        client.close()
        
    except Exception as e:
        print(f"❌ Error saving to MongoDB: {e}")

# --- 3. AI से द्विभाषी न्यूज़ जनरेट करना ---
def generate_bilingual_news(topic):
    if not LLM_API_KEY:
        print("❌ Error: AI API Key not found.")
        return None

    prompt = (
        f"कृपया आज की ताजा खबर '{topic}' पर एक आकर्षक समाचार लेख लिखें। आउटपुट में शीर्षक, एक संक्षिप्त सारांश और पूरा लेख हिंदी और मराठी दोनों भाषाओं में JSON फॉर्मेट का उपयोग करके होना चाहिए।"
    )
    
    # !!! इसे अपनी असली AI सर्विस के URL से बदलना होगा !!!
    LLM_API_ENDPOINT = "YOUR_LLM_API_ENDPOINT" 

    try:
        response = requests.post(
            LLM_API_ENDPOINT,
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
            json={"prompt": prompt, "max_tokens": 1500}
        )
        response.raise_for_status()
        
        # यह AI आउटपुट को आपके डेटाबेस फॉर्मेट में बदलने का एक अनुमानित तरीका है
        ai_data = response.json() 
        
        news_record = {
            "title_hi": ai_data.get("title_hindi"),
            "content_hi": ai_data.get("content_hindi"),
            "title_mr": ai_data.get("title_marathi"),
            "content_mr": ai_data.get("content_marathi"),
            "source": "AI Generated",
            "topic": topic
        }
        return news_record
        
    except Exception as e:
        print(f"❌ Error generating news from AI: {e}")
        return None

# --- 4. मुख्य ऑटोमेशन फंक्शन ---
def run_scheduler():
    print("--- 🤖 Daily News Scheduler Started ---")
    
    topics = [
        "महाराष्ट्र के किसानों के लिए नई सरकारी योजना", 
        "पुणे-मुंबई एक्सप्रेसवे पर आज का ट्रैफिक अपडेट"
    ]

    for topic in topics:
        news_data = generate_bilingual_news(topic)
        if news_data:
            save_news_to_db(news_data)
        
    print("--- ✅ Scheduler Finished ---")

if __name__ == '__main__':
    run_scheduler()
  
