import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.runnables import RunnablePassthrough
from modules.weather_api import WeatherClient

weather_client = WeatherClient()

def weather_node():
    def _fetch(inputs):
        forecast = weather_client.get_daily_forecast(inputs.get("destination"), inputs.get("start_date"), inputs.get("num_days"))
        # print("Forecast from weather_node.py", forecast)
        # return {"weather_data": forecast}
        # forecast = {'city': 'Jaipur', 'country': 'IN', 'forecast': [{'date': '2025-10-10', 'temp': 27.29, 'weather': 'Sky is clear', 'humidity': 35, 'wind_speed': 3.31}, {'date': '2025-10-11', 'temp': 28.38, 'weather': 'Sky is clear', 'humidity': 30, 'wind_speed': 5.68}, {'date': '2025-10-12', 'temp': 28.84, 'weather': 'Sky is clear', 'humidity': 30, 'wind_speed': 4.21}]}
        return forecast
    return RunnablePassthrough.assign(weather_data=_fetch)
