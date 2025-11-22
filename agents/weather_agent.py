import requests

class WeatherAgent:
    def get_weather(self, lat, lon):
        try:
            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}&current_weather=true"
            )

            res = requests.get(url, timeout=10)

            if res.status_code != 200:
                print("Weather API Error:", res.text)
                return None

            data = res.json()

            cw = data.get("current_weather")
            if not cw:
                return None

            temperature = cw.get("temperature")
            weather_code = cw.get("weathercode")

            description = self.weather_description(weather_code)

            return f"it's currently {temperature}°C with {description}."

        except Exception as e:
            print("Weather error:", e)
            return None

    def weather_description(self, code):
        mapping = {
            0: "a clear sky",
            1: "mainly clear weather",
            2: "partly cloudy skies",
            3: "overcast conditions",
            51: "light drizzle",
            61: "light rain",
            71: "snowfall",
            95: "a thunderstorm",
        }
        return mapping.get(code, "normal weather")
