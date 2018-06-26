import tensorflow as tf
import os.path

INPUT_LEN = 3
OUTPUT_LEN = 2
HIDDEN_LAYERS = [600,200]

# example: tf.tanh, tf.sigmoid, tf.nn.relu, tf.identity
LAST_LAYER_AF = tf.tanh
OTHER_LAYERS_AF = [tf.tanh]*len(HIDDEN_LAYERS)
LEARNING_RATE = 0.01

# example: tf.train.GradientDescentOptimizer, tf.train.AdagradOptimizer,
# tf.train.AdadeltaOptimizer, tf.train.AdamOptimizer,
# tf.train.FtrlOptimizer, tf.train.ProximalAdagradOptimizer,
# tf.train.ProximalGradientDescentOptimizer, tf.train.RMSPropOptimizer
OPTIMIZER = tf.train.AdamOptimizer
INIT_WEIGHTS = tf.random_normal #tf.random_normal, tf.zeros

IN_PLACEHOLDER = tf.placeholder(shape=[None, INPUT_LEN], dtype=tf.float32)  
OUT_PLACEHOLDER = tf.placeholder(shape=[None, OUTPUT_LEN], dtype=tf.float32)

class FNN(object):

	def __init__(self, optimizer, index):
		self.index = index
		self.fnn_directory = "./FNN" + str(index) + "/"
		self.fnn_file = self.fnn_directory + "FNN.ckpt"
		# creating network
		layers = [INPUT_LEN] + HIDDEN_LAYERS + [OUTPUT_LEN]
		self.last_tensor = IN_PLACEHOLDER
		afs = OTHER_LAYERS_AF + [LAST_LAYER_AF]

		for i in range(0, len(layers) - 1):
			weights = tf.Variable(INIT_WEIGHTS([layers[i], layers[i+1]]))
			bias = tf.Variable(tf.zeros([layers[i+1]]))
			af = afs[i]
			out = af(tf.add(tf.matmul(self.last_tensor, weights), bias))
			self.last_tensor = out
		
		error = tf.subtract(OUT_PLACEHOLDER, self.last_tensor)
		self.mse = tf.reduce_mean(tf.square(error))
		
		self.train = optimizer(learning_rate=LEARNING_RATE).minimize(self.mse)

		self.sess = tf.Session()
		self.sess.run(tf.global_variables_initializer())
		print("Network initialized.")
		
		self.saver = tf.train.Saver()
		if os.path.isdir(self.fnn_directory):
			print("Network restored.")
			self.saver.restore(self.sess, self.fnn_file)

	def train_step(self, input_data, output_data, train_count):
		if train_count <= 0: return
		for i in range(train_count):
			_, err, _ = self.sess.run(fetches=[self.train, self.mse, self.last_tensor],\
				feed_dict={IN_PLACEHOLDER: input_data,\
				OUT_PLACEHOLDER: output_data})
		return err

	def predict(self, data):
		return self.sess.run(fetches=self.last_tensor,\
			feed_dict={IN_PLACEHOLDER: data})

	def save(self):
		self.saver.save(self.sess, self.fnn_file)

	def close(self):
		self.save()
		self.sess.close()
