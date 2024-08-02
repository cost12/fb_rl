import tkinter as tk
from tkinter import ttk

import sys
sys.path.append('../fb_rl')

import fbrl_code.retro_env as retro_env
import fbrl_code.fb_controller as fb_controller
import tk_fbrl_site.display_game as display_game
import fbrl_code.rl_models as rl_models

def build_home(root:tk.Tk) -> display_game.View:
    home = display_game.View(root, borderwidth=2, relief='groove')
    ttk.Label(home, text="Welcome Home, use the buttons to navigate").grid(row=0,column=0,sticky='news')
    return home

def football_vis(env:retro_env.FootballEnv, controller1, controller2) -> None:
    root = tk.Tk()
    view = display_game.MainFrame(root)
    home = build_home(view)
    #controller1 = fb_controller.FbKeyboardController(root)
    #controller2 = fb_controller.FbKeyboardController(root)
    game_manager = fb_controller.GameManager(env,controller1,controller2)
    user1 = fb_controller.FbKeyboardControllerTk("User1", root)
    #user2 = fb_controller.FbKeyboardControllerTk("User2", root)
    rando1 = fb_controller.FbRandomController("Random1")
    rando2 = fb_controller.FbRandomController("Random2")
    controllers = [user1, controller1, controller2, rando1, rando2]
    frames = dict[str,display_game.View]( \
                {
                    "Game Setup" : display_game.GameSetFrame(view, controllers),
                    "Game" :     display_game.GameFrame(view, game_manager),
                    "Training":  display_game.TrainingFrame(view,retro_env.FootballEnv(),controller1.model,controller2.model),
                    "Home" :     home
                    #"Settings" : SettingsFrame(root) \
                } \
            )
    access = dict[str,list[str]]( \
                {
                    "Game Setup" : ["Home"],
                    "Game" :    ["Home"],
                    "Training": ["Home"],
                    "Home" :    ["Training","Game Setup"]
                } \
            )
    start = "Home"
    view.set_frames_and_access(frames, access, start)
    view.pack()
    #view.change_view("Game")
    view.change_view(start)
    root.after(100,view.main_loop)
    root.mainloop()

def main():
    env = retro_env.FootballEnv()
    learner1 = rl_models.DQN((1,3,10),7)
    learner2 = rl_models.DQN((1,3,10),7)
    #rl_models.learning_loop(env, learner1, learner2,100000)
    learn_controller1 = fb_controller.FbLearningController(learner1,"DQN1")
    learn_controller2 = fb_controller.FbLearningController(learner2,"DQN2")
    #env.reset(total_reset=True)
    football_vis(env,learn_controller1,learn_controller2)
    

if __name__=="__main__":
    main()