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
AIR_API_URL = 'https://api.api-ninjas.com/v1/airquality'
AIR_API_KEY = 'xy3f78YBcCE5/DNQW/dqKA==Op4Zzd3SCjm5IRtK'
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
weather_photos = {
    'clear sky': 'yasno.jpeg',
    'light rain': 'malenki_dozhd.jpg',
    'few clouds': 'malooblachno.jpg',
    'scattered clouds': 'rasseyannie_oblaka.jpeg',
    'broken clouds': 'oblachno_s_proyasneniyami.jpg',
    'overcast clouds': 'pasmurno.jpeg',
    'mist': 'tuman.jpeg',
    'smoke': 'dyimka.jpeg',
    'haze': 'mgla.jpeg',
    'dust': 'pilno.jpeg',
    'fog': 'tuman.jpeg',
    'sand': 'pilno.jpeg',
    'ash': 'pepl.jpeg',
    'squall': 'shkval.jpeg',
    'tornado': 'tornado.jpeg',
    'light intensity drizzle': 'malenki_dozhd.jpg',
    'error': 'errorimg.jpeg'
}

#Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

#Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Отправить местоположение", request_location=True)
    keyboard.add(button)
    await message.reply("Привет!🖐 \nЯ бот для определения погоды. Просто отправь мне название города, или нажми кнопку ниже, чтобы отправить свое местоположение.", reply_markup=keyboard)

#Обработчик текстовых сообщений или местоположений
@dp.message_handler(content_types=[types.ContentType.TEXT, types.ContentType.LOCATION])
async def get_weather(message: types.Message):
    chat_id = message['chat']['id']
    #Если получено текстовое сообщение, то выбираем город название города
    if message.content_type == types.ContentType.TEXT:
        city = message.text.capitalize()#Каждое название города с большой буквы

        weather_params = {
            'q': city, #Название города
            'appid': OPENWEATHERMAP_API_KEY,
            'units': 'metric'#Единица измерения
        }
        air_params = {
            'city': city
        }
    else:  # Если пользователь отправил локацию
        latitude = message.location.latitude
        longitude = message.location.longitude

        weather_params = {
            'lat': latitude,
            'lon': longitude,
            'appid': OPENWEATHERMAP_API_KEY,
            'units': 'metric'
        }
        air_params = {
            'lat': latitude,
            'lon': longitude
        }

    response = requests.get(OPENWEATHERMAP_API_URL, params=weather_params)
    weather_data = response.json()
    air_response = requests.get(
        AIR_API_URL, headers={'X-Api-Key': AIR_API_KEY}, params=air_params)
    air_data = air_response.json()
    if response.status_code == 200 and air_response.status_code == requests.codes.ok:
        weather_description = weather_data['weather'][0]['description']#Обработка JSON файла
        temperature = round(weather_data['main']['temp'])#Температура
        humidity = weather_data['main']['humidity']#Влажность
        timezone_offset = weather_data['timezone']#Часовой пояс
        local_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=timezone_offset)
        formatted_local_time = local_time.strftime('%d.%m.%Y %H:%M:%S')
        air_quality_points = air_data["overall_aqi"]
        air_NO2_amount = air_data["NO2"]["concentration"]
        if air_NO2_amount < 5:
            air_NO2_text = str(air_NO2_amount) + ' (Низкое содержание)'
        elif 5 < air_NO2_amount < 10:
            air_NO2_text = str(air_NO2_amount) + ' (Среднее содержание)'
        else:
            air_NO2_text = str(air_quality_points) + ' (Опасное для здоровья)'
        if air_quality_points < 30:
            air_quality_text = str(air_quality_points) + ' (Грязный воздух)'
        elif 30 < air_quality_points < 70:
            air_quality_text = str(air_quality_points) + ' (Воздух средней чистоты)'
        else:
            air_quality_text = str(air_quality_points) + ' (Чистый воздух)'
        #Перевод описания погоды на русский язык
        if weather_description in cloudiness_translation:
            weather_description_ru = cloudiness_translation[weather_description]
        else:
            weather_description_ru = weather_description
        weather_content = f"\nОблачность: {weather_description_ru}\nТемпература: {temperature}°C\nВлажность: {humidity}%\nМестное время: {formatted_local_time}\nСодержание азота в воздухе: {air_NO2_text}\nИндекс качества воздуха: {air_quality_text}"
        if message.content_type == types.ContentType.TEXT:
            weather_message = f"Погода в городе {city}: {weather_content}"
            weather_photo = weather_photos[weather_description]
        else:  # Если пользователь отправил локацию
            weather_message = f"Погода в вашем текущем местоположении: {weather_content}"
            weather_photo = weather_photos[weather_description]
    else:
        if message.content_type == types.ContentType.TEXT:
            weather_message = 'Такого города в реале не существует, только в ваших мыслях...\n＞﹏＜'
            weather_photo = weather_photos['error']
        else:  # Если пользователь отправил локацию
            weather_message = 'Не удалось получить погоду для вашего текущего местоположения.'
            weather_photo = weather_photos['error']

    await message.reply(weather_message)
    await bot.send_photo(chat_id, photo=open(f'Weather_photos/{weather_photo}', 'rb'))
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
