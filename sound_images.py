import pyaudio
import wave
import numpy as np
import cv2
from datetime import datetime
import time
import os

# --- Конфигурация ---
THRESHOLD = 600
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_TIMEOUT = 3  # секунд тишины до остановки записи

# --- Папки ---
os.makedirs("photos", exist_ok=True)
os.makedirs("recordings", exist_ok=True)

# --- Инициализация аудио ---
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# --- Инициализация камеры ---
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("❌ Не удалось открыть камеру")
    exit()

print("🎙️ Ожидание громкого звука...")

recording = False
frames = []
silence_timer = None
session_id = None  # для группы файлов

def take_photo(tag=""):
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S_%f")
    filename = f"photos/photo_{tag}_{timestamp}.jpg"
    ret, frame = camera.read()
    if ret:
        cv2.imwrite(filename, frame)
        print(f"📷 Снимок сделан: {filename}")
    else:
        print("❌ Ошибка при съёмке")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        volume = np.linalg.norm(audio_data)

        if volume > THRESHOLD:
            if not recording:
                session_id = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
                print("🔴 Громкий звук! Запись началась.")
                recording = True
                frames = []

            # Делать снимок при каждом громком событии
            take_photo(tag=session_id)

            frames.append(data)
            silence_timer = time.time()

        elif recording:
            frames.append(data)
            if time.time() - silence_timer > SILENCE_TIMEOUT:
                print("⏹️ Тишина. Завершаю запись.")
                filename = f"recordings/recording_{session_id}.wav"
                wf = wave.open(filename, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                print(f"💾 Аудио сохранено: {filename}")
                recording = False
        else:
            pass

except KeyboardInterrupt:
    print("\n🚪 Выход по Ctrl+C")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    camera.release()
