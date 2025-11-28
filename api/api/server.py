# api/server.py
import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mongo_client: AsyncIOMotorClient | None = None

def get_db(request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise RuntimeError("Database not configured. Missing MONGO_URL or DB_NAME.")
    return db

app = FastAPI(title="Mahadeshnews API", version="1.0.0")

@app.on_event("startup")
async def startup():
    global mongo_client
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME")

    if mongo_url and db_name:
        mongo_client = AsyncIOMotorClient(mongo_url)
        app.state.db = mongo_client[db_name]
        logger.info("MongoDB connection established.")
    else:
        logger.warning("MongoDB NOT configured. Add MONGO_URL + DB_NAME in Vercel env.")

@app.get("/api/health")
async def health():
    return {"ok": True, "status": "running"}

# Import routes after app is ready
from routes import news as news_router
app.include_router(news_router.router, prefix="/api/news")
