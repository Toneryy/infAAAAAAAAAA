from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Message
from requests import get, Response
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
menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
menu_markup.add(KeyboardButton('🏙 Выбор города'), KeyboardButton('🗺 Погода по геолокации', request_location=True))
menu_markup.add(KeyboardButton('🇺🇸 Выбор языка'), KeyboardButton('ℹ️ Информация'))
menu_markup.add(KeyboardButton('🔧 Настройки'), KeyboardButton('✍️ Написать разработчикам'))
menu_markup.add(KeyboardButton('💸 Поддержать проект'))
back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
back_markup.add(KeyboardButton('🔙 Назад'))


def get_weather(message: Message, result: Response) -> None:
    if result.status_code == 200:
        data = loads(result.text)
        city = translator.translate(data['name'], src='en', dest='ru').text
        temp = data['main']['temp']
        real_temp = data['main']['feels_like']
        conditions = data['weather'][0]['description']
        pressure = data['main']['pressure']
        humidity = data['main']['humidity']
        bot.reply_to(message,
                     f'Температура в городе {city}: {temp} °C, ощущается как {real_temp} °C\nПогодные условия: '
                     f'{conditions}\nДавление воздуха: {int(pressure/1.333)} мм. рт. ст.\nВлажность воздуха: '
                     f'{humidity}%')
        if conditions == 'clear sky':
            sticker_id = 'CAACAgIAAxkBAAEKWV9lC2QKSuI1rAHW6qA-v9CBnw00iQACOzYAAjVQYUjAUz1pjKjxtjAE'
        elif conditions == 'light rain':
            sticker_id = 'CAACAgIAAxkBAAEKWS9lC1GI2grIW91nBQc7h4R2Iet8JwACPDcAAjTpUEiCyCmPfMIF2jAE'
        elif conditions == 'moderate rain':
            sticker_id = 'CAACAgIAAxkBAAEKWTxlC1PpXf-hn28iQriymSDihXzIsAAC90AAAqfUWUilawirv5bpLzAE'
        elif conditions == 'heavy intensity rain':
            sticker_id = 'CAACAgIAAxkBAAEKWS1lC1EWKMRvJ_pxkL3r3YZItnx28QACMzwAAtaTYEjjYaSA5JG9ZTAE'
        elif conditions in ['broken clouds', 'scattered clouds', 'overcast clouds']:
            sticker_id = 'CAACAgIAAxkBAAEKWSZlC0iq2_M72eEYRmnqB_tQr92KgQACsjkAAkdbWEhyZFRbA_1pHzAE'
        elif conditions in ['mist', 'smoke']:
            sticker_id = 'CAACAgIAAxkBAAEKWFdlCvMgbEyu0ovY3RTLWljNlCQNsgACrTgAAq4lWUjCR7-2E9FdODAE'
        bot.send_sticker(message.chat.id, sticker_id, reply_markup=back_markup)
    else:
        bot.send_message(message.chat.id, 'Название города некорректно, введи еще раз:')


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    username = ''
    if message.from_user.first_name:
        username += message.from_user.first_name
    if message.from_user.last_name:
        username += ' ' + message.from_user.last_name
    username = username.strip()
    bot.send_message(message.chat.id,
                     f'Привет, {username}! Я универсальный чат-бот для выдачи информации о погоде.\nПродолжая '
                     f'пользоваться ботом, ты даешь свое <a href="https://docs.google.com/document/d/'
                     f'1Y8jrM_0F6xaME0gTi3hUVM7O6FSjxAIFiSFuyHFIt2E/edit?usp=sharing">согласие на обработку '
                     f'персональных данных</a>\n\nВыбери то, что тебе нужно:', reply_markup=menu_markup,
                     parse_mode='HTML')


@bot.message_handler(commands=['menu'])
def menu(message: Message) -> None:
    bot.send_message(message.chat.id,
                     f'Ты вернулся в меню!\nВыбери то, что тебе нужно:', reply_markup=menu_markup)


@bot.message_handler(func=lambda message: message.text == '🏙 Выбор города')
def choose_city(message: Message) -> None:
    bot.send_message(message.chat.id, f'Введите название города: ')


@bot.message_handler(func=lambda message: message.text == '🇺🇸 Выбор языка')
def choose_lang(message: Message) -> None:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(language) for language in langs_names]
    for button in buttons:
        markup.add(button)
    bot.send_message(message.chat.id, f'Please choose your language or write in English', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'ℹ️ Информация')
def information(message: Message) -> None:
    bot.send_message(message.chat.id,
                     'Данный бот создан группой разработчиков из России, представлен в более чем сотне языков мира.\n'
                     'Создан для выдачи информации о погоде в выбранных пользователями городах.\n'
                     'Написан на языке программирования Python c использованием следующих библиотек:\n'
                     'telebot, json, requests, googletrans, logging.', reply_markup=back_markup)


@bot.message_handler(func=lambda message: message.text == '🔧 Настройки')
def settings(message: Message) -> None:
    bot.send_message(message.chat.id, 'здесь пусто :(', reply_markup=back_markup)


@bot.message_handler(func=lambda message: message.text == '💸 Поддержать проект')
def donate(message: Message) -> None:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Поддержать', url='https://google.com'))
    bot.send_message(message.chat.id, 'Спасибо, что поддерживаете наш продукт, так мы станем лучше.',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '✍️ Написать разработчикам')
def write(message: Message) -> None:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Написать', url='https://forms.gle/4ET9KWs1Vqh3vZo37'))
    bot.send_message(message.chat.id, 'Мы всегда рады вашим предложениям. Спасибо, что помогаете нам стать лучше!',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🔙 Назад')
def back(message: Message) -> None:
    menu(message)


@bot.message_handler(func=lambda message: message.text.strip().lower() in langs_names)
def switch_lang(message: Message) -> None:
    bot.send_message(message.chat.id, f'Your language: {message.text.strip().lower()}', reply_markup=back_markup)


@bot.message_handler(content_types=['text'])
def text_type(message: Message) -> None:
    city = message.text.strip().lower()
    result = get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_open_weather}&units=metric')
    get_weather(message, result)


@bot.message_handler(content_types=['location'])
def location_type(message: Message) -> None:
    location = message.location
    print(location)
    result = get(f'https://api.openweathermap.org/data/2.5/weather?lon={location.longitude}&lat='
                 f'{location.latitude}&appid={API_open_weather}&units=metric')
    get_weather(message, result)


@bot.message_handler(content_types=['audio', 'document', 'animation', 'game', 'photo', 'sticker', 'video', 'video_note',
                                    'voice', 'contact', 'venue', 'dice', 'invoice', 'successful_payment',
                                    'connected_website', 'poll', 'passport_data', 'web_app_data'])
def unknown_type(message: Message) -> None:
    bot.reply_to(message, 'Я не распознал введенные вами данные😢\nНажмите кнопку 🔙 Назад, чтобы вернуться в меню',
                 parse_mode='html', reply_markup=back_markup)


bot.polling(none_stop=True)
