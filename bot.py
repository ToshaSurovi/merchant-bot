import logging
import os
import uvicorn
from fastapi import FastAPI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
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
    return {"status": "Merchant Bot OK", "telegram": "polling", "uptime": "live"}

@app.get("/health")
async def health():
    return {"status": "healthy", "bot": "active"}

# Telegram handlers
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
        logger.info("✅ Товары отправлены!")

def main():
    logger.info("🚀 MerchantTemplateBot на Render.com")
    logger.info(f"TOKEN: {TOKEN[:10]}...")
    
    # 1. Web сервер для Render (главное!)
    port = int(os.environ.get('PORT', 10000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    server.serve()  # Render ждет ЭТОТ порт!

if __name__ == '__main__':
    main()
