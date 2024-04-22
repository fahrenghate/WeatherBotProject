import os
import datetime
import requests
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Location

BOT_TOKEN = "7193872414:AAFA_aW7LzLKppy5fSZ-iYVW6A0fy0aMSgw"
OPENWEATHERMAP_API_KEY = "6df40c91c04d29efe8ab5a85c0d29e51"
OPENWEATHERMAP_API_URL = "http://api.openweathermap.org/data/2.5/weather"

cloudiness_translation = {
    'clear sky': 'Ясно',
    'light rain': 'Маленький дождь',
    'few clouds': 'Малооблачно',
    'scattered clouds': 'Рассеянные облака',
    'broken clouds': 'Облачно с прояснениями',
    'overcast clouds': 'Пасмурно',
    'mist': 'Туман',
    'smoke': 'Дымка',
    'haze': 'Мгла',
    'dust': 'Пыльно',
    'fog': 'Туман',
    'sand': 'Песок',
    'ash': 'Пепел',
    'squall': 'Шквалистая погода',
    'tornado': 'Торнадо',
    'light intensity drizzle': 'Грибной дождик'
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Отправить местоположение", request_location=True)
    keyboard.add(button)
    await message.reply("Привет!🖐 \nЯ бот для определения погоды. Просто отправь мне название города, или нажми кнопку ниже, чтобы отправить свое местоположение.", reply_markup=keyboard)


@dp.message_handler(content_types=[types.ContentType.TEXT, types.ContentType.LOCATION])
async def get_weather(message: types.Message):
    if message.content_type == types.ContentType.TEXT:
        city = message.text.capitalize()

        params = {
            'q': city,
            'appid': OPENWEATHERMAP_API_KEY, 
            'units': 'metric'
        }
    else:  # Если пользователь отправил локацию
        latitude = message.location.latitude
        longitude = message.location.longitude

        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': OPENWEATHERMAP_API_KEY,
            'units': 'metric'
        }

    response = requests.get(OPENWEATHERMAP_API_URL, params=params)
    weather_data = response.json()

    if response.status_code == 200:
        weather_description = weather_data['weather'][0]['description']
        temperature = round(weather_data['main']['temp'])
        humidity = weather_data['main']['humidity']
        timezone_offset = weather_data['timezone']
        local_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=timezone_offset)
        formatted_local_time = local_time.strftime('%d.%m.%Y %H:%M:%S')

        if weather_description in cloudiness_translation:
            weather_description_ru = cloudiness_translation[weather_description]
        else:
            weather_description_ru = weather_description

        if message.content_type == types.ContentType.TEXT:
            weather_message = f"Погода в городе {city}: \nОблачность: {weather_description_ru}\nТемпература: {temperature}°C\nВлажность: {humidity}%\nМестное время: {formatted_local_time}"
        else:  # Если пользователь отправил локацию
            weather_message = f"Погода в вашем текущем местоположении:\nОблачность: {weather_description_ru}\nТемпература: {temperature}°C\nВлажность: {humidity}%\nМестное время: {formatted_local_time}"
    else:
        if message.content_type == types.ContentType.TEXT:
            weather_message = 'Такого города в реале не существует, только в ваших мыслях...\n＞﹏＜'
        else:  # Если пользователь отправил локацию
            weather_message = 'Не удалось получить погоду для вашего текущего местоположения.'

    await message.reply(weather_message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
