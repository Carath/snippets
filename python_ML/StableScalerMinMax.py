import json
import numpy as np

# Will convert the argument to a numpy array, while doing no
# copy if it already is. To copy it, use np.array(x) instead.
convertToNumpyArray = lambda x : x if type(x) == np.ndarray else np.array(x)

numpyToList = lambda x : x.tolist() if type(x) == np.ndarray else x

class StableScalerMinMax:
	def __init__(self):
		self.output_range = None
		self.xMinArray = None
		self.xMaxArray = None
		self.scaleArray = None
		self.offsetArray = None

	def __init_check(self):
		assert self.output_range is not None, "Cannot process, the scaler was not fitted to any data."

	# Returns the samples dimensions seen during fit.
	def dimensions(self):
		self.__init_check()
		return self.scaleArray.shape

	def fit(self, data, output_range=(0., 1.), outlier_ratio=0.02):
		data = convertToNumpyArray(data)
		assert len(output_range) == 2 and output_range[0] < output_range[1] and 0. <= outlier_ratio <= 1.
		assert len(data) > 0, "No data to be fitted on."
		assert np.isfinite(data).sum() == len(data.flatten()), "Data contains non finite values."
		self.output_range = output_range
		self.xMinArray = np.nanpercentile(data, outlier_ratio/2. * 100., axis=0)
		self.xMaxArray = np.nanpercentile(data, (1.-outlier_ratio/2.) * 100., axis=0)
		self.scaleArray = np.divide(output_range[1] - output_range[0], self.xMaxArray - self.xMinArray,
			out=np.zeros_like(self.xMinArray), where=self.xMinArray < self.xMaxArray)
		self.offsetArray = output_range[0] - self.scaleArray * self.xMinArray

	def transform(self, data, clip=False):
		self.__init_check()
		data = convertToNumpyArray(data)
		result = self.offsetArray + self.scaleArray * data
		if clip:
			np.clip(result, self.output_range[0], self.output_range[1], out=result)
		return result

	def fit_transform(self, data, output_range=(0., 1.), outlier_ratio=0.02, clip=False):
		self.fit(data, output_range=output_range, outlier_ratio=outlier_ratio)
		return self.transform(data, clip=clip)

	def inverse_transform(self, data): # assumes no clipping has been done.
		self.__init_check()
		data = convertToNumpyArray(data)
		return np.divide(data - self.offsetArray, self.scaleArray,
			out=self.xMinArray.copy(), where=self.scaleArray != 0)

	# Returns a numpy array of the same length as the input, filled with boolean values.
	def get_outliers(self, data):
		self.__init_check()
		data = convertToNumpyArray(data)
		return np.logical_or(data < self.xMinArray, self.xMaxArray < data).any(axis=1)

	def save(self, path):
		self.__init_check()
		with open(path, "w") as file:
			json.dump({ key : numpyToList(value) for (key, value) in vars(self).items() }, file)
			print(f"Saved scaler to: '{path}'")

	@staticmethod
	def load(path):
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

	from sklearn.datasets import load_digits
	data = load_digits().data
	data = data.astype("uint8")
	data = data.reshape((len(data), 8, 8)) # 2D shaped data
	# data = data.tolist() # converting to lists
	# data = data[:, :2] # 2 dimensions only

	print("data:", data[:2], "...\n",
		"data shape:", np.array(data).shape, "", sep="\n")

	scaler = StableScalerMinMax()
	scaler.fit(data, output_range=(0., 1.), outlier_ratio=0.02)

	path = "scaler.json"
	scaler.save(path)
	scaler = StableScalerMinMax.load(path)
	scaler.print()

	normalized = scaler.transform(data, clip=False)
	print("\nnormalized data:", normalized[:2], "...", sep="\n")

	denormalized = scaler.inverse_transform(normalized)
	print("\ndenormalized data:", denormalized[:2], "...", sep="\n")

	outliers = scaler.get_outliers(data)
	print("\noutliers:", outliers[:2], "...", sep="\n")

# StableScalerMinMax issues:
# - Outlier_ratio is applied on each dimension independantly,
#   so this will not work well for a large number of dimensions.
# - This treats column equally, where it probably shoudn't.
# - Works well only on symmetrical distributions.
