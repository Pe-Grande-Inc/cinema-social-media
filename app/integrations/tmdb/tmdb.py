import os
from enum import IntEnum

import requests

TMDB_RESOURCES = {
    'multi-search': '/search/multi',

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

    def search(self, query, page=1):
        response = self._execute_request('multi-search', {'query': query, 'page': page})

        if response.status_code != 200:
            raise Exception('Failed to retrieve search results')

        return response.json()
