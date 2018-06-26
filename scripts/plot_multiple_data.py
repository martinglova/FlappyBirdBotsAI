import csv
import os
import matplotlib.pyplot as plt
import numpy as np

# dpi of figure
DPI=500
# number of previous values to calculate average
TREND_ACCURACY=1000

TESTS_COUNT = 100

TYPE = "lr"
FOLDER_BASE = "../../data/" + TYPE + "/"

colors = ["#000000", "#0000FF", "#A52A2A", "#7FFF00", "#DC143C", "#006400",\
	"#FF8C00", "#FF1493", "#FFD700", "#808080", "#669900", "#ff66ff"]

indices = ["0.00001","0.1","0.2","0.3","0.4","0.5","0.6","0.7","0.8","0.9","0.99999","1"]

files =\
	[["0.00001/scores_q_learning_" + TYPE + "_0.00001_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.1/scores_q_learning_" + TYPE + "_0.1_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.2/scores_q_learning_" + TYPE + "_0.2_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.3/scores_q_learning_" + TYPE + "_0.3_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.4/scores_q_learning_" + TYPE + "_0.4_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.5/scores_q_learning_" + TYPE + "_0.5_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.6/scores_q_learning_" + TYPE + "_0.6_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.7/scores_q_learning_" + TYPE + "_0.7_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.8/scores_q_learning_" + TYPE + "_0.8_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.9/scores_q_learning_" + TYPE + "_0.9_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["0.99999/scores_q_learning_" + TYPE + "_0.99999_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)],\
	["1/scores_q_learning_" + TYPE + "_1_" + str(i+1) + ".csv" for i in range(TESTS_COUNT)]]

data = 	[\
			[\
				[\
					float(line.split(',')[1])\
					for line in open(FOLDER_BASE + f, 'r').read().split()\
				]\
				for f in files[i]\
			]\
			for i in range(len(files))\
		]

col = {}

info_file = open(FOLDER_BASE + TYPE + ".txt", "w")
#print(data)
def add_to_plot(idx):
	best_average = 0
	highest_score = 0
	all_best_scores = [0]*TESTS_COUNT
	all_best_averages = [0]*TESTS_COUNT
	iterations = []
	averages = []
	scores = {}
	averages_tmp = {}
	for i in range(TESTS_COUNT):
		scores[i] = []
		averages_tmp[i] = []

	for i in range(len(data[idx][0])):
		iterations.append(i)
		for j in range(len(data[idx])):
			actual_score = data[idx][j][i]
			scores[j].append(actual_score)
			if actual_score > highest_score: highest_score = actual_score
			if actual_score > all_best_scores[j]: all_best_scores[j] = actual_score
			# calculating trend
			actual_average = np.mean(scores[j][-TREND_ACCURACY:])
			if actual_average > best_average: best_average = actual_average
			if actual_average > all_best_averages[j]: all_best_averages[j] = actual_average
			averages_tmp[j].append(actual_average)
		averages.append(np.mean([averages_tmp[k][i] for k in averages_tmp]))

	col[indices[idx]]=[iterations,averages,colors[idx]]
	worse_score_single = min(all_best_scores)
	worse_average_single = min(all_best_averages)

	message = "Highest score for " + indices[idx] + " is " + str(highest_score) + " with highest average " + str(best_average) + "."
	print(message)
	info_file.write(message+"\n")
	message = "Smallest score for " + indices[idx] + " is " + str(worse_score_single) + " with smallest average " + str(worse_average_single) + "."
	print(message)
	info_file.write(message+"\n")

for i in range(len(files)):
	add_to_plot(i)

for i in range(len(files)):
	plt.plot(col[indices[i]][0], col[indices[i]][1], col[indices[i]][2], label=indices[i], linewidth=2)

plt.xlim(0, 50000)
plt.legend(loc=2, borderaxespad=.5)
plt.xlabel('Iterations')
plt.ylabel('Scores')
plt.savefig(FOLDER_BASE + TYPE + ".png", dpi=DPI)
info_file.close()
