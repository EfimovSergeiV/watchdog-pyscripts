import pyaudio
import numpy as np

CHUNK = 1024
RATE = 16000

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("🎤 Слушаю микрофон...")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio ** 2))
        db = 20 * np.log10(rms + 1)  # +1 чтобы избежать log(0)
        print(f"🔊 Уровень громкости: {db:.2f} дБ")
except KeyboardInterrupt:
    print("\nЗавершение")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
