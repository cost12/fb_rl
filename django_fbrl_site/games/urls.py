from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.choose_teams, name="create"),
    path("play_game/<str:game_name>/", views.play_game, name="play_game")
]