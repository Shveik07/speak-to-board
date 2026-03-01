from flask import Flask
from threading import Thread
import asyncio
import logging
from bot.main import main

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Voice to Kanban Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    """Запускает Flask-сервер в отдельном потоке"""
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    # Запускаем Flask в фоновом потоке (daemon, чтобы он завершился вместе с главным)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Запускаем бота в главном потоке (здесь aiogram может установить сигналы)
    asyncio.run(main())