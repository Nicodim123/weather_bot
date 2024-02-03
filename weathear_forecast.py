import requests
from datetime import datetime, date
from pprint import pprint
import json



class WeatherForecast:
    def __init__(self, latitude: float, longitude: float, forecast_days: int, params=None):
        if params is None:
            self.params = ["temperature_2m", "cloud_cover", "wind_gusts_10m", "rain", "snowfall"]
        self.latitude = latitude
        self.longitude = longitude
        self.forecast_days = forecast_days
        self.days = dict()
        self.__url = "https://api.open-meteo.com/v1/forecast"
        self.create_date_time()

    def __get_hourly_parameter(self, parameter: str) -> str:
        if parameter == "time":
            response = requests.get(self.__url, params={
                "latitude": self.latitude,
                "longitude": self.longitude,
                "hourly": "temperature_2m",
                "forecast_days": self.forecast_days,
                "timezone": "auto",
            })
        else:
            response = requests.get(self.__url, params={
                "latitude": self.latitude,
                "longitude": self.longitude,
                "hourly": parameter,
                "forecast_days": self.forecast_days,
                "timezone": "auto",
            })
        response = response.json()
        results = response["hourly"][parameter]
        for i in results:
            yield i

    def create_date_time(self):
        for time in self.__get_hourly_parameter("time"):
            dt = datetime.strptime(time, "%Y-%m-%dT%H:%M")
            if dt.hour == 0:
                self.days[str(dt.date())] = dict()
            self.days[str(dt.date())][dt.hour] = None

    def forecast_any_days(self):
        generators = [self.__get_hourly_parameter(parameter) for parameter in self.params]
        emoji_manager = EmojiManager()

        for data, hours in self.days.items():
            for hour in hours.keys():
                result_forecast_hour = ""
                for i in range(len(self.params)):
                    result_forecast_hour += f"{emoji_manager.get_emoji(self.params[i], next(generators[i]))}"
                self.days[data][hour] = result_forecast_hour
        print(self.days)

    def forecast_days_generator(self) -> str:
        result = ""
        self.forecast_any_days()
        for date, hours in self.days.items():
            result += "--------------------- \n"
            result += f"{date} \n"
            result += "--------------------- \n"
            for hour, forecast in hours.items():
                result += f"{hour}:00 |{forecast} \n\n"
            yield result
            result = ""



class EmojiManager:
    def __init__(self):
        self.parameters = {"temperature_2m": self.temperature_emoji,
                           "rain": self.rain_emoji,
                           "cloud_cover": self.clouds_emoji,
                           "wind_gusts_10m": self.wind_emoji,
                           "snowfall": self.snow_emoji}

    def get_emoji(self, parameter: str, data):
        if parameter in self.parameters:
            return self.parameters[parameter](data)
    def clouds_emoji(self, cloud_cover: int) -> str:
        if cloud_cover in range(0, 25):
            return "☀|"
        elif cloud_cover in range(25, 50):
             return "🌤|"
        elif cloud_cover in range(50, 75):
            return "🌥|"
        elif cloud_cover in range(75, 101):
            return "☁|"
        else:
            return ""

    def rain_emoji(self, rain_mm: float) -> str:
        if rain_mm > 0:
            return f"{rain_mm}mm🌧|"
        else:
            return ""

    def wind_emoji(self, wind_speed_m_s: float) -> str:
        wind_speed_m_s *= 5/18
        wind_speed_m_s = round(wind_speed_m_s, 1)
        if wind_speed_m_s > 0:
            return f"{wind_speed_m_s}m/s💨|"
        else:
            return ""

    def snow_emoji(self, snow_cm: float) -> str:
        if snow_cm > 0:
            return f"{snow_cm}cm☃️|"
        else:
            return ""

    def temperature_emoji(self, temperature: float):
        if temperature <= 0:
            return f"{temperature}°C❄️|"
        elif 0 < temperature < 20:
            return f"{temperature}°C😶‍🌫️|"
        elif 20 <= temperature <= 30:
            return f"{temperature}°C☀️|"
        elif temperature > 30:
            return f"{temperature}°C🔥|"

class DayForecast:
    def __init__(self, data: date, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.data = data
        self.__url = "https://api.open-meteo.com/v1/forecast"




h = date(2024, 12, 1)
forecast = WeatherForecast(47.7, 27.9, 3)
forecast.forecast_any_days()

