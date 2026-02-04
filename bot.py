# merchant-bot.com → ТВОЙ ДИЗАЙН + 24/7 KEEP-ALIVE + os.getenv TOKEN!
import logging
import os
import uvicorn
import asyncio  # 🔥 KEEP-ALIVE
import aiohttp  # 🔥 KEEP-ALIVE
from fastapi import FastAPI
from contextlib import asynccontextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔥 ТОКЕН ИЗ RENDER ENVIRONMENT (как было изначально!)
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("❌ TOKEN не найден!")
    raise SystemExit(1)

logger.info(f"✅ TOKEN OK: {TOKEN[:20]}...")

ptb_app = None

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
        # ТОВАР 1: Кеды Лидские
        await query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=111BeCUFi_saVPxGvgF3k0c4sWShBdJbC",
            caption="👟 Кеды Лидские арт. 1234567\n\n💰 Цена 105 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )

        # ТОВАР 2: New Balance
        await query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=1voH__n5tiTlbQVvljrZt7ecn-sxWZCpw",
            caption="👟 Кроссовки New Balance Арт. 123456789\n\n💰 Цена 250 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )

# 🔥 KEEP-ALIVE 24/7 ФУНКЦИЯ
async def keep_alive():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get("https://merchant-bot.onrender.com/") as resp:
                    logger.info("❤️ Keep-Alive ping OK")
            except:
                pass
            await asyncio.sleep(840)  # 14 минут

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ptb_app
    try:
        logger.info("🔄 Инициализация бота...")
        ptb_app = Application.builder().token(TOKEN).build()
        ptb_app.add_handler(CommandHandler("start", start))
        ptb_app.add_handler(CallbackQueryHandler(button_callback))

        await ptb_app.initialize()
        await ptb_app.start()

        await ptb_app.updater.start_polling(
            poll_interval=2.0,
            timeout=10,
            drop_pending_updates=True
        )
        
        # 🔥 KEEP-ALIVE: Render НЕ заснёт 24/7!
        asyncio.create_task(keep_alive())

        logger.info("🚀 Telegram Bot LIVE! ✅ merchant-bot.com 24/7")
        yield

    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        raise
    finally:
        if ptb_app:
            try:
                await ptb_app.updater.stop()
                await ptb_app.stop()
                await ptb_app.shutdown()
            except:
                pass
            logger.info("🛑 Bot остановлен")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "🟢 merchant-bot.com LIVE", "telegram": "Polling OK"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Render порт: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
