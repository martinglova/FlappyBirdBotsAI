import matplotlib.pyplot as plt
import numpy as np
import pickle

import sys
sys.path.insert(0, '..')
#from bots.bot_deep_3 import BotDeep3
from bots.bot_q_learning import BotQLearning

bot = BotQLearning("") #BotDeep3("")

BLUE = [0/255.0,191/255.0,255/255.0]
RED = [255/255.0,0/255.0,0/255.0]
VEL = 10
OUT_IMAGE = "ql" + str(VEL) + ".png"
DPI=500

FLAP = True
NOT_FLAP = False

X_MIN = 0
X_MAX = 200
Y_MIN = -225
Y_MAX = 387

tmp = [[None for j in range(abs(X_MIN) + abs(X_MAX)+1)] for i in range(abs(Y_MIN) + abs(Y_MAX)+1)]

for y in range(Y_MIN, Y_MAX + 1):
	for x in range(X_MIN, X_MAX + 1):
		yidx = Y_MAX - y
		xidx = X_MAX - x
		tmp[yidx][xidx] = BLUE if bot.act(x, y, VEL) == NOT_FLAP else RED

a = np.array(tmp)
plt.imshow(a,extent=[X_MAX,X_MIN,Y_MIN,Y_MAX])#, interpolation='nearest',interpolation='bicubic',cmap='hot'
plt.grid(True)
plt.savefig(OUT_IMAGE, dpi=DPI)

