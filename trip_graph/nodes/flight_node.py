from langchain_core.runnables import RunnablePassthrough
from modules.flight_api import FlightSearch

flight_searcher = FlightSearch()

def flight_node():
    def _search_flights(inputs):
        source = inputs.get("source", "Delhi")
        destination = inputs.get("destination")
        start_date = inputs.get("start_date")
        end_date = inputs.get("end_date")
        # print("Flight Runnable")
        flights = flight_searcher.get_round_trip_flights(source, destination, start_date, end_date)
        return flights
    return RunnablePassthrough.assign(flights=_search_flights)