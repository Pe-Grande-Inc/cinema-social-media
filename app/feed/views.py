from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.http import HttpRequest
from django.views import generic

from core.models import Title, Post, User, PostRating, Comment
from user.views import login_redirect

from integrations.tmdb import TMDB

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
    """
    Base post details view, used for visualizing a post details and as a base for other
    operations like comment and liking
    """
    template_name = "post.html"

    def get(self, request, post_id=None, *args, **kwargs):
        # Check for user authentication
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Load base context
        base_context = load_base_context(request,
                                         page_title='Post')

        # Try loading post
        try:
            post = Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            # If post was not found, redirect to feed
            return redirect(reverse_lazy('feed'))

        # Render post screen
        return self.render_to_response({**base_context, 'post': post})


class LikePostView(BasePostView):
    """
    Handle like/dislike on posts
    """

    def post(self, request, post_id=None, *args, **kwargs):
        # Check for user authentication
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Load base context
        base_context = load_base_context(request,
                                         page_title='Post')

        # Target rating
        rating_positive = True
        if 'dislike' in request.POST and request.POST['dislike']:
            rating_positive = False

        # Try loading target post
        try:
            post = Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            # If post was not found, return to feed
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
            # If it's the user's first rating, create it
            rating = PostRating.objects.create(post=post, user=request.user,
                                               positive=rating_positive)

        # Render post screen
        return self.render_to_response({**base_context, 'post': post})


class CommentPostView(BasePostView):
    """
    Create comment view
    """

    def post(self, request, post_id=None, *args, **kwargs):
        # Check for user authentication
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Load base context
        base_context = load_base_context(request,
                                         page_title='Post')

        # Load target post
        try:
            post = Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            # If post does not exist, return to feed
            return redirect(reverse_lazy('feed'))

        # If content is absent, render error screen
        if 'content' not in request.POST or not request.POST['content']:
            return self.render_to_response({**base_context, 'post': post, 'error': True,
                                            'error_msg': _('Comentário inválido')})

        # Create comment
        comment = Comment.objects.create(author=request.user, post=post,
                                         content=request.POST['content'])

        # Render post screen
        return self.render_to_response({**base_context, 'post': post})


class FollowView(generic.TemplateView):
    """
    Handle following visualization and follow/unfollow
    """
    template_name = "follow.html"

    def get(self, request, *args, **kwargs):
        # Check for user authentication
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Load context
        base_context = load_base_context(request, active_tab='follow',
                                         page_title='Seguindo')

        # Check for users query, if there isn't get current following
        if 'query' in request.GET and request.GET['query']:
            users = User.objects.filter(username__search=request.GET['query']).exclude(
                id=request.user.id)
        else:
            users = request.user.following.all()

        # Render response
        return self.render_to_response(
            {**base_context, 'following': users})

    def post(self, request, user_id=None, *args, **kwargs):
        # Check for user authentication
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Load context
        base_context = load_base_context(request, active_tab='follow',
                                         page_title='Seguindo')

        # Try loading target user
        try:
            target_user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            # If user does not exist return error
            return self.render_to_response(
                {**base_context, 'error': True,
                 'error_msg': _("Usuário não encontrado")})

        # Handle follow/unfollow
        if 'remove' in request.POST:
            request.user.following.remove(target_user)
        else:
            request.user.following.add(target_user)

        # Return response
        return self.render_to_response(
            {**base_context, 'following': request.user.following.all()})


class FeedView(generic.TemplateView):
    """
    Feed view
    """
    template_name = "feed.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        # Check for user authentication
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
                # noinspection PyTypeChecker
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

        # Render response
        return self.render_to_response(
            {**base_context, 'posts_page': page, 'next_page_url': next_page_url,
             'previous_page_url': previous_page_url})


class CreatePostView(generic.TemplateView):
    """
    Post creation screen and handling
    """
    template_name = 'new_post.html'

    def get(self, request: HttpRequest, title_id=None, *args, **kwargs):
        # Check for user authentication
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Go to search page if title is missing
        if title_id is None:
            return redirect(reverse_lazy('search'))

        # Load base context
        base_context = load_base_context(request, page_title="Novo post",
                                         active_tab="post")

        # Try retrieving title
        try:
            title = Title.objects.get(id=title_id)
            return self.render_to_response({**base_context, 'title': title})
        except (ValidationError, Title.DoesNotExist) as ex:
            # Redirect to search on errors
            print(repr(ex))
            return redirect(reverse_lazy('search'))

    def post(self, request, title_id=None, *args, **kwargs):
        # Check for user authentication
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Go to search page if title is missing
        if title_id is None:
            return redirect(reverse_lazy('search'))

        # Load base context
        base_context = load_base_context(request, page_title="Novo post",
                                         active_tab="post")
        # Try loading title
        try:
            title = Title.objects.get(id=title_id)
        except (ValidationError, Title.DoesNotExist) as ex:
            # Redirect to search on error
            print(repr(ex))
            return redirect(reverse_lazy('search'))

        try:
            # Try loading content from request data
            if 'content' not in request.POST or not request.POST['content'].strip():
                raise ValidationError("Post vazio")

            # Create new post
            post = Post.objects.create(
                author=self.request.user,
                movie=title,
                content=request.POST['content'].strip()
            )

            # Redirect to feed
            return redirect(reverse_lazy('feed'))
        except (ValidationError, IntegrityError) as ex:
            # Return to post creation screen on error
            return self.render_to_response(
                {**base_context, 'title': title, 'error': True,
                 'error_msg': ex.message}, status=400)


class SearchMoviesView(generic.TemplateView):
    """
    Search for movies/tv shows view
    """
    template_name = 'search.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        # Check for user authentication
        if not request.user.is_authenticated:
            return login_redirect(unauthorized=True)

        # Load default context
        base_context = load_base_context(request, page_title="Busca",
                                         active_tab='search')

        # Try loading movies for the given query
        try:
            query = request.GET['query'] if 'query' in request.GET else None
            page = int(str(request.GET['page'])) if 'page' in request.GET else 1

            # Load movies
            if query:
                # If query is present show search results
                search_response = tmdb.search(query, page=page)
            else:
                # If query is not present, show popular movies/tv shows
                search_response = tmdb.discover(page=page)

            # Create pagination URLs
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

            # Sort titles by popularity
            titles = list(Title.objects.load_from_tmdb(search_response['results']))
            titles.sort(key=lambda x: -x.popularity)

            # Render
            return self.render_to_response(
                {**base_context, 'titles': titles, 'next_page_url': next_page_url,
                 'previous_page_url': previous_page_url, 'query': query})
        except ValueError as ex:
            # Log error
            print(repr(ex))
            context = {
                **base_context,
                'error': True
            }
            # Render response error
            return self.render_to_response(context, status=400)
