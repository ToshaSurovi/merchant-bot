import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI
import uvicorn

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get('TOKEN', '8339938445:AAGgDjcHBKbF0l7lDrhoktanSOAyQYRJR20')

MAIN_PHOTO = "https://imagizer.imageshack.com/img924/2237/7sxBBH.png"
PRODUCT1_PHOTO = "https://imagizer.imageshack.com/img922/9003/TrMGJ5.jpg"
PRODUCT2_PHOTO = "https://imagizer.imageshack.com/img921/8790/4gtW6O.jpg"

# FastAPI для Render port binding
web_app = FastAPI()

@web_app.get("/")
async def root():
    return {"status": "Merchant Bot OK", "telegram": "polling", "uptime": "24/7"}

@web_app.get("/health")
async def health():
    return {"status": "healthy", "bot": "active"}

# Telegram Bot функции
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"🚀 /start от {chat_id}")
    
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

async def run_bot():
    """Запуск Telegram бота в фоне"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 Telegram Bot запущен (polling)")
    await application.run_polling(drop_pending_updates=True)

async def main():
    """Запуск Web + Bot"""
    print("🚀 MerchantTemplateBot на Render.com (Web+Bot)")
    print(f"TOKEN: {TOKEN[:10]}...")
    
    # Запуск бота в фоне
    bot_task = asyncio.create_task(run_bot())
    
    # Запуск Web сервера
    port = int(os.environ.get('PORT', 10000))
    config = uvicorn.Config(web_app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    print(f"🌐 Web сервер на порту {port}")
    await server.serve()

if __name__ == '__main__':
    asyncio.run(main())
