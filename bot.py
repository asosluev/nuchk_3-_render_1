# bot.py
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, WEBHOOK_URL, PORT
from handlers.menu import start_menu, menu_callback, register_handlers as register_menu_handlers
from handlers.admin import register_handlers as register_admin_handlers

async def health(request):
    return web.Response(text="OK")

async def handle_webhook(request):
    try:
        data = await request.json()
        print("Update received:", data)  # лог апдейту для дебагу
    except Exception as e:
        print("Invalid request:", e)
        return web.Response(status=400, text="Invalid request")
    
    update = Update.de_json(data, app.bot)
    await app.update_queue.put(update)
    return web.Response(text="OK")

async def main():
    global app
    # Створюємо Application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Команди
    app.add_handler(CommandHandler("start", start_menu))

    # Підключаємо меню та адмін-хендлери
    register_menu_handlers(app)
    register_admin_handlers(app)

    # aiohttp сервер
    aio_app = web.Application()
    aio_app.router.add_post("/webhook", handle_webhook)
    aio_app.router.add_get("/", health)

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    # Встановлюємо webhook у Telegram
    await app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    print(f"Webhook set to: {WEBHOOK_URL}/webhook")
    print(f"Server started on 0.0.0.0:{PORT}")

    # Чекаємо завершення
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
