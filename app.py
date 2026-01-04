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
    /* 1. Reset Streamlit Button to a Perfect Circle */
    div.stButton > button {
        border-radius: 50% !important;
        width: 100px !important;
        height: 100px !important;
        border: none !important;
        color: white !important; /* This makes the X/Check white */
        font-weight: bold !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }

    /* 2. Red Circle for Skip (X) */
    div.stButton > button[key="skip_btn"] {
        background-color: #FF4B4B !important; /* Bright Red */
        font-size: 50px !important;
    }

    /* 3. Green Circle for Like (Check) */
    div.stButton > button[key="like_btn"] {
        background-color: #2ECC71 !important; /* Bright Green */
        font-size: 50px !important;
    }

    /* 4. Hover Effects */
    div.stButton > button:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        color: white !important;
    }

    /* 5. Title & Info Styling */
    .title { text-align: center; font-size: 40px; font-weight: bold; color: #FF4B4B; }
    .movie-info { text-align: center; margin-top: 10px; }
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

# ---------------- FETCH LOGIC ----------------
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

# ---------------- UI LAYOUT ----------------
st.markdown('<div class="title">🎬 app made for Annette</div>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.movies):
    movie = st.session_state.movies[st.session_state.index]
    
    # Show Movie
    st.markdown(f"<h2 style='text-align:center;'>{movie['Title']}</h2>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if movie.get("Poster") != "N/A":
            st.image(movie["Poster"], use_container_width=True)
    
    st.markdown(f"<div class='movie-info'><b>{movie['Genre']}</b> • ⭐ {movie['imdbRating']}</div>", unsafe_allow_html=True)
    st.write(f"_{movie['Plot']}_")

    st.divider()

    # ---------------- THE CIRCLE BUTTONS ----------------
    col_left, col_right = st.columns(2)

    with col_left:
        # The text inside 'st.button' is what appears in white
        if st.button("✕", key="skip_btn"):
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()

    with col_right:
        if st.button("✔", key="like_btn"):
            st.session_state.liked.append(movie)
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()
else:
    st.write("Finding more movies...")
    load_movies()
    st.rerun()

# ---------------- LIKED GALLERY ----------------
if st.session_state.liked:
    st.divider()
    st.subheader("❤️ Annette's Matches")
    cols = st.columns(3)
    for i, m in enumerate(st.session_state.liked):
        with cols[i % 3]:
            if m.get("Poster") != "N/A":
                st.image(m["Poster"], caption=m["Title"], use_container_width=True)
