import numpy as np

import nn_models
import torch
from utils import ReplayBuffer
import copy
import torch.optim as optim
import torch.nn.functional as F

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class DQN:

    def __init__(self, input_dim, output_dim):
        seed = 100
        torch.manual_seed(seed)
        np.random.seed(seed)

        # Hyperparameters
        self.batch_size = 128 #64
        self.buffer_size = 1e4 # 1e6
        self.learning_rate = 3e-4
        self.eps = 0.9
        self.eps_dec = 0.001
        self.eps_min = 0.01
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.num_hidden_layers = 2 # 2
        self.num_neurons_per_layer = 128 # 256
        self.discount = 0.99
        self.warmup_steps = 1e3
        self.target_update_freq = 60 # 50
        self.tau = 0.005 # ? 
        self.eval_freq = 5000 # 100
        self.train_freq = 20
        self.alpha = 1
        self.weight_decay = 0
        self.dropout = 0

        self.replay_buffer = ReplayBuffer(self.input_dim, self.batch_size,self.buffer_size, device)
        self.policy = nn_models.SimpleNN(self.input_dim,self.output_dim,self.num_hidden_layers,self.num_neurons_per_layer)
        #self.policy = nn_models.ComplexNN(self.input_dim, self.output_dim, self.num_hidden_layers, self.num_neurons_per_layer, self.dropout).to(device)
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

    def eval_policy(self, env, num_steps=1000, num_episodes=10):
        env.reset(total_reset=True)
        observation = env.get_state()
        total_reward = 0
        for ep in range(num_episodes):
            for step in range(num_steps):
                action = self.select_action(observation, env.get_actions())
                observation, reward, done = env.step(action)
                total_reward += reward
                if done:
                    env.reset(total_reset=True)
                    observation = env.get_state()
                    break
        print(f"Average reward over {num_episodes} episodes: {total_reward/num_episodes}")
        return total_reward/num_episodes

    def train_policy(self, policy, target_policy, buffer, optimizer, discount, alpha):
        state, action, next_state, reward, done = buffer.sample()
        policy.train()
        for s,a,s2,r,d in zip(state,action,next_state,reward,done):
            optimizer.zero_grad()
            q_vals = policy(s)[0]
            with torch.no_grad():
                next_q_vals = target_policy(s2)[0]
            max_q = torch.max(next_q_vals)
            target = q_vals.detach().clone()
            if d:
                target[a] = r
            else:
                target[a] = alpha*(r + discount*max_q)
            loss = F.mse_loss(q_vals, target)
            loss.backward()
            optimizer.step()

    def learning_loop(self, env, steps=100000):
        num_steps = steps
        env.reset(total_reset=True)
        observation = env.get_state()
        episode_num = 1
        total_reward = 0

        for t in range(num_steps):
            if t < self.warmup_steps:
                action = np.random.choice(env.get_actions())
            else:
                action = self.select_action(observation, env.get_actions(), self.eps)
                self.eps = self.eps-self.eps_dec
                if self.eps < self.eps_min:
                    self.eps = self.eps_min
            next_observation, reward, done = env.step(action)
            self.replay_buffer.add(observation, action, next_observation, reward, done)
            observation = copy.copy(next_observation)
            total_reward += reward

            if t % self.train_freq == 0 and t > 0:
                self.train_policy(self.policy,self.target_policy,self.replay_buffer,self.optimizer,self.discount,self.alpha)
                self.policy.eval()
            if t % self.eval_freq == 0 and t > 0:
                if self.eval_policy(env,1000,100) > 200:
                    break # success
            if t % self.target_update_freq == 0 and t > 0:
                for param, target_param in zip(self.policy.parameters(), self.target_policy.parameters()):
                    target_param.data.copy_(param.data)

            if t%1000 == 0:
                print(t)
            if done:
                print(f"Time Steps: {t}, Episode: {episode_num}, Reward: {total_reward}")
                env.reset(total_reset=True)
                observation = env.get_state()
                total_reward = 0
                episode_num += 1