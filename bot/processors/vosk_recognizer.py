import json
import wave
import os
from vosk import Model, KaldiRecognizer

class VoskRecognizer:
    def __init__(self, model_path):
        """Инициализация модели Vosk [1]"""
        if not os.path.exists(model_path):
            raise Exception(f"Модель не найдена: {model_path}")
        self.model = Model(model_path)
        self.rec = None
        
    def transcribe(self, audio_path):
        """Распознавание речи из WAV файла [9]"""
        try:
            wf = wave.open(audio_path, "rb")
            
            # Проверка формата [7]
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                raise Exception("Аудио должно быть моно, 16-bit PCM")
            
            self.rec = KaldiRecognizer(self.model, wf.getframerate())
            
            # Чтение и обработка аудио
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                self.rec.AcceptWaveform(data)
            
            # Получение финального результата
            result = json.loads(self.rec.FinalResult())
            wf.close()
            
            return result.get("text", "")
            
        except Exception as e:
            print(f"Ошибка распознавания: {e}")
            return ""