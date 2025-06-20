""" Сторожевая собака котороя разбудит Джека """
import websocket, json, time
from utils.wake_on_lan import send_wol
from utils.mattermost import send_notification

from conf import WS_URL, BOT_TOKEN, USER_ACCESS, MAC_ADDRESS, BROADCAST_IP



def on_message(ws, message):
    print("📨 Получено сообщение:")

    data = json.loads(message)

    if data.get("event") == "posted":
        post_raw = data["data"]["post"]
        post_data = json.loads(post_raw)

        message_text = post_data.get("message")
        sender_name = data["data"].get("sender_name", "Неизвестный пользователь")

        print(f"💬 {sender_name}: {message_text}")

        WORDS = ["вкл", "включи", "разбуди","включить", "запуск", "wake", "старт"]
        command = message_text.lower().strip()
        
        if sender_name in USER_ACCESS:
            if command in WORDS:
                print("🔔 Разбудим Джека!")
                send_notification("Пробую разбудить миникомпьютер...")
                send_wol(MAC_ADDRESS, BROADCAST_IP)

    else:
        print("📨 Получено сообщение (не post):")
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
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()