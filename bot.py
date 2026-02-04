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

# Environment variables
TOKEN = os.getenv("TOKEN")
RENDER_URL = os.getenv("RENDER_URL", "https://merchant-bot-cs1d.onrender.com")
WEBHOOK_URL = f"{RENDER_URL.rstrip('/')}/webhook"

if not TOKEN:
    logger.error("❌ TOKEN не найден!")
    raise SystemExit(1)

logger.info(f"✅ TOKEN OK: {TOKEN[:20]}...")
logger.info(f"🌐 WEBHOOK URL: {WEBHOOK_URL}")

# Твои хендлеры (без изменений)
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

# Глобальное состояние бота
application = None

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    global application
    logger.info("🔄 Инициализация Telegram бота...")
    
    try:
        # Создаем приложение Telegram
        application = Application.builder().token(TOKEN).build()
        
        # Добавляем хендлеры
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # ✅ Удаляем старый webhook
        await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("🗑️ Старый webhook удален")
        
        # ✅ Устанавливаем новый webhook
        await application.bot.set_webhook(WEBHOOK_URL)
        
        # Проверяем установку
        webhook_info = await application.bot.get_webhook_info()
        logger.info(f"✅ WEBHOOK УСТАНОВЛЕН: {webhook_info.url}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации бота: {e}")
        raise

@app.get("/")
async def root():
    return {
        "status": "🟢 merchant-bot.com LIVE 24/7",
        "webhook": WEBHOOK_URL,
        "bot_ready": application is not None
    }

@app.get("/ping")
async def ping():
    return {"status": "pong 🏓", "live": True, "bot_ready": application is not None}

@app.post("/webhook")
async def webhook(request: Request):
    global application
    
    if not application:
        raise HTTPException(status_code=503, detail="🤖 Бот загружается...")
    
    try:
        # Получаем JSON от Telegram
        json_update = await request.json()
        
        # Парсим update
        update = Update.de_json(json_update, application.bot)
        
        if update and update.to_dict():
            # Обрабатываем сообщение
            await application.process_update(update)
            logger.info("✅ Update обработан")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"❌ Ошибка webhook: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обработки webhook")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 FastAPI сервер на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
