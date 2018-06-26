from bot import *
import pickle
import random
from random import randint
import os.path

LEARNING = False

VERTICAL_ACCURACY_OF_STATES = 5
HORIZONTAL_ACCURACY_OF_STATES = 5

ALIVE_REWARD = 1
DEAD_PENALIZATION = -1000

MODEL_BASE = "./models/QLearning/"
Q_FILE_BASE = MODEL_BASE + "q_"
DATA_FILE_BASE = "scores_q_learning_"

DISCOUNT = 1
LEARNING_RATE = 0.8
EPSILON_POLICY = False

DUMPING_RATE = 100

LAST_STATES_PENALIZED = 3

STEPS = 4

class BotQLearning(Bot):


	def __init__(self, tag):
		self.__q_file = Q_FILE_BASE + "_" + tag
		self.__data_file = DATA_FILE_BASE + "_" + tag + ".csv"
		self.__q_values = self.__load_q()
		if LEARNING: self.__history = []
		if LEARNING: self.__last_state = 'first'
		if LEARNING: self.__last_action = FLAP


	def __load_q(self):
		if os.path.isfile(self.__q_file):
			with open(self.__q_file, 'rb') as f:
				return pickle.load(f)
		else:
			return {'iterations': 0}


	def __state_round(self, num, base):
		return int(base * round(float(int(num))/base))


	def __get_state(self, xdif, ydif, vel):
		return (self.__state_round(xdif, HORIZONTAL_ACCURACY_OF_STATES),\
			self.__state_round(ydif, VERTICAL_ACCURACY_OF_STATES), vel)


	def __get_q_value(self, state, action):
		return self.__q_values[state][action]\
			if state in self.__q_values and\
			action in self.__q_values[state] else 0


	def __generate_variations(self, idx, xdif, ydif, vel):
		if idx == STEPS:
			self.__variations[self.__actual_variation] = self.__actual_sum
			return
        
		state = self.__get_state(xdif, ydif, vel)
        
		q_value = self.__get_q_value(state, FLAP)
		self.__actual_sum += q_value
		self.__actual_variation += "1"
		self.__generate_variations(idx + 1, xdif - HORIZONTAL_VELOCITY, ydif - FLAP_VELOCITY, FLAP_VELOCITY)
        
		self.__actual_variation = self.__actual_variation[:-1]
		self.__actual_sum -= q_value
        
		q_value = self.__get_q_value(state, NOT_FLAP)
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


	def __get_next_max_q_value(self, state):
		return max(self.__q_values[state][FLAP] if state in self.__q_values and FLAP in self.__q_values[state] else 0,\
			self.__q_values[state][NOT_FLAP] if state in self.__q_values and NOT_FLAP in self.__q_values[state] else 0)


	def __update_qvalues(self):
		history = list(reversed(self.__history))
		upper_pipe_hit = 1 if history[len(history) - 1][2][1] >= GAP_SIZE - IMAGES_PLAYER_HEIGHT else 0

		good_idxs = range(LAST_STATES_PENALIZED + upper_pipe_hit, len(history))
		bad_idxs = range(0, LAST_STATES_PENALIZED + upper_pipe_hit)

		for i in bad_idxs:
			state = history[i][0]
			action = history[i][1]
			next_state = history[i][2]
			max_next_q_value = self.__get_next_max_q_value(next_state)

			self.__q_values[state] = {} if state not in self.__q_values else self.__q_values[state]
			self.__q_values[state][action] =\
				(1 - LEARNING_RATE) * self.__q_values[state][action] + LEARNING_RATE * (DEAD_PENALIZATION + DISCOUNT * max_next_q_value)\
				if action in self.__q_values[state] else LEARNING_RATE * (DEAD_PENALIZATION + DISCOUNT * max_next_q_value)

		for i in good_idxs:
			state = history[i][0]
			action = history[i][1]
			next_state = history[i][2]
			max_next_q_value = self.__get_next_max_q_value(next_state)

			self.__q_values[state] = {} if state not in self.__q_values else self.__q_values[state]
			self.__q_values[state][action] = (1 - LEARNING_RATE) * self.__q_values[state][action] + LEARNING_RATE * (ALIVE_REWARD + DISCOUNT * max_next_q_value)\
				if action in self.__q_values[state] else LEARNING_RATE * (ALIVE_REWARD + DISCOUNT * max_next_q_value)

		self.__history = []


	def __save_q_values(self, now):
		if now or (self.__q_values['iterations']) % DUMPING_RATE == 0:
			with open(self.__q_file, 'wb') as f:
				pickle.dump(self.__q_values, f, pickle.HIGHEST_PROTOCOL)
				print('values saved')


	def __save_score(self, score):
		with open(self.__data_file, 'a') as f:
			f.write(str(self.__q_values['iterations']) + ',' + str(score) + '\n')


	def act(self, xdif, ydif, vel):
		if EPSILON_POLICY: epsilon = 1 / (self.__q_values['iterations'] + 1)
		state = self.__get_state(xdif, ydif, vel)
		action = randint(0, 1) if EPSILON_POLICY and random.uniform(0,1) <= epsilon else self.__get_action_by_policy(xdif, ydif, vel)[0]
		if action == FLAP:
			if LEARNING: self.__history.append([self.__last_state, self.__last_action, state, FLAP])
			if LEARNING: self.__last_state = state
			if LEARNING: self.__last_action = FLAP
			return FLAP
		else:
			if LEARNING: self.__history.append([self.__last_state, self.__last_action, state, NOT_FLAP])
			if LEARNING: self.__last_state = state
			if LEARNING: self.__last_action = NOT_FLAP
			return NOT_FLAP


	def dead(self, score):
		if LEARNING: self.__update_qvalues()

		if LEARNING: self.__q_values['iterations'] += 1
		if LEARNING: self.__save_q_values(False)
		self.__save_score(score)


	def stop(self):
		if LEARNING: self.__save_q_values(True)
