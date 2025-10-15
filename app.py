import streamlit as st
import re
import json
import math
from datetime import date
from trip_graph.langgraph_flow import create_trip_graph
from langsmith.run_helpers import traceable


@traceable(name="Trip Planner Streamlit Run", tags=["frontend", "streamlit"])
def generate_trip(
    source, destination, start_date, num_days, trip_type, budget, travellers
):
    return create_trip_graph(
        source, destination, start_date, num_days, trip_type, budget, travellers
    )

def add_space(num_spaces=1):
    """Adds vertical space to the app."""
    for _ in range(num_spaces):
        st.markdown("<br>", unsafe_allow_html=True)

def display_flight_card(flights):
    for idx, flight in enumerate(flights):
        print(flight)
        with st.container(border=True):

            total_duration = flight.get("total_duration", "duration")
            price = flight.get("price", "N/A")
            airline_logo = flight.get("airline_logo")
            carbon_info = flight.get("carbon_emissions", {})
            this_flight = carbon_info.get("this_flight")
            typical = carbon_info.get("typical_for_this_route")
            diff = carbon_info.get("difference_percent", 0)
            layovers = flight.get("layovers", [])
            flight_legs = flight.get("flights", [])


            # --- Each Flight Leg ---
            for i, leg in enumerate(flight_legs):
                dep = leg.get("departure_airport", {})
                arr = leg.get("arrival_airport", {})
                airline = leg.get("airline", "N/A")
                travel_class = leg.get("travel_class", "N/A")
                flight_number = leg.get("flight_number", "N/A")
                airplane = leg.get("airplane", "N/A")
                duration = leg.get("duration", "N/A")
                legroom = leg.get("legroom", "")
                logo = leg.get("airline_logo", airline_logo)

                cols = st.columns([1.5, 3, 2])
                with cols[0]:
                    if logo:
                        st.image(logo, width=60)
                    st.markdown(f"**{airline}**  \n{travel_class}")
                with cols[1]:
                    st.markdown(
                        f"🕓 **{dep.get('time', '')}** — {arr.get('time', '')}  \n"
                        f"📍 **{dep.get('id', '')} → {arr.get('id', '')}**"
                    )
                with cols[2]:
                    st.markdown(
                        f"⏱️ {duration} min  \n"
                        f"✈️ {airplane} ({flight_number})"
                    )
                    if legroom:
                        st.caption(legroom)

                # --- Layover After Each Leg (if applicable) ---
                if i < len(layovers):
                    lay = layovers[i]
                    lay_text = f"🕒 Layover: {lay['duration']} min at {lay['name']} ({lay['id']})"
                    if lay.get("overnight"):
                        lay_text += " 🌙 (Overnight)"
                    st.info(lay_text)


def display_flight_options(flights):
    """
    Displays a list of flight options, correctly rendering multi-leg
    journeys and layovers with a continuous timeline.
    """
    if not flights:
        st.warning("No flight data is available to display.")
        return

    # --- CSS with minor additions for leg separation ---
    st.markdown("""
    <style>
    .flight-card-container {
        border: 1px solid #444; border-radius: 12px; margin-bottom: 20px;
        background-color: #2F2F2F; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .flight-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 15px 20px; border-bottom: 1px solid #444;
    }
    .airline-logo-bg {
        background-color: #FFFFFF;
        border-radius: 6px;
        padding: 3px;
    }
    .header-left { display: flex; align-items: center; gap: 15px; }
    .header-left span { font-weight: 500; font-size: 1.1em; }
    .flight-price { font-size: 1.2em; font-weight: 600; color: #E0E0E0; }
    .flight-body { padding: 20px; display: flex; gap: 20px; }
    .timeline-container { display: flex; flex-direction: column; align-items: center; }
    .timeline-dot { min-width: 12px; min-height: 12px; border: 2px solid #888; border-radius: 50%; background-color: #2F2F2F; }
    .timeline-line { width: 2px; flex-grow: 1; min-height: 80px; border-left: 2px dotted #888; }
    .timeline-layover-space { min-height: 70px; } /* Space for layover text */
    .flight-details { flex-grow: 1; }
    .leg-block { margin-bottom: 15px; } /* Added to space out legs */
    .airport-info { margin-bottom: 5px; }
    .airport-info .time { font-weight: 600; font-size: 1.1em; margin-right: 10px; }
    .travel-time-info { font-size: 0.9em; color: #aaa; padding-left: 30px; margin: 5px 0 10px 0; }
    .layover-details {
        font-size: 0.9em; color: #FFD700; text-align: center;
        padding: 10px; margin: 10px 0; border-radius: 8px;
        background-color: rgba(70, 70, 70, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

    for flight in flights:
        price = flight.get("price")
        flight_legs = flight.get("flights", [])
        layovers = flight.get("layovers", [])
        if not flight_legs:
            continue

        main_logo = flight_legs[0].get("airline_logo", "")

        # --- FIX: Build Timeline and Details HTML separately ---
        timeline_html = ""
        details_html = ""

        for i, leg in enumerate(flight_legs):
            dep = leg.get("departure_airport", {})
            arr = leg.get("arrival_airport", {})
            duration_min = leg.get("duration", 0)
            travel_time = f"{math.floor(duration_min / 60)} hr {duration_min % 60} min"
            
            # 1. Build the timeline part for this leg
            timeline_html += '<div class="timeline-dot"></div><div class="timeline-line"></div>'
            
            # 2. Build the details part for this leg
            details_html += f"""
                <div class="leg-block">
                    <div class="airport-info"><span class="time">{dep.get('time', '')}</span><span>{dep.get('name', '')} ({dep.get('id', '')})</span></div>
                    <div class="travel-time-info">Travel time: {travel_time}</div>
                    <div class="airport-info"><span class="time">{arr.get('time', '')}</span><span>{arr.get('name', '')} ({arr.get('id', '')})</span></div>
                </div>
            """

            # 3. Add layover info to both timeline and details if it exists
            if i < len(layovers):
                lay = layovers[i]
                lay_duration_min = lay.get('duration', 0)
                layover_time = f"{math.floor(lay_duration_min / 60)} hr {lay_duration_min % 60} min"
                layover_text = f"🕒 {layover_time} layover in {lay.get('name', '')}"
                
                timeline_html += '<div class="timeline-layover-space"></div>'
                details_html += f'<div class="layover-details">{layover_text}</div>'
        
        # Add the final dot at the end of the timeline
        timeline_html += '<div class="timeline-dot"></div>'
        
        # --- Assemble and Render the Final Card ---
        st.markdown(f"""
        <div class="flight-card-container">
            <div class="flight-header">
                <div class="header-left"><img src="{main_logo}" width="30" class="airline-logo-bg"><span>Departure</span></div>
                <div>{leg.get("airline", "N/A")} · {leg.get("travel_class", "N/A")} · {leg.get("airplane", "N/A")} · {leg.get("flight_number", "N/A")}</div>
                <div class="flight-price">₹{price if price else 'N/A'}</div>
            </div>
            <div class="flight-body">
                <div class="timeline-container">{timeline_html}</div>
                <div class="flight-details">{details_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_hotel_card(hotel):
    """Displays a single hotel in a styled card."""
    name = hotel.get("name", "Unnamed Hotel")
    images = hotel.get("images", [])
    hotel_img = images[0].get("thumbnail") if images else "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
    total_rate = hotel.get("total_rate", {}).get("lowest", "N/A")
    rating = hotel.get("overall_rating", "N/A")
    link = hotel.get("link", "#")
    amenities = ''.join([f'<span style="border:1px solid #ddd; border-radius:8px; padding:3px 8px; font-size:0.8rem;">{a}</span>' for a in hotel.get("amenities", [])[:5]])
    
    st.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none; color: inherit;">
        <div style="display: flex; border: 1px solid #444; border-radius: 12px; padding: 15px; margin-bottom: 20px; gap: 20px;">
            <div style="flex: 1;"><img src="{hotel_img}" style="width:100%; border-radius: 10px; object-fit: cover; height: 180px;"></div>
            <div style="flex: 2;">
                <h4 style="margin-top:0; margin-bottom:10px;">{name}</h4>
                <p style="margin:5px 0;"><b>⭐ {rating}</b> | <b>{total_rate}</b></p>
                <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:10px;">{amenities}</div>
            </div>
        </div>
        </a>
    """, unsafe_allow_html=True)

def parse_llm_json_response(response_text):
    """Extracts and parses a JSON object from a string."""
    if isinstance(response_text, (dict, list)):
        return response_text
    
    # If it's not a string, we can't parse it
    if not isinstance(response_text, str):
        print(f"Warning: Cannot parse data of type {type(response_text)}")
        return None
    
    match = re.search(r"\{[\s\S]*\}", response_text)
    if match:
        # print(match)
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            # st.error("Failed to parse JSON from the model's response.")
            # return {}
            return None
    # st.error("No JSON object found in the model's response.")
    # return {}
    return None

def display_itinerary(itinerary_data):    
    card_style = """
    <style>
    .itinerary-card { background-color: #2F2F2F; border-radius: 18px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); padding: 10px; margin-bottom: 25px; }
    .itinerary-header { display: flex; justify-content: space-between; align-items: center; }
    .day-part-title { font-weight: bold; margin-bottom: 5px; }
    .day-part-content { font-size: 0.95rem; color: #E0E0E0; }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)

    icons = {"Morning": "🌅", "Lunch": "🍽️", "Afternoon": "🌇", "Evening": "🌃"}

    for day_key, day_content in itinerary_data.items():
        day_number = day_key.replace("day", "")
        day_number = day_number.replace("Day", "")
        st.markdown(f'<div class="itinerary-card"><div class="itinerary-header"><h3>🗓️ Day {day_number}</h3></div></div>', unsafe_allow_html=True)
        
        with st.expander("View Daily Plan", expanded=True):
            cols = st.columns(4)
            day_parts = ['Morning', 'Lunch', 'Afternoon', 'Evening']
            for i, part in enumerate(day_parts):
                with cols[i]:
                    st.markdown(f'<p class="day-part-title">{icons[part]} {part.capitalize()}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="day-part-content">{day_content.get(part, "No plan available.")}</p>', unsafe_allow_html=True)
        add_space()

def display_trip_summary(summary_data):
    st.markdown("## 🧳 Trip Summary Overview")
    st.markdown("---")

    # 🌤 Weather Tips Section
    with st.expander("🌤 Weather & Travel Tips", expanded=True):
        weather_tips = summary_data.get("weather_tips", [])
        if weather_tips:
            st.markdown("### ☀️ Weather Insights")
            for tip in weather_tips:
                st.markdown(f"- {tip}")
        else:
            st.info("No weather information available.")

    # ✈️ Flights Section
    with st.expander("✈️ Flight Recommendations", expanded=True):
        flight_text = summary_data.get("flight", "No flight info available.")
        st.markdown(f"🛫 **{flight_text}**")

    # 🏨 Accommodation Section
    with st.expander("🏨 Accommodation Suggestions", expanded=True):
        accomodation = summary_data.get("accomodation", "No accommodation info available.")
        st.markdown(f"🏡 {accomodation}")

    # 🎯 Activities Section
    with st.expander("🎯 Top Activities & Attractions", expanded=True):
        activities = summary_data.get("activities", [])
        if activities:
            st.markdown("### 🗺️ Must-Visit Places & Experiences:")
            for activity in activities:
                st.markdown(f"- {activity}")
        else:
            st.info("No activity data available.")

    # 🍽 Dining Section
    with st.expander("🍽 Recommended Dining", expanded=True):
        dining = summary_data.get("dining", [])
        if dining:
            st.markdown("### 🍛 Popular Food & Dining Spots:")
            for dish in dining:
                st.markdown(f"- {dish}")
        else:
            st.info("No dining recommendations found.")

    # ✨ Footer Separator
    st.markdown("---")
    st.success("✅ Trip summary loaded successfully — review the details above!")




st.set_page_config(page_title="Intelligent Trip Planner", layout="wide")

st.title("🧭 Intelligent Trip Planner")
st.write(
    "Plan your perfect trip with AI — personalized itinerary, flights, hotels, and weather forecast."
)

with st.form("trip_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        source = st.text_input("✈️ From (City or Airport)")
        destination = st.text_input("🗺️ To (City or Airport)")

    with col2:
        start_date = st.date_input("📅 Start Date")
        # end_date = st.date_input("📆 End Date")
        travellers = st.number_input(
            "👨‍👩‍👧 Number of Travellers", min_value=1, max_value=15, step=1, value=2
        )

    with col3:
        num_days = st.number_input(
            "🌞 Number of Days", min_value=1, max_value=15, value=3
        )

    st.markdown("---")

    col4, col5 = st.columns(2)

    with col4:
        budget = st.selectbox(
            "💰 Budget Range", options=["Low", "Medium", "High", "Luxury"], index=1
        )

    with col5:
        trip_type = st.selectbox(
            "🏕️ Trip Type",
            options=[
                "Family",
                "Adventure",
                "Romantic",
                "Cultural",
                "Relaxation",
                "Fun",
            ],
            index=0,
        )

    submitted = st.form_submit_button("🚀 Plan My Trip")

if submitted or st.session_state.get("rerun_with_alternate"):
    st.session_state["rerun_with_alternate"] = False
    
    try:
        with st.spinner("Generating your personalized trip plan..."):
            result = generate_trip(
                source=st.session_state.get("source", source),
                destination=st.session_state.get("destination", destination),
                start_date=start_date.strftime("%Y-%m-%d"),
                num_days=num_days,
                trip_type=trip_type,
                budget=budget,
                travellers=travellers
            )

        st.session_state["trip_result"] = result
    
    except Exception as e:
        st.error("An error occurred while planning your trip. Please check your inputs and try again.")



# If result exists
if "trip_result" in st.session_state:
    result = st.session_state["trip_result"]
    # print(result)
    if result.get("status") == "unfavorable":
        st.error(
            "⚠️ Weather conditions are unfavorable for your selected dates at the destination."
        )
        st.write(f"### 🌦 Weather Forecast:")
        # print(result['weather_forecast'])
        for day in result["weather_data"]["forecast"]:
            cols = st.columns([1, 1, 1, 1, 1, 1])
            with cols[1]:
                st.write(f"📅 {day.get('date')}")
            with cols[2]:
                st.write(f"{day.get('weather')}")
            with cols[3]:
                st.write(f"🌡️ {day.get('temp')}°C")
            with cols[4]:
                st.write(f"💧 {day.get('humidity')}%")
            with cols[5]:
                st.write(f"💨 {day.get('wind_speed')} m/s")
                
        st.markdown("---")
        st.subheader("🧭 Alternate Destinations Suggested")
        
        suggestions_output = result.get("alternate_suggestions")
        parsed_suggestions = parse_llm_json_response(suggestions_output)

        # Determine the actual list of suggestions, whether it's a dict or a list
        suggestions_list = []
        if isinstance(parsed_suggestions, dict):
            suggestions_list = parsed_suggestions.get('alternate_suggestions', [])
        elif isinstance(parsed_suggestions, list):
            suggestions_list = parsed_suggestions

        if suggestions_list:
            for item in suggestions_list:
                # --- THIS IS THE FIX ---
                # Check if the item in the list is a dictionary or just a string
                if isinstance(item, dict):
                    place = item.get('place', 'N/A')
                    reason = item.get('reason', '')
                    cols = st.columns([1, 2, 1])
                    with cols[0]:
                        st.markdown(f"**🏖 {place}**")
                    with cols[1]:
                        st.markdown(reason)
                    with cols[2]:
                        if st.button(f"Plan for {place}", key=f"alt_{place}"):
                            st.session_state["destination"] = place
                            st.session_state.rerun_with_alternate = True
                            st.rerun()
                
                elif isinstance(item, str):
                    # If it's just a string, display it simply and provide a button
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.markdown(f"- **{item}**")
                    with cols[1]:
                        if st.button(f"Plan for {item}", key=f"alt_{item}"):
                            st.session_state.trip_params["destination"] = item
                            st.session_state.rerun_with_alternate = True
                            st.rerun()

        else:
            # --- REGENERATION LOGIC (as requested) ---
            st.error("⚠️ Failed to load or parse alternate suggestions.")
            if st.button("🔁 Regenerate Suggestions"):
                with st.spinner("Rethinking some alternatives..."):
                    from trip_graph.nodes.alternate_suggestion_node import alternate_suggestion_node
                    
                    alt_sugg_node = alternate_suggestion_node()
                    new_suggestions = alt_sugg_node.invoke(st.session_state.trip_result)
                    
                    st.session_state.trip_result["alternate_suggestions"] = new_suggestions
                    st.rerun()
        
        st.stop()

        
    
    st.success(
        f"✅ Favorable conditions for your trip to **{result['destination']}**!"
    )
    # st.subheader(f"🗓 {result['duration']}")
    st.write(f"👨‍👩‍👧 Travellers: {result['travellers']}")
    st.write(f"🎒 Trip Type: {result['trip_type']}")
    st.write(f"💰 Budget: {result['budget']}")

    # print(result)
    # WEATHER FORECAST
    st.divider()
    st.subheader(f"🌤 Weather Forecast")
    # print(result['weather_forecast'])
    for day in result["weather_data"]["forecast"]:
        cols = st.columns([1, 1, 1, 1, 1, 1])
        with cols[1]:
            st.write(f"📅 {day.get('date')}")
        with cols[2]:
            st.write(f"{day.get('weather')}")
        with cols[3]:
            st.write(f"🌡️ {day.get('temp')}°C")
        with cols[4]:
            st.write(f"💧 {day.get('humidity')}%")
        with cols[5]:
            st.write(f"💨 {day.get('wind_speed')} m/s")

    # FLIGHTS
    st.divider()
    st.subheader(f"✈️ Outbound Flights: {source} to {st.session_state.get('destination')}")
    onward_data = result.get("flights", {}).get("onward", {})
    flights_to_display = onward_data.get("best_flights") or onward_data.get("other_flights")
    # print(flights_to_display)

    if flights_to_display:
        display_flight_options(flights_to_display)
    else:
        st.error('Error fetching onward flight details.')
    
    st.subheader(f"✈️ Return Flights: {st.session_state.get('destination')} to {source}")
    return_data = result.get("flights", {}).get("return", {})

    flights_to_display = return_data.get("best_flights") or return_data.get("other_flights")

    if flights_to_display:
        display_flight_options(flights_to_display)
    else:
        st.error('No return flight details could be fetched.')

    # HOTELS
    st.divider()
    st.subheader("🏨 Recommended Hotels")
    # st.json(result["hotels"])
    for hotel in result["hotels"]:
        display_hotel_card(hotel)

    # ITINERARY — day-wise expandable divs
    st.divider()
    st.subheader("🧭 Personalized Itinerary Plan")

    itinerary = result["itinerary"]
    try:
        itinerary_data = parse_llm_json_response(itinerary)
        display_itinerary(itinerary_data)

    except Exception:
        st.error("⚠️ Failed to parse itinerary. The model’s response wasn’t valid JSON.")
        st.info("You can regenerate the itinerary using the button below without re-entering details.")
        if st.button("🔁 Regenerate Itinerary"):
            with st.spinner("Re-generating itinerary..."):
                from trip_graph.nodes.planner_node import planner_node
                p_node = planner_node()
                last_params = st.session_state.get("last_itinerary_params", {
                    "destination": result["destination"],
                    "start_date": result["start_date"],
                    "end_date": result["end_date"],
                    "trip_type": result["trip_type"],
                    "budget": result["budget"],
                    "travellers": result["travellers"]
                })
                new_itinerary = p_node.invoke(last_params)
                # print(new_itinerary)

                try:
                    itinerary_data = parse_llm_json_response(new_itinerary['itinerary'])
                    result["itinerary"] = new_itinerary
                    st.session_state["trip_result"]["itinerary"] = new_itinerary
                    st.success("✅ Itinerary regenerated successfully!")
                    display_itinerary(itinerary_data)
                except Exception:
                    st.error("❌ Regeneration failed again. Please try regenerating your ititnerary in a few minutes.")

    # SUMMARY
    st.divider()
    summary = parse_llm_json_response(result["summary"])
    # print(summary)
    display_trip_summary(summary)
