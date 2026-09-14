# This scaler is meant to act like sklearn's MinMaxScaler, yet in a more robust
# way: instead of fitting on the global column-wise minimum and maximum of the
# dataset, the most extreme percentiles of each column are discarded. This makes
# the scaler more resilient to outliers while also using an internal linear model.

# StableScalerMinMax limitations:
# - 'outlier_ratio' is applied on each dimension independantly,
#   so this will not work well for a large number of dimensions.
# - This treats each column equally, which might not be desired.

import json
import numpy as np

class StableScalerMinMax:
	def __init__(self):
		self.xMinArray = None
		self.xMaxArray = None
		self.scaleArray = None
		self.offsetArray = None
		self.output_range = None
		self.outlier_ratio = None

	def __init_check(self):
		assert self.output_range is not None, "Cannot process, the scaler was not fitted to any data."

	# Returns the samples dimensions seen during fit.
	def dimensions(self):
		self.__init_check()
		return self.scaleArray.shape

	# If 'outlier_ratio' receive only 1 value, it will be used for both sides.
	def fit(self, data, output_range: tuple=(0., 1.), outlier_ratio: tuple=(0.01, 0.01)):
		data = np.asarray(data)
		l, r = outlier_ratio[0], outlier_ratio[-1]
		assert len(output_range) == 2 and output_range[0] < output_range[1]
		assert 0. <= l and 0. <= r and l + r < 1.
		assert len(data) > 0, "No data to be fitted on."
		assert np.isfinite(data).all(), "Data contains non finite values."
		self.output_range = output_range
		self.outlier_ratio = outlier_ratio
		self.xMinArray = np.nanpercentile(data, l * 100., axis=0)
		self.xMaxArray = np.nanpercentile(data, (1.-r) * 100., axis=0)
		self.scaleArray = np.divide(output_range[1] - output_range[0], self.xMaxArray - self.xMinArray,
			out=np.zeros_like(self.xMinArray), where=self.xMinArray < self.xMaxArray)
		self.offsetArray = output_range[0] - self.scaleArray * self.xMinArray

	def transform(self, data, clip: bool=False):
		self.__init_check()
		data = np.asarray(data)
		result = self.offsetArray + self.scaleArray * data
		if clip:
			np.clip(result, self.output_range[0], self.output_range[1], out=result)
		return result

	def fit_transform(self, data, output_range: tuple=(0., 1.),
			outlier_ratio: tuple=(0.01, 0.01), clip: bool=False):
		self.fit(data, output_range=output_range, outlier_ratio=outlier_ratio)
		return self.transform(data, clip=clip)

	def inverse_transform(self, data): # assumes no clipping has been done.
		self.__init_check()
		data = np.asarray(data)
		out = np.broadcast_to(self.xMinArray, data.shape).copy()
		return np.divide(data - self.offsetArray, self.scaleArray, out=out, where=self.scaleArray != 0.)

	# Returns a numpy array of the same length as the input, filled with boolean values.
	def get_outliers(self, data):
		self.__init_check()
		data = np.asarray(data)
		axis = tuple(range(1, data.ndim))
		return ((data < self.xMinArray) | (self.xMaxArray < data)).any(axis=axis)

	def save(self, path: str):
		self.__init_check()
		with open(path, "w") as file:
			numpyToList = lambda x : x.tolist() if type(x) == np.ndarray else x
			json.dump({ key : numpyToList(value) for (key, value) in vars(self).items() }, file)
			print(f"Saved scaler to: '{path}'")

	@staticmethod
	def load(path: str):
		with open(path, "r") as file:
			d = json.load(file)
			scaler = StableScalerMinMax()
			for key, value in d.items():
				value = np.array(value) if type(value) == list else value
				setattr(scaler, key, value)
			print(f"Loaded scaler from: '{path}'")
			return scaler

	def print(self):
		print("Scaler info:", *vars(self).items(), sep="\n")


if __name__ == "__main__":

	##########################################
	# Dataset loading / creation:

	# Random values:
	np.random.seed(123)
	data = np.random.uniform(low=0.0, high=1.0, size=(20, 2))
	# data = np.random.uniform(low=0.0, high=1.0, size=(20,))

	# # Digit Dataset:
	# from sklearn.datasets import load_digits
	# data = load_digits().data
	# data = data.astype("uint8")
	# data = data.reshape((len(data), 8, 8)) # 2D shaped data
	# # data = data[:, :2] # 2 dimensions only

	# # MNIST Dataset:
	# from tensorflow import keras
	# (data, _), (_, _) = keras.datasets.mnist.load_data()
	# # data = data.reshape(data.shape[0], -1) # (n, p*q), each row is one flattened entry

	##########################################
	# Scaler fitting and usage:

	print("Data:", data, f"shape: {data.shape}", sep="\n")

	scaler = StableScalerMinMax()
	scaler.fit(data, output_range=(0., 1.), outlier_ratio=(0.01, 0.01))

	path = "scaler.json"
	scaler.save(path)
	scaler = StableScalerMinMax.load(path)
	scaler.print()

	normalized = scaler.transform(data, clip=False)
	print("\nNormalized data:", normalized, f"shape: {normalized.shape}", sep="\n")

	denormalized = scaler.inverse_transform(normalized)
	print("\nDenormalized data:", denormalized, f"shape: {denormalized.shape}", sep="\n")

	outliers = scaler.get_outliers(data)
	print(f"\nFound {outliers.sum()} outliers:", outliers, f"shape: {outliers.shape}", sep="\n")
