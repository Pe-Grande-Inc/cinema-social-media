from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from core.models import Title, Post, User, PostRating, Comment
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
        'feed_url': reverse_lazy('feed'),
        'follow_url': reverse_lazy('follow'),
        'post_url': reverse_lazy('search'),
        'search_url': reverse_lazy('search'),
        'logout_url': reverse_lazy('logout'),
        **kwargs
    }


class BasePostView(generic.TemplateView):
    template_name = "post.html"

    def get(self, request, post_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        base_context = load_base_context(request,
                                         page_title='Post')

        try:
            post = Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            return redirect(reverse_lazy('feed'))

        return self.render_to_response({**base_context, 'post': post})


class LikePostView(BasePostView):
    def post(self, request, post_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        base_context = load_base_context(request,
                                         page_title='Post')

        # Target rating
        rating_positive = True
        if 'dislike' in request.POST and request.POST['dislike']:
            rating_positive = False

        try:
            post = Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            return redirect(reverse_lazy('feed'))

        # Try update rating, if it does not exist, create a new one
        try:
            rating = PostRating.objects.get(post=post, user=request.user)

            # Handle rating toggle
            if rating.positive != rating_positive:
                rating.positive = rating_positive
                rating.save()
            else:
                rating.delete()

        except PostRating.DoesNotExist:
            rating = PostRating.objects.create(post=post, user=request.user,
                                               positive=rating_positive)

        return self.render_to_response({**base_context, 'post': post})


class CommentPostView(BasePostView):
    def post(self, request, post_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        base_context = load_base_context(request,
                                         page_title='Post')

        try:
            post = Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            return redirect(reverse_lazy('feed'))

        if 'content' not in request.POST or not request.POST['content']:
            return self.render_to_response({**base_context, 'post': post, 'error': True,
                                            'error_msg': _('Comentário inválido')})

        comment = Comment.objects.create(author=request.user, post=post,
                                         content=request.POST['content'])

        return self.render_to_response({**base_context, 'post': post})


class FollowView(generic.TemplateView):
    template_name = "follow.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        base_context = load_base_context(request, active_tab='follow',
                                         page_title='Seguindo')

        # Check for users query, if there isn't get current following
        if 'query' in request.GET and request.GET['query']:
            users = User.objects.filter(username__search=request.GET['query']).exclude(
                id=request.user.id)
        else:
            users = request.user.following.all()

        return self.render_to_response(
            {**base_context, 'following': users})

    def post(self, request, user_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        base_context = load_base_context(request, active_tab='follow',
                                         page_title='Seguindo')

        try:
            target_user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return self.render_to_response(
                {**base_context, 'error': True,
                 'error_msg': _("Usuário não encontrado")})

        if 'remove' in request.POST:
            request.user.following.remove(target_user)
        else:
            request.user.following.add(target_user)

        return self.render_to_response(
            {**base_context, 'following': request.user.following.all()})


class FeedView(generic.TemplateView):
    template_name = "feed.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Common context for rendering
        base_context = load_base_context(request, page_title="Feed",
                                         active_tab="feed")

        # Query filters
        filters = {}

        # Author filtering
        if 'author' in request.GET and request.GET['author']:
            filters['author_id'] = request.GET['author']

        # Title filtering
        if 'title' in request.GET and request.GET['title']:
            filters['movie_id'] = request.GET['title']

        # If no other filters are defined, fallback to posts from followed users
        if len(filters.keys()) == 0:
            user_ids = [user.id for user in request.user.following.all().only('id')]
            user_ids.append(request.user.id)
            filters['author_id__in'] = user_ids

        # Load page for pagination
        page = 1
        if 'page' in request.GET and request.GET['page']:
            try:
                page = int(request.GET['page'])
            except ValueError:
                pass

        # Load posts for given filters
        posts = Post.objects.filter(**filters).order_by('creation_date')

        # Paginate response
        paginator = Paginator(posts, 20)
        page = paginator.get_page(page)

        # Pagination references
        next_page_url = None
        if page.has_next():
            next_page_url = f'{request.path}?page={page + 1}'
            if filters['author_id']:
                next_page_url += f'&author={filters["author_id"]}'
            if filters['movie_id']:
                next_page_url += f'&title={filters["movie_id"]}'

        previous_page_url = None
        if page.has_previous():
            previous_page_url = f'{request.path}?page={page - 1}'
            if filters['author_id']:
                previous_page_url += f'&author={filters["author_id"]}'
            if filters['movie_id']:
                previous_page_url += f'&title={filters["movie_id"]}'

        return self.render_to_response(
            {**base_context, 'posts_page': page, 'next_page_url': next_page_url,
             'previous_page_url': previous_page_url})


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
