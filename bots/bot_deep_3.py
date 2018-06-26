from bot import *
from FNN_3 import FNN3
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import random
import os.path
import pickle

import tensorflow as tf

LEARNING = False

REWARD = 1
PENALIZATION = -1

DATA_FILE = "data.csv"

EPSILON_POLICY = False

DUMPING_RATE = 1

LAST_STATES_IGNORED = 30

STEPS = 1

VELOCITIES = range(FLAP_VELOCITY, MAX_VELOCITY + 1)
# xdif, ydif, vel, flap/not flap
MAX_MIN = [[200, 387, 10],[0, -225, -9]]
SCALER = MinMaxScaler(feature_range=(-1,1))
SCALER.fit(MAX_MIN)

REPLAY_MEMORY_CAPACITY = 10000
MINIBATCH_SIZE = 5000
REPLAY_STEPS = 100
TRAIN_STEP = 1

PROBABILITY_TO_FLAP = 0.05
GREEDY_PROBABILITY = 0.8

FLAP_POSITION = 0
NOT_FLAP_POSITION = 1

NETWORKS_COUNT = 15

#OPTIMIZERS = [tf.train.AdamOptimizer]
OPTIMIZERS = [tf.train.GradientDescentOptimizer, tf.train.AdamOptimizer,\
	tf.train.ProximalGradientDescentOptimizer, tf.train.RMSPropOptimizer]

class BotDeep3(Bot):


	def __init__(self, tag):
		global NETWORKS_COUNT
		if LEARNING: self.__history = []
		self.__fnn_bots = [FNN3(OPTIMIZERS[i % len(OPTIMIZERS)], i) for i in range(NETWORKS_COUNT)]
		self.__fnn_bots = [self.__fnn_bots[5],self.__fnn_bots[9]]
		NETWORKS_COUNT = 2
		if LEARNING: self.__last_state = None
		if LEARNING: self.__last_action = FLAP
		self.__episode = 0
		
		if LEARNING: self.__initialization = False
		if LEARNING: self.__replay_memory = set()
		if LEARNING: self.__greedy_vs_random = random.uniform(0,1)


	def __get_random_action(self):
		return FLAP if random.uniform(0,1) < PROBABILITY_TO_FLAP else NOT_FLAP


	def __get_greedy_action(self, xdif, ydif, vel):
		have_to_flap = False
		for i in range(0, 20):
			x = xdif - 4*i
			idx = vel + 9 + i if vel + 9 + i < len(VELOCITIES) else len(VELOCITIES)-1
			y = ydif - VELOCITIES[idx]
			if y <= -82 or (x <= 52 + 34 and y <= 0):
				have_to_flap = True

		if have_to_flap:
			for i in range(0, 20):
				x = xdif - 4*i
				y = ydif - VELOCITIES[i]
				if x <= 52 + 34 and y >= 100 - 24:
					return 0
			return 1

		return 0#self.__get_random_action()


	def __get_q_values(self, xdif, ydif, vel):
		pos1 = 0
		pos2 = 0
		for i in range(NETWORKS_COUNT):
			tmp = self.__fnn_bots[i].predict([SCALER.transform([[xdif, ydif, vel]])[0].tolist()])[0]
			if (tmp[0] < 0 and tmp[1] < 0) or (tmp[0] > 0 and tmp[1] > 0):
				continue
			else:
				pos1 += tmp[0]
				pos2 += tmp[1]
		return [pos1, pos2]


	def __generate_variations(self, idx, xdif, ydif, vel):
		if idx == STEPS or xdif < 0 or ydif > 387 or ydif < -225:
			self.__variations[self.__actual_variation] = self.__actual_sum
			return
		
		q_values = self.__get_q_values(xdif, ydif, vel)

		q_value = q_values[FLAP_POSITION]
		self.__actual_sum += q_value
		self.__actual_variation += "1"
		self.__generate_variations(idx + 1, xdif - HORIZONTAL_VELOCITY, ydif - FLAP_VELOCITY, FLAP_VELOCITY)
        
		self.__actual_variation = self.__actual_variation[:-1]
		self.__actual_sum -= q_value
        
		q_value = q_values[NOT_FLAP_POSITION]
		self.__actual_sum += q_value
		self.__actual_variation += "0"
		new_velocity = min(vel + 1, MAX_VELOCITY)
		self.__generate_variations(idx + 1, xdif - 4, ydif - new_velocity, new_velocity)
        
		self.__actual_variation = self.__actual_variation[:-1]
		self.__actual_sum -= q_value


	def __get_action_by_policy(self, xdif, ydif, vel):
		self.__actual_variation = ""
		self.__actual_sum = 0
		self.__variations = {}
		self.__generate_variations(0, xdif, ydif, vel)

		max = float("-inf")
		action_to_take = 0
		for key, value in self.__variations.iteritems():
			if max <= value:
				if max == value and action_to_take == 0:
					continue
				max = value
				action_to_take = int(key[0])
		return action_to_take, max


	def __get_training_sample(self, sample):
		state = sample[0]
		in_values = SCALER.transform([[state[0],state[1],state[2]]])[0].tolist()

		rewarded_action = sample[1]
		rewarded_position = FLAP_POSITION if rewarded_action == FLAP else NOT_FLAP_POSITION
		not_rewarded_position = NOT_FLAP_POSITION if rewarded_action == FLAP else FLAP_POSITION
		out = [0]*2
		out[rewarded_position] = REWARD
		out[not_rewarded_position] = PENALIZATION
		return in_values, out


	def __save_score(self, score):
		with open(DATA_FILE, 'a') as f:
			f.write(str(self.__episode) + ',' + str(score) + '\n')


	def act(self, xdif, ydif, vel):
		if xdif > 200:
			if ydif < 0:
				return FLAP
			else:
				return NOT_FLAP
		if LEARNING and self.__initialization:
			new_state = (xdif, ydif, vel)
			if self.__last_state is None: self.__last_state = new_state
			new_action = self.__get_greedy_action(xdif, ydif, vel) if\
				self.__greedy_vs_random <= GREEDY_PROBABILITY else self.__get_random_action()
			self.__history.append([self.__last_state, self.__last_action])
			self.__last_state = new_state
			self.__last_action = new_action
			return new_action
		else:
			if EPSILON_POLICY: epsilon = 1 / (self.__episode + 1)
			action = self.__get_random_action() if EPSILON_POLICY and\
				random.uniform(0,1) <= epsilon\
				else self.__get_action_by_policy(xdif, ydif, vel)[0]
			
			if action == FLAP:
				if LEARNING: new_state = (xdif, ydif, vel)
				if LEARNING: self.__history.append([self.__last_state, self.__last_action])
				if LEARNING: self.__last_state = new_state
				if LEARNING: self.__last_action = FLAP
				return FLAP
			else:
				if LEARNING: new_state = (xdif, ydif, vel)
				if LEARNING: self.__history.append([self.__last_state, self.__last_action])
				if LEARNING: self.__last_state = new_state
				if LEARNING: self.__last_action = NOT_FLAP
				return NOT_FLAP


	def dead(self, score):
		if LEARNING and (self.__initialization): print("Score: " + str(score))

		if LEARNING and len(self.__history) != 0:
			history = list(reversed(self.__history))

			used_idxs = range(LAST_STATES_IGNORED, len(history)-1)

			for i in used_idxs:
				state = history[i][0]
				action = history[i][1]

				if len(self.__replay_memory) >= REPLAY_MEMORY_CAPACITY:
					sample = random.sample(self.__replay_memory, 1)[0]
					self.__replay_memory.remove(sample)
				self.__replay_memory.add((state, action))
		
		if LEARNING and (len(self.__replay_memory) >= REPLAY_MEMORY_CAPACITY\
			or not self.__initialization):
			train_in_arr = []
			train_out_arr = []
			if self.__initialization:
				self.__initialization = False

				for sample in self.__replay_memory:
					inn, outt = self.__get_training_sample(sample)#, True)
					train_in_arr.append(inn)
					train_out_arr.append(outt)

				for bot in self.__fnn_bots:
					bot.train_step(train_in_arr, train_out_arr, REPLAY_STEPS)

			else:
				if self.__episode == 0: print("Initialization finished.")

				minibatch = random.sample(self.__replay_memory, min(MINIBATCH_SIZE, len(self.__replay_memory)))
				for sample in minibatch:
					inn, outt = self.__get_training_sample(sample)#, False)
					train_in_arr.append(inn)
					train_out_arr.append(outt)

				if len(train_in_arr) > 0:
					for bot in self.__fnn_bots:
						bot.train_step(train_in_arr, train_out_arr, TRAIN_STEP)
				self.__episode += 1
				if self.__episode % DUMPING_RATE == 0:
					for bot in self.__fnn_bots:
						bot.save()
				self.__save_score(score)

		if not LEARNING: self.__save_score(score)
		if LEARNING: self.__greedy_vs_random = random.uniform(0,1)
		if LEARNING: self.__history = []


	def stop(self):
		return
