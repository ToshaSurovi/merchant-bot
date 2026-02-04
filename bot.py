import logging
import os
from fastapi import FastAPI
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TOKEN', '8339938445:AAGgDjcHBKbF0l7lDrhoktanSOAyQYRJR20')

app = FastAPI()

@app.get("/")
async def root():
    return {
        "status": "Merchant Web OK", 
        "telegram_bot": "deployed_separately", 
        "url": "https://merchant-bot-cs1d.onrender.com",
        "token": TOKEN[:10] + "..."
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "web_ok"}

@app.get("/info")
async def info():
    return {
        "merchant": "Иванов Иван Иванович",
        "location": "г.Минск ул Петра Мстиславца 9", 
        "упн": "123456789",
        "phone": "+375(29) 1112233"
    }

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Merchant Web Server на порту {port}")
    uvicorn.run(
        "bot:app", 
        host="0.0.0.0", 
        port=port,
        log_level="info",
        reload=False
    )
