from django.urls import path
from .views import SearchMoviesView, CreatePostView

urlpatterns = [
    path('search/', SearchMoviesView.as_view(), name="search"),
    path('new-post/', CreatePostView.as_view(), name="new-post-no-param"),
    path('new-post/<str:title_id>/', CreatePostView.as_view(), name="new-post"),
]
