from models import *

from telebot.handler_backends import State, StatesGroup
from telebot import types
from telebot.storage import StateMemoryStorage
from telebot import custom_filters, TeleBot
from geopy.geocoders import Nominatim
from weathear_forecast import WeatherForecast


bot = TeleBot("6616347109:AAHwJyDC34DGkcdR-v2R84tYmEp_BeySDhg")
state_storage = StateMemoryStorage()
create_models()

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

geolocator = Nominatim(user_agent="Tester")


# Отправляем сообщение с кнопками
class UserState(StatesGroup):
    registrate_location = State()
    location_confirmation = State()

class ForecastState(StatesGroup):
    choose_amount_of_days = State()
    write_forecast = State()

def create_new_buttons(*buttons) -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    for button in buttons:
        keyboard.add(types.KeyboardButton(text=button))
    return keyboard



@bot.message_handler(commands=["start"])
def start(message: types.Message):
    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.reply_to(message, "Добро пожаловать в менеджер погоды, для начала давайте зарегистрируем вас. \n"
                              "Введите ваше место проживание, это нужно что бы дать прогноз погоды в вашем городе или поселке:")
        bot.set_state(user_id, UserState.registrate_location)
        return

@bot.message_handler(state=UserState.registrate_location)
def handler_location(message: types.Message):
    adress = message.text
    location = geolocator.geocode(adress)
    keyboard = create_new_buttons("да", "нет")
    bot.reply_to(message, f"эта ваше местоположение - {location}?\nвведите да/нет", reply_markup=keyboard)
    bot.set_state(message.from_user.id, UserState.location_confirmation)

    with bot.retrieve_data(message.from_user.id) as data:
        data["location"] = (location.latitude, location.longitude)



@bot.message_handler(state=UserState.location_confirmation)
def confirmation_location(message: types.Message):
    user_id = message.from_user.id
    if message.text == "да":
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        with bot.retrieve_data(user_id) as data:
            location = data["location"]
        if User.get_or_none(User.user_id == user_id) is not None:
            user = User.get(User.user_id == message.from_user.id)
            user.delete_instance()
        User.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            latitude=location[0],
            longitude=location[1]
        )
        keyboard = create_new_buttons("/forecast", "/re-register")
        bot.reply_to(message, "вы зарегестрированы\n"
                              " чтобы получить прогноз погоды введите /forecast\n"
                              " если вам нужно изменить расположение введите /re-register", reply_markup=keyboard)
        bot.delete_state(message.from_user.id, message.chat.id)
    elif message.text == "нет":
        bot.set_state(user_id, UserState.registrate_location)
        none_keyboard = types.ReplyKeyboardRemove()
        bot.reply_to(message, "попробуйте снова:", reply_markup=none_keyboard)


@bot.message_handler(commands=["forecast"])
def process_new_forecast(message: types.Message):
    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.reply_to(message, "вы не зарегестрированы \n "
                              "введите ваше место положение:")
        bot.set_state(user_id, UserState.registrate_location)
        return
    keyboard = create_new_buttons("1", "2", "5")
    bot.reply_to(message, "введите на сколько дней вы хотите получить прогноз:", reply_markup=keyboard)
    bot.set_state(user_id, ForecastState.choose_amount_of_days)

@bot.message_handler(state=ForecastState.choose_amount_of_days)
def choose_days(message: types.Message):
    user_id = message.from_user.id
    if int(message.text) > 10:
        keyboard = create_new_buttons("/forecast")
        bot.reply_to(message, "мы не можем вам предоставить прогноз на столько дней", reply_markup=keyboard)
        return
    with bot.retrieve_data(user_id) as data:
        data["amount_days"] = int(message.text)
    bot.set_state(user_id, ForecastState.write_forecast)
    write_forecast(message)

@bot.message_handler(commands=["re-register"])
def re_register(message: types.Message):
    none_keyboard = types.ReplyKeyboardRemove()
    bot.reply_to(message, "введите ваш город и страну:", reply_markup=none_keyboard)
    bot.set_state(message.from_user.id, UserState.registrate_location)
def write_forecast(message: types.Message):
    user_id = message.from_user.id
    with bot.retrieve_data(user_id) as data:
        user = User.get(User.user_id == user_id)
        forecast = WeatherForecast(user.latitude, user.longitude, data["amount_days"])
        for day in forecast.forecast_days_generator():
            bot.reply_to(message, day)
    keyboard = create_new_buttons("/forecast", "/re-register")
    bot.reply_to(message, "хотите еще раз запросить прогноз?\nнажмите на кнопку forecast", reply_markup=keyboard)





bot.infinity_polling(skip_pending=True)
if __name__ == '__main__':
    bot.infinity_polling()