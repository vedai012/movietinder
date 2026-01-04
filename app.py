import streamlit as st
import requests
import random
from collections import Counter

# ---------------- CONFIG ----------------
API_KEY = "c978ed19"
SEARCH_TERMS = ["love", "war", "future", "night", "dark", "hero", "life", "game", "dream", "world"]

st.set_page_config(page_title="Movie Tinder", layout="centered")

# ---------------- THE "BIG & BOLD" CSS ----------------
st.markdown("""
<style>
    /* 1. Make the Title and Summary MASSIVE */
    .main-title {
        text-align: center;
        font-size: 55px !important;
        font-weight: 800;
        color: #FF4B4B;
        margin-bottom: 5px;
    }
    
    .summary-text {
        text-align: center;
        font-size: 24px !important;
        line-height: 1.4;
        padding: 10px 20px;
    }

    /* 2. BIG STARS */
    .big-stars {
        text-align: center;
        font-size: 40px !important;
        margin: 10px 0;
    }

    /* 3. THE CIRCLE BUTTONS - FORCED COLORS */
    div.stButton > button {
        border-radius: 50% !important;
        width: 130px !important;
        height: 130px !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4) !important;
        transition: all 0.2s ease !important;
    }

    /* RED SKIP BUTTON */
    div.stButton > button[key="skip_btn"] {
        background-color: #E74C3C !important; /* Solid Red */
    }
    div.stButton > button[key="skip_btn"] div p {
        font-size: 60px !important;
        color: white !important;
        font-weight: bold !important;
    }

    /* GREEN LIKE BUTTON */
    div.stButton > button[key="like_btn"] {
        background-color: #2ECC71 !important; /* Solid Green */
    }
    div.stButton > button[key="like_btn"] div p {
        font-size: 60px !important;
        color: white !important;
        font-weight: bold !important;
    }

    /* Hover effect */
    div.stButton > button:hover {
        transform: scale(1.1) !important;
        filter: brightness(1.2);
    }
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

# ---------------- LOGIC ----------------
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
st.markdown('<div class="main-title">🎬 app made for Annette</div>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.movies):
    movie = st.session_state.movies[st.session_state.index]
    
    # Title
    st.markdown(f"<h1 style='text-align:center; font-size: 45px;'>{movie['Title']} ({movie['Year']})</h1>", unsafe_allow_html=True)
    
    # Big Stars
    try:
        rating = float(movie.get("imdbRating", 0))
        stars = round(rating / 2)
        st.markdown(f'<div class="big-stars">{"⭐" * stars}</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="big-stars">⭐⭐⭐</div>', unsafe_allow_html=True)

    # Poster
    col_a, col_b, col_c = st.columns([1, 4, 1])
    with col_b:
        if movie.get("Poster") != "N/A":
            st.image(movie["Poster"], use_container_width=True)
    
    # Summary
    st.markdown(f'<div class="summary-text"><b>Genre:</b> {movie["Genre"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-text">{movie["Plot"]}</div>', unsafe_allow_html=True)

    st.divider()

    # ---------------- CIRCLE BUTTONS ----------------
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("✕", key="skip_btn"):
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()

    with btn_col2:
        if st.button("✔", key="like_btn"):
            st.session_state.liked.append(movie)
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()

# ---------------- MATCH GALLERY ----------------
if st.session_state.liked:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>❤️ Liked Movies</h2>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, m in enumerate(st.session_state.liked):
        with cols[i % 3]:
            st.image(m["Poster"], caption=m["Title"], use_container_width=True)
