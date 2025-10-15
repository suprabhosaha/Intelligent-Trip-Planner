from modules.llm_gemini import GeminiLLM
from langchain_core.runnables import RunnablePassthrough

def alternate_suggestion_node():
    gemini = GeminiLLM()

    def _generate_alternatives(state):
        weather_data = state.get("weather_data")
        destination = state.get("destination")
        start_date = state.get("start_date")
        num_days = state.get("num_days")
        trip_type = state.get("trip_type")
        budget = state.get("budget")
        
        prompt = f"""
        The weather forecast for {destination} from {start_date} for {num_days} days is unfavorable 
        (details: {weather_data}).

        Suggest 3 alternate Indian destinations with airports that would be better suited for a {trip_type.lower()} trip 
        around the same time. Consider similar budget range ({budget}) and traveler comfort.
        
        For each alternate destination, provide:
        - The destination name
        - A short reason why it’s a good alternative (e.g., weather, attractions, vibe)
        
        **Output Format:**
        You must respond ONLY with a single, valid JSON in the below-mentioned format. Do not include any introductory text, explanations, or markdown formatting outside of the JSON structure.

        {{
        "alternate_suggestions": [
            {{
            "place": "Name of Destination 1",
            "reason": "A short, compelling reason why this is a good alternative, highlighting its great weather and suitability for the trip type."
            }},
            {{
            "place": "Name of Destination 2",
            "reason": "A short, compelling reason why this is a good alternative, highlighting its great weather and suitability for the trip type."
            }},
            {{
            "place": "Name of Destination 3",
            "reason": "A short, compelling reason why this is a good alternative, highlighting its great weather and suitability for the trip type."
            }}
        ]
        }}
        """

        response = gemini.generate(prompt, use_google_search=True)
        # print(response)
        return response.strip()

    return RunnablePassthrough.assign(alternate_suggestions=_generate_alternatives)
