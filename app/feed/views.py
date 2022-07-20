from django.shortcuts import render, redirect

from django.http import HttpResponse, HttpRequest
from django.views import generic
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

from core.models import Title
from integrations.tmdb import TMDB
from user.views import login_redirect

tmdb = TMDB()


def load_base_context(request: HttpRequest, active_tab=None, page_title=None, **kwargs):
    return {
        'active_tab': active_tab,
        'page_title': page_title,
        'username': request.user.username,
        'user_fullname': request.user.get_full_name(),
        # 'feed_url': reverse_lazy('feed'),
        # 'follow_url': reverse_lazy('follow'),
        # 'post_url': reverse_lazy('post'),
        'logout_url': reverse_lazy('logout'),
        **kwargs
    }


class SearchMoviesView(generic.TemplateView):
    template_name = 'search.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        base_context = load_base_context(request, page_title="Busca")

        # No search query (may show popular movies here by defaul)
        if 'query' not in request.GET:
            return self.render_to_response({**base_context, 'titles': []})

        # Try loading movies for the given query
        try:
            query = request.GET['query']
            page = int(str(request.GET['page'])) if 'page' in request.GET else 1
            search_response = tmdb.search(query, page=page)
            titles = list(Title.objects.load_from_tmdb(search_response['results']))
            titles.sort(key=lambda x: -x.vote_average)
            return self.render_to_response({**base_context, 'titles': titles})

        except ValueError as ex:
            print(ex)
            context = {
                **base_context,
                'error': True
            }
            return self.render_to_response(context, status=400)

        pass
