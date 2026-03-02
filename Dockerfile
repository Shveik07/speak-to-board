FROM python:3.11-slim

# Установка FFmpeg и системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-пакеты
RUN pip install --no-cache-dir -r requirements.txt

# Скачиваем модель Vosk (можно вынести в отдельный слой для кэширования)
RUN mkdir -p models && \
    wget -O model.zip https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip && \
    unzip model.zip -d models/ && \
    mv models/vosk-model-small-ru-0.22 models/vosk-model && \
    rm model.zip

# Копируем исходный код
COPY . .

# Создаём папку для временных файлов
RUN mkdir -p temp

# Указываем порт, который слушает Flask (для health check)
EXPOSE 5000

# Команда запуска
CMD ["python", "app.py"]