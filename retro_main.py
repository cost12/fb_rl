import random
import time
import tkinter as tk
from tkinter import ttk

import retro_env
import fb_controller
import display_game
import rl_models

def build_home(root:tk.Tk) -> display_game.View:
    home = display_game.View(root, borderwidth=2, relief='groove')
    ttk.Label(home, text="Welcome Home, use the buttons to navigate").grid(row=0,column=0,sticky='news')
    return home

def football_vis(env:retro_env.FootballEnv, controller1, controller2) -> None:
    root = tk.Tk()
    home = build_home(root)
    #controller1 = fb_controller.FbKeyboardController(root)
    #controller2 = fb_controller.FbKeyboardController(root)
    game_manager = fb_controller.GameManager(env,controller1,controller2)
    frames = dict[str,display_game.View]( \
                {
                    "Game" :     display_game.GameFrame(root, game_manager),
                    "Training":  display_game.TrainingFrame(root,retro_env.FootballEnv(),controller1.model,controller2.model),
                    "Home" :     home
                    #"Settings" : SettingsFrame(root) \
                } \
            )
    access = dict[str,list[str]]( \
                {
                    "Game" :    ["Home"],
                    "Training": ["Home"],
                    "Home" :    ["Game","Training"]
                } \
            )
    start = "Home"
    view = display_game.MainFrame(root, frames, access, start)
    view.pack()
    view.change_view("Game")
    view.change_view(start)
    root.after(100,view.main_loop)
    root.mainloop()

def main():
    env = retro_env.FootballEnv()
    learner1 = rl_models.DQN(23,7)
    learner2 = rl_models.DQN(23,7)
    #rl_models.learning_loop(env, learner1, learner2,100000)
    learn_controller1 = fb_controller.FbLearningController(learner1)
    learn_controller2 = fb_controller.FbLearningController(learner2)
    #env.reset(total_reset=True)
    football_vis(env,learn_controller1,learn_controller2)
    

if __name__=="__main__":
    main()