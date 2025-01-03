import sys
import locale
import requests
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

url = 'https://api.x.ai/v1/chat/completions'
api_key = 'XAI TOKEN'

bot_token = 'TG TOKEN'
messages = [
    {"role": "system", "content": "Roles"}
]

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

def send_telegram_message(text, chat_id):
    telegram_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(telegram_url, json=payload)

def chat_with_ai_tg(update):
    chat_id = update['message']['chat']['id']

    user_input = update['message'].get('text')

    if not user_input:
        send_telegram_message("Пожалуйста, отправьте текстовое сообщение.", chat_id)
        return

    if user_input.lower() == 'exit':
        send_telegram_message("Чат завершен. До свидания!", chat_id)
        return

    messages.append({"role": "user", "content": user_input})

    data = {
        "model": "grok-2-1212",
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        response_data = response.json()
        ai_response = response_data['choices'][0]['message']['content']
        send_telegram_message(ai_response, chat_id)

        messages.append({"role": "assistant", "content": ai_response})

    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP ошибка: {http_err}\nОтвет сервера: {response.text}"
        send_telegram_message(error_message, chat_id)
    except requests.exceptions.RequestException as err:
        error_message = f"Ошибка при запросе: {err}"
        send_telegram_message(error_message, chat_id)

def handle_update(update):
    if 'message' in update:
        chat_with_ai_tg(update)

url_updates = f'https://api.telegram.org/bot{bot_token}/getUpdates'
last_update_id = None

while True:
    response = requests.get(url_updates, params={"offset": last_update_id + 1 if last_update_id else None})
    updates = response.json().get('result', [])

    for update in updates:
        handle_update(update)
        last_update_id = update['update_id']

    time.sleep(2)
