import requests
from bs4 import BeautifulSoup
import os


url_list = {}
api_key = os.getenv("TOKEN")


def search_movies(query):
    movies_list = []
    movies_details = {}
    website = BeautifulSoup(requests.get(f"https://mkvcinemas.skin/?s={query.replace(' ', '+')}").text, "html.parser")
    movies = website.find_all("a", {'class': 'ml-mask jt'})
    for movie in movies:
        if movie:
            movies_details["id"] = f"link{movies.index(movie)}"
            movies_details["title"] = movie.find("span", {'class': 'mli-info'}).text
            url_list[movies_details["id"]] = movie['href']
        movies_list.append(movies_details)
        movies_details = {}
    return movies_list

def get_movie(query):
    movie_details = {}
    file_path = f"{query}.txt"  # Assuming each movie has a separate text file with its details

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            movie_details["title"] = lines[0].strip()
            movie_details["img"] = lines[1].strip()
            links = {}
            for line in lines[2:]:
                parts = line.split(':')
                links[parts[0].strip()] = parts[1].strip()
            movie_details["links"] = links
    except FileNotFoundError:
        print(f"Movie details not found for: {query}")

    return movie_details

# Example usage
movie_data = get_movie("movie_name")
print(movie_data)


'''
def get_movie(query):
    movie_details = {}
    movie_page_link = BeautifulSoup(requests.get(f"{url_list[query]}").text, "html.parser")
    if movie_page_link:
        title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
        movie_details["title"] = title
        img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg']
        movie_details["img"] = img
        links = movie_page_link.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
        final_links = {}
        for i in links:
            url = f"https://urlshortx.com/api?api={api_key}&url={i['href']}"
            response = requests.get(url)
            link = response.json()
            final_links[f"{i.text}"] = link['shortenedUrl']
        movie_details["links"] = final_links
    return movie_details

'''