'''
from functions import *
'''
import pickle
import os.path
import numpy as np
from FNN import FNN
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf

OPTIMIZERS = [tf.train.GradientDescentOptimizer, tf.train.AdamOptimizer,\
	tf.train.ProximalGradientDescentOptimizer, tf.train.RMSPropOptimizer]

HORIZONTAL_VELOCITY = 4
FLAP_VELOCITY = -9
MAX_VELOCITY = 10
STEPS = 4

MAX_MIN = [[200, 387, 10],[0, -225, -9]]
SCALER = MinMaxScaler(feature_range=(-1,1))
SCALER.fit(MAX_MIN)

VERTICAL_ACCURACY_OF_STATES = 5
HORIZONTAL_ACCURACY_OF_STATES = 5

TANH_POSITIVE = np.tanh(1)
TANH_NEGATIVE = -1

FLAP_POSITION = 0
NOT_FLAP_POSITION = 1

FLAP = 1
NOT_FLAP = 0

NETWORKS_COUNT = 5

'''
from init_train_functions import *
q = get_q_values("../models/QLearning/q__")
'''
def get_q_values(file_name):
	if os.path.isfile(file_name):
		with open(file_name, 'rb') as f:
			return pickle.load(f)

'''
from init_train_functions import *
q = get_q_values("../models/QLearning/q__")
positive_and_negative_values(q)
'''
def positive_and_negative_values(q):
	positive_sum = 0
	positive = 0
	negative_sum = 0
	negative = 0
	for dic in q:
		if 'iterations' == dic:
			continue
		for val in q[dic]:
			if q[dic][val] < 0:
				negative_sum += q[dic][val]
				negative += 1
			else:
				positive_sum += q[dic][val]
				positive += 1
	result = {"positive": {"count": positive, "sum": positive_sum, "average": positive_sum/positive},\
		"negative": {"count": negative, "sum": negative_sum, "average": negative_sum/negative} }
	print("Positive: " + str(result["positive"]["count"]) + " with sum: " + str(result["positive"]["sum"])\
		+ " average: " + str(result["positive"]["average"]))
	print("Negative: " + str(result["negative"]["count"]) + " with sum: " + str(result["negative"]["sum"])\
		+ " average: " + str(result["negative"]["average"]))
	return result

'''
from init_train_functions import *
q = get_q_values("../models/QLearning/q__")
max_min_value(q)
'''
def max_min_value(q):
	maxx = float("-inf")
	minn = float("inf")
	for dic in q:
		if 'iterations' == dic:
			continue
		for val in q[dic]:
			if q[dic][val] > maxx:
				maxx = q[dic][val]
			if q[dic][val] < minn:
				minn = q[dic][val]
	print("Max: " + str(maxx))
	print("Min: " + str(minn))

def __prepare_for_training(x, y, v):
	return SCALER.transform([[x,y,v]])[0].tolist()

'''
from init_train_functions import *
q = get_q_values("../models/QLearning/q__")
get_data_for_training(q)
'''
def get_data_for_training(q):
	inn = []
	outt = []

	for dic in q:
		if 'iterations' == dic or dic[0] == 'f' or dic[0] > 200:
			continue
		action = q[dic]["action"]
		not_action = FLAP if action == NOT_FLAP else NOT_FLAP
		inn.append(__prepare_for_training(dic[0], dic[1], dic[2]))
		tmp_out = [0]*2
		action_bool = True if action == 1 else False
		tmp_out[__get_out_index(action)] = TANH_POSITIVE

		val = __q_function(q, dic[0], dic[1], dic[2], not_action)
		tmp_out[__get_out_index(not_action)] = TANH_NEGATIVE
		outt.append(tmp_out)
	return inn, outt

def __get_bool_of_action(action):
	return True if action == 1 else False

def __get_out_index(action):
	return FLAP_POSITION if action == FLAP else NOT_FLAP_POSITION

'''
from init_train_functions import *
q = get_q_values("../models/QLearning/q__")
save_decisions(q, "q")
'''
def save_decisions(q, file_name):
	for dic in q:
		if 'iterations' == dic or dic[0] == 'f':
			continue
		action = __get_action_by_policy(__q_function, q, dic[0], dic[1], dic[2])
		q[dic]["action"] = action
	with open(file_name, 'wb') as f:
		pickle.dump(q, f, pickle.HIGHEST_PROTOCOL)
		print('values saved')

'''
from init_train_functions import *
q = get_q_values("q")
inn, outt = get_data_for_training(q)
count = len(inn)
networks = [FNN(OPTIMIZERS[i % len(OPTIMIZERS)], i) for i in range(NETWORKS_COUNT)]
train_networks(networks, inn[:count], outt[:count], 10)
'''
def train_networks(networks, data_in, data_out, train_count):
	for i in range(len(networks)):
		network = networks[i]
		print("start training network " + str(i))
		network.train_step(data_in, data_out, train_count)
		network.save()
		print("finished training network " + str(i))
	return networks

'''
from init_train_functions import *
q = get_q_values("q")
inn, outt = get_data_for_training(q)
count = len(inn)
networks = [FNN(OPTIMIZERS[i % len(OPTIMIZERS)], i) for i in range(NETWORKS_COUNT)]
networks = train_networks(networks, inn[:count], outt[:count], 100)
compare_computation(networks, q, 100)
'''
def compare_computation(networks, q, size):
	same_output = 0
	different_output = 0
	i = 0
	for t in q:
		if 'iterations' == t or t[0] == 'f' or t[0] > 200:
			continue
		x = t[0]
		y = t[1]
		v = t[2]
		q_action = q[t]["action"]#__get_q_action(q, x, y, v)
		n_action = __get_n_action(networks, x, y, v)
		if q_action == n_action:
			same_output += 1
		else:
			different_output += 1
			print(t)
		if i == size: break
		i += 1
	print("Same: " + str(same_output))
	print("Different: " + str(different_output))

def __q_function(q, x, y, v, a):
	s = __get_state(x, y, v)
	action = True if a == 1 else False
	return q[s][action] if s in q and action in q[s] else 0

def __n_function(n, x, y, v):
	return n.predict([SCALER.transform([[x, y, v]])[0].tolist()])[0]

actual_variation = None
actual_sum = None
variations = None

def __get_action_by_policy(function, q_or_net, x, y, v):
	global actual_variation, actual_sum, variations
	actual_variation = ""
	actual_sum = 0
	variations = {}
	__generate_variations(0, x, y, v, function, q_or_net)

	max = float("-inf")
	action_to_take = 0
	for key, value in variations.iteritems():
		if max <= value:
			if max == value and action_to_take == 0:
				continue
			max = value
			action_to_take = int(key[0])
	return action_to_take

def __generate_variations(idx, xdif, ydif, vel, function, q_or_net):
	global actual_variation, actual_sum, variations
	if idx == STEPS:
		variations[actual_variation] = actual_sum
		return
    
	q_value = function(q_or_net, xdif, ydif, vel, 1)
	actual_sum += q_value
	actual_variation += "1"
	__generate_variations(idx + 1, xdif - HORIZONTAL_VELOCITY, ydif - FLAP_VELOCITY, FLAP_VELOCITY, function, q_or_net)
    
	actual_variation = actual_variation[:-1]
	actual_sum -= q_value
    
	q_value = function(q_or_net, xdif, ydif, vel, 0)
	actual_sum += q_value
	actual_variation += "0"
	new_velocity = min(vel + 1, MAX_VELOCITY)
	__generate_variations(idx + 1, xdif - 4, ydif - new_velocity, new_velocity, function, q_or_net)
    
	actual_variation = actual_variation[:-1]
	actual_sum -= q_value

def __get_q_action(q, x, y, v):
	return __get_action_by_policy(__q_function, q, x, y, v)

def __get_network_action(network, x, y, v):
	predict = __n_function(network, x, y, v)
	return predict[FLAP_POSITION], predict[NOT_FLAP_POSITION]

def __get_n_action(networks, x, y, v):
	flaps = 0
	not_flaps = 0
	for network in networks:
		f,n_f = __get_network_action(network, x, y, v)
		if (f < 0 and n_f < 0) or (f > 0 and n_f > 0):
			continue
		a = NOT_FLAP if f <= n_f else FLAP
		if a == FLAP:
			flaps += 1
		else:
			not_flaps += 1
	return NOT_FLAP if not_flaps >= flaps else FLAP

def __state_round(num, base):
	return int(base * round(float(int(num))/base))

def __get_state(xdif, ydif, vel):
	return (__state_round(xdif, HORIZONTAL_ACCURACY_OF_STATES),\
		__state_round(ydif, VERTICAL_ACCURACY_OF_STATES), vel)
