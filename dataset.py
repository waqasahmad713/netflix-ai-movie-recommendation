import requests
import pandas as pd
import time

# API Configuration
API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
BASE_URL = "https://api.themoviedb.org/3/movie/top_rated"

# Dictionary to map genre IDs to genre names
GENRE_URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=en-US"

genre_response = requests.get(GENRE_URL)

if genre_response.status_code == 200:
    genres = genre_response.json()["genres"]
    genre_dict = {genre["id"]: genre["name"] for genre in genres}
else:
    print("Failed to fetch genres.")
    genre_dict = {}

movies_data = []

# Loop through pages 1 to 471
for page in range(1, 472):

    url = f"{BASE_URL}?api_key={API_KEY}&language=en-US&page={page}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            for movie in data.get("results", []):

                movie_name = movie.get("title", "")
                description = movie.get("overview", "")

                genre_ids = movie.get("genre_ids", [])
                genres = [genre_dict.get(gid, "Unknown") for gid in genre_ids]
                genre = ", ".join(genres)

                movies_data.append({
                    "movie_name": movie_name,
                    "description": description,
                    "genre": genre
                })

            print(f"Page {page}/471 completed")

        else:
            print(f"Failed page {page}: {response.status_code}")

        # Avoid hitting rate limits
        time.sleep(0.2)

    except Exception as e:
        print(f"Error on page {page}: {e}")

# Create DataFrame
df = pd.DataFrame(movies_data)

# Remove duplicates
df = df.drop_duplicates(subset=["movie_name"])

# Save CSV
df.to_csv("movies_dataset.csv", index=False, encoding="utf-8")

print(f"\nDataset saved successfully!")
print(f"Total Movies: {len(df)}")
print(df.head())