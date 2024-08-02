import tkinter as tk
import random

import fbrl_code.retro_env as retro_env

class FbController:
    i = 0

    def __init__(self, name=None):
        if name is None:
            self.name = str(self.i)
            self.i += 1
        else:
            self.name = name
        self.send = False

    def on(self) -> None:
        self.send = True

    def off(self) -> None:
        self.send = False

    def select_action(self, state, actions,eps):
        pass

    def sarsa(self, s1, action, s2, reward, done):
        pass

class GameManager:
    i = 0

    def __init__(self, env:retro_env.FootballEnv, c1:FbController, c2:FbController, name=None):
        self.env = env
        self.controller1 = c1
        self.controller2 = c2
        self.current_reward = 0
        self.last_reward = 0
        if name is None:
            self.name = str(self.i)
            self.i += 1
        else:
            self.name = name

    def reset(self):
        self.env.reset(total_reset=True)

    def on(self):
        self.controller1.on()
        self.controller2.on()

    def off(self):
        self.controller1.off()
        self.controller2.off()

    def get_current_reward(self):
        return self.current_reward
    
    def get_last_reward(self):
        return self.last_reward

    def advance_play(self,eps=0) -> int:
        if self.env.is_over():
            return
        s1 = self.env.get_state()
        poss = self.env.possession()
        if poss:
            self.controller1.off()
            self.controller2.on()
            action = self.controller2.select_action(s1, self.env.get_actions(),eps)
        else:
            self.controller1.on()
            self.controller2.off()
            action = self.controller1.select_action(s1, self.env.get_actions(),eps)
        if action is None:
            #print("no action")
            return # Why would this happen? Ans: user hasn't input move yet
        s2, r, done = self.env.step(action)

        if done:
            self.last_reward = self.current_reward + r
            self.current_reward = 0
        else:
            self.current_reward += r
        
        # sarsa isn't implemented yet
        if poss:
            self.controller2.sarsa(s1,action,s2,r,done)
        else:
            self.controller1.sarsa(s1,action,s2,r,done)
        return s2, r, done, self.env.possession(), action

class FbRandomController(FbController):

    def __init__(self, name=None):
        super().__init__(name)

    def select_action(self, state, actions:list[int],eps):
        if retro_env.FootballEnv.PUNT in actions:
            actions.remove(retro_env.FootballEnv.PUNT)
        return random.choice(actions)
    
class FbKeyboardControllerDjango(FbController):
    def __init__(self, name=None):
        super().__init__(name)
        self.moves = []

    def select_action(self, state, actions,eps):
        if len(self.moves) > 0:
            move = self.moves.pop(0)
            while len(self.moves) > 0 and not (move in actions):
                move = self.moves.pop(0)
            return move
        
    def off(self) -> None:
        super().off()
        self.moves = []

    def key_press(self, key):
        if not self.send:
            return
        if key == 'space':
            action = retro_env.FootballEnv.NO_MOVE
        elif key == 'Left':
            action = retro_env.FootballEnv.LEFT
        elif key == 'Right':
            action = retro_env.FootballEnv.RIGHT
        elif key == 'Up':
            action = retro_env.FootballEnv.UP
        elif key == 'Down':
            action = retro_env.FootballEnv.DOWN
        elif 0 and key == 'r':
            action = retro_env.FootballEnv.RESET
        elif key == 'k':
            action = retro_env.FootballEnv.KICK
        elif key == 'p':
            action = retro_env.FootballEnv.PUNT
        else:
            return
        self.moves.append(action)

class FbKeyboardControllerTk(FbController):
    """
    Keyboard controller for retro_env
    Calls actions based on user input to the keyboard
    """

    def __init__(self, name=None, root=None):
        super().__init__(name)
        root.bind('<KeyPress>', self.key_press)
        self.moves = []

    def select_action(self, state, actions,eps):
        if len(self.moves) > 0:
            move = self.moves.pop(0)
            while len(self.moves) > 0 and not (move in actions):
                move = self.moves.pop(0)
            return move
        
    def off(self) -> None:
        super().off()
        self.moves = []

    def key_press(self, event:tk.Event):
        if not self.send:
            return
        if event.keysym == 'space':
            action = retro_env.FootballEnv.NO_MOVE
        elif event.keysym == 'Left':
            action = retro_env.FootballEnv.LEFT
        elif event.keysym == 'Right':
            action = retro_env.FootballEnv.RIGHT
        elif event.keysym == 'Up':
            action = retro_env.FootballEnv.UP
        elif event.keysym == 'Down':
            action = retro_env.FootballEnv.DOWN
        elif 0 and event.keysym == 'r':
            action = retro_env.FootballEnv.RESET
        elif event.keysym == 'k':
            action = retro_env.FootballEnv.KICK
        elif event.keysym == 'p':
            action = retro_env.FootballEnv.PUNT
        else:
            if 1:
                print(event.keysym)
                print(type(event.keysym))
            return
        self.moves.append(action)

class FbLearningController(FbController):
    
    def __init__(self, rl_model, name=None):
        super().__init__(name)
        self.train = True
        self.model = rl_model

    def select_action(self, state, actions,eps):
        return self.model.select_action(state, actions,eps)
    
    def sarsa(self, s1, action, s2, reward, done):
        pass