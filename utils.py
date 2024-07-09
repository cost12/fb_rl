#import cv2
import gym
import numpy as np
import torch


# Replay buffer for standard gym tasks
class ReplayBuffer():
	def __init__(self, state_dim, batch_size, buffer_size, device, more_state_dim=0):
		self.batch_size = batch_size
		self.max_size = int(buffer_size)
		self.device = device

		self.ptr = 0
		self.size = 0
		self.is_more_state = more_state_dim > 0

		self.state = np.zeros((self.max_size, *state_dim))
		if self.is_more_state:
			self.more_state = np.zeros((self.max_size, more_state_dim))
			self.next_more_state = np.array(self.more_state)
		self.action = np.zeros((self.max_size, 1))
		self.next_state = np.array(self.state)
		self.reward = np.zeros((self.max_size, 1))
		self.not_done = np.zeros((self.max_size, 1))

	def add(self, state, action, next_state, reward, done):
		
		if self.is_more_state:
			self.state[self.ptr] = state[0]
			self.more_state[self.ptr] = state[1]
			self.next_state[self.ptr] = next_state[0]
			self.next_more_state[self.ptr] = next_state[1]
		else:
			self.state[self.ptr] = state
			self.next_state[self.ptr] = next_state
		self.action[self.ptr] = action
		self.reward[self.ptr] = reward
		self.not_done[self.ptr] = 1. - done
		
		self.ptr = (self.ptr + 1) % self.max_size
		self.size = min(self.size + 1, self.max_size)

	def sample(self):
		ind = np.random.randint(0, self.size, size=self.batch_size)

		if self.is_more_state:
			batch = (
				torch.FloatTensor(self.state[ind]).to(self.device),
				torch.FloatTensor(self.more_state[ind]).to(self.device),
				torch.LongTensor(self.action[ind]).to(self.device),
				torch.FloatTensor(self.next_state[ind]).to(self.device),
				torch.FloatTensor(self.next_more_state[ind]).to(self.device),
				torch.FloatTensor(self.reward[ind]).to(self.device),
				torch.FloatTensor(self.not_done[ind]).to(self.device)
			)
		else:
			batch = (
				torch.FloatTensor(self.state[ind]).to(self.device),
				torch.LongTensor(self.action[ind]).to(self.device),
				torch.FloatTensor(self.next_state[ind]).to(self.device),
				torch.FloatTensor(self.reward[ind]).to(self.device),
				torch.FloatTensor(self.not_done[ind]).to(self.device)
			)

		return batch
