from .connections import OPEN_WEATHER_API_KEY
import requests


def check_good_weather(city):
    """
    See if its going to rain in the city or not
    :param city: Location of the query
    :return: 0 if city not found 1 if sunny 2 if rains
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + OPEN_WEATHER_API_KEY + "&q=" + city
    response = requests.get(complete_url).json()
    if response["cod"] == "404":
        return 0
    weather = response["weather"][0]["id"]
    if weather//100 == 8 or (700 < weather < 762):
        return 1
    return 2