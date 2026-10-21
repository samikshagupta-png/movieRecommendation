import pandas as pd
import ast
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

# # Step 11: Check the result
print(movies.head())
print(movies[["title", "tags"]].iloc[0])
print("Total movies:", len(movies))