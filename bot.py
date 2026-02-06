import logging
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response  # 🔥 ФИКС 1: Добавлен!
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot  # 🔥 ФИКС 2: Bot добавлен

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

# ✅ Хендлеры БЕЗ изменений
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
        
        # ✅ WEBHOOK через отдельный Bot (ПРАВИЛЬНО!)
        bot = Bot(token=TOKEN)
        bot.delete_webhook(drop_pending_updates=True)
        bot.set_webhook(WEBHOOK_URL)
        logger.info(f"✅ WEBHOOK установлен: {WEBHOOK_URL}")
        
        bot_ready = True
        
    except Exception as e:
        logger.error(f"❌ Startup: {e}")
        bot_ready = False
    
    yield
    
    if updater:
        updater.bot.delete_webhook()
        logger.info("🛑 Bot stopped")

app = FastAPI(lifespan=lifespan)

# 🔥 ФИКС 3: Render healthcheck + HEAD поддержка
@app.get("/", include_in_schema=False)
async def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)  # Render happy!
    return {"status": "🟢 LIVE", "webhook": WEBHOOK_URL, "ready": bot_ready}

@app.get("/ping")
async def ping():
    return {"status": "pong 🏓", "ready": bot_ready}

@app.get("/keepalive")
async def keepalive():
    return {"status": "🟢 ALIVE", "timestamp": "2026-02-06"}

# 🔥 ГЛАВНЫЙ ФИКС: Прямая обработка webhook без dispatcher!
@app.post("/webhook")
async def webhook(request: Request):
    global updater, bot_ready
    
    if not bot_ready or not updater:
        raise HTTPException(status_code=503, detail="Bot loading...")
    
    try:
        json_update = await request.json()
        logger.info(f"📨 Webhook получен: {json_update.get('update_id', 'unknown')}")
        update = Update.de_json(json_update, updater.bot)
        
        if update:
            # 🔥 ПРЯМАЯ обработка (v13.15 + FastAPI совместимо!)
            if update.message and update.message.text == '/start':
                start(update, None)
                logger.info("🚀 /start обработан!")
            elif update.callback_query:
                button_callback(update, None)
                logger.info("🔘 Callback обработан!")
            else:
                logger.info("ℹ️ Неизвестное сообщение")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"❌ Webhook: {e}")
        raise HTTPException(status_code=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
