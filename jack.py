import websocket, json, time, os, threading
from utils.mattermost import send_notification
from conf import MATTERMOST_WS, BOT_TOKEN, USER_ACCESS


# from utils.sound import sound_func, stop_sound, reset_sound
from utils.sound_images import sound_func, stop_sound, reset_sound


sound_thread = None

def start_sound():
    global sound_thread
    if sound_thread is None or not sound_thread.is_alive():
        print("▶️ Запускаем прослушивание микрофона...")
        reset_sound()  # Сбрасываем Event перед стартом
        sound_thread = threading.Thread(target=sound_func)
        sound_thread.start()
    else:
        print("🔄 Уже прослушиваем...")
        send_notification("Уже прослушиваем...")

def stop_sound_thread():
    global sound_thread
    if sound_thread and sound_thread.is_alive():
        print("⏹ Останавливаем прослушивание микрофона...")
        stop_sound()
        sound_thread.join(timeout=5)
        # send_notification("Больше не слушаю.") # До сюда не доходит
    else:
        print("🔇 Нечего останавливать.")
        send_notification("Прослушивание не запущено...")


def on_message(ws, message):
    print("📨 Получено сообщение:")

    data = json.loads(message)

    if data.get("event") == "posted":
        post_raw = data["data"]["post"]
        post_data = json.loads(post_raw)

        message_text = post_data.get("message", "")
        sender_name = data["data"].get("sender_name", "Неизвестный пользователь")

        print(f"💬 {sender_name}: {message_text}")

        if sender_name in USER_ACCESS:
            command = message_text.lower().strip()

            if command in ["стоп", "останови", "не слушай", "не слушать"]:
                stop_sound()

            elif command in ["старт", "слушай", "слушать", "запись", "начать",]:
                start_sound()

            elif command in ["выкл", "выключить",]:
                send_notification("Выключаем миникомпьютер.")
                stop_sound()
                ws.close()
                os.system("shutdown /s /t 1")

            elif command in ["вкл", "включи", "разбуди","включить", "запуск", "wake", "старт"]:
                send_notification("Миникомпьютер уже запущен")

            else:
                print(f"❓ Неизвестная команда: {command}")
                send_notification(f"Неизвестная команда: `{command}`")

    else:
        print("📨 Сообщение не является post:")
        print(json.dumps(data, indent=2, ensure_ascii=False))


def on_error(ws, error):
    print("❌ Ошибка:", error)


def on_close(ws, close_status_code, close_msg):
    print(f"🔒 Соединение закрыто: {close_status_code} {close_msg}")


def on_open(ws):
    print("🔓 WebSocket подключен, ждём 1 секунду перед отправкой токена...")
    time.sleep(1)
    payload = {
        "seq": 1,
        "action": "authentication_challenge",
        "data": {
            "token": BOT_TOKEN
        }
    }
    print("➡️ Отправляем токен авторизации...")
    ws.send(json.dumps(payload))


if __name__ == "__main__":
    send_notification("Миникомпьютер запущен.")
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        MATTERMOST_WS,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    try:
        ws.run_forever()
    finally:
        stop_sound()