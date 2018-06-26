from bot import *

PIPE_WIDTH = 52
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
VERTICAL_GAP_SIZE = 100
VELOCITIES = range(-9,10+1)

SAVE_SCORE_FOLDER = "greedy2_scores.csv"

class BotGreedy2(Bot):


	def __init__(self, tag):
		self.__count = 1


	def act(self, xdif, ydif, vel):
		have_to_flap = False
		for i in range(0, 20):
			x = xdif - 4*i
			idx = vel + 9 + i if vel + 9 + i < len(VELOCITIES) else len(VELOCITIES)-1
			y = ydif - VELOCITIES[idx]
			if y <= -82 or (x <= PIPE_WIDTH + BIRD_WIDTH and y <= 0):
				have_to_flap = True

		if have_to_flap:
			for i in range(0, 20):
				x = xdif - 4*i
				y = ydif - VELOCITIES[i]
				if x <= PIPE_WIDTH + BIRD_WIDTH and y >= VERTICAL_GAP_SIZE - BIRD_HEIGHT:
					return NOT_FLAP
			return FLAP

		return NOT_FLAP


	def dead(self, score):
		with open(SAVE_SCORE_FOLDER, 'a') as f:
			f.write(str(score) + '\n')

		if (self.__count % 100 == 0):
			print(str(self.__count) + ". game score saved.")
		self.__count += 1


	def stop(self):
		return
