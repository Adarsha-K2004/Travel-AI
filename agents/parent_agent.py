import re
from agents.weather_agent import WeatherAgent
from agents.places_agent import PlacesAgent


class ParentAgent:
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()

    # -----------------------
    # SMART PLACE EXTRACTION
    # -----------------------
    def extract_place(self, text):
        text = text.lower()

        # Patterns like:
        # "I'm going to Bangalore"
        # "trip to delhi"
        # "visit goa"
        match = re.search(r"(?:to|in|near)\s+([a-zA-Z\s]+)$", text)
        if match:
            return match.group(1).strip()

        # Generic queries:
        match2 = re.search(r"(?:visit|places in|places near|around)\s+([a-zA-Z\s]+)", text)
        if match2:
            return match2.group(1).strip()

        # If user enters only place name:
        if len(text.split()) <= 3:
            return text.strip()

        return None

    # -----------------------
    # MAIN HANDLER
    # -----------------------
    def handle_input(self, user_input):
        place = self.extract_place(user_input)

        if not place:
            return "I couldn't detect a city or place. Try: 'I'm going to Delhi' or 'Bangalore'"

        lat, lon = self.places_agent.get_coordinates(place)
        if not lat:
            return f"Couldn't find the location '{place}'. Try another city."

        # Get weather
        weather = self.weather_agent.get_weather(lat, lon)

        # Get tourist attractions
        attractions = self.places_agent.get_places(lat, lon)

        # -------------------------
        # Build final response
        # -------------------------
        result = f"### 📍 Travel Info for **{place.title()}**\n\n"

        if weather:
            result += f"**🌤 Weather:** {weather}\n\n"

        if attractions:
            result += "**🏛 Top Tourist Attractions:**\n"
            for p in attractions:
                result += f"- {p}\n"

        return result
