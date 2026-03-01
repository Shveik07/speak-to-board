import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from bot.core import config
from bot.processors.audio_processor import convert_ogg_to_wav, cleanup_temp_files
from bot.processors.vosk_recognizer import VoskRecognizer
from bot.processors.trello_api import create_task

logging.basicConfig(level=logging.INFO)

os.makedirs(config.TEMP_DIR, exist_ok=True)

# Инициализация
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
recognizer = VoskRecognizer(config.VOSK_MODEL_PATH)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для создания задач из голосовых сообщений.\n\n"
        "📢 Отправь мне голосовое сообщение, и я создам задачу в Trello.\n"
        "👥 Задача будет назначена на тебя автоматически.\n"
    )

@dp.message(lambda message: message.voice)
async def handle_voice(message: types.Message):
    processing_msg = await message.reply("🎤 Распознаю речь...")
    
    ogg_path = None
    wav_path = None
    
    try:
        # Скачиваем голосовое сообщение
        file = await bot.get_file(message.voice.file_id)
        ogg_path = f"{config.TEMP_DIR}/{message.voice.file_id}.ogg"
        wav_path = f"{config.TEMP_DIR}/{message.voice.file_id}.wav"
        
        await bot.download_file(file.file_path, ogg_path)
        
        # Конвертируем в WAV [4]
        await asyncio.to_thread(convert_ogg_to_wav, ogg_path, wav_path)
        
        # Распознаем текст [1]
        text = await asyncio.to_thread(recognizer.transcribe, wav_path)
        
        if not text:
            await processing_msg.edit_text("❌ Не удалось распознать речь. Попробуйте еще раз.")
            return
        
        # Создаем задачу в Trello
        title = f"🎤 Задача от {message.from_user.first_name}\n{text}\n"
        description = f"**Голосовая задача**\n\n{text}\n\n---\nСоздано через @{config.BOT_USERNAME}"
        
        result = create_task(title, description)
        
        if result:
            card_url = result.get('url', '#')
            await processing_msg.edit_text(
                f"✅ **Задача создана!**\n\n"
                f"**Текст:** {text}\n"
                f"**Исполнитель:** {message.from_user.first_name}\n"
                f"**Ссылка:** [Открыть в Trello]({card_url})",
                parse_mode="Markdown"
            )
        else:
            await processing_msg.edit_text("❌ Ошибка создания задачи в Trello")
        
    except Exception as e:
        logging.exception("Ошибка обработки")
        await processing_msg.edit_text(f"❌ Произошла ошибка: {str(e)[:100]}")
    finally:
        # Очищаем временные файлы
        cleanup_temp_files(ogg_path, wav_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())