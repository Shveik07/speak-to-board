import subprocess
import os
from bot.core import config

def convert_ogg_to_wav(ogg_path, wav_path):
    # Конвертирует OGG в WAV с параметрами, необходимыми для Vosk:
    # - частота дискретизации 16000 Гц
    # - моно
    # - 16-bit PCM
    # Использует FFmpeg (должен быть установлен в системе).
    cmd = [
        config.FFMPEG_PATH,     # используем полный путь или имя
        '-i', ogg_path,         # входной файл
        '-ar', '16000',         # частота 16 кГц
        '-ac', '1',             # моно
        '-sample_fmt', 's16',   # 16-bit PCM
        '-y',                   # перезаписывать, если файл существует
        wav_path
    ]
    try:
        # Запускаем FFmpeg и проверяем результат
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return wav_path
    except subprocess.CalledProcessError as e:
        print(f"Ошибка FFmpeg: {e.stderr}")
        raise
    except FileNotFoundError:
        raise Exception("FFmpeg не найден. Убедитесь, что он установлен и добавлен в PATH.")

def cleanup_temp_files(*file_paths):
    # Удаляет временные файлы, если они существуют.
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Не удалось удалить {file_path}: {e}")