import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Step 1: Load both datasets
movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")
# Step 2: Merge datasets using movie IDs
movies = movies.merge(
    credits,
    left_on="id",
    right_on="movie_id",
    suffixes=("movies","_credits")
)
#extract names from json_formatted txt
def extract(text):
    try:
        items = ast.literal_eval(text)
        return [item["name"] for item in items]
    except(ValueError,TypeError,SyntaxError,KeyError):
        return[]
# Step 4: Extract genres and keywords
movies["genres"] = movies["genres"].apply(extract)
movies["keywords"] = movies["keywords"].apply(extract)
#extract first 3 actor
def extract_cast(text):
    try:
        items = ast.literal_eval(text)
        return[item["name"] for item in items[:3]]
    except(ValueError,TypeError,SyntaxError,KeyError):
        return[]

#extract director 
def extract_director(text):
    try:
        items=ast.literal_eval(text)
        for item in items:
            if item.get("job") == "Director":
                return[item["name"]]
        return []
    except(ValueError,KeyError,SyntaxError,TypeError):
        return[]

movies["crew"] = movies["crew"].apply(extract_director)
# Step 7: Clean the overview
movies["overview"] = movies["overview"].fillna("").apply(
    lambda text: text.split()
)
# Step 8: Combine all features into one column
# Make sure every feature is a list
feature_columns = ["genres", "keywords", "overview", "cast", "crew"]

for column in feature_columns:
    movies[column] = movies[column].apply(
        lambda value: value if isinstance(value, list) else []
    )

# Combine all movie features
movies["tags"] = (
    movies["genres"]
    + movies["keywords"]
    + movies["overview"]
    + movies["cast"]
    + movies["crew"]
)

# Step 9: Convert the lists into text
movies["tags"] = movies["tags"].apply(
    lambda words: " ".join(words).lower()
)
print(movies.columns.tolist())
# Step 10: Keep the columns needed for recommendations
movies = movies[["id", "titlemovies", "tags"]]
movies = movies.rename(columns={"titlemovies": "title"})

# # # Step 11: Check the result
# print(movies.head())
# print(movies[["title", "tags"]].iloc[0])
# print("Total movies:", len(movies))

# Step 12: Convert tags into numerical vectors
cv = CountVectorizer(max_features=5000, stop_words="english")

vectors = cv.fit_transform(movies["tags"])

print("Vector shape:", vectors.shape)



# Step 13: Calculate similarity between movies
similarity = cosine_similarity(vectors)

print("Similarity matrix shape:", similarity.shape)


#step 14:recommend similar movies
def recommend(movie_title):
    matches = movies[
        movies["title"].str.lower() == movie_title.lower()
    ]
    if matches.empty:
        print("Movie not found!")
        return
    movie_index= matches.index[0]
    distance = similarity[movie_index]
    movie_list = sorted(
        enumerate(distance), #enumerate() attaches each score to its movie index:
        key = lambda item :item[1], #his tells Python to sort the pairs using their similarity scores, not their indexes.

        reverse=True
    )
    print(f"\nMovies similar to {movie_title}:")

    count = 0
    for index, score in movie_list:
        if index == movie_index:
            continue

        print(movies.iloc[index]["title"])
        count += 1

        if count == 5:
            break

recommend("Avatar")