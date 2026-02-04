import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

TOKEN = os.environ.get('TOKEN', '8339938445:AAGgDjcHBKbF0l7lDrhoktanSOAyQYRJR20')
print(f"🚀 Bot starting... TOKEN OK: {TOKEN[:20]}...")

MAIN_PHOTO = "https://imagizer.imageshack.com/img924/2237/7sxBBH.png"
PRODUCT1_PHOTO = "https://imagizer.imageshack.com/img922/9003/TrMGJ5.jpg"
PRODUCT2_PHOTO = "https://imagizer.imageshack.com/img921/8790/4gtW6O.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"🚀 /start от {chat_id}")
    
    keyboard = [[InlineKeyboardButton("🛒 Выбрать товары", callback_data='products')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=MAIN_PHOTO,
        caption="""
<b>👋 Самозанятый Иванов Иван Иванович</b>

📍 г.Минск ул Петра Мстиславца 9
🆔 УНП <a href="tel:123456789">123456789</a>
📞 +375(29) 1112233

✅ <b>Продаем только оригинальный товар!</b>
        """,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    print("✅ Главное сообщение отправлено!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    print(f"🔘 Кнопка нажата: {query.data}")
    
    if query.data == 'products':
        chat_id = query.message.chat_id
        
        # Кеды Лидские
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=PRODUCT1_PHOTO,
            caption="""
<b>👟 Кеды Лидские</b> 
🆔 арт. 1234567

💰 <b>Цена 105 BYN</b>""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Купить", url='https://www.alfabank.by/business/payment/internet-acquiring/')]
            ]),
            parse_mode='HTML'
        )
        
        # New Balance
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=PRODUCT2_PHOTO,
            caption="""
<b>🏃‍♂️ Кроссовки New Balance</b>
🆔 Арт. <a href="tel:123456789">123456789</a>

💰 <b>Цена 250 BYN</b>""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Купить", url='https://www.alfabank.by/business/payment/internet-acquiring/')]
            ]),
            parse_mode='HTML'
        )
        print("✅ Товары отправлены!")

def main():
    print("🚀 Merchant Bot на Render (Background Worker)")
    print("Настройка...")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Bot готов! Тестируйте /start в Telegram")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
