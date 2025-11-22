import requests

class PlacesAgent:

    # -------------------------------------------------------------------
    # GET COORDINATES
    # -------------------------------------------------------------------
    def get_coordinates(self, place: str):
        """
        Convert a city/place name into (lat, lon) using Nominatim.
        """
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": place, "format": "json"}
            headers = {"User-Agent": "TourismAgent/1.0"}

            res = requests.get(url, params=params, headers=headers, timeout=10)
            data = res.json()

            if not data:
                return None, None

            return float(data[0]["lat"]), float(data[0]["lon"])

        except Exception as e:
            print("Error in geocoding:", e)
            return None, None

    # -------------------------------------------------------------------
    # MAIN: GET PLACES
    # -------------------------------------------------------------------
    def get_places(self, lat: float, lon: float):
        """
        Try Overpass first.
        If Overpass fails OR only returns hotels → use Wikipedia fallback.
        """
        # 1) Try Overpass
        overpass_places = self._query_overpass(lat, lon)

        # If Overpass returns real attractions → use them
        if overpass_places and not self._are_hotels(overpass_places):
            return overpass_places[:10]

        print("Overpass returned only hotels or invalid results — switching to Wikipedia...")
        
        # 2) Wikipedia fallback
        wiki_places = self._query_wikipedia(lat, lon)
        if wiki_places:
            return wiki_places[:10]

        return ["No popular tourist places found."]

    # -------------------------------------------------------------------
    # OVERPASS API (Primary)
    # -------------------------------------------------------------------
    def _query_overpass(self, lat: float, lon: float):
        """
        Query Overpass API but ONLY fetch real tourist attractions.
        """
        overpass_urls = [
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass-api.de/api/interpreter",
            "https://lz4.overpass-api.de/api/interpreter",
        ]

        # STRICT FILTER: Only real tourist attractions (no hotels)
        query = f"""
        [out:json][timeout:25];
        (
          node(around:15000,{lat},{lon})["tourism"~"attraction|museum|gallery|artwork|theme_park|zoo|park|viewpoint|monument|palace|fort|historic"];
          way(around:15000,{lat},{lon})["tourism"~"attraction|museum|gallery|artwork|theme_park|zoo|park|viewpoint|monument|palace|fort|historic"];
          relation(around:15000,{lat},{lon})["tourism"~"attraction|museum|gallery|artwork|theme_park|zoo|park|viewpoint|monument|palace|fort|historic"];
        );
        out center;
        """

        headers = {"User-Agent": "TourismAgent/1.0"}

        for url in overpass_urls:
            try:
                res = requests.post(url, data=query, headers=headers, timeout=25)

                text = res.text.strip()
                if not text:
                    print("Overpass empty response:", url)
                    continue

                data = res.json()
                places = []

                for el in data.get("elements", []):
                    tags = el.get("tags", {})
                    name = tags.get("name")
                    if name:
                        places.append(name)

                if places:
                    print("Overpass (clean) found:", places)
                    return places

            except Exception as e:
                print("Overpass error:", url, "→", e)

        return []

    # -------------------------------------------------------------------
    # DETECT IF A LIST IS MOSTLY HOTELS
    # -------------------------------------------------------------------
    def _are_hotels(self, places_list):
        hotel_keywords = [
            "hotel", "lodge", "residency", "hostel", "inn", "rooms",
            "pg", "service apartment", "guest house", "resort", "motel"
        ]

        count = 0
        for p in places_list:
            lower = p.lower()
            if any(h in lower for h in hotel_keywords):
                count += 1

        # If 70% of results are hotels → reject list
        return count >= max(3, int(0.7 * len(places_list)))

    # -------------------------------------------------------------------
    # WIKIPEDIA FALLBACK — NO API KEY REQUIRED
    # -------------------------------------------------------------------
    def _query_wikipedia(self, lat: float, lon: float):
        """
        Wikipedia fallback with enhanced filters and ranking:
        
        Priority:
        1. Natural attractions
        2. Palaces / Forts / Heritage
        3. Museums / Galleries
        4. Parks / Gardens
        5. Temples / Religious Sites
        """
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "geosearch",
                "gscoord": f"{lat}|{lon}",
                "gsradius": 30000,
                "gslimit": 50,
                "format": "json"
            }

            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            raw_places = [item["title"] for item in data["query"]["geosearch"]]

            # ----------------------------------------------------
            # BLOCKLIST: REMOVE HOTELS / HOSTELS / PG / OFFICES
            # ----------------------------------------------------
            blocklist = [
                "hotel", "hostel", "lodge", "residency", "inn", "pg", "rooms",
                "guest house", "apartment", "resort", "motel", "canteen",
                "restaurant", "bar", "bank", "atm", "office", "corporation",
                "hospital", "clinic", "school", "college", "mall", "complex"
            ]

            cleaned = []
            for place in raw_places:
                l = place.lower()
                if any(bad in l for bad in blocklist):
                    continue
                cleaned.append(place)

            if not cleaned:
                return raw_places[:5]

            # ----------------------------------------------------
            # CATEGORY DEFINITION WITH PRIORITY SCORES
            # LOWER SCORE = HIGHER PRIORITY
            # ----------------------------------------------------
            categories = {
                "natural": (
                    0,
                    ["falls", "waterfall", "lake", "dam", "hill", "hills",
                     "valley", "forest", "beach", "river", "peak",
                     "viewpoint", "sunset point"]
                ),
                "heritage": (
                    1,
                    ["palace", "fort", "monument", "heritage", "gate",
                     "arch", "tower", "statue"]
                ),
                "museum": (
                    2,
                    ["museum", "gallery", "planetarium", "science center",
                     "observatory"]
                ),
                "park": (
                    3,
                    ["park", "garden", "botanical", "arboretum", "national park",
                     "zoo"]
                ),
                "temple": (
                    4,
                    ["temple", "mandir", "cathedral", "church", "mosque",
                     "dargah", "ashram"]
                ),
            }

            # ----------------------------------------------------
            # CLASSIFY EACH PLACE INTO A CATEGORY
            # ----------------------------------------------------
            scored_list = []

            for place in cleaned:
                l = place.lower()
                score = 999  # default = lowest priority

                for cat, (cat_score, keywords) in categories.items():
                    if any(k in l for k in keywords):
                        score = cat_score
                        break

                scored_list.append((score, place))

            # ----------------------------------------------------
            # SORT BY: score ASC → then alphabetical
            # ----------------------------------------------------
            scored_list.sort(key=lambda x: (x[0], x[1].lower()))

            # Extract clean list
            final_list = [place for score, place in scored_list]

            print("Wikipedia Ranked List:", final_list)

            return final_list[:10]

        except Exception as e:
            print("Wikipedia fallback error:", e)
            return []
