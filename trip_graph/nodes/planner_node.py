import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.runnables import RunnablePassthrough
from modules.llm_gemini import GeminiLLM

gemini = GeminiLLM()

def planner_node():
  def _generate_plan(state):
    destination = state.get("destination")
    start_date = state.get("start_date")
    end_date = state.get("end_date")
    trip_type = state.get("trip_type")
    budget = state.get("budget")
    travellers = state.get("travellers")
    
    prompt = f"""
    You are a travel planner AI. Plan a detailed day-wise itinerary for a {trip_type.lower()} trip 
    to {destination} from {start_date} to {end_date} for {travellers} people 
    with a {budget.lower()} budget. Type of trip to be planned is {trip_type}

    Include morning, lunch, afternoon, and evening activities for each day.
    Suggest realistic tourist spots, restaurants, and local experiences.
    Format JSON response keeping the key value format exact as given:
    Day 1:
      - Morning: ...
      - Lunch: ...
      - Afternoon: ...
      - Evening: ...
    """

    itinerary = gemini.generate(prompt, use_google_search=True)
    return itinerary
  
  return RunnablePassthrough.assign(itinerary=_generate_plan)