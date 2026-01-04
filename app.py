import streamlit as st
import requests
import random
from collections import Counter

# ---------------- CONFIG ----------------
API_KEY = "c978ed19"

SEARCH_TERMS = [
    "love", "war", "future", "night", "dark",
    "hero", "life", "game", "dream", "world"
]

st.set_page_config(page_title="Movie Tinder", layout="centered")

# ---------------- ROBUST CSS ----------------
st.markdown("""
<style>
    /* Title Styling */
    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #ff4b4b;
        margin-bottom: 20px;
    }

    /* Poster and Info Styling */
    .poster-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .movie-card {
        text-align: center;
    }

    /* THE BUTTON FIX: Force Streamlit buttons to be circles */
    div.stButton > button {
        border-radius: 50% !important;
        width: 100px !important;
        height: 100px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        transition: all 0.2s ease !important;
    }

    /* Red Skip Button */
    div.stButton > button[key="skip_btn"] {
        background-color: #ff4b4b !important;
        font-size: 40px !important;
    }

    /* Green Like Button */
    div.stButton > button[key="like_btn"] {
        background-color: #2ecc71 !important;
        font-size: 40px !important;
    }

    /* Hover effect */
    div.stButton > button:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
    }

    /* Hide the default focus ring */
    div.stButton > button:focus {
        outline: none !important;
        box-shadow: none !important;
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
    # Recommendation logic based on likes
    if st.session_state.liked:
        liked_genres = []
        for movie_title in st.session_state.liked:
            info = st.session_state.movie_dict.get(movie_title)
            if info: liked_genres.extend(info['Genre'].split(', '))
        term = Counter(liked_genres).most_common(1)[0][0] if liked_genres else random.choice(SEARCH_TERMS)
    else:
        term = random.choice(SEARCH_TERMS)

    res = requests.get("http://www.omdbapi.com/", params={"apikey": API_KEY, "s": term, "type": "movie", "page": random.randint(1, 10)}).json()
    
    if res.get("Search"):
        for m in res["Search"]:
            details = requests.get("http://www.omdbapi.com/", params={"apikey": API_KEY, "i": m["imdbID"]}).json()
            if details.get("Title") and details["Title"] not in st.session_state.movie_dict:
                st.session_state.movies.append(details)
                st.session_state.movie_dict[details["Title"]] = details

# Initial fetch
if not st.session_state.movies:
    load_movies()

# ---------------- UI ----------------
st.markdown('<div class="title">🎬 Movie Match</div>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.movies):
    movie = st.session_state.movies[st.session_state.index]
    
    # Display Movie Card
    st.markdown(f"<h2 style='text-align:center;'>{movie['Title']} ({movie['Year']})</h2>", unsafe_allow_html=True)
    
    col_img_1, col_img_2, col_img_3 = st.columns([1, 2, 1])
    with col_img_2:
        if movie.get("Poster") != "N/A":
            st.image(movie["Poster"], use_container_width=True)
    
    st.markdown(f"<p style='text-align:center;'><b>Genre:</b> {movie['Genre']} | <b>Rating:</b> {movie['imdbRating']}/10</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color: #555;'>{movie['Plot']}</p>", unsafe_allow_html=True)

    st.divider()

    # ---------------- CIRCULAR BUTTONS ----------------
    # Placing buttons in columns so they stay side-by-side
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("✖", key="skip_btn"):
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()

    with btn_col2:
        if st.button("✔", key="like_btn"):
            st.session_state.liked.append(movie['Title'])
            st.session_state.index += 1
            if st.session_state.index >= len(st.session_state.movies) - 2:
                load_movies()
            st.rerun()

else:
    st.write("Searching for more movies...")
    load_movies()
    st.rerun()

# Show matches at the very bottom
if st.session_state.liked:
    with st.expander("❤️ Your Matches"):
        for m in st.session_state.liked:
            st.write(f"✅ {m}")
