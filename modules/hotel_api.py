import requests
from datetime import datetime, timedelta
from config import SERPAPI_KEY

class HotelSearch:
    BASE_URL = "https://serpapi.com/search"

    def __init__(self):
        self.api_key = SERPAPI_KEY

    def search_hotels(
        self,
        query: str,
        check_in: str,
        check_out: str,
        adults:str,
        budget: str,
        num_hotels: int = 5,
    ):
        """
        Search for hotels in a city (query) between check_in and check_out dates.
        Returns top N hotel entries with relevant data.
        """
        match budget:
            case "Low":
                hotel_class = 2
            case "Medium":
                hotel_class = 3
            case "High":
                hotel_class = 4
            case "Luxury":
                hotel_class = 5
                
        params = {
            "hl": "en",
            "engine": "google_hotels",
            "q": query,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": adults,
            "hotel_class": hotel_class,
            "currency": "INR",
            "api_key": self.api_key,
        }
        res = requests.get(self.BASE_URL, params=params)
        if res.status_code != 200:
            raise Exception(f"Hotel search failed: {res.text}")
        data = res.json()
        hotels = data.get("properties")
        # Return top num_hotels
        return hotels[:num_hotels]
