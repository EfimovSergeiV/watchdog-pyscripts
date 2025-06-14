import pyaudio
import wave
import numpy as np
from datetime import datetime
from collections import deque
import time

# --- Конфигурация ---
THRESHOLD = 400  # Порог активации микрофона (чем ниже — тем чувствительнее)
CHUNK = 1024     # Размер блока аудио
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000     # Частота дискретизации
SILENCE_TIMEOUT = 2  # Секунды тишины до остановки записи

# --- Инициализация ---
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("🎙️ Ожидание громкого звука...")

recording = False
frames = []
silence_timer = None

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        volume = np.linalg.norm(audio_data)

        if volume > THRESHOLD:
            if not recording:
                print("🔴 Звук обнаружен, начинаю запись...")
                recording = True
                frames = []

            frames.append(data)
            silence_timer = time.time()
        elif recording:
            frames.append(data)
            # Проверяем, не истекло ли время тишины
            if time.time() - silence_timer > SILENCE_TIMEOUT:
                print("⏹️ Тихо. Завершаю запись.")
                filename = datetime.now().strftime("recording_%Y%m%d_%H%M%S.wav")
                wf = wave.open(f"recordings/{filename}", 'wb') # Под виндой тут будет проблема с путём
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                print(f"💾 Записано в файл: {filename}")
                recording = False
        else:
            pass  # Тихо, ждем

except KeyboardInterrupt:
    print("\n🚪 Завершение по Ctrl+C")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
