# merchant-bot.com → ПОЛНЫЙ КОД для Render 2026
import logging
import os
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из Environment Variables Render
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("❌ TOKEN не найден в Environment Variables!")
    raise ValueError("TOKEN required")

# FastAPI lifespan для Telegram Bot
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем приложение Telegram
    app_state.ptb = Application.builder().token(TOKEN).build()
    
    # Добавляем handlers
    app_state.ptb.add_handler(CommandHandler("start", start))
    app_state.ptb.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    await app_state.ptb.initialize()
    await app_state.ptb.start()
    await app_state.ptb.updater.start_polling(poll_interval=1.0, timeout=10)
    
    logger.info("🚀 Telegram Background Worker запускается...")
    yield
    
    # Останавливаем бота
    await app_state.ptb.updater.stop()
    await app_state.ptb.stop()
    await app_state.ptb.shutdown()
    logger.info("🛑 Telegram Bot остановлен")

# Глобальное состояние
app_state = FastAPI()

# FastAPI приложение
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    """Health check для Render"""
    return {"status": "🟢 merchant-bot.com LIVE", "telegram": "OK"}

@app.post("/telegram")
async def telegram_webhook(request: Request):
    """Webhook для Telegram (опционально)"""
    try:
        update = Update.de_json(await request.json(), app_state.ptb.bot)
        await app_state.ptb.update_queue.put(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error"}

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    logger.info(f"🚀 /start от {update.effective_user.id}")
    
    # Титульное сообщение
    text = (
        "👟 **Кроссовки Premium**\n\n"
        "💰 Самозанятый\n"
        "✅ Быстрая доставка\n"
        "🔥 Лучшие цены"
    )
    
    # Кнопки каталога
    keyboard = [
        [InlineKeyboardButton("🛒 КЕДЫ", callback_data="kedu")],
        [InlineKeyboardButton("🔥 New Balance", callback_data="new_balance")],
        [InlineKeyboardButton("👑 Nike Air", callback_data="nike")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_photo(
        photo="https://i.ibb.co/0mQhYkY/sneakers.jpg",
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "kedu":
        text = "👟 **Кеды Premium** 105 BYN\n\n✅ Размер 39-45\n✅ Оригинал\n📦 Доставка 1-2 дня"
        keyboard = [[InlineKeyboardButton("🛒 Купить", callback_data="buy_kedu")]]
        
    elif query.data == "new_balance":
        text = "🔥 **New Balance 550** 250 BYN\n\n✅ Белые/Серые\n✅ EU 40-44\n💎 Premium качество"
        keyboard = [[InlineKeyboardButton("🛒 Купить", callback_data="buy_nb")]]
    
    elif query.data == "nike":
        text = "👑 **Nike Air Force 1** 320 BYN\n\n✅ Классика\n✅ Все цвета\n⚡ В наличии"
        keyboard = [[InlineKeyboardButton("🛒 Купить", callback_data="buy_nike")]]
    
    else:
        text = "✅ Заказ принят!\n\nНапишите в личку для оплаты и доставки:"
        keyboard = [[InlineKeyboardButton("📱 Написать", url="https://t.me/твой_ник")]]
    
    await query.edit_message_caption(
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Запуск на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
