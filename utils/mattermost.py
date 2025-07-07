import requests
from conf import BOT_TOKEN, MATTERMOST_URL


def send_notification(channel_id, message):
    """ Отправляет сообщение в Mattermost """
   
    url = f"{MATTERMOST_URL}/api/v4/posts"
    headers = {
        'Authorization': f'Bearer { BOT_TOKEN }',
        'Content-Type': 'application/json'
    }
    payload = {
        'channel_id': channel_id,
        'message': message
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print("✅ Notification sent successfully.")
    else:
        print(f"❌ Failed to send notification: { response.status_code } - { response.text }")

