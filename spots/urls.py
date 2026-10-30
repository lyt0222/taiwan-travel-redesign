from django.urls import path

from . import views

app_name = "spots"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("spots/", views.results, name="results"),
    path("spots/<int:pk>/", views.detail, name="detail"),
    path("spots/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("my-trip/", views.my_trip, name="my_trip"),
    path("my-trip/<int:pk>/", views.update_favorite, name="update_favorite"),
    path("api/towns/", views.towns_api, name="towns_api"),
]
