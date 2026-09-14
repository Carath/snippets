# Example of training on a _very_ unbalanced dataset.

# Requirements:
# numpy==2.0.2
# matplotlib==3.10.0
# scikit-learn==1.6.1
# tensorflow==2.18.0
# keras==3.8.0

import random, math, os, csv, time
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
# print("Tensorflow version:", tf.__version__)

from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score

from scipy import ndimage # for image rotations

from DataGenerator import DataGenerator
from StableScalerMinMax import StableScalerMinMax

##########################################
# Settings:

digit_neg = 3
digit_pos = 5

# Removing from the train set almost all instances from the second class:
threshold = 0.01

useNormalization = True
# useNormalization = False

useAugmentation = True
# useAugmentation = False

addNoise = True
# addNoise = False

noiseLevel_add = 20.
noiseLevel_mul = 0.10
noiseLevel_ang = 20

# useClassWeight = True
useClassWeight = False

batch_size = 32
dropout = 0.75

##########################################
# For consistency:

seed = 42
random.seed(seed)
np.random.seed(seed)
keras.utils.set_random_seed(seed)
tf.random.set_seed(seed)

##########################################
# Dataset loading:

(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
# (x_train, y_train), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()
# (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()

cutoff = 2*len(y_test)
x_train, x_valid = x_train[:-cutoff], x_train[-cutoff:]
y_train, y_valid = y_train[:-cutoff], y_train[-cutoff:]

src_input_shape = x_train.shape[1:] # 28x28
input_shape = x_train[0].flatten().shape # 784
print("src_input_shape:", src_input_shape)
print("input_shape:", input_shape)
assert digit_neg != digit_pos, "Same digit!"

x_train = np.array([ img.flatten() for img in x_train ], dtype="float32")
x_valid = np.array([ img.flatten() for img in x_valid ], dtype="float32")
x_test  = np.array([ img.flatten() for img in x_test  ], dtype="float32")

y_train = y_train.reshape((-1, 1)) # necessary for 'f1_metric'
y_valid = y_valid.reshape((-1, 1))
y_test  = y_test.reshape((-1, 1))

print(x_train.shape)
print(y_train.shape)
print(x_valid.shape)
print(y_valid.shape)
print(x_test.shape)
print(y_test.shape)

def noisyImage(img, rng=None):
	if addNoise:
		if rng is None:
			rng = np.random # static numpy RNG

		# # Multiplicative noise:
		# noise = rng.uniform(low=1.-noiseLevel_add, high=1.+noiseLevel_add, size=img.shape)
		# # noise = rng.normal(loc=1., scale=noiseLevel_mul, size=img.shape)
		# img = (img * noise).round().clip(0, 255)

		# Additive noise:
		mask = ((img > 0) * 255).astype("uint8")
		noise = rng.uniform(low=-noiseLevel_add, high=noiseLevel_add, size=img.shape)
		#noise = rng.normal(loc=0., scale=noiseLevel_add, size=img.shape)
		# noise = noise.round().clip(0, 255).astype("uint8") & mask
		# noise = rng.normal(loc=0., scale=noiseLevel_add, size=img.shape).round()
		img = (img + noise).clip(0, 255)

		# # Random rotations - do not use it, black frame issue!
		# angle = float(rng.uniform(-noiseLevel_ang, noiseLevel_ang, size=1)[0])
		# # angle = float(rng.normal(loc=0., scale=noiseLevel_ang, size=1)[0])

		# if len(img.shape) == 1:
		# 	# plt.imshow(img.reshape(*src_input_shape), cmap="binary")
		# 	img = ndimage.rotate(img.reshape(*src_input_shape), angle, reshape=False, order=1)
		# 	img = img.flatten().round().astype("uint8")
		# 	# plt.imshow(img.reshape(*src_input_shape), cmap="binary")
		# 	# plt.show()
		# 	# exit()
		# else:
		# 	img = np.array([ ndimage.rotate(x.reshape(*src_input_shape), angle,
		# 		reshape=False, order=1).flatten().round().astype("uint8") for x in img ])
	return img

def buildBinaryDataset(X, y, createScarcity: bool):
	newX, newY = [], []
	for i in range(len(y)):
		if y[i] == digit_neg:
			newX.append(X[i])
			newY.append(0)
		elif y[i] == digit_pos and (not createScarcity or random.random() < threshold):
			newX.append(X[i])
			newY.append(1)
	return np.array(newX), np.array(newY).reshape((-1, 1))

# Must be called after buildBinaryDataset()
def augmentDataset(X, y, enableAugmentation: bool, cycles: int=1):
	if not enableAugmentation:
		return X, y
	newX, newY = [], []
	for k in range(cycles):
		for i in range(len(y)):
			if y[i] == 0:
				newX.append(noisyImage(X[i]))
				newY.append(y[i])
			else:
				for k in range(round(1./threshold)):
					newX.append(noisyImage(X[i])) # different noise each time
					newY.append(y[i])
	return np.array(newX), np.array(newY).reshape((-1, 1))

def countLabel(y):
	d = {}
	for label in y:
		label = int(label[0])
		if label not in d:
			d[label] = 0
		d[label] += 1
	return d

# Building the datasets:
x_train, y_train = buildBinaryDataset(x_train, y_train, True) # scarcity
x_valid, y_valid = buildBinaryDataset(x_valid, y_valid, True) # scarcity
x_test , y_test  = buildBinaryDataset(x_test , y_test, False) # no scarcity, no augmentation!

print("Before the augmentation:")
print("d_train:", countLabel(y_train))
print("d_valid:", countLabel(y_valid))
print("d_test: ", countLabel(y_test), "\n")

# Rare event augmentation:
x_train, y_train = augmentDataset(x_train, y_train, useAugmentation) # augmented with noise!
x_valid, y_valid = augmentDataset(x_valid, y_valid, useAugmentation) # augmented with noise!

if useAugmentation:
	print("After the augmentation:")
	print("d_train:", countLabel(y_train))
	print("d_valid:", countLabel(y_valid))
	print("d_test: ", countLabel(y_test), "\n")

# Scaler fitting (for demonstration purposes, here one could just divide by 255):
scaler = StableScalerMinMax()
scaler.fit(x_train, output_range=(0., 1.), outlier_ratio=0.02)

path = "scaler.json"
scaler.save(path)
scaler = StableScalerMinMax.load(path)

# Adding noise and normalizing the data:
def process_data(img, label, rng):
	img = noisyImage(img, rng=rng)
	if useNormalization:
		img = scaler.transform(img)
	return (img, label)

# prior: class augmentation (with a bit of noise to not repeat).
dag_train = DataGenerator(x_train, y_train, batch_size,
	process_data=process_data, cycles=1, seed=321)
dag_valid = DataGenerator(x_valid, y_valid, batch_size,
	process_data=process_data, cycles=2, seed=654, epoch_invariance=True)

# b = dag_train.__getitem__(0)
# import matplotlib.pyplot as plt
# for i in range(5):
# 	print(b[1][i])
# 	plt.imshow((b[0][i].reshape(28, 28, 1) * 255).astype("uint8"), cmap="gray")
# 	# plt.imshow((b[0][i].reshape(32, 32, 3) * 255).astype("uint8"), cmap="gray")
# 	plt.show()
# exit()

# Normalization:
if useNormalization:
	x_train = scaler.transform(x_train)
	x_valid = scaler.transform(x_valid)
	x_test  = scaler.transform(x_test)

print("x_train.shape:", x_train.shape)
print("y_train.shape:", y_train.shape)
print("x_valid.shape:", x_valid.shape)
print("y_valid.shape:", y_valid.shape)
print("x_test.shape: ", x_test.shape)
print("y_test.shape: ", y_test.shape, "\n")

n_class = len(set(map(int, y_train.flatten())) | set(map(int, y_valid.flatten())))
print("n_class:", n_class)
# exit()

##########################################
# Model definition:

# model = keras.models.Sequential([
# 	keras.layers.Input(shape=input_shape),
# 	keras.layers.Dense(64, activation="relu"),
# 	keras.layers.Dropout(dropout),
# 	keras.layers.BatchNormalization(),
# 	keras.layers.Dense(n_class if n_class > 2 else 1,
# 		activation="softmax" if n_class > 2 else "sigmoid")
# ])

model = keras.models.Sequential([
	keras.layers.Input((*input_shape, 1)),
	keras.layers.Conv1D(32, kernel_size=1, strides=1, activation="relu"),
	keras.layers.BatchNormalization(),
	keras.layers.Dropout(dropout),
	keras.layers.MaxPooling1D(pool_size=2, strides=2),
	keras.layers.Conv1D(16, kernel_size=5, strides=1, activation="relu"),
	keras.layers.BatchNormalization(),
	keras.layers.Dropout(dropout),
	keras.layers.MaxPooling1D(pool_size=2, strides=2),
	keras.layers.Flatten(),
	keras.layers.Dense(16, activation="relu"),
	keras.layers.BatchNormalization(),
	keras.layers.Dropout(dropout),
	keras.layers.Dense(n_class if n_class > 2 else 1,
		activation="softmax" if n_class > 2 else "sigmoid")
])

# ********** choice of F1 type **********
f1_metric = tf.keras.metrics.F1Score(average=None, threshold=0.5)
# f1_metric = tf.keras.metrics.F1Score(average="macro", threshold=0.5) # seems bugged
# f1_metric = tf.keras.metrics.F1Score(average="micro", threshold=0.5)
# f1_metric = tf.keras.metrics.F1Score(average="weighted", threshold=0.5)

model.compile(
	optimizer="adam",
	metrics=[
		# "accuracy",
		f1_metric
	],
	# loss="sparse_categorical_crossentropy",

	# ********** choice of standard loss function **********
	# loss="binary_crossentropy",
	loss="mean_squared_error",
)

model.summary()

modelPath = "model.keras"

model_checkpoint_callback = keras.callbacks.ModelCheckpoint(
	filepath=modelPath,
	save_best_only=True,
	verbose=1,
	# save_freq=1,

	# ********** choice of metric used for the model selection **********
	monitor="val_loss",
	# monitor="f1_score",
)

early_stopping_callback = keras.callbacks.EarlyStopping(
	# ********** choice of metric used for the early stopping **********
	monitor="val_loss",
	# monitor="f1_score",

	patience=5,
	verbose=0,
)

d_train = countLabel(y_train)
class_weight = { 0: 1., 1: 1. } # no weights
if useClassWeight:
	class_weight = { 0: d_train[1], 1: d_train[0] }
	# class_weight = { 0: 1./d_train[0], 1: 1./d_train[1] }
	# class_weight = { 0: d_train[1]/d_train[0], 1: 1. }
	# class_weight = { 0: 1., 1: d_train[0]/d_train[1] }
	# class_weight = { 0: threshold, 1: 1. }
	# class_weight = { 0: 1., 1: 1./threshold }

start = time.time()
history = model.fit(

	# x=x_train, y=y_train,
	dag_train,

	validation_data=(x_valid, y_valid),
	# validation_data=dag_valid,

	epochs=20,
	batch_size=batch_size,
	callbacks=[model_checkpoint_callback, early_stopping_callback],

	# ********** weighting the loss computation for unbalanced datasets **********
	class_weight=class_weight,
)
end = time.time()
print("Elapsed time: %.3f s\n" % (end-start))

model = keras.models.load_model(modelPath)

model.evaluate(x_train, y_train, verbose=2)
model.evaluate(x_valid, y_valid , verbose=2)
# print(model.evaluate(x_train, y_train, verbose=2, return_dict=True))
# print(model.evaluate(x_valid, y_valid , verbose=2, return_dict=True))

print("\n" + "-" * 50 + "\n")
print("Training stats:\n")
ref, pred = y_train, model.predict(x_train, verbose=0).round()
print(confusion_matrix(ref, pred, labels=[0, 1]).flatten(), "\n")
print(classification_report(ref, pred, digits=4, zero_division=0))

print("\n" + "-" * 50 + "\n")
print("Validation stats:\n")
ref, pred = y_valid, model.predict(x_valid, verbose=0).round()
print(confusion_matrix(ref, pred, labels=[0, 1]).flatten(), "\n")
print(classification_report(ref, pred, digits=4, zero_division=0))

print("\n" + "-" * 50 + "\n")
print("Test stats:\n")
ref, pred = y_test, model.predict(x_test, verbose=0).round()
print(confusion_matrix(ref, pred, labels=[0, 1]).flatten(), "\n")
print(classification_report(ref, pred, digits=4, zero_division=0))

# f1 = f1_score(ref, pred, average="binary", zero_division=0) # default
# print(f"F1 Score (binary):      {f1:.4f}")

# f1 = f1_score(ref, pred, average="micro", zero_division=0)
# print(f"F1 Score (micro):       {f1:.4f}")

# f1 = f1_score(ref, pred, average="macro", zero_division=0)
# print(f"F1 Score (macro):       {f1:.4f}")

# f1 = f1_score(ref, pred, average="weighted", zero_division=0)
# print(f"F1 Score (weighted):    {f1:.4f}")
