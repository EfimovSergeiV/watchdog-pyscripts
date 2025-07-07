""" Пробуждение компьютеров в сети """
import websocket, json, time
from utils.wake_on_lan import send_wol
from utils.mattermost import send_notification

from conf import MATTERMOST_WS, BOT_TOKEN, ACCESS_LIST, SERVER_ID


def on_message(ws, message):
    data = json.loads(message)
    # print(f"📨 Получено сообщение: {data}")
    if data.get("event") == "posted":
        post_raw = data["data"]["post"]
        post_data = json.loads(post_raw)

        message_text = post_data.get("message")
        sender_name = data["data"].get("sender_name", "Неизвестный пользователь")

        print(f"💬 { sender_name }: { message_text }")

        user = ACCESS_LIST.get(sender_name)

        WORDS = ["вкл", "on", "включи", "разбуди","включить", "запуск", "wake", "старт" ]
        if user:
            command = message_text.lower().strip().split()

            first_word = command.pop(0) if command else None
            if len(command) == 0 and first_word in WORDS:
                # Запуск первого доступного
                print(f"Проверка команды 1: запуск первого доступного для пользователя компьютера")
                send_notification(user['channel_id'], f"{ SERVER_ID }: Пробую разбудить {user['computers'][0]['name']}...")

            elif len(command) >= 1 and first_word in WORDS:
                # Пробуждение нескольких компьютеров по имени или индексу

                # Пробуждение по индексу
                if command[0].isdigit():
                    computer_index = [int(index) for index in command if index.isdigit()]
                    for computer in computer_index:
                        print(f"COMPUTER: {computer - 1}")
                        watch_comp = user["computers"][computer - 1] if computer - 1 < len(user["computers"]) else None
                        if watch_comp:
                            print(f"Пробуждаю компьютер {watch_comp['name']} ({watch_comp['mac']})")
                            send_notification(user['channel_id'], f"{ SERVER_ID }: Пробую разбудить {watch_comp['name']}...")
                            send_wol(watch_comp['mac'], watch_comp['broadcast_ip'])
                
                else:
                    # Пробуждение по имени
                    for computer_name in command:
                        watch_comp = next((comp for comp in user["computers"] if comp["name"].lower() == computer_name.lower()), None)
                        if watch_comp:
                            print(f"Пробуждаю компьютер {watch_comp['name']} ({watch_comp['mac']})")
                            send_notification(user['channel_id'], f"{ SERVER_ID }: Пробую разбудить {watch_comp['name']}...")
                            send_wol(watch_comp['mac'], watch_comp['broadcast_ip'])
                        else:
                            print(f"Компьютер с именем '{computer_name}' не найден в списке пользователя.")

    else:
        print("📨 Получено сообщение (не post):")
        # print(json.dumps(data, indent=2, ensure_ascii=False))


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

    try:
        while True:
            try:
                ws = websocket.WebSocketApp(
                    MATTERMOST_WS,
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close
                )
                print("🔁 Подключаемся к WebSocket...")
                ws.run_forever(ping_interval=30, ping_timeout=10)

            except Exception as e:
                print(f"⚠️ Ошибка WebSocket: {e}")

            print("⏳ Переподключение через 2 минуты...")
            time.sleep(120)

    except KeyboardInterrupt:
        print("⏹️ Прерывание работы скрипта пользователем.")