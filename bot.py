import logging
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
RENDER_URL = os.getenv("RENDER_URL", "https://merchant-bot-cs1d.onrender.com")
WEBHOOK_URL = f"{RENDER_URL.rstrip('/')}/webhook"

if not TOKEN:
    logger.error("❌ TOKEN не найден!")
    raise SystemExit(1)

logger.info(f"✅ TOKEN: {TOKEN[:10]}...")
logger.info(f"🌐 WEBHOOK: {WEBHOOK_URL}")

# ✅ Хендлеры
def start(update: Update, context):
    logger.info(f"🚀 /start от {update.effective_user.id}")
    
    # 1️⃣ ФОТО + контакты
    update.message.reply_photo(
        photo="https://drive.google.com/uc?export=download&id=13fIvNBs3rc2ygCqp0boZQgaW76yZvRg3",
        caption="""🧼 Магазин handmade мыла

Продавец: Иванов Иван Иванович
УНП BA123456
Регистрация: ИМНС по Первомайскому району г. Минска
Юридический и почтовый адрес:
220114, Республика Беларусь, г. Минск, ул. Петра Мстиславца, 9
Телефон +375(29) 111223, электронная почта mylo@gmail.com
"""
    )
    
    # 2️⃣ ТОЧНЫЙ ТЕКСТ + КНОПКА ПОД НИМ
    exact_text = """Для оформления заказа и получения ссылки на оплату свяжитесь по телефону +375(29) 111223 или напишите сообщение (отправьте запрос через бот).

Способы оплаты:
• наличными при получении
• банковской картой онлайн

К оплате принимаются карты международных платежных систем VISA, MasterCard, платежной системы БЕЛКАРТ. Оплату также можно совершить посредством сервисов Apple Pay, Samsung Pay. 
Доставка по г.Минску бесплатная, стоимость доставки почтовой службой - 20 BYN.
Срок доставки согласовывается с продавцом после оформления заказа.
Товар надлежащего качества возврату и обмену не подлежи. По вопросу согласования возврата товара и денежных средств по иным причинам обратитесь по указанными контактным данным продавца."""
    
    update.message.reply_text(
        exact_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Выбрать мыло", callback_data="catalog")]])
    )

def button_callback(update: Update, context):
    query = update.callback_query
    query.answer()
    if query.data == "catalog":
        query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=13PulEWZCQ4f5yrUVmm6BDvbxHBaA-6nt",
            caption="Ароматное мыло ручной работы для лица и тела\nАрт. 1234567\n\n💰 Цена 5 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )
        query.message.reply_photo(
            photo="https://drive.google.com/uc?export=download&id=1syCff3Anitk9hy9DGjz5um7Xb20rpKH3",
            caption="Ароматное мыло ручной работы для лица и тела\nАрт. 123456789\n\n💰 Цена 7 BYN",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Купить", url="https://www.alfabank.by/business/payment/internet-acquiring/")]])
        )

# ✅ Lifespan БЕЗ Updater
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔄 Инициализация...")
    
    try:
        bot = Bot(token=TOKEN)
        bot.delete_webhook(drop_pending_updates=True)
        bot.set_webhook(WEBHOOK_URL)
        logger.info(f"✅ WEBHOOK установлен: {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"❌ Startup: {e}")
    
    yield
    
    logger.info("🛑 Bot stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/", include_in_schema=False)
async def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"status": "🟢 LIVE", "webhook": WEBHOOK_URL, "ready": True}

@app.get("/ping")
async def ping():
    return {"status": "pong 🏓", "ready": True}

@app.get("/keepalive")
async def keepalive():
    return {"status": "🟢 ALIVE", "timestamp": "2026-02-13"}

# ✅ Webhook обработка
@app.post("/webhook")
async def webhook(request: Request):
    try:
        json_update = await request.json()
        logger.info(f"📨 Webhook получен: {json_update.get('update_id', 'unknown')}")
        update = Update.de_json(json_update, Bot(token=TOKEN))
        
        if update and update.message and update.message.text == '/start':
            start(update, None)
            logger.info("🚀 /start обработан!")
        elif update and update.callback_query:
            button_callback(update, None)
            logger.info("🔘 Callback обработан!")
        else:
            logger.info("ℹ️ Неизвестное обновление")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"❌ Webhook: {e}")
        return {"ok": True}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🌐 Port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

