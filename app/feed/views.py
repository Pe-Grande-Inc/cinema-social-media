from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from core.models import Title, Post
from integrations.tmdb import TMDB
from user.views import login_redirect

tmdb = TMDB()


def load_base_context(request: HttpRequest, active_tab=None, page_title=None, **kwargs):
    return {
        'active_tab': active_tab,
        'page_title': page_title,
        'username': request.user.username,
        'user_fullname': request.user.get_full_name(),
        "user_avatar_url": request.user.avatar_url,
        # 'feed_url': reverse_lazy('feed'),
        # 'follow_url': reverse_lazy('follow'),
        'post_url': reverse_lazy('search'),
        'search_url': reverse_lazy('search'),
        'logout_url': reverse_lazy('logout'),
        **kwargs
    }


class CreatePostView(generic.TemplateView):
    template_name = 'new_post.html'

    def get(self, request: HttpRequest, title_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Go to search page if title is missing
        if title_id is None:
            return redirect(reverse_lazy('search'))

        base_context = load_base_context(request, page_title="Novo post",
                                         active_tab="post")

        try:
            title = Title.objects.get(id=title_id)
            return self.render_to_response({**base_context, 'title': title})

        except (ValidationError, Title.DoesNotExist) as ex:
            print(repr(ex))
            return redirect(reverse_lazy('search'))

    def post(self, request, title_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Go to search page if title is missing
        if title_id is None:
            return redirect(reverse_lazy('search'))

        base_context = load_base_context(request, page_title="Novo post",
                                         active_tab="post")

        try:
            title = Title.objects.get(id=title_id)
        except (ValidationError, Title.DoesNotExist) as ex:
            print(repr(ex))
            return redirect(reverse_lazy('search'))

        try:
            if 'content' not in request.POST or not request.POST['content'].strip():
                raise ValidationError("Post vazio")

            post = Post.objects.create(
                author=self.request.user,
                movie=title,
                content=request.POST['content'].strip()
            )

            return redirect(reverse_lazy('search') + "?query=ok")
        except ValidationError as ex:
            return self.render_to_response(
                {**base_context, 'title': title, 'error': True,
                 'error_msg': ex.message}, status=400)


class SearchMoviesView(generic.TemplateView):
    template_name = 'search.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        base_context = load_base_context(request, page_title="Busca",
                                         active_tab='search')

        # Try loading movies for the given query
        try:
            query = request.GET['query'] if 'query' in request.GET else None
            page = int(str(request.GET['page'])) if 'page' in request.GET else 1

            if query:
                # If query is present show search results
                search_response = tmdb.search(query, page=page)
            else:
                # If query is not present, show popular movies/tv shows
                search_response = tmdb.discover(page=page)

            next_page_url = None
            if search_response.get('total_pages', 1) > page:
                next_page_url = f'{request.path}?page={page + 1}'
                if query:
                    next_page_url += f'&query={query}'

            previous_page_url = None
            if page != 1:
                previous_page_url = f'{request.path}?page={page - 1}'
                if query:
                    previous_page_url += f'&query={query}'

            titles = list(Title.objects.load_from_tmdb(search_response['results']))
            titles.sort(key=lambda x: -x.popularity)

            return self.render_to_response(
                {**base_context, 'titles': titles, 'next_page_url': next_page_url,
                 'previous_page_url': previous_page_url, 'query': query})

        except ValueError as ex:
            print(repr(ex))
            context = {
                **base_context,
                'error': True
            }
            return self.render_to_response(context, status=400)

        pass
