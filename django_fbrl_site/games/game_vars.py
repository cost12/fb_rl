import sys
sys.path.append('../fb_rl')

import fbrl_code.retro_env as retro_env
import fbrl_code.fb_controller as fb_controller
import fbrl_code.rl_models as rl_models

class GameEnvironment():

    def __init__(self):
        learner1 = rl_models.DQN((1,3,10),7)
        learner2 = rl_models.DQN((1,3,10),7)
        learn_controller1 = fb_controller.FbLearningController(learner1,"DQN 1")
        learn_controller2 = fb_controller.FbLearningController(learner2,"DQN 2")
        self.controllers = {
            "User":fb_controller.FbKeyboardControllerDjango("User"),
            "DQN 1": learn_controller1,
            "DQN 2": learn_controller2
        }

        self.managers = {}

    def getEnv(self):
        return retro_env.FootballEnv()

    def getGameManager(self, env, controller1, controller2, name=None) -> fb_controller.GameManager:
        manager = fb_controller.GameManager(env, controller1, controller2, name)
        self.managers[manager.name] = manager
        return manager
    
    def getControllers(self) -> list[fb_controller.FbController]:
        return self.controllers.values()
    
    def getController(self, name) -> fb_controller.FbController:
        return self.controllers[name]
    
    def getManagers(self) -> list[fb_controller.GameManager]:
        return self.managers.values()
    
    def getManager(self, name) -> fb_controller.FbController:
        return self.managers[name]
    

game_env = GameEnvironment()