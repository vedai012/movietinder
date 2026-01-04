import streamlit as st
import requests
import random
from collections import Counter

# ---------------- CONFIG ----------------
API_KEY = "c978ed19"
SEARCH_TERMS = ["love", "war", "future", "night", "dark", "hero", "life", "game", "dream", "world"]

st.set_page_config(page_title="Movie Tinder", layout="centered")

# ---------------- THE ULTIMATE CSS FIX ----------------
st.markdown("""
<style>
    /* Center the title */
    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #ff4b4b;
        margin-bottom: 20px;
    }

    /* Target the button containers to center them */
    [data-testid="stHorizontalBlock"] {
        align-items: center;
        justify-content: center;
    }

    /* Reset Streamlit Button Styles */
    div.stButton > button {
        border-radius: 50% !important;
        width: 120px !important;
        height: 120px !important;
        border: none !important;
        color: transparent !important; /* Hide the text, we'll use pseudo-elements */
        box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        display: block !important;
        margin: 0 auto !important;
    }

    /* RED SKIP BUTTON (X) */
    div.stButton > button[key="skip_btn"] {
        background-color: #ff4b4b !important;
    }
    div.stButton > button[key="skip_btn"]::after {
        content: "✕";
        color: white !important;
        font-size: 60px !important;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-weight: bold;
    }

    /* GREEN LIKE BUTTON (Check) */
    div.stButton > button[key="like_btn"] {
        background-color: #2ecc71 !important;
    }
    div.stButton > button[key="like_btn"]::after {
        content: "✔";
        color: white !important;
        font-size: 60px !important;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-weight: bold;
    }

    /* Hover animation */
    div.stButton > button:hover {
        transform: scale(1.15) !important;
        box-shadow: 0 12px 24px rgba(0,0,0,0.3) !important;
    }

    /* Match Gallery Styling */
    .match-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "movies" not in st.session_state:
    st.session_state.movies = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = [] # List of dicts for the gallery
if "movie_dict" not in st.session_state:
    st.session_state.movie_dict = {}

# ---------------- FUNCTIONS ----------------
def load_movies():
    term = random.choice(SEARCH_TERMS)
    try:
        res = requests.get("http://www.omdbapi.com/", params={"apikey": API_KEY, "s": term, "type": "movie", "page": random.randint(1, 10)}).json()
        if res.get("Search"):
            for m in res["Search"]:
                details = requests.get("http://www.omdbapi.com/", params={"apikey": API_KEY, "i": m["imdbID"]}).json()
                if details.get("Title") and details["Title"] not in st.session_state.movie_dict:
                    st.session_state.movies.append(details)
                    st.session_state.movie_dict[details["Title"]] = details
    except:
        pass

if not st.session_state.movies:
    load_movies()

# ---------------- MAIN UI ----------------
st.markdown('<div class="title">🎬 app made for Annette</div>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.movies):
    movie = st.session_state.movies[st.session_state.index]
    
    # Poster Display
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if movie.get("Poster") != "N/A":
            st.image(movie["Poster"], use_container_width=True)
        st.markdown(f"<h3 style='text-align:center;'>{movie['Title']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>{movie['Genre']} • {movie['imdbRating']}/10</p>", unsafe_allow_html=True)

    # ---------------- CIRCULAR BUTTONS ----------------
    # We use empty spacer columns to push buttons to the center
    btn_spacer1, btn_skip, btn_like, btn_spacer2 = st.columns([1, 1, 1, 1])

    with btn_skip:
        if st.button(" ", key="skip_btn"): # Space is hidden by CSS anyway
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()

    with btn_like:
        if st.button(" ", key="like_btn"):
            st.session_state.liked.append({
                "title": movie['Title'],
                "poster": movie.get("Poster"),
                "year": movie.get("Year")
            })
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()
else:
    st.write("Fetching movies...")
    load_movies()
    st.rerun()

# ---------------- MATCH GALLERY ----------------
if st.session_state.liked:
    st.divider()
    st.subheader("❤️ Annette's Liked Movies")
    
    # Display matches in a grid
    cols = st.columns(3)
    for idx, item in enumerate(st.session_state.liked):
        with cols[idx % 3]:
            st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
            if item["poster"] != "N/A":
                st.image(item["poster"], use_container_width=True)
            st.caption(f"{item['title']} ({item['year']})")
            st.markdown('</div>', unsafe_allow_html=True)
