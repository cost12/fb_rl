from django import forms

# Data/ models initialized here
from . import game_vars
game_env = game_vars.game_env

class GameForm(forms.Form):
    CHOICES = []
    for controller in game_env.getControllers():
        CHOICES.append((controller.name,controller.name))
    controller1 = forms.ChoiceField(label="Choose team 1", choices=CHOICES)
    controller2 = forms.ChoiceField(label="Choose team 2", choices=CHOICES)
