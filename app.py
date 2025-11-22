import streamlit as st
from agents.parent_agent import ParentAgent

# --------------------------------------------------
# PAGE CONFIG (MOBILE FRIENDLY)
# --------------------------------------------------
st.set_page_config(
    page_title="Travel Planner AI",
    page_icon="🌍",
    layout="wide"     # important for mobile
)

# --------------------------------------------------
# BACKGROUND IMAGE + OVERLAY
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* Background image */
    .stApp {
        background-image: url("https://wallpapercave.com/wp/wp2115638.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Dark overlay for readability */
    .overlay {
        position: fixed;
        top: 0; 
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.65);
        z-index: -1;
        backdrop-filter: blur(3px);
    }
    </style>
    <div class="overlay"></div>
    """,
    unsafe_allow_html=True
)

agent = ParentAgent()

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------
st.markdown(
    """
    <style>

    /* Full page padding */
    .main {
        padding: 15px 20px;
    }

    /* Card container */
    .card {
        background: #1e1e1e;
        padding: 18px;
        border-radius: 14px;
        margin-top: 12px;
        margin-bottom: 12px;
        box-shadow: 0 0 12px rgba(255,255,255,0.1);
    }

    /* Header */
    .header {
        font-size: 30px;
        font-weight: 900;
        padding-bottom: 5px;
    }

    .subheader {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .emoji-title {
        font-size: 26px;
        margin-right: 10px;
    }

    .place-item {
        font-size: 18px;
        padding: 6px 0;
        color: #dcdcdc;
    }

    /* Mobile responsiveness fix */
    @media (max-width: 600px) {
        .header {
            font-size: 24px;
        }
        .subheader {
            font-size: 18px;
        }
        .card {
            padding: 15px;
        }
        .place-item {
            font-size: 16px;
        }
    }

    /* Rounded textarea */
    textarea {
        border-radius: 10px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# HEADER (more lively)
# --------------------------------------------------
st.markdown(
    "<div class='header'>🌍 Your AI Travel Buddy</div>",
    unsafe_allow_html=True
)

st.markdown(
    "Tell me where you're going — I’ll show weather, attractions, and more ✈️🌤️🎒"
)

# --------------------------------------------------
# INPUT AREA
# --------------------------------------------------
user_input = st.text_area(
    "Where are you planning to go?",
    placeholder="Try: 'Bangalore', 'Plan a trip to Delhi', 'Places near Mysore'",
    height=90
)

if st.button("Explore ✨"):
    if not user_input.strip():
        st.warning("Please enter a city or place name.")
    else:
        with st.spinner("🔍 Finding the best places for you… "):
            result = agent.handle_input(user_input)

        # --------------------------------------------------
        # PARSE THE RESULT (simple markdown)
        # --------------------------------------------------
        st.markdown(" ")
        st.markdown("---")
        

       # --------------------------------------------------
# CLEAN PARSING OF MODEL OUTPUT
# --------------------------------------------------

    weather_text = "No weather info available."
    places_list = []

    # Weather extraction
    if "Weather:" in result:
        try:
            weather_block = result.split("Weather:")[1].split("Top Tourist")[0].strip()
            weather_text = weather_block.replace("**", "").strip()
        except:
            pass

    # Places extraction
    if "Top Tourist Attractions" in result:
        try:
            places_block = result.split("Top Tourist Attractions:")[1]
            raw_places = [p.strip() for p in places_block.split("\n") if p.strip()]

            # Remove markdown bullets and stray characters
            cleaned_places = []
            for p in raw_places:
                p = p.replace("-", "").replace("*", "").strip()
                if len(p) > 1:
                    cleaned_places.append(p)

            places_list = cleaned_places
        except:
            pass


    # --------------------------------------------------
    # WEATHER CARD (INSIDE CARD ONLY)
    # --------------------------------------------------
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='subheader'>🌤️ Weather</div>", unsafe_allow_html=True)
    st.write(weather_text)
    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------
    # PLACES CARD (INSIDE CARD ONLY)
    # --------------------------------------------------
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='subheader'>📍 Popular Attractions</div>", unsafe_allow_html=True)

    if places_list:
        for p in places_list:
            st.markdown(f"<div class='place-item'>🟢 {p}</div>", unsafe_allow_html=True)
    else:
        st.write("No attractions found.")

    st.markdown("</div>", unsafe_allow_html=True)
