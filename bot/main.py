import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from bot.core import config
from bot.processors.audio_processor import convert_ogg_to_wav, cleanup_temp_files
from bot.processors.vosk_recognizer import VoskRecognizer
# from bot.processors.trello_api import create_task
from bot.processors import trello_api
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Хранилище выбора списка для каждого пользователя (user_id -> list_id)
user_list_choice = {}

logging.basicConfig(level=logging.INFO)

os.makedirs(config.TEMP_DIR, exist_ok=True)

# Инициализация
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
recognizer = VoskRecognizer(config.VOSK_MODEL_PATH)

# Убедимся, что папка temp существует
os.makedirs(config.TEMP_DIR, exist_ok=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для создания задач из голосовых сообщений.\n\n"
        "📢 Отправь мне голосовое сообщение, и я создам задачу в Trello.\n"
        "👥 Задача будет назначена на тебя автоматически.\n"
        "Команды:\n"
        "/lists - показать все колонки на доске и выбрать одну\n"
        "/reset - сбросить выбранную колонку на значение по умолчанию (Задачи создаваемые ботом)"
    )

@dp.message(Command("reset"))
async def cmd_reset(message: types.Message):
    #Сбрасывает выбранный пользователем список на значение по умолчанию (Задачи создаваемые ботом).
    user_id = message.from_user.id
    if user_id in user_list_choice:
        del user_list_choice[user_id]
    await message.answer("✅ Выбор сброшен. Используется колонка по умолчанию -**Задачи создаваемые ботом.**")

@dp.message(Command("lists"))
async def cmd_lists(message: types.Message):
    #Показывает все списки на доске и предлагает выбрать один.
    try:
        lists = trello_api.get_board_lists()
        if not lists:
            await message.answer("❌ Не удалось получить списки или на доске нет колонок.")
            return

        # Создаём инлайн-кнопки для каждого списка
        buttons = [
            [InlineKeyboardButton(text=lst['name'], callback_data=f"setlist_{lst['id']}")]
            for lst in lists
        ]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("Выберите колонку, в которую будут попадать новые задачи:", reply_markup=kb)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.callback_query(lambda c: c.data.startswith('setlist_'))
async def process_setlist(callback: types.CallbackQuery):
    """Обработчик выбора списка из инлайн-кнопок."""
    list_id = callback.data.split('_')[1]
    user_id = callback.from_user.id
    user_list_choice[user_id] = list_id
    await callback.answer("✅ Выбор сохранён", show_alert=False)
    # Найдём название списка для красивого ответа (можно дополнительно)
    lists = trello_api.get_board_lists()
    list_name = next((lst['name'] for lst in lists if lst['id'] == list_id), "Неизвестный список")
    await callback.message.edit_text(f"✅ Теперь задачи будут создаваться в колонке **{list_name}**.")

@dp.message(lambda message: message.voice)
async def handle_voice(message: types.Message):
    processing_msg = await message.reply("🎤 Распознаю речь...")
    
    ogg_path = None
    wav_path = None
    
    try:
        # Определяем, какой список использовать для этого пользователя
        user_id = message.from_user.id
        target_list = user_list_choice.get(user_id, config.TRELLO_LIST_ID)

        # Скачиваем голосовое сообщение
        file = await bot.get_file(message.voice.file_id)
        ogg_path = f"{config.TEMP_DIR}/{message.voice.file_id}.ogg"
        wav_path = f"{config.TEMP_DIR}/{message.voice.file_id}.wav"
        
        await bot.download_file(file.file_path, ogg_path)
        
        # Конвертируем в WAV
        await asyncio.to_thread(convert_ogg_to_wav, ogg_path, wav_path)
        
        # Распознаем текст
        text = await asyncio.to_thread(recognizer.transcribe, wav_path)
        
        if not text:
            await processing_msg.edit_text("❌ Не удалось распознать речь. Попробуйте еще раз.")
            return
        
        # Создаем задачу в Trello
        title = f"🎤 Задача от {message.from_user.first_name}\n{text}\n"
        description = f"**Голосовая задача**\n\n{text}\n\n---\nСоздано через @{config.BOT_USERNAME}"
        
        result = trello_api.create_task(title, description, list_id=target_list)
        
        if result:
            card_url = result.get('url', '#')
            await processing_msg.edit_text(
                f"✅ **Задача создана!**\n\n"
                f"**Текст:** {text}\n"
                f"**Исполнитель:** {message.from_user.first_name}\n"
                # f"**Колонка** {list_name}\n",
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