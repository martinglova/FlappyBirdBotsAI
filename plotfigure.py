import csv
import numpy as np
import matplotlib.pyplot as plt

# dpi of figure
DPI=500
# number of previous values to calculate average
TREND_ACCURACY=150

colors = ["#0000FF", "#A52A2A", "#000000", "#7FFF00", "#DC143C", "#006400",\
	"#FF8C00", "#FF1493", "#FFD700", "#808080", "#669900", "#ff66ff"]

# runp plotfigure.py plot_figure:"data.csv","image.png"
def plot_figure(in_csv_file, out_image_file):
	iterations = []
	scores = []
	averages = []
	with open(in_csv_file, 'r') as csvfile:
		rows = csv.reader(csvfile, delimiter=',')
		#i = 0
		for row in rows:
			iterations.append(float(row[0]))
			scores.append(float(row[1]))
			averages.append(np.mean(scores[-TREND_ACCURACY:]))
	
	plt.xlim(len(iterations) + 150)
	plt.gca().invert_xaxis()
	plt.xlabel('Iterations')
	plt.ylabel('Scores')
	plt.title("Q-network")
	# plotting real values
	plt.plot(iterations, scores, 'r.')
	# plotting trend
	plt.plot(iterations, averages, "b")
	plt.savefig(out_image_file, dpi=DPI)
	plt.clf()

SCORE_IDX = 1
# runp plotfigure.py plot_scores_with_average:"greedy_scores.csv","greedy_scores.png"
def plot_scores_with_average(in_csv_file, out_image_file):
	iterations = []
	scores = []
	i=1
	with open(in_csv_file, 'r') as csvfile:
		rows = csv.reader(csvfile, delimiter=',')
		for row in rows:
			score = int(row[SCORE_IDX])
			scores.append(score)
			iterations.append(i)
			i+=1
	average = np.mean(scores)
	
	plt.xlim(len(scores))
	plt.gca().invert_xaxis()
	plt.xlabel('Games')
	plt.ylabel('Scores')
	plt.plot(iterations, scores, 'r.', color="blue")
	plt.plot(iterations, [average for i in range(len(iterations))], "b")
	plt.text(len(scores)*0.8,average*1.05,str(average), color="black")

	plt.savefig(out_image_file, dpi=DPI)
	plt.clf()

FILES = ["ql.csv", "dql.csv"]
# runp plotfigure.py plot_scores_with_average_compare:"comparison.png"
def plot_scores_with_average_compare(out_image_file):
	XLIM = 100
	plt.xlim(XLIM)
	plt.gca().invert_xaxis()
	plt.xlabel('Games')
	plt.ylabel('Scores')

	for j in range(len(FILES)):
		iterations = []
		scores = []
		i=1
		with open(FILES[j], 'r') as csvfile:
			rows = csv.reader(csvfile, delimiter=',')
			for row in rows:
				if i > XLIM: break
				score = int(row[SCORE_IDX])
				scores.append(score)
				iterations.append(i)
				i+=1
				
		average = np.mean(scores)

		plt.scatter(iterations, scores, color=colors[j], s=0.1)
		plt.plot(iterations, [average for k in range(len(iterations))], "b", color=colors[j])
		plt.text(XLIM*0.85,average+400,str(round(average,2)))

	plt.savefig(out_image_file, dpi=DPI)
	plt.clf()
