# Деплой на Render

1. Создайте аккаунт на [render.com](https://render.com) (через GitHub)
2. Нажмите "New +" → "Web Service"
3. Подключите GitHub и выберите репозиторий
4. Настройки:
   - **Name**: voice-to-kanban-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Plan**: Free
5. Добавьте переменные окружения (из `.env`)
6. Нажмите "Create Web Service"

Готово! Ваш бот будет автоматически обновляться при каждом push в main ветку.