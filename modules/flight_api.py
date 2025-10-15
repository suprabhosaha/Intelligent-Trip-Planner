import os
import requests
from .llm_gemini import GeminiLLM
from config import SERPAPI_KEY

class FlightSearch:
    def __init__(self):
        self.gemini = GeminiLLM()
        self.serp_base = "https://serpapi.com/search"

    def get_airport_code_from_gemini(self, city_name: str):
        search_params = {
            "engine": "google",
            "q": f"{city_name} airport IATA code",
            "api_key": SERPAPI_KEY
        }

        serp_resp = requests.get(self.serp_base, params=search_params)
        if serp_resp.status_code != 200:
            raise Exception(f"SerpApi failed to fetch search results for {city_name}")

        serp_data = serp_resp.json()
        snippets = " ".join(
            [r.get("snippet", "") for r in serp_data.get("organic_results", [])]
        )

        prompt = f"""
        You are a travel assistant. Based on the following Google search result snippets, 
        identify the 3-letter IATA airport code for the city "{city_name}".
        If multiple airports exist, choose the main international one.
        Just return the 3-letter code, nothing else.

        Search snippets:
        {snippets}
        """
        iata_code = self.gemini.generate(prompt).strip().upper()
        if len(iata_code) == 3 and iata_code.isalpha():
            return iata_code
        raise ValueError(f"Gemini could not determine IATA code for {city_name}")

    def get_flights(self, origin, destination, date):
        origin_code = self.get_airport_code_from_gemini(origin)
        destination_code = self.get_airport_code_from_gemini(destination)
        
        params = {
            "gl": "in",
            "hl": "en",
            "engine": "google_flights",
            "departure_id": origin_code,
            "arrival_id": destination_code,
            "outbound_date": date,
            "currency": "INR",
            "type": "2",
            "api_key": SERPAPI_KEY
        }
        # print("Fetching Data...")
        response = requests.get(self.serp_base, params=params)
        # print("Response", response)
        # if response.status_code != 200:
        #     raise Exception("Failed to fetch flight data")
        response.raise_for_status() 
        return response.json()
    
    def get_round_trip_flights(self, source, destination, start_date, end_date):
        # print("API calling...")
        onward = self.get_flights(source, destination, start_date)
        return_ = self.get_flights(destination, source, end_date)
        return {"onward": onward, "return": return_}    
