import os
import random

SCREENHEIGHT	= 512

BASEY			= SCREENHEIGHT * 0.79
PIPEGAPSIZE		= 100

FOLDER = "../../pipes/"
PIPES_IN_ONE_GAME = 10
NUMBER_OF_GAMES = 2

def generate():
	if os.path.isdir(FOLDER):
		print("Folder exists!")
		return
	else:
		os.makedirs(FOLDER)

	for game_idx in range(NUMBER_OF_GAMES):
		with open(FOLDER + str(game_idx), "w") as f:
			for pipe_idx in range(PIPES_IN_ONE_GAME):
				f.write(str(random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))) + "\n")

	print("Sucessfully created!")

generate()
