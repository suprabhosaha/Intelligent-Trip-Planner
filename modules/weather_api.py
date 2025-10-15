import requests
from datetime import datetime, timedelta
from config import OPENWEATHER_API_KEY

class WeatherClient:
    def __init__(self, api_key: str = OPENWEATHER_API_KEY):
        self.api_key = api_key
        self.session = requests.Session()
        self.BASE_URL = "https://api.openweathermap.org/data/2.5/forecast/daily"

    def get_daily_forecast(self, city: str, start_date: str, days: int = 5):
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            today = datetime.today()
            delta_days = (start - today).days + days + 1
            # print("delta", delta_days)
            cnt = min(max(delta_days, days), 16)
            # print(cnt)
            
            params = {
                "q": city,
                "units": "metric",
                "cnt": cnt + 1,
                "appid": self.api_key
            }

            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            # url = f"{self.base_url}/forecast/daily?q={city}&units=metric&cnt={cnt}&appid={self.api_key}"
            # res = requests.get(url)
            # if res.status_code != 200:
            #     raise Exception(f"Weather fetch failed: {res.text}")

            data = response.json()
            forecast = []
            for d in data.get("list", []):
                date = datetime.utcfromtimestamp(d["dt"])
                if start <= date < start + timedelta(days=days):
                    forecast.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "temp": d["temp"]["day"],
                        "weather": d["weather"][0]["description"].capitalize(),
                        "humidity": d["humidity"],
                        "wind_speed": d["speed"]
                    })
            return {
                "city": data.get("city", {}).get("name", city),
                "country": data.get("city", {}).get("country", ""),
                "forecast": forecast
            }

        except Exception as e:
            raise Exception(f"Error fetching forecast: {e}")
