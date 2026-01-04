import streamlit as st
import requests
import random
from collections import Counter

# ---------------- CONFIG ----------------
API_KEY = "c978ed19"
SEARCH_TERMS = ["love", "war", "future", "night", "dark", "hero", "life", "game", "dream", "world"]

st.set_page_config(page_title="Movie Tinder", layout="centered")

# ---------------- CSS (KEEPING EVERYTHING THE SAME) ----------------
st.markdown("""
<style>
    div.stButton > button {
        border-radius: 50% !important;
        width: 140px !important;
        height: 140px !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    div.stButton > button[key="skip_btn"] {
        background-color: #FF0000 !important; 
        color: white !important;
    }

    div.stButton > button[key="like_btn"] {
        background-color: #00FF00 !important; 
        color: white !important;
    }

    div.stButton > button p {
        font-size: 80px !important;
        font-weight: 900 !important;
        color: white !important;
        margin: 0 !important;
    }

    .movie-title { text-align: center; font-size: 50px !important; font-weight: 800 !important; }
    .summary-text { text-align: center; font-size: 26px !important; line-height: 1.4; margin-top: 20px; }
    .huge-stars { text-align: center; font-size: 60px !important; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "movies" not in st.session_state:
    st.session_state.movies = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = []
if "movie_dict" not in st.session_state:
    st.session_state.movie_dict = {}

def load_movies():
    term = random.choice(SEARCH_TERMS)
    try:
        res = requests.get(f"http://www.omdbapi.com/?apikey={API_KEY}&s={term}&type=movie&page={random.randint(1,5)}").json()
        if res.get("Search"):
            for m in res["Search"]:
                details = requests.get(f"http://www.omdbapi.com/?apikey={API_KEY}&i={m['imdbID']}").json()
                if details.get("Title") not in st.session_state.movie_dict:
                    st.session_state.movies.append(details)
                    st.session_state.movie_dict[details["Title"]] = details
    except: pass

if not st.session_state.movies:
    load_movies()

# ---------------- UI ----------------
st.markdown('<h1 style="text-align:center; color:#FF4B4B;">🎬 app made for Annette</h1>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.movies):
    movie = st.session_state.movies[st.session_state.index]
    
    st.markdown(f'<div class="movie-title">{movie["Title"]} ({movie["Year"]})</div>', unsafe_allow_html=True)

    col_1, col_2, col_3 = st.columns([1, 4, 1])
    with col_2:
        if movie.get("Poster") != "N/A":
            st.image(movie["Poster"], use_container_width=True)

    try:
        rating = float(movie.get("imdbRating", 0))
        stars_count = round(rating / 2)
        st.markdown(f'<div class="huge-stars">{"⭐" * stars_count}</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="huge-stars">⭐⭐⭐</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="summary-text"><b>Genre:</b> {movie["Genre"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-text">{movie["Plot"]}</div>', unsafe_allow_html=True)

    st.divider()

    # ---------------- THE CENTERED BUTTONS ----------------
    # We use 4 columns: Two "spacers" on the outside, two buttons in the middle
    # Adjusting the [2, 1, 1, 2] ratio moves the buttons closer or further apart
    spacer_left, btn_skip, btn_like, spacer_right = st.columns([1.5, 1, 1, 1.5])

    with btn_skip:
        if st.button("✕", key="skip_btn"):
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()

    with btn_like:
        if st.button("✔", key="like_btn"):
            st.session_state.liked.append(movie)
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()

# Match Gallery
if st.session_state.liked:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>❤️ Annette's Matches</h2>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, m in enumerate(st.session_state.liked):
        with cols[i % 3]:
            st.image(m["Poster"], caption=m["Title"], use_container_width=True)
