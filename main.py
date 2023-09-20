from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from requests import get
from json import loads
from googletrans import Translator, LANGCODES
from logging import basicConfig, getLogger, DEBUG


basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=DEBUG)
logger = getLogger(__name__)
TOKEN = '6058507940:AAEAb_bmD0lXXT_a742jKCXlHrYRfaGNsaI'
bot = TeleBot(TOKEN)
API_open_weather = 'c507bcf8971af71b550c3281cad1b275'
translator = Translator(service_urls=['translate.googleapis.com'])
langs_names = list(LANGCODES.keys())


@bot.message_handler(commands=['choose_lang'])
def choose_lang(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(language) for language in langs_names]
    for button in buttons:
        markup.add(button)
    bot.send_message(message.chat.id, f'Please choose your language or write in English', reply_markup=markup)


@bot.message_handler(commands=['start', 'menu'])
def start(message):
    print(message.from_user.first_name == None, message.from_user.last_name == None)
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name} {message.from_user.last_name}! Я универсальный чат-бот для выдачи информации о '
                     f'погоде.\nДля выдачи информации о погоде в городе введи его название:')


@bot.message_handler(func=lambda message: message.text.strip().lower() in langs_names)
def switch_lang(message):
    bot.send_message(message.chat.id, f'Your language: {message.text.strip().lower()}')


@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    result = get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_open_weather}&units=metric')
    if result.status_code == 200:
        data = loads(result.text)
        city = translator.translate(data['name'], src='en', dest='ru').text
        temp = data['main']['temp']
        real_temp = data['main']['feels_like']
        conditions = data['weather'][0]['description']
        pressure = data['main']['pressure']
        humidity = data['main']['humidity']
        bot.reply_to(message, f'Температура в городе {city}: {temp} °C, ощущается как {real_temp} °C\nПогодные условия: '
                              f'{conditions}\nДавление воздуха: {pressure} гПа\nВлажность воздуха: {humidity}%')
        if 'clear sky' in conditions:
            sticker_id = 'CAACAgIAAxkBAAEKWRdlC0Wx9frwcRPpLexyORlPRdSaqgAC1DEAAqY7WEjqpGH2oeOzlTAE'
        elif 'light rain' in conditions:
            sticker_id = 'CAACAgIAAxkBAAEKWS9lC1GI2grIW91nBQc7h4R2Iet8JwACPDcAAjTpUEiCyCmPfMIF2jAE'
        elif 'moderate rain' in conditions:
            sticker_id = 'CAACAgIAAxkBAAEKWTxlC1PpXf-hn28iQriymSDihXzIsAAC90AAAqfUWUilawirv5bpLzAE'
        elif 'heavy intensity rain' in conditions:
            sticker_id = 'CAACAgIAAxkBAAEKWS1lC1EWKMRvJ_pxkL3r3YZItnx28QACMzwAAtaTYEjjYaSA5JG9ZTAE'
        elif 'overcast clouds' in conditions or 'broken clouds' in conditions:
            sticker_id = 'CAACAgIAAxkBAAEKWSZlC0iq2_M72eEYRmnqB_tQr92KgQACsjkAAkdbWEhyZFRbA_1pHzAE'
        elif 'mist' in conditions or 'fog' in conditions:
            sticker_id = 'CAACAgIAAxkBAAEKWFdlCvMgbEyu0ovY3RTLWljNlCQNsgACrTgAAq4lWUjCR7-2E9FdODAE'
        bot.send_sticker(message.chat.id, sticker_id)
    else:
        bot.send_message(message.chat.id, 'Название города некорректно')

@bot.message_handler(content_types=['photo', 'audio', 'voice', 'video', 'text'])
def GetMedia(message):
    bot.reply_to(message, 'Я не определил вашу команду\nВведите <u>/start</u> , чтобы продолжить', parse_mode='html')

bot.polling(none_stop=True)
