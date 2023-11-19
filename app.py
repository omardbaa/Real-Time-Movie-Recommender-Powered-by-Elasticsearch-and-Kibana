

from math import ceil
from flask import Flask, render_template, request, jsonify, redirect, url_for
from elasticsearch import Elasticsearch

app = Flask(__name__)
client = Elasticsearch("http://localhost:9200")  # Your Elasticsearch endpoint


def get_paginated_movies(page=1, page_size=10):
    from_, size = (page - 1) * page_size, page_size
    query = {
        "query": {
            "match_all": {}
        },
        "from": from_,
        "size": size,
        "sort": [
            {"popularity": {"order": "desc"}}
        ]
    }
    result = client.search(index='moviedb_data', body=query)
    total_movies = result['hits']['total']['value']
    movies = [hit['_source'] for hit in result['hits']['hits']]
    total_pages = ceil(total_movies / page_size)

    if not movies:
        total_pages = 1

    return movies, total_pages

def get_movie_details(title):
    query = {
        "query": {
            "match": {
                "title.keyword": title
            }
        }
    }
    result = client.search(index='moviedb_data', body=query)
    return result['hits']['hits'][0]['_source'] if result['hits']['hits'] else None

@app.route('/', methods=['GET'])
def index():
    page = int(request.args.get('page', 1))
    movies, total_pages = get_paginated_movies(page)

    start_page = max(page - 3, 1)
    end_page = min(page + 4, total_pages + 1)

    return render_template(
        "index.html",
        movies=movies,
        total_pages=total_pages,
        current_page=page,
        start_page=start_page,
        end_page=end_page
    )
@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    title = request.args.get('title')
    if not title:
        return redirect(url_for('index'))

    movie_details = get_movie_details(title)
    if not movie_details:
        return jsonify({"error": f"Movie with title '{title}' not found"}), 404

    similar_movies = find_similar_movies(movie_details)
    page = int(request.args.get('page', 1))  # Get the page number
    movies, total_pages = get_paginated_movies(page)
    start_page = max(page - 3, 1)
    end_page = min(page + 4, total_pages + 1)

    return render_template(
        "index.html",
        movies=movies,
        total_pages=total_pages,
        current_page=page,
        start_page=start_page,
        end_page=end_page,
        movie=movie_details,
        similar_movies=similar_movies
    )


def find_similar_movies(movie_details):
    title = movie_details.get('title', '')
    genres = movie_details.get('genres_name', [])
    popularity = movie_details.get('popularity', 0)
    vote_average = movie_details.get('vote_average', 0)
    collections = movie_details.get('collections', [])

    query = {
        "query": {
            "bool": {
                "must_not": {
                    "match": {
                        "title.keyword": title  # Exclude the current movie by title
                    }
                },
                "should": [
                    {"terms": {"genres_name.keyword": genres}},
                    {"range": {"popularity": {"gte": popularity * 0.8, "lte": popularity * 1.2}}},
                    {"range": {"vote_average": {"gte": vote_average - 1, "lte": vote_average + 1}}},
                    {"terms": {"collections.keyword": collections}}
                ],
                "minimum_should_match": 2
            }
        }
    }

    result = client.search(index='moviedb_data', body=query)
    similar_movies = [movie['_source'] for movie in result['hits']['hits']]

    # Filter out duplicates by title
    similar_movies = [movie for movie in similar_movies if movie.get('title', '') != title]

    return similar_movies

if __name__ == '__main__':
    app.run(debug=True)