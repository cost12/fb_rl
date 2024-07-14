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
        self.eps_dec = 0.00005
        self.eps_min = 0.1
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.num_hidden_layers = 1 # 2
        self.num_neurons_per_layer = 16 # 256
        self.discount = 0.99
        self.warmup_steps = 1e5
        self.target_update_freq = 50 # 50
        self.tau = 0.005 # ? 
        self.eval_freq = 5000000000 # 100
        self.train_freq = 20
        self.alpha = 1
        self.weight_decay = 0.001
        self.dropout = 0.5
        self.num_cvn_layers = 2
        self.num_filters = 2
        self.kernel_size=(2,2)
        self.num_add=11
        self.hybrid=True

        self.replay_buffer = ReplayBuffer(self.input_dim, self.batch_size,self.buffer_size, device, more_state_dim=self.num_add)
        #self.policy = nn_models.SimpleNN(self.input_dim,self.output_dim,self.num_hidden_layers,self.num_neurons_per_layer).to(device)
        #self.policy = nn_models.ComplexNN(self.input_dim, self.output_dim, self.num_hidden_layers, self.num_neurons_per_layer, self.dropout).to(device)
        #self.policy = nn_models.CNN(self.input_dim, self.output_dim, self.num_cvn_layers, self.num_filters, self.num_hidden_layers, self.num_neurons_per_layer, self.dropout,kernel_size=self.kernel_size).to(device)
        self.policy = nn_models.HybridNN(self.input_dim, self.output_dim, self.num_add, self.num_cvn_layers, self.num_filters, self.num_hidden_layers, self.num_neurons_per_layer, self.dropout,kernel_size=self.kernel_size).to(device)
        self.target_policy = copy.deepcopy(self.policy)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay)

    def select_action(self, state, actions, eps=0):
        if np.random.random() < eps:
            return np.random.choice(actions)
        vals = self.get_q_vals(state)
        max_as = torch.topk(vals,len(vals)).indices
        i = 0
        while not (max_as[i] in actions):
            i += 1
        return max_as[i].item()
    
    def get_q_vals(self,state):
        self.policy.eval()
        with torch.no_grad():
            if self.hybrid:
                torch_board = torch.tensor([state[0]], dtype=torch.float32)
                torch_state = torch.tensor([state[1]], dtype=torch.float32)
                vals = self.policy(torch_board, torch_state)[0]
            else:
                torch_state=torch.tensor([state[0]],dtype=torch.float32)
                vals = self.policy(torch_state)[0]
            return vals
    
    def train_policy(self):
        if self.replay_buffer.size <= 0:
            return
        if self.hybrid:
            state, more_state, action, next_state, next_more_state, reward, not_done = self.replay_buffer.sample()
        else:
            state, action, next_state, reward, not_done = self.replay_buffer.sample()
        self.policy.train()
        self.optimizer.zero_grad()
        if self.hybrid:
            q_vals = self.policy(state,more_state)
        else:
            q_vals = self.policy(state)
        with torch.no_grad():
            if self.hybrid:
                next_q_vals = self.target_policy(next_state,next_more_state)
            else:
                next_q_vals = self.target_policy(next_state)
        max_q = torch.max(next_q_vals,1).values.view(q_vals.shape[0],1)
        target = q_vals.detach().clone()
        not_done = not_done.bool()
        change = torch.where(not_done,self.alpha*(reward + self.discount*max_q),reward)
        for i in range(target.shape[0]):
            target[i,action[i]] = change[i]
        loss = F.huber_loss(q_vals, target)
        loss.backward()
        self.optimizer.step()

def eval_policies(model1, model2, env, num_steps=1000, num_episodes=10):
    game_manager = fb_controller.GameManager(env, fb_controller.FbLearningController(model1),fb_controller.FbLearningController(model2))
    #env.reset(total_reset=True)
    #observation = env.get_state()
    total_reward1 = 0
    total_reward2 = 0
    for ep in range(num_episodes):
        game_manager.reset()
        for step in range(num_steps):
            poss = env.possession()
            _, reward, done, possession, _ = game_manager.advance_play()
            if poss:
                total_reward2 += reward
            else:
                total_reward1 += reward
            if done:
                break
    #print(f"Average reward 1 over {num_episodes} episodes: {total_reward1/num_episodes}")
    #print(f"Average reward 2 over {num_episodes} episodes: {total_reward2/num_episodes}")
    return total_reward1/num_episodes,total_reward2/num_episodes

def learning_loop(env, model1:DQN, model2:DQN, steps=100000, start=0):
    """
    Where training starts for DQNs
    """
    game_manager = fb_controller.GameManager(env, fb_controller.FbLearningController(model1),fb_controller.FbLearningController(model2))
    num_steps = steps
    observation = env.get_state()
    episode_num = 1
    total_reward1 = 0
    total_reward2 = 0

    turnover_group = None # group of plays that result in turnovers, the reward is calculated separately

    for t in range(start,start+num_steps):
        # code below stores data in buffers
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
            pass
            #turnover_group[3] -= reward

        if poss == possession:
            if possession:
                if not model2.hybrid:
                    observation = observation[0]
                model2.replay_buffer.add(observation, action, next_observation, reward, done)
                total_reward2 += reward
            else:
                if not model1.hybrid:
                    observation = observation[0]
                model1.replay_buffer.add(observation, action, next_observation, reward, done)
                total_reward1 += reward
        if (not (poss == possession)) or done:
            if turnover_group is not None:
                if not possession:
                    if not model2.hybrid:
                        observation = observation[0]
                    model2.replay_buffer.add(*turnover_group)
                    total_reward2 += turnover_group[3]
                else:
                    if not model1.hybrid:
                        observation = observation[0]
                    model1.replay_buffer.add(*turnover_group)
                    total_reward1 += turnover_group[3]
            turnover_group = [observation, action, next_observation, reward, done]
        # code above deals with adding plays to buffer

        # code below decides when to train, evaluate, and update policy
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

        if done:
            #print(f"Time Steps: {t}, Episode: {episode_num}, Reward 1: {total_reward1}")
            #print(f"Time Steps: {t}, Episode: {episode_num}, Reward 2: {total_reward2}")
            game_manager.reset()
            observation = env.get_state()
            total_reward1 = 0
            total_reward2 = 0
            episode_num += 1