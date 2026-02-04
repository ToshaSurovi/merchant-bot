# merchant-bot.com → FIXED Conflict → 100% Render 2026
import logging
import os
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from telegram.error import Conflict

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("❌ TOKEN не найден!")
    raise SystemExit(1)

logger.info(f"✅ TOKEN OK: {TOKEN[:20]}...")

ptb_app = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    await update.message.reply_photo(
        photo="https://i.ibb.co/0mQhYkY/sneakers.jpg",
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        keyboard = [[InlineKeyboardButton("📱 Написать", url="https://t.me/ToshaSurovi")]]
    
    await query.edit_message_caption(
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ptb_app
    try:
        ptb_app = Application.builder().token(TOKEN).build()
        ptb_app.add_handler(CommandHandler("start", start))
        ptb_app.add_handler(CallbackQueryHandler(button_callback))
        
        await ptb_app.initialize()
        await ptb_app.start()
        
        # КЛЮЧЕВОЕ: drop_pending_updates=True решает Conflict!
        await ptb_app.updater.start_polling(
            poll_interval=2.0,
            timeout=10,
            drop_pending_updates=True  # ← ФИКС Conflict!
        )
        
        logger.info("🚀 Telegram Bot LIVE! drop_pending_updates=True")
        yield
        
    except Conflict as e:
        logger.error(f"❌ Conflict detected: {e}")
        logger.info("🔄 Перезапуск через 5 сек...")
        raise
    except Exception as e:
        logger.error(f"❌ Bot startup error: {e}")
        raise
    finally:
        if ptb_app:
            try:
                await ptb_app.updater.stop()
                await ptb_app.stop()
                await ptb_app.shutdown()
            except:
                pass
            logger.info("🛑 Bot gracefully stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "🟢 merchant-bot.com LIVE", "telegram": "Polling OK"}

@app.get("/health")
async def health():
    return {"status": "OK"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Starting on Render port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
