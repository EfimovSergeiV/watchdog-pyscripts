import requests
from conf import BOT_TOKEN, MATTERMOST_URL, CHANNEL_ID


def send_notification(message="Hello, Mattermost!"):
    """ Send a notification to the Mattermost channel. """
   
    url = f"{MATTERMOST_URL}/api/v4/posts"
    headers = {
        'Authorization': f'Bearer {BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'channel_id': CHANNEL_ID,
        'message': message
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print("✅ Notification sent successfully.")
    else:
        print(f"❌ Failed to send notification: {response.status_code} - {response.text}")

