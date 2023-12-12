import requests
import configparser


class WeatherData():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.api_key = self.config['WEATHER']['api']
        self.city = self.config['WEATHER']['city']
        self.url = f'http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}'
        self.address = ''
        self.temperature = ''
        self.k_temp = 0
        self.desc = ''

    def getWeatherData(self):
        self.response = requests.get(self.url)

        if self.response.status_code == 200:
            self.data = self.response.json()
            self.main_temp_kelvin = int(self.data['main']['temp'])
            self.temperature = ((int(self.data['main']['temp'])-273.15)*9//5+32)
            self.feels_temp = ((int(self.data['main']['feels_like'])-273.15)*9//5+32)
            self.min_temp = ((int(self.data['main']['temp_min'])-273.15)*9//5+32)
            self.max_temp = ((int(self.data['main']['temp_max'])-273.15)*9//5+32)
            self.humidity = int(self.data['main']['humidity'])
            self.desc = self.data['weather'][0]['description']

            return self.temperature

        else:
            print('Error fetching weather data')





