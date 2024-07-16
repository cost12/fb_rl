from django.shortcuts import render, redirect
from .forms import GameForm

# Data/ models initialized here
from . import game_vars
game_env = game_vars.game_env

# Create your views here.
def index(request):
    context = {"managers":game_env.managers}
    return render(request, "games/index.html", context)

def choose_teams(request):
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            controller1 = form.cleaned_data["controller1"]
            controller2 = form.cleaned_data["controller2"]
            game = game_env.getGameManager(
                game_env.getEnv(),
                game_env.getController(controller1),
                game_env.getController(controller2)
            )
            #context = {"game_name":game.name}
            return redirect('play_game', game_name=game.name)
    else:
        form = GameForm()
    context = {
        "controllers": game_env.controllers,
        "form" : form
    }
    return render(request, "games/choose_teams.html", context)

def play_game(request, game_name):
    context = {"game":game_env.getManager(game_name)}
    return render(request, "games/play_game.html", context)