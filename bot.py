import logging
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Логирование
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

# Твои хендлеры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"🚀 /start от {update.effective_user.id}")
    text = """Самозанятый Иванов Иван Иванович
Зарегистрирован г.Минск ул Петра Мстиславца 9
УНП 123456789
+375(29) 1112233

Продаем только оригинальный товар!"""
    keyboard = [[InlineKeyboardButton("Выбрать товары", callback_data="catalog")]]
    await update.message.reply_photo(
        photo="https://drive.google.com/uc?export=download&id=1YmdAxQZD5GDnzV08HG429StHM4pFll05",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "catalog":
        await query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=111BeCUFi_saVPxGvgF3k0c4sWShBdJbC",
            caption="👟 Кеды Лидские арт. 1234567\n\n💰 Цена 105 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )
        await query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=1voH__n5tiTlbQVvljrZt7ecn-sxWZCpw",
            caption="👟 Кроссовки New Balance Арт. 123456789\n\n💰 Цена 250 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )

# Глобальное состояние
application = None
bot_ready = False

app = FastAPI()

@app.on_event("startup")
async def startup():
    global application, bot_ready
    logger.info("🔄 Инициализация...")
    
    try:
        # Создание приложения
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # ✅ КРИТИЧНО: правильная последовательность v20.7
        await application.initialize()
        await application.start()
        
        # Webhook
        await application.bot.delete_webhook(drop_pending_updates=True)
        await application.bot.set_webhook(WEBHOOK_URL)
        
        webhook_info = await application.bot.get_webhook_info()
        logger.info(f"✅ WEBHOOK OK: {webhook_info.url}")
        bot_ready = True
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise

@app.get("/")
async def root():
    return {"status": "🟢 LIVE", "webhook": WEBHOOK_URL, "ready": bot_ready}

@app.get("/ping")
async def ping():
    return {"status": "pong 🏓", "ready": bot_ready}

@app.post("/webhook")
async def webhook(request: Request):
    global application, bot_ready
    
    if not bot_ready or not application:
        raise HTTPException(status_code=503, detail="Bot loading...")
    
    try:
        json_update = await request.json()
        update = Update.de_json(json_update, application.bot)
        
        if update and update.to_dict():
            await application.process_update(update)
            logger.info("✅ Processed")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"❌ Webhook: {e}")
        raise HTTPException(status_code=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
