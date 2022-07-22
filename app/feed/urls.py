from django.urls import path
from .views import SearchMoviesView, CreatePostView, FeedView, FollowView

urlpatterns = [
    path('search/', SearchMoviesView.as_view(), name="search"),
    path('new-post/', CreatePostView.as_view(), name="new-post-no-param"),
    path('new-post/<str:title_id>/', CreatePostView.as_view(), name="new-post"),
    path('feed/', FeedView.as_view(), name="feed"),
    path('follow/', FollowView.as_view(), name="follow"),
    path('follow/<str:user_id>/', FollowView.as_view(), name="follow-user"),
]
