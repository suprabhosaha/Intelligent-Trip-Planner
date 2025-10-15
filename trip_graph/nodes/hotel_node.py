import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_core.runnables import RunnablePassthrough
from modules.hotel_api import HotelSearch

hotel_searcher = HotelSearch()

def hotel_node():
    def _fetch(inputs):
        q = inputs.get("destination")
        check_in_date = inputs.get("start_date")
        check_out_date = inputs.get("end_date")
        num_travellers = inputs.get("num_travellers")
        budget = inputs.get("budget")
        hotel_results = hotel_searcher.search_hotels(q, check_in_date, check_out_date, num_travellers, budget)
        return hotel_results
    return RunnablePassthrough.assign(hotels=_fetch)
