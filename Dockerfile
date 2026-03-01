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
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Скачиваем модель Vosk
RUN mkdir -p models && \
    wget -O model.zip https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip && \
    unzip model.zip -d models/ && \
    mv models/vosk-model-small-ru-0.22 models/vosk-model && \
    rm model.zip

# Создаем папку для временных файлов
RUN mkdir -p temp

# Запускаем приложение
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "120"]