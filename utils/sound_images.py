from utils.mattermost import send_notification
from datetime import datetime
import numpy as np
from conf import ABSOLUTE_PATH

import time, os, cv2, pyaudio, wave, threading

_stop_event = threading.Event()



def save_recording(frames, p, FORMAT, CHANNELS, RATE, duration):
    directory = f"{ABSOLUTE_PATH}/recordings"
    os.makedirs(directory, exist_ok=True)  # Создаем каталог, если нет

    filename = datetime.now().strftime("%d-%m-%Y_%H-%M-%S.wav")
    filepath = os.path.join(directory, filename)

    wf = wave.open(filepath, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"💾({int(duration)} сек.) Запись сохранена: {filepath}")
    send_notification(f"({int(duration)} сек.) Запись сохранена: {filename}")


def save_image(frame):
    filename = datetime.now().strftime("%d-%m-%Y_%H-%M-%S.jpg")
    directory = f'{ABSOLUTE_PATH}/photos/{datetime.now().strftime("%d-%m-%Y")}'
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
    MINIMUM_LOUD_DURATION = 1   # Минимальная длительность громкого звука для начала записи
    SILENCE_TIMEOUT = 8         # Время ожидания тишины перед сохранением

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

    loud_start_time = None      # Время начала громкого звука
    record_start_time = None    # Время начала записи
    recording = False
    frames = []
    silence_timer = None

    try:
        while not _stop_event.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.linalg.norm(audio_data)

            now = time.time()

            if volume > THRESHOLD:
                if loud_start_time is None:
                    loud_start_time = now

                print(f"Шумим в течении {now - loud_start_time:.2f} секунд, громкость: {volume:.2f}")

                if not recording and (now - loud_start_time) >= MINIMUM_LOUD_DURATION:
                    print("Обнаружен звук, начинаю запись...")
                    send_notification("Обнаружен звук, начинаю запись...")
                    record_start_time = time.time()
                    recording = True
                    frames = []

                    # 💡 Сделать снимок камеры
                    if cap is not None:
                        ret, frame = cap.read()
                        if ret:
                            save_image(frame)
                        else:
                            print("❌ Ошибка при получении кадра с камеры")

                if recording:
                    frames.append(data)
                    silence_timer = now

            else:
                # 🔇 Сброс таймера громкости, если нет устойчивого звука
                loud_start_time = None

                if recording:
                    frames.append(data)
                    if now - silence_timer > SILENCE_TIMEOUT:
                        duration = time.time() - record_start_time
                        save_recording(frames, p, FORMAT, CHANNELS, RATE, duration)
                        recording = False
                        frames = []

    finally:
        if recording and frames:
            print("⚠️ Прерывание во время записи — сохраняем вручную...")
            duration = time.time() - record_start_time
            save_recording(frames, p, FORMAT, CHANNELS, RATE, duration)
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