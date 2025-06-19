from utils.mattermost import send_notification
from datetime import datetime
from collections import deque
import numpy as np

import time, os, cv2, pyaudio, wave, threading

_stop_event = threading.Event()



def save_recording(frames, p, FORMAT, CHANNELS, RATE):
    directory = "../REC/recordings"
    os.makedirs(directory, exist_ok=True)  # Создаем каталог, если нет

    filename = datetime.now().strftime("%d-%m-%Y_%H-%M-%S.wav")
    filepath = os.path.join(directory, filename)

    wf = wave.open(filepath, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"💾 Запись сохранена: {filepath}")
    send_notification(f"Сохранена запись: {filename}")


def save_image(frame):
    filename = datetime.now().strftime("%d-%m-%Y_%H-%M-%S.jpg")
    directory = f'../REC/photos/{datetime.now().strftime("%d-%m-%Y")}'
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, filename)
    cv2.imwrite(filepath, frame)


def sound_func():
    # --- Конфигурация ---
    THRESHOLD = 15000
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    SILENCE_TIMEOUT = 3

    # Инициализая микрофона
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    # Инициализация камеры
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("🚫 Камера недоступна")
        cap = None

    print("🎙️ Начинаем прослушивать...")
    send_notification("Начинаем прослушивать...")

    recording = False
    frames = []
    silence_timer = None

    try:
        while not _stop_event.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.linalg.norm(audio_data)

            if volume > THRESHOLD:
                if not recording:
                    print("🔴 Звук обнаружен, начинаю запись...")
                    send_notification("Обнаружен звук, начинаю запись...")
                    recording = True
                    frames = []

                if cap is not None:
                    ret, frame = cap.read()
                    if ret:
                        save_image(frame)
                    else:
                        print("❌ Ошибка при получении кадра с камеры")

                frames.append(data)
                silence_timer = time.time()

            elif recording:
                frames.append(data)
                if time.time() - silence_timer > SILENCE_TIMEOUT:
                    save_recording(frames, p, FORMAT, CHANNELS, RATE)
                    recording = False
                    frames = []

    finally:
        if recording and frames:
            print("⚠️ Прерывание во время записи — сохраняем вручную...")
            save_recording(frames, p, FORMAT, CHANNELS, RATE)
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("FINALLY: Поток микрофона остановлен.")
        send_notification("Прослушивание остановлено.")


def stop_sound():
    _stop_event.set()


def reset_sound():
    global _stop_event
    _stop_event = threading.Event()