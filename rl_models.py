import numpy as np
import nn_models
import torch
import copy
import torch.optim as optim
import torch.nn.functional as F

from utils import ReplayBuffer
import fb_controller

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class DQN:

    def __init__(self, input_dim, output_dim):
        seed = 100
        torch.manual_seed(seed)
        np.random.seed(seed)

        # Hyperparameters
        self.batch_size = 128 #64
        self.buffer_size = 1e6 # 1e6
        self.learning_rate = 3e-4
        self.eps = 0.9
        self.eps_dec = 0.0001
        self.eps_min = 0.01
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.num_hidden_layers = 3 # 2
        self.num_neurons_per_layer = 128 # 256
        self.discount = 0.99
        self.warmup_steps = 1e5
        self.target_update_freq = 60 # 50
        self.tau = 0.005 # ? 
        self.eval_freq = 5000000000 # 100
        self.train_freq = 20
        self.alpha = 1
        self.weight_decay = 0.0001
        self.dropout = 0.5

        self.replay_buffer = ReplayBuffer(self.input_dim, self.batch_size,self.buffer_size, device)
        #self.policy = nn_models.SimpleNN(self.input_dim,self.output_dim,self.num_hidden_layers,self.num_neurons_per_layer).to(device)
        self.policy = nn_models.ComplexNN(self.input_dim, self.output_dim, self.num_hidden_layers, self.num_neurons_per_layer, self.dropout).to(device)
        self.target_policy = copy.deepcopy(self.policy)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay)

    def select_action(self, state, actions, eps=0):
        if np.random.random() < eps:
            return np.random.choice(actions)
        with torch.no_grad():
            vals = self.policy(torch.tensor(state,dtype=torch.float32))[0]
        max_as = torch.topk(vals,len(vals)).indices
        i = 0
        while not (max_as[i] in actions):
            i += 1
        return max_as[i].item()
    
    def train_policy(self):
        if self.replay_buffer.size <= 0:
            return
        state, action, next_state, reward, not_done = self.replay_buffer.sample()
        self.policy.train()
        #for s,a,s2,r,d in zip(state,action,next_state,reward,done):
        self.optimizer.zero_grad()
        q_vals = self.policy(state)
        with torch.no_grad():
            next_q_vals = self.target_policy(next_state)
        max_q = torch.max(next_q_vals,1).values.view(q_vals.shape[0],1)
        target = q_vals.detach().clone()
        not_done = not_done.bool()
        change = torch.where(not_done,self.alpha*(reward + self.discount*max_q),reward)
        for i in range(target.shape[0]):
            target[i,action[i]] = change[i]
        if 0:
            if done:
                target[action] = reward
            else:
                target[action] = self.alpha*(reward + self.discount*max_q)
        loss = F.mse_loss(q_vals, target)
        loss.backward()
        self.optimizer.step()

def eval_policies(model1, model2, env, num_steps=1000, num_episodes=10):
    game_manager = fb_controller.GameManager(env, fb_controller.FbLearningController(model1),fb_controller.FbLearningController(model2))
    #env.reset(total_reset=True)
    #observation = env.get_state()
    total_reward1 = 0
    total_reward2 = 0
    for ep in range(num_episodes):
        for step in range(num_steps):
            poss = env.possession()
            _, reward, done, possession, _ = game_manager.advance_play()
            if poss:
                total_reward2 += reward
            else:
                total_reward1 += reward
            if done:
                game_manager.reset()
                break
    print(f"Average reward 1 over {num_episodes} episodes: {total_reward1/num_episodes}")
    print(f"Average reward 2 over {num_episodes} episodes: {total_reward2/num_episodes}")
    return total_reward1/num_episodes,total_reward2/num_episodes

def learning_loop(env, model1:DQN, model2:DQN, steps=100000, start=0):
    game_manager = fb_controller.GameManager(env, fb_controller.FbLearningController(model1),fb_controller.FbLearningController(model2))
    num_steps = steps
    observation = env.get_state()
    episode_num = 1
    total_reward1 = 0
    total_reward2 = 0

    turnover_group = None

    for t in range(start,start+num_steps):
        possession = env.possession()
        if t < model1.warmup_steps:
            next_observation, reward, done, poss, action = game_manager.advance_play(1)
        else:
            if possession:
                next_observation, reward, done, poss, action = game_manager.advance_play(model2.eps)
            else:
                next_observation, reward, done, poss, action = game_manager.advance_play(model1.eps)
            model1.eps = model1.eps-model1.eps_dec
            if model1.eps < model1.eps_min:
                model1.eps = model1.eps_min
            model2.eps = model2.eps-model2.eps_dec
            if model2.eps < model2.eps_min:
                model2.eps = model2.eps_min
        if turnover_group is not None:
            turnover_group[3] -= reward
        if poss == possession:
            if possession:
                model2.replay_buffer.add(observation, action, next_observation, reward, done)
                total_reward2 += reward
            else:
                model1.replay_buffer.add(observation, action, next_observation, reward, done)
                total_reward1 += reward
        if (not (poss == possession)) or done:
            if turnover_group is not None:
                if not possession:
                    model2.replay_buffer.add(*turnover_group)
                    total_reward2 += turnover_group[3]
                else:
                    model1.replay_buffer.add(*turnover_group)
                    total_reward1 += turnover_group[3]
            turnover_group = [observation, action, next_observation, reward, done]

        observation = copy.copy(next_observation)
        if t % model1.train_freq == 0 and t > 0:
            model1.train_policy()
            model1.policy.eval()
        if t % model2.train_freq == 0 and t > 0:
            model2.train_policy()
            model2.policy.eval()
        if t % model1.eval_freq == 0 and t > 0:
            eval_policies(model1, model2, env,1000,100)
        if t % model1.target_update_freq == 0 and t > 0:
            for param, target_param in zip(model1.policy.parameters(), model1.target_policy.parameters()):
                target_param.data.copy_(param.data)
        if t % model2.target_update_freq == 0 and t > 0:
            for param, target_param in zip(model2.policy.parameters(), model2.target_policy.parameters()):
                target_param.data.copy_(param.data)

        #if t%1000 == 0:
            #print(t)
        if done:
            print(f"Time Steps: {t}, Episode: {episode_num}, Reward 1: {total_reward1}")
            print(f"Time Steps: {t}, Episode: {episode_num}, Reward 2: {total_reward2}")
            game_manager.reset()
            observation = env.get_state()
            total_reward1 = 0
            total_reward2 = 0
            episode_num += 1