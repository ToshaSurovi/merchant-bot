import logging
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
RENDER_URL = os.getenv("RENDER_URL", "https://your-bot.onrender.com")
WEBHOOK_URL = f"{RENDER_URL.rstrip('/')}/webhook"

if not TOKEN:
    logger.error("❌ TOKEN не найден!")
    raise SystemExit(1)

logger.info(f"✅ TOKEN OK: {TOKEN[:20]}...")
logger.info(f"🌐 WEBHOOK URL: {WEBHOOK_URL}")

# Хендлеры (твоя логика)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"🚀 /start от {update.effective_user.id}")
    
    text = """Самозанятый Иванов Иван Иванович
Зарегистрирован г.Минск ул Петра Мстиславца 9
УНП 123456789
+375(29) 1112233

Продаем только оригинальный товар!"""
    
    keyboard = [[InlineKeyboardButton("Выбрать товары", callback_data="catalog")]]
    
    await update.message.reply_photo(
        photo="https://drive.google.com/uc?export=download&id=14qLvobylDK4j6N8a0rEONhFv8s8dP0Bd",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "catalog":
        # Кеды Лидские
        await query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=111BeCUFi_saVPxGvgF3k0c4sWShBdJbC",
            caption="👟 Кеды Лидские арт. 1234567\n\n💰 Цена 105 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )
        
        # New Balance
        await query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=1voH__n5tiTlbQVvljrZt7ecn-sxWZCpw",
            caption="👟 Кроссовки New Balance Арт. 123456789\n\n💰 Цена 250 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )

# Глобальное состояние
application = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global application
    logger.info("🔄 Инициализация webhook...")
    
    # Создаем приложение Telegram
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # ✅ КРИТИЧНО: Удаляем старые webhook'и
    await application.bot.delete_webhook(drop_pending_updates=True)
    
    # Устанавливаем новый webhook
    await application.bot.set_webhook(WEBHOOK_URL)
    
    webhook_info = await application.bot.get_webhook_info()
    logger.info(f"✅ Webhook установлен: {webhook_info.url}")
    
    yield  # FastAPI запущен
    
    # Cleanup
    if application:
        await application.bot.delete_webhook()
        logger.info("🛑 Webhook удален")

# FastAPI приложение
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "🟢 merchant-bot.com LIVE 24/7", "webhook": WEBHOOK_URL}

@app.get("/ping")
async def ping():
    return {"status": "pong 🏓", "time": "online 24/7"}

@app.post("/webhook")
async def webhook(request: Request):
    global application
    if not application:
        raise HTTPException(status_code=503, detail="Bot not ready")
    
    json_update = await request.json()
    update = Update.de_json(json_update, application.bot)
    
    if update:
        await application.process_update(update)
    
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Render порт: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
