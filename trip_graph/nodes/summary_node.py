import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.runnables import RunnablePassthrough
from modules.llm_gemini import GeminiLLM

gemini = GeminiLLM()

def summary_node():
    def _create_summary(state):
        destination = state.get("destination")
        itinerary = state.get("itinerary")
        flights = state.get("flights")
        hotels = state.get("hotels")
        weather = state.get("weather")
        travellers = state.get("travellers")
        budget = state.get("budget")
        
        prompt = f"""
        Create a short summary for a trip to {destination} for {travellers} people having {budget} budget.

        Here are the details:
        - Itinerary: {itinerary}
        - Flights: {flights}
        - Hotels: {hotels}
        - Weather: {weather}

        Summarize key highlights, best activities, and overall travel plan.
        Format for the output should be JSON response keeping the key value format exact as given:
        - weather_tips: According give tips such as carry sunscreen, umbrella, drink coconut water or something relevant. Generate in list format
        - flight: Summary to choose the best flight for the round trip keeping budget in mind. 2-3 lines of summary/recommendation from {flights}
        - accomodation: Recommendation of hotel based on data given. 2-3 lines of summary/recommendation from {hotels}
        - activities: List format of activities for example, [bungee jumping at XYZ, camel riding at XYZ, ....]
        - dining: List format of dishes to try out special at {destination}, for example format, [Salmon fish, Rasgulla, ...]
        """
        return gemini.generate(prompt)
    
    return RunnablePassthrough.assign(summary=_create_summary)