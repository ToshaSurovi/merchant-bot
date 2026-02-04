# merchant-bot.com → ✅ ИСПРАВЛЕННЫЙ КОД для Render 2026
import logging
import os
import uvicorn
from fastapi import FastAPI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
import asyncio
import threading

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("❌ TOKEN не найден!")
    exit(1)

logger.info(f"✅ TOKEN OK: {TOKEN[:20]}...")

# FastAPI для Render порта
app = FastAPI()

# Telegram Application (глобальный)
application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    logger.info(f"🚀 /start от {update.effective_user.id}")
    
    text = (
        "👟 **Кроссовки Premium**\n\n"
        "💰 Самозанятый\n"
        "✅ Быстрая доставка\n"
        "🔥 Лучшие цены"
    )
    
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

def run_bot():
    """Запуск Telegram бота в отдельном потоке"""
    global application
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("🚀 Telegram Bot запускается...")
    application.run_polling(poll_interval=1.0, timeout=10)

@app.on_event("startup")
async def startup_event():
    """Запуск бота при старте FastAPI"""
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("🌐 FastAPI + Telegram Bot LIVE!")

@app.get("/")
async def root():
    return {"status": "🟢 merchant-bot.com LIVE", "telegram": "Polling"}

@app.get("/health")
async def health():
    return {"status": "OK"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Render порт: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
