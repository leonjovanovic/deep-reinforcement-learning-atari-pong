# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 11:15:15 2021

@author: Leon Jovanovic
"""
from numpy import random
from sympy import hyper

from agent_control import AgentControl
from replay_buffer import ReplayBuffer
from collections import namedtuple
import time
import numpy as np
import math
import telegram_bot as tg


class Agent:

    Transition = namedtuple('Transition',('state', 'action', 'next_state', 'reward', 'done'), rename = False) # 'rename' means not to overwrite invalid field

    def __init__(self, env, hyperparameters, device, writer, max_games, tg_bot):
        self.eps_start = hyperparameters['eps_start']
        self.eps_end = hyperparameters['eps_end']
        self.eps_decay = hyperparameters['eps_decay']
        self.epsilon = hyperparameters['eps_start']
        self.n_iter_update_nn = hyperparameters['n_iter_update_nn']
        self.max_games = max_games
        self.tg_bot = tg_bot
        self.env = env

        self.agent_control = AgentControl(env, device, hyperparameters['learning_rate'], hyperparameters['gamma'], hyperparameters['multi_step'], hyperparameters['double_dqn'], hyperparameters['dueling'])
        self.replay_buffer = ReplayBuffer(hyperparameters['buffer_size'], hyperparameters['buffer_minimum'], hyperparameters['multi_step'], hyperparameters['gamma'])
        self.summary_writer = writer

        self.num_iterations = 0
        self.total_reward = 0
        self.num_games = 0
        self.total_loss = []
        self.ts_frame = 0
        self.ts = time.time()
        self.birth_time = time.time()
        self.rewards = []

        if self.tg_bot:
            tg.welcome_msg(hyperparameters['multi_step'], hyperparameters['double_dqn'], hyperparameters['dueling'])

    def select_greedy_action(self, obs):
        # Give current state to the control who will pass it to NN which will
        # return all actions and the control will take max and return it here
        return self.agent_control.select_greedy_action(obs)

    def select_eps_greedy_action(self, obs):
        rand_num = random.rand()
        if self.epsilon > rand_num:
            # Select random action - explore
            return self.env.action_space.sample()
        else:
            # Select best action
            return self.select_greedy_action(obs)

    def add_to_buffer(self, obs, action, new_obs, reward, done):
        transition = self.Transition(state = obs, action = action, next_state = new_obs, reward = reward, done = done)
        self.replay_buffer.append(transition)
        self.num_iterations = self.num_iterations + 1
        if self.epsilon > self.eps_end:
            self.epsilon = self.eps_start - self.num_iterations / self.eps_decay
        self.total_reward = self.total_reward + reward

    def sample_and_improve(self, batch_size):
        # If buffer is big enough
        if len(self.replay_buffer.buffer) > self.replay_buffer.minimum:
            # Sample batch_size number of transitions from buffer B
            mini_batch = self.replay_buffer.sample(batch_size)
            # Calculate loss and improve NN
            loss = self.agent_control.improve(mini_batch)
            # So we can calculate mean of all loss during one game
            self.total_loss.append(loss)

        if ( self.num_iterations % self.n_iter_update_nn) == 0:
            self.agent_control.update_target_nn()

    def reset_parameters(self):
        self.rewards.append(self.total_reward)
        self.total_reward = 0
        self.num_games = self.num_games + 1
        self.total_loss = []

    def print_info(self):
        # print(self.num_iterations, self.ts_frame, time.time(), self.ts)
        fps = (self.num_iterations-self.ts_frame)/(time.time()-self.ts)
        print('%d %d rew:%d mean_rew:%.2f fps:%d, eps:%.2f, loss:%.4f' % (self.num_iterations, self.num_games, self.total_reward, np.mean(self.rewards[-40:]), fps, self.epsilon, np.mean(self.total_loss)))
        self.ts_frame = self.num_iterations
        self.ts = time.time()

        if self.summary_writer != None:
            self.summary_writer.add_scalar('reward', self.total_reward, self.num_games)
            self.summary_writer.add_scalar('mean_reward', np.mean(self.rewards[-40:]), self.num_games)
            self.summary_writer.add_scalar('10_mean_reward', np.mean(self.rewards[-10:]), self.num_games)
            self.summary_writer.add_scalar('esilon', self.epsilon, self.num_games)
            self.summary_writer.add_scalar('loss', np.mean(self.total_loss), self.num_games)

        if self.tg_bot:
            if (self.num_games % 10) == 0:
                tg.info_msg(self.num_games+1, self.max_games, np.mean(self.rewards[-40:]), np.mean(self.total_loss))
            if self.num_games == (self.max_games - 1):
                tg.end_msg(time.time() - self.birth_time)




