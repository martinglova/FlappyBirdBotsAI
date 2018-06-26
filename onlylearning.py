from itertools import cycle
import random
import sys

from bot import BOT
# import constants
from constants import *
# import for disabling screen
import os
# to load hitmasks
import numpy as np

TAG = "" if len(sys.argv) <= 1 else sys.argv[1]

# initialize the bot
bot = BOT(TAG)

# ctrl + c
import signal
def sigint_handler(signum, frame):
    bot.stop()
    exit()

SCREENWIDTH  = 288
SCREENHEIGHT = 512
# amount by which base can maximum shift to left
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
HITMASKS = {}

### new variables
IMAGES_PLAYER_HEIGHT = 24
IMAGES_BASE_WIDTH = 336
IMAGES_BACKGROUND_WIDTH = 288
IMAGES_PIPE_HEIGHT = 320
IMAGES_PLAYER_WIDTH = 34
IMAGES_PIPE_WIDTH = 52

HITMASKS_FOLDER = "assets/hitmasks/"

USE_OWN_PIPES = False
if USE_OWN_PIPES: pipes = []
if USE_OWN_PIPES: PIPES_FOLDER = "../pipes/"

NUMBER_OF_GAMES = 15000

def main():
	played_games = 0
	if USE_OWN_PIPES: games_count = 1
	if USE_OWN_PIPES: games_to_play = len([x for x in os.walk(PIPES_FOLDER)][0][2])
	
	signal.signal(signal.SIGINT, sigint_handler)
	global SCREEN, FPSCLOCK
	
	HITMASKS['pipe'] = (
		np.load(open(HITMASKS_FOLDER + 'uHitmask.var')),
		np.load(open(HITMASKS_FOLDER + 'lHitmask.var'))
	)
	HITMASKS['player'] = (
		np.load(open(HITMASKS_FOLDER + 'player0.var')),
		np.load(open(HITMASKS_FOLDER + 'player1.var')),
		np.load(open(HITMASKS_FOLDER + 'player2.var')),
	)
	while NUMBER_OF_GAMES == INFINITE_GAMES or played_games < NUMBER_OF_GAMES:
		if USE_OWN_PIPES: global pipes
		if USE_OWN_PIPES:
			with open(PIPES_FOLDER + str(games_count-1), "r") as f:
				pipes = [int(l) for l in f]
	
		movementInfo = showWelcomeAnimation()
		crashInfo = mainGame(movementInfo)
		showGameOverScreen(crashInfo)
		if USE_OWN_PIPES: games_count += 1
		if USE_OWN_PIPES: 
			if (games_count > games_to_play):
				return

		played_games += 1


def showWelcomeAnimation():
	"""Shows welcome screen animation of flappy bird"""
	# index of player to blit on screen
	'''playerIndex = 0'''
	playerIndexGen = cycle([0, 1, 2, 1])
	# iterator used to change playerIndex after every 5th iteration
	'''loopIter = 0
	
	playerx = int(SCREENWIDTH * 0.2)'''
	playery = int((SCREENHEIGHT - IMAGES_PLAYER_HEIGHT) / 2)
	
	'''messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
	messagey = int(SCREENHEIGHT * 0.12)'''
	
	basex = 0
	# amount by which base can maximum shift to left
	'''baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()'''
	
	# player shm for up-down motion on welcome screen
	playerShmVals = {'val': 0, 'dir': 1}
	
	while True:	
		return {
			'playery': playery + playerShmVals['val'],
			'basex': basex,
			'playerIndexGen': playerIndexGen,
		}

def flap(playery, playerFlapAcc):
	if playery > -2 * IMAGES_PLAYER_HEIGHT:
		return playerFlapAcc, True
        

def mainGame(movementInfo):
	if USE_OWN_PIPES: pipes_count = 0
	score = playerIndex = loopIter = 0
	playerIndexGen = movementInfo['playerIndexGen']
	playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']
	
	basex = movementInfo['basex']
	baseShift = IMAGES_BASE_WIDTH - IMAGES_BACKGROUND_WIDTH
	
	# get 2 new pipes to add to upperPipes lowerPipes list
	newPipe1 = getRandomPipe(pipes_count) if USE_OWN_PIPES else getRandomPipe()
	if USE_OWN_PIPES: pipes_count += 1
	newPipe2 = getRandomPipe(pipes_count) if USE_OWN_PIPES else getRandomPipe()
	if USE_OWN_PIPES: pipes_count += 1
	
	# list of upper pipes
	upperPipes = [
		{'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
		{'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
	]
	
	# list of lowerpipe
	lowerPipes = [
		{'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
		{'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
	]

	myPipe = lowerPipes[0]
	pipeVelX = -4
	
	# player velocity, max velocity, downward accleration, accleration on flap
	playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
	playerMaxVelY =  10   # max vel along Y, max descend speed
	playerAccY    =   1   # players downward accleration
	playerFlapAcc =  -9   # players speed on flapping
	playerFlapped = False # True when player flaps
	
	while True:
		if USE_OWN_PIPES and pipes_count - 1 > len(pipes) and\
			myPipe['x'] + IMAGES_PIPE_WIDTH - playerx <= 0:
			bot.dead(score)
			return {
				'y': playery,
				'groundCrash': True,
				'basex': basex,
				'upperPipes': upperPipes,
				'lowerPipes': lowerPipes,
				'score': score,
				'playerVelY': playerVelY,
			}
		if lowerPipes[0]['x'] + IMAGES_PIPE_WIDTH - playerx\
			> 0: myPipe = lowerPipes[0]
		else: myPipe = lowerPipes[1]
	
		xdif = myPipe['x'] + IMAGES_PIPE_WIDTH - playerx
		ydif = myPipe['y'] - playery - IMAGES_PLAYER_HEIGHT
		playerVelY_bak = playerVelY

		move = bot.act(xdif, ydif, playerVelY)

		if move and playery > -2 * IMAGES_PLAYER_HEIGHT:
			playerVelY, playerFlapped = flap(playery, playerFlapAcc)
	
		# check for crash here
		crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
							upperPipes, lowerPipes)
		if crashTest[0]:
			bot.dead(score)#xdif, ydif, playerVelY_bak, move, score)
			return {
				'y': playery,
				'groundCrash': crashTest[1],
				'basex': basex,
				'upperPipes': upperPipes,
				'lowerPipes': lowerPipes,
				'score': score,
				'playerVelY': playerVelY,
			}
	
		# check for score
		playerMidPos = playerx + IMAGES_PLAYER_WIDTH / 2
		for pipe in upperPipes:
			pipeMidPos = pipe['x'] + IMAGES_PIPE_WIDTH / 2
			if pipeMidPos <= playerMidPos < pipeMidPos + 4:
				score += 1
	
		# playerIndex basex change
		if (loopIter + 1) % 3 == 0:
			playerIndex = next(playerIndexGen)
		loopIter = (loopIter + 1) % 30
		basex = -((-basex + 100) % baseShift)
	
		# player's movement
		if playerVelY < playerMaxVelY and not playerFlapped:
			playerVelY += playerAccY
		if playerFlapped:
			playerFlapped = False
		playerHeight = IMAGES_PLAYER_HEIGHT
		playery += min(playerVelY, BASEY - playery - playerHeight)
	
		# move pipes to left
		for uPipe, lPipe in zip(upperPipes, lowerPipes):
			uPipe['x'] += pipeVelX
			lPipe['x'] += pipeVelX
	
		# add new pipe when first pipe is about to touch left of screen
		if 0 < upperPipes[0]['x'] < 5:
			newPipe = getRandomPipe(pipes_count) if USE_OWN_PIPES else getRandomPipe()
			if USE_OWN_PIPES: pipes_count += 1
			upperPipes.append(newPipe[0])
			lowerPipes.append(newPipe[1])
	
		# remove first pipe if its out of the screen
		if upperPipes[0]['x'] < -IMAGES_PIPE_WIDTH:
			upperPipes.pop(0)
			lowerPipes.pop(0)


def showGameOverScreen(crashInfo):
	"""crashes the player down ans shows gameover image"""
	score = crashInfo['score']
	playerx = SCREENWIDTH * 0.2
	playery = crashInfo['y']
	playerHeight = IMAGES_PLAYER_HEIGHT
	playerVelY = crashInfo['playerVelY']
	playerAccY = 2
	
	basex = crashInfo['basex']
	
	upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']


def playerShm(playerShm):
	"""oscillates the value of playerShm['val'] between 8 and -8"""
	if abs(playerShm['val']) == 8:
		playerShm['dir'] *= -1
	
	if playerShm['dir'] == 1:
		playerShm['val'] += 1
	else:
		playerShm['val'] -= 1


def getRandomPipe(idx=None):
	"""returns a randomly generated pipe"""
	# y of gap between upper and lower pipe
	if USE_OWN_PIPES and idx >= len(pipes):
		gapY = 0
	else:
		gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE)) if not USE_OWN_PIPES else pipes[idx]
	#gapY = 0
	gapY += int(BASEY * 0.2)
	pipeHeight = IMAGES_PIPE_HEIGHT
	pipeX = SCREENWIDTH + 10
	yUpper = gapY - pipeHeight
	yLower = gapY + PIPEGAPSIZE
	
	if USE_OWN_PIPES and idx >= len(pipes): yUpper = 0
	if USE_OWN_PIPES and idx >= len(pipes): yLower = 100
	return [
		{'x': pipeX, 'y': yUpper},  # upper pipe
		{'x': pipeX, 'y': yLower}, # lower pipe
	]

def checkCrash(player, upperPipes, lowerPipes):
	"""returns True if player collders with base or pipes."""
	pi = player['index']
	player['w'] = IMAGES_PLAYER_WIDTH
	player['h'] = IMAGES_PLAYER_HEIGHT

	# if player crashes into ground
	if player['y'] + player['h'] >= BASEY - 1:
		return [True, True]
	else:
	
		playerRect = [player['x'], player['y'],	player['w'], player['h']]
		pipeW = IMAGES_PIPE_WIDTH
		pipeH = IMAGES_PIPE_HEIGHT
	
		for uPipe, lPipe in zip(upperPipes, lowerPipes):
			# upper and lower pipe rects
			uPipeRect = [uPipe['x'], uPipe['y'], pipeW, pipeH]
			lPipeRect = [lPipe['x'], lPipe['y'], pipeW, pipeH]
	
			# player and upper/lower pipe hitmasks
			pHitMask = HITMASKS['player'][pi]
			uHitmask = HITMASKS['pipe'][0]
			lHitmask = HITMASKS['pipe'][1]
	
			# if bird collided with upipe or lpipe
			uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
			lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)
	
			if uCollide or lCollide:
				return [True, False]

	return [False, False]

X_COO = 0
Y_COO = 1
W_COO = 2
H_COO = 3

def clip(A, B):
	# Source: https://github.com/pygame/pygame/blob/master/src/rect.c
	default = [A[X_COO], A[Y_COO], 0, 0]
	# Left
	if ((A[X_COO] >= B[X_COO]) and (A[X_COO] < (B[X_COO] + B[W_COO]))):
		x = A[X_COO]
	elif ((B[X_COO] >= A[X_COO]) and (B[X_COO] < (A[X_COO] + A[W_COO]))):
		x = B[X_COO]
	else:
		return default
	# Right
	if (((A[X_COO] + A[W_COO]) > B[X_COO]) and ((A[X_COO] + A[W_COO]) <= (B[X_COO] + B[W_COO]))):
		w = (A[X_COO] + A[W_COO]) - x
	elif (((B[X_COO] + B[W_COO]) > A[X_COO]) and ((B[X_COO] + B[W_COO]) <= (A[X_COO] + A[W_COO]))):
		w = (B[X_COO] + B[W_COO]) - x
	else:
		return default
	# Top
	if ((A[Y_COO] >= B[Y_COO]) and (A[Y_COO] < (B[Y_COO] + B[H_COO]))):
		y = A[Y_COO]
	elif ((B[Y_COO] >= A[Y_COO]) and (B[Y_COO] < (A[Y_COO] + A[H_COO]))):
		y = B[Y_COO]
	else:
		return default
	# Bottom
	if (((A[Y_COO] + A[H_COO]) > B[Y_COO]) and ((A[Y_COO] + A[H_COO]) <= (B[Y_COO] + B[H_COO]))):
		h = (A[Y_COO] + A[H_COO]) - y
	elif (((B[Y_COO] + B[H_COO]) > A[Y_COO]) and ((B[Y_COO] + B[H_COO]) <= (A[Y_COO] + A[H_COO]))):
		h = (B[Y_COO] + B[H_COO]) - y
	else:
		return default

	return [x, y, w, h]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
	"""Checks if two objects collide and not just their rects"""
	rect = clip(rect1, rect2)
	
	if rect[W_COO] == 0 or rect[H_COO] == 0:
		return False
	
	x1, y1 = rect[X_COO] - rect1[X_COO], rect[Y_COO] - rect1[Y_COO]
	x2, y2 = rect[X_COO] - rect2[X_COO], rect[Y_COO] - rect2[Y_COO]
	
	for x in range(rect[W_COO]):
		for y in range(rect[H_COO]):
			if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
				return True
	return False


if __name__ == '__main__':
	main()
