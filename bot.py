import logging
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# Глобальное состояние
updater = None
bot_ready = False

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
RENDER_URL = os.getenv("RENDER_URL", "https://merchant-bot-cs1d.onrender.com")
WEBHOOK_URL = f"{RENDER_URL.rstrip('/')}/webhook"

if not TOKEN:
    logger.error("❌ TOKEN не найден!")
    raise SystemExit(1)

logger.info(f"✅ TOKEN: {TOKEN[:10]}...")
logger.info(f"🌐 WEBHOOK: {WEBHOOK_URL}")

# ✅ v13.15 СИНХРОННЫЕ хендлеры
def start(update: Update, context):
    logger.info(f"🚀 /start от {update.effective_user.id}")
    text = """Самозанятый Иванов Иван Иванович
Зарегистрирован г.Минск ул Петра Мстиславца 9
УНП 123456789
+375(29) 1112233

Продаем только оригинальный товар!"""
    keyboard = [[InlineKeyboardButton("Выбрать товары", callback_data="catalog")]]
    update.message.reply_photo(
        photo="https://drive.google.com/uc?export=download&id=1YmdAxQZD5GDnzV08HG429StHM4pFll05",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button_callback(update: Update, context):
    query = update.callback_query
    query.answer()
    if query.data == "catalog":
        query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=111BeCUFi_saVPxGvgF3k0c4sWShBdJbC",
            caption="👟 Кеды Лидские арт. 1234567\n\n💰 Цена 105 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )
        query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=1voH__n5tiTlbQVvljrZt7ecn-sxWZCpw",
            caption="👟 Кроссовки New Balance Арт. 123456789\n\n💰 Цена 250 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    global updater, bot_ready
    logger.info("🔄 Инициализация...")
    
    try:
        updater = Updater(token=TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CallbackQueryHandler(button_callback))
        
        # 🔥 WEBHOOK ФИКС — ВСТАВЬ МЕЖДУ ЭТИМИ СТРОКАМИ:
        logger.info(f"🔄 Webhook setup: {WEBHOOK_URL}")
        updater.bot.delete_webhook(drop_pending_updates=True)
        updater.bot.set_webhook(WEBHOOK_URL)
        
        webhook_info = updater.bot.get_webhook_info()
        logger.info(f"✅ WEBHOOK: {webhook_info.url}")
        logger.info(f"✅ Pending: {webhook_info.pending_update_count}")
        bot_ready = True
        
    except Exception as e:
        logger.error(f"❌ Startup: {e}")
        bot_ready = False
    
    yield
    
    if updater:
        updater.bot.delete_webhook()
        logger.info("🛑 Bot stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "🟢 LIVE", "webhook": WEBHOOK_URL, "ready": bot_ready}

@app.get("/ping")
async def ping():
    return {"status": "pong 🏓", "ready": bot_ready}

@app.get("/keepalive")  # ← НОВОЕ!
async def keepalive():
    return {"status": "🟢 ALIVE", "timestamp": "2026-02-06"}  # ← НОВОЕ!

@app.post("/webhook")
async def webhook(request: Request):
    global updater, bot_ready
    
    if not bot_ready or not updater:
        raise HTTPException(status_code=503, detail="Bot loading...")
    
    try:
        json_update = await request.json()
        update = Update.de_json(json_update, updater.bot)
        
        if update:
            updater.dispatcher.process_update(update)
            logger.info("✅ Processed")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"❌ Webhook: {e}")
        raise HTTPException(status_code=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)


