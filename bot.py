import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ДЕБАГ ЛОГИ
print("🔧 telegram_bot.py старт...")
print(f"TOKEN из ENV: '{os.environ.get('TOKEN')}'")
print(f"TOKEN длина: {len(os.environ.get('TOKEN', '')) if os.environ.get('TOKEN') else 'НЕ НАЙДЕН'}")

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: TOKEN не найден в Environment Variables!")
    exit(1)

print(f"✅ TOKEN OK: {TOKEN[:10]}...")

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
<b>Самозанятый Иванов Иван Иванович</b>
Зарегистрирован г.Минск ул Петра Мстиславца 9
УНП <a href="tel:123456789">123456789</a>
+375(29) 1112233

<b>Продаем только оригинальный товар!</b>
        """, 
        reply_markup=reply_markup, 
        parse_mode='HTML'
    )
    print("✅ /start отправлен!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    print(f"🔘 Кнопка: {query.data}")
    
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
        print("✅ Товары отправлены!")

if __name__ == '__main__':
    print("🚀 Telegram Background Worker запускается...")
    try:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CallbackQueryHandler(button_handler))
        print("✅ Бот настроен, начинаем polling...")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"❌ ОШИБКА БОТА: {e}")
