import telebot
import requests
import json
import webbrowser
import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

@bot.message_handler(commands=['start', 'main', 'hello'])
def send_welcome(message):
    bot.reply_to(message, f'Привет, {message.from_user.first_name}! Чем могу помочь?')
@bot.message_handler(commands=['site', 'website'])
def site(message):
    webbrowser.open('https://developers.sber.ru/portal/products/gigachat-api')
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, f'Привет, Я нейронная сеть GigaChat. Могу помочь тебе с любым вопросом!')

@bot.message_handler(commands=['profile'])
def profile(message):
    bot.reply_to(message, message)

@bot.message_handler()
def gpt_request(message):
    token = update_token() # получаю токен авторизации
    print(token)
    text = message.text
    r_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = json.dumps({
        "model": "GigaChat:latest",
        "temperature": 0.87,
        # от 0 до 2, чем выше, тем вывод более случайный, не рекомендуетсы использовать совместно c top_p
        "top_p": 0.47,
        # от 0 до 1, альтернатива параметру temperature, не рекомендуется использовать совместно c temperature
        "n": 1,  # от 1 до 4, число вариантов ответов модели
        "max_tokens": 512,  # максимальное число токенов для генерации ответов
        "repetition_penalty": 1.07,
        # количество повторений слов, 1.0 - ни чего не менять, от 0 до 1 повторять уже сказанные слова, от 1 и далее не использовать сказанные слова
        "stream": False,  # если true, будут отправляться частичные ответы сообщений
        "update_interval": 0,  # интервал в секундах, не чаще которого будут присылаться токены в stream режиме
        "messages": [
            {
                "role": "system",  # контекст
                "content": "Отвечай как научный сотрудник"
            },
            {
                "role": "user",  # запрос пользователя
                "content": f'{text}'
            }

        ]
    })
    headers = r_headers
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print(response.text)
    p_object = json.loads(response.text)
    user_answer = p_object['choices'][0]['message']['content']
    tokens = count_tokens(text, token)
    bot.reply_to(message, user_answer)
    bot.send_message(message.chat.id, f'<b>Потрачено - {tokens} токенов</b>',  parse_mode='HTML')
def update_token():
    url_2 = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload = 'scope=GIGACHAT_API_PERS'
    headers_2 = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': '6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e',
        'Authorization': 'Basic ZmQxYTM0NTUtMzQwMy00NDk1LTkxYTUtN2FiZGJjNGEzODVmOmEzMzA5OWVmLTA5ZDUtNDU2OC04ZWZiLTkxYTQ5OTJjZWU2YQ=='
    }
    response = requests.request("POST", url_2, headers=headers_2, data=payload, verify=False)
    result = json.loads(response.text)
    token = result['access_token']
    return token

def count_tokens(text, token):
    url_tokens = 'https://gigachat.devices.sberbank.ru/api/v1/tokens/count'
    payload = json.dumps({
        "model": "GigaChat",
        "input": [
            f'{text}'
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url_tokens, headers=headers, data=payload, verify=False)
    result = json.loads(response.text)
    print(result)
    tokens = result[0]['tokens']
    return tokens

bot.polling(non_stop=True)








