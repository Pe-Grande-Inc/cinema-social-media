from django.urls import path
from .views import SearchMoviesView

urlpatterns = [
    path('search/', SearchMoviesView.as_view(), name="search"),
]
