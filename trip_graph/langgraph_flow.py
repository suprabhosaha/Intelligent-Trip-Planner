# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# from datetime import datetime, timedelta
# from langsmith import traceable

# from trip_graph.nodes.flight_node import flight_node
# from trip_graph.nodes.hotel_node import hotel_node
# from trip_graph.nodes.weather_node import weather_node
# from trip_graph.nodes.weather_decision_node import weather_decision_node
# from trip_graph.nodes.summary_node import summary_node
# from trip_graph.nodes.planner_node import planner_node
# from trip_graph.nodes.alternate_suggestion_node import alternate_suggestion_node


# @traceable(name="Trip Creation Graph", tags=["trip-planner", "langgraph"])
# def create_trip_graph(source, destination, start_date, num_days, trip_type, budget, travellers):
#     start_dt = datetime.strptime(start_date, '%Y-%m-%d')
#     delta = timedelta(days=(num_days-1))
#     end_dt = start_dt + delta
#     end_date = end_dt.strftime('%Y-%m-%d')
    
#     weather_step = weather_node()
#     weather_params = {
#         "destination": destination,
#         "start_date": start_date,
#         "num_days": num_days
#     }
#     weather = weather_step.invoke(weather_params)
    
#     weather_decision_runnable = weather_decision_node()
#     weather_decision = weather_decision_runnable.invoke(weather)
#     # print("Weather Decision", weather_decision)
#     # print("Reason", weather_decision.get('func', {}).get('reason',{}))
        
#     if weather_decision.get('func', {}).get('decision') in ["unfavourable", "unfavorable"]:
#         alt_sugg_runnable = alternate_suggestion_node()
#         alt_params = {
#             "weather_data": weather_decision["weather_data"],
#             "destination": destination,
#             "start_date": start_date,
#             "num_days": num_days,
#             "trip_type": trip_type,
#             "budget": budget
#         }
#         suggestions = alt_sugg_runnable.invoke(alt_params)
        
#         return {
#             "status": "unfavorable",
#             "message": f"❌ Weather not suitable for {destination}: {weather_decision['func']['reason']}",
#             "weather_forecast": weather_decision["weather_data"],
#             "suggestions": suggestions.get('func', "No alternate destinations found.")
#         }

#     planner_runnable = planner_node()
#     itinerary_params = {
#         "destination": destination,
#         "start_date": start_date,
#         "end_date": end_date,
#         "trip_type": trip_type,
#         "budget": budget,
#         "travellers": travellers,
#     }
#     itinerary = planner_runnable.invoke(itinerary_params)

#     flight_params = {
#         "destination": destination,
#         "source": source,
#         "depart_date": start_date,
#         "return_date": end_date
#     }
#     flight_runnable = flight_node()
#     flights = flight_runnable.invoke(flight_params)

#     hotel_runnable = hotel_node()
#     hotel_params = {
#         "destination": destination,
#         "check_in_date": start_date,
#         "check_out_date": end_date,
#         "num_travellers": travellers,
#         "budget": budget
#     }
#     hotels = hotel_runnable.invoke(hotel_params)

#     summary_runnable = summary_node()
#     summary_params = {
#         "destination": destination,
#         "itinerary": itinerary,
#         "flights": flights,
#         "hotels": hotels,
#         "weather": weather,
#         "travellers": travellers,
#     }
#     summary = summary_runnable.invoke(summary_params)

#     return {
#         "status": "favorable",
#         "destination": destination,
#         "duration": f"{start_date} → {end_date}",
#         "travellers": travellers,
#         "trip_type": trip_type,
#         "budget": budget,
#         "weather_forecast": weather,
#         "itinerary": itinerary,
#         "flights": flights,
#         "hotels": hotels,
#         "summary": summary
#     }


# langgraph/langgraph_flow.py
import sys, os
from datetime import datetime, timedelta
from typing import TypedDict, List, Optional

# LangGraph imports
from langgraph.graph import StateGraph, END
from langsmith import traceable

# Make sure project modules are accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Import your node factory functions
from trip_graph.nodes.weather_node import weather_node
from trip_graph.nodes.weather_decision_node import weather_decision_node
from trip_graph.nodes.planner_node import planner_node
from trip_graph.nodes.flight_node import flight_node
from trip_graph.nodes.hotel_node import hotel_node
from trip_graph.nodes.summary_node import summary_node
from trip_graph.nodes.alternate_suggestion_node import alternate_suggestion_node

# --- 1. Define the State for the Graph ---
# This dictionary will be passed between all of your nodes.
class TripState(TypedDict):
    source: str
    destination: str
    start_date: str
    end_date: str
    num_days: int
    trip_type: str
    budget: str
    travellers: int
    weather_data: Optional[dict]
    decision: Optional[str]
    itinerary: Optional[dict]
    flights: Optional[dict]
    hotels: Optional[dict]
    summary: Optional[str]
    alternate_suggestions: Optional[list]

# --- 2. Build the Graph ---

# Create the graph object
workflow = StateGraph(TripState)

# Add all the nodes to the graph. The first argument is a unique name for the node.
# The second argument is the runnable object created by your factory function.
workflow.add_node("weather", weather_node())
workflow.add_node("weather_decision", weather_decision_node())
workflow.add_node("planner", planner_node())
workflow.add_node("flight", flight_node())
workflow.add_node("hotel", hotel_node())
workflow.add_node("summary", summary_node())
workflow.add_node("alternate_suggestions", alternate_suggestion_node())

# --- 3. Define the Edges (the Flow of Logic) ---

# Set the entry point of the graph
workflow.set_entry_point("weather")

# Simple edges connect one node directly to the next
workflow.add_edge("weather", "weather_decision")
workflow.add_edge("planner", "flight")
workflow.add_edge("flight", "hotel")
workflow.add_edge("hotel", "summary")
workflow.add_edge("summary", END) # The summary node is a final step
workflow.add_edge("alternate_suggestions", END) # The alternate suggestions node is also a final step

# Conditional edges decide the next step based on the current state
def decide_on_weather(state: TripState) -> str:
    """Determines the next step based on the weather decision."""
    print("---Conditional Branch: Evaluating Weather---")
    if state.get('decision').get('decision') in ["unfavorable", "unfavourable"]:
        print("---Decision: Unfavorable weather. Suggesting alternatives.---")
        return "alternate_suggestions"
    else:
        print("---Decision: Favorable weather. Proceeding with planning.---")
        return "planner"

workflow.add_conditional_edges(
    "weather_decision", # The node that produces the output for the decision
    decide_on_weather,  # The function that makes the decision
    {
        "alternate_suggestions": "alternate_suggestions",
        "planner": "planner"
    }
)

# --- 4. Compile the Graph into a Runnable App ---
app = workflow.compile()

# --- 5. Create the Main Function to Invoke the Graph ---
@traceable(name="Trip Creation Graph", tags=["trip-planner", "langgraph"])
def create_trip_graph(source, destination, start_date, num_days, trip_type, budget, travellers):
    """Prepares inputs and invokes the compiled LangGraph app."""
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    delta = timedelta(days=(num_days - 1))
    end_dt = start_dt + delta
    end_date = end_dt.strftime('%Y-%m-%d')
    
    # Initial input state for the graph
    initial_state = {
        "source": source,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "num_days": num_days,
        "trip_type": trip_type,
        "budget": budget,
        "travellers": travellers
    }

    # Invoke the graph with the initial state
    final_state = app.invoke(initial_state)
    
    # Determine the final status based on the graph's path
    weather_decision_result = final_state.get("decision", {})
    if weather_decision_result.get("decision") in ["unfavorable", "unfavourable"]:
        final_state["status"] = "unfavorable"
    else:
        final_state["status"] = "favorable"
        
    return final_state