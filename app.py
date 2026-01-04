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

# ---------------- CSS ----------------
st.markdown("""
<style>
/* Title */
.title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
    margin-bottom: 20px;
}

/* Poster centered */
.poster {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
}

/* Stars */
.stars {
    text-align: center;
    font-size: 28px;
    margin-top: 10px;
}

/* Genre & summary */
.info {
    text-align: center;
    font-size: 18px;
    margin-top: 5px;
}

/* Circular buttons using <button> */
.button-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
    gap: 150px;
}

.circle-button {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: none;
    font-size: 60px;
    color: white;
    cursor: pointer;
    font-weight: bold;
    transition: transform 0.1s;
}

.circle-button:hover {
    transform: scale(1.1);
}

#like {
    background-color: #2ecc71;
}

#skip {
    background-color: #e74c3c;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="title">🎬 app made for Annette</div>', unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "movies" not in st.session_state:
    st.session_state.movies = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = []
if "skipped" not in st.session_state:
    st.session_state.skipped = []
if "movie_dict" not in st.session_state:
    st.session_state.movie_dict = {}

# ---------------- FUNCTION TO LOAD MOVIES ----------------
def load_movies():
    if st.session_state.liked:
        liked_genres = []
        for movie_title in st.session_state.liked:
            info = st.session_state.movie_dict.get(movie_title)
            if info:
                liked_genres.extend(info['Genre'].split(', '))
        term = Counter(liked_genres).most_common(1)[0][0] if liked_genres else random.choice(SEARCH_TERMS)
    else:
        term = random.choice(SEARCH_TERMS)

    page = random.randint(1, 5)
    search_res = requests.get(
        "http://www.omdbapi.com/",
        params={
            "apikey": API_KEY,
            "s": term,
            "type": "movie",
            "page": page
        }
    ).json()

    if search_res.get("Search"):
        for m in search_res["Search"]:
            details = requests.get(
                "http://www.omdbapi.com/",
                params={
                    "apikey": API_KEY,
                    "i": m["imdbID"],
                    "plot": "short"
                }
            ).json()
            st.session_state.movies.append(details)
            st.session_state.movie_dict[details["Title"]] = details

# Load movies if list is short
if len(st.session_state.movies) < 3:
    load_movies()

# ---------------- CURRENT MOVIE ----------------
movie = st.session_state.movies[st.session_state.index]

title = movie.get("Title", "Unknown")
year = movie.get("Year", "")
poster = movie.get("Poster")
rating = movie.get("imdbRating", "N/A")
genre = movie.get("Genre", "N/A")
plot = movie.get("Plot", "No summary available.")

# ---------------- DISPLAY ----------------
st.markdown(f"<h2 style='text-align:center;'>{title} ({year})</h2>", unsafe_allow_html=True)

# Poster centered under title
if poster and poster != "N/A":
    st.markdown(f"""
    <div class="poster">
        <img src="{poster}" width="300">
    </div>
    """, unsafe_allow_html=True)

# Stars
if rating != "N/A":
    stars = round(float(rating)/2)
    st.markdown(
        f'<div class="stars">{"★"*stars}{"☆"*(5-stars)}<br>({rating}/10)</div>',
        unsafe_allow_html=True
    )

# Genre & summary
st.markdown(f'<div class="info"><b>Genre:</b> {genre}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="info">{plot}</div>', unsafe_allow_html=True)

# ---------------- CIRCULAR BUTTONS ----------------
st.markdown("""
<div class="button-container">
    <form action="" method="post">
        <button id="skip" class="circle-button" name="skip">✖</button>
        <button id="like" class="circle-button" name="like">✔</button>
    </form>
</div>
""", unsafe_allow_html=True)

# Detect button clicks using session_state
clicked = st.experimental_get_query_params().get("clicked", [""])[0]

# Workaround: Use regular Streamlit buttons hidden to trigger logic
col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("✖ Skip", key="skip_hidden"):
        st.session_state.skipped.append(title)
        st.session_state.index += 1
        st.rerun()
with col3:
    if st.button("✔ Like", key="like_hidden"):
        st.session_state.liked.append(title)
        st.session_state.index += 1
        st.rerun()

# ---------------- LOAD MORE ----------------
if st.session_state.index >= len(st.session_state.movies) - 1:
    load_movies()
