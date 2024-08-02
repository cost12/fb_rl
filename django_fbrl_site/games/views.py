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
    game = game_env.getManager(game_name)
    vals = [0,0,0,0,0,0,0]
    if game.env.possession() and 'DQN' in game.controller2.name:
            vals = game.controller2.model.get_q_vals(game.env.get_state()).tolist()
    elif not game.env.possession() and 'DQN' in game.controller1.name:
            vals = game.controller1.model.get_q_vals(game.env.get_state()).tolist()
    context = {
        "name":game.name,
        "team1": game.env.t1(),
        "team2":game.env.t2(),
        "score1":game.env.s1(),
        "score2":game.env.s2(),
        "q":game.env.q()+1,
        "time":game.env.time_str(),
        "down":game.env.down()+1,
        "dist":game.env.dist(),
        "yd":game.env.get_yd_str(),
        "fg":game.env.state.fg_dist(),
        "gain":game.env.gain(),
        "to1":game.env.to1(),
        "to2":game.env.to2(),
        "current_reward":game.get_current_reward(),
        "last_reward":game.get_last_reward(),
        "qstay":vals[0],
        "qleft":vals[1],
        "qright":vals[2],
        "qup":vals[3],
        "qdown":vals[4],
        "qkick":vals[5],
        "qpunt":vals[6]
    }
    return render(request, "games/play_game.html", context)