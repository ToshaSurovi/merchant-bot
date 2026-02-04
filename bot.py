import logging
import os
import asyncio
from fastapi import FastAPI
import uvicorn
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TOKEN', '8339938445:AAGgDjcHBKbF0l7lDrhoktanSOAyQYRJR20')

MAIN_PHOTO = "https://imagizer.imageshack.com/img924/2237/7sxBBH.png"
PRODUCT1_PHOTO = "https://imagizer.imageshack.com/img922/9003/TrMGJ5.jpg"
PRODUCT2_PHOTO = "https://imagizer.imageshack.com/img921/8790/4gtW6O.jpg"

# FastAPI для Render
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Merchant Bot OK", "telegram": "active", "url": "https://merchant-bot-cs1d.onrender.com"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": "live"}

# Telegram handlers (копируются в Background Worker)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logger.info(f"🚀 /start от {chat_id}")
    
    keyboard = [[InlineKeyboardButton("🛒 Выбрать товары", callback_data='products')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=chat_id, 
        photo=MAIN_PHOTO, 
        caption="""
<b>Самозанятый Иванов Иван Иванович</b>
Зарегистрирован г.Минск ул Петра Мстиславца 9
УНП <a href="tel:123456789">123456789</a>
+375(29) 1112233

<b>Продаем только оригинальный товар!</b>
        """, 
        reply_markup=reply_markup, 
        parse_mode='HTML'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'products':
        chat_id = query.message.chat_id
        
        await context.bot.send_photo(
            chat_id=chat_id, 
            photo=PRODUCT1_PHOTO,
            caption="""<b>Кеды Лидские</b> арт. 1234567

<b>Цена 105 BYN</b>""",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Купить", 
                url='https://www.alfabank.by/business/payment/internet-acquiring/')]]),
            parse_mode='HTML'
        )
        
        await context.bot.send_photo(
            chat_id=chat_id, 
            photo=PRODUCT2_PHOTO,
            caption="""<b>Кроссовки New Balance</b> Арт. <a href="tel:123456789">123456789</a>

<b>Цена 250 BYN</b>""",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Купить", 
                url='https://www.alfabank.by/business/payment/internet-acquiring/')]]),
            parse_mode='HTML'
        )

async def run_telegram_bot():
    """Telegram Bot polling"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("🚀 Telegram Bot запущен!")
    await application.run_polling(drop_pending_updates=True)

async def main():
    logger.info("🚀 MerchantTemplateBot на Render.com")
    logger.info(f"TOKEN: {TOKEN[:10]}...")
    
    # Запуск бота и веб-сервера ПАРАЛЛЕЛЬНО
    bot_task = asyncio.create_task(run_telegram_bot())
    web_task = asyncio.create_task(start_web_server())
    
    await asyncio.gather(bot_task, web_task)

async def start_web_server():
    """FastAPI сервер для Render"""
    port = int(os.environ.get('PORT', 10000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    logger.info(f"🌐 Web сервер на порту {port}")
    await server.serve()  # ✅ AWAIT!

if __name__ == '__main__':
    asyncio.run(main())
