from bot import *

SAVE_SCORE_FOLDER = "greedy_scores.csv"

class BotGreedy(Bot):


	def __init__(self, tag):
		self.__count = 1


	def act(self, xdif, ydif, vel):
		if ydif < 10:
			return FLAP
		else:
			return NOT_FLAP


	def dead(self, score):
		with open(SAVE_SCORE_FOLDER, 'a') as f:
			f.write(str(score) + '\n')

		if (self.__count % 100 == 0):
			print(str(self.__count) + ". game score saved.")
		self.__count += 1


	def stop(self):
		return
