import os
from enum import IntEnum

import requests

TMDB_RESOURCES = {
    'multi-search': '/search/multi',
    'tv-search': '/search/tv',
    'movie-search': '/search/movie',

    'tv-discover': '/discover/tv',
    'movie-discover': '/discover/movie',

    'movie-details': '/movie/%s',
    'movie-keywords': '/movie/%s/keywords',
    'list-movie-genres': '/genre/movie/list',

    'tv-details': '/tv/%s',
    'tv-keywords': '/tv/%s/keywords',
    'list-tv-genres': '/genre/tv/list',
}
TMDB_HOST = 'https://api.themoviedb.org/3'
TMDB_KEY_ENV = 'TMDB_API_KEY'


class TMDBAuthVersion(IntEnum):
    AUTH_V3 = 3
    AUTH_V4 = 4


class TMDB:
    configuration = {
        "base_url": "https://image.tmdb.org/t/p/",
        "backdrop_sizes": [
            "w300",
            "w780",
            "w1280",
            "original"
        ],
        "base_backdrop_url": "https://image.tmdb.org/t/p/original/",
        "poster_sizes": [
            "w92",
            "w154",
            "w185",
            "w342",
            "w500",
            "w780",
            "original"
        ],
        "base_poster_url": "https://image.tmdb.org/t/p/original/",
    }

    def __init__(self, api_key: str = None,
                 auth_version: TMDBAuthVersion = TMDBAuthVersion.AUTH_V4,
                 host: str = None,
                 resources: dict = None,
                 api_key_env: str = TMDB_KEY_ENV):
        # Fill defaults
        if host is None:
            host = TMDB_HOST
        if resources is None:
            resources = TMDB_RESOURCES
        if api_key is None:
            api_key = os.environ.get(api_key_env)

        # Validate
        if api_key is None:
            raise ValueError('Invalid TMDB API key')

        self._host = host
        self._api_key = api_key
        self._auth_version = auth_version
        self._resources = resources

    def _execute_request(self, resource_name, payload=None):
        url = f'{self._host}{self._resources[resource_name]}'
        headers = {}
        query_params = {'language': 'pt-BR', **payload}

        if self._auth_version is TMDBAuthVersion.AUTH_V4:
            headers['Authorization'] = f'Bearer {self._api_key}'
        else:
            query_params['api-key'] = self._api_key

        return requests.get(url, params=query_params, headers=headers, timeout=30)

    def search_tv(self, query, page=1):
        response = self._execute_request('tv-search', {'query': query, 'page': page})

        if response.status_code != 200:
            raise Exception('Failed to retrieve search results')

        return response.json()

    def search_movie(self, query, page=1):
        response = self._execute_request('movie-search', {'query': query, 'page': page})

        if response.status_code != 200:
            raise Exception('Failed to retrieve search results')

        return response.json()

    def discover_tv(self, page=1):
        response = self._execute_request('tv-discover', {'page': page})

        if response.status_code != 200:
            raise Exception('Failed to retrieve search results')

        return response.json()

    def discover_movie(self, page=1):
        response = self._execute_request('movie-discover', {'page': page})

        if response.status_code != 200:
            raise Exception('Failed to retrieve search results')

        return response.json()

    def search_multi(self, query, page=1):
        response = self._execute_request('multi-search', {'query': query, 'page': page})

        if response.status_code != 200:
            raise Exception('Failed to retrieve search results')

        return response.json()

    @staticmethod
    def _aggregate(response_tv, response_movie):
        merged_results = []

        for tv_title in response_tv.get('results', []):
            tv_title['media_type'] = 'tv'
            merged_results.append(tv_title)

        for movie_title in response_movie.get('results', []):
            movie_title['media_type'] = 'movie'
            merged_results.append(movie_title)

        aggregate = {
            'page': max(response_tv.get('page', 1), response_movie.get('page', 1)),
            'results': merged_results,
            'total_pages': max(response_tv.get('total_pages', 1),
                               response_movie.get('total_pages', 1)),
            'total_results': response_tv.get('total_results', 0) +
                             response_movie.get('total_results', 0),
        }

        return aggregate

    def search(self, query, page=1):
        response_tv = self.search_tv(query, page)
        response_movie = self.search_movie(query, page)

        return self._aggregate(response_tv, response_movie)

    def discover(self, page=1):
        response_tv = self.discover_tv(page)
        response_movie = self.discover_movie(page)

        return self._aggregate(response_tv, response_movie)
