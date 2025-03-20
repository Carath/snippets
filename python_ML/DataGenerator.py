from math import ceil
import numpy as np
import keras

def inverse_permutation(p):
	inv = np.empty_like(p)
	inv[p] = np.arange(len(p))
	return inv

# Behavior: one epoch is defined by going through batches of data, from index 0 to __len__()-1.
# During one epoch, the data is shuffled and some operation can be done on it (e.g. normalizing
# or adding noise) by applying a function 'process_data' which should use its own RNG passed as
# argument. Additionally an epoch might contain several cycles of going through the whole data.
# Each cycle can be different to the other (shuffling or noise). However when 'epoch_invariance'
# is True (typically during validation), each full epoch will yield the very same output. Finally
# batches of data will always have the same size when 'const_batch_size' is set to True (even if
# 'batch_size' does not divide the data length).
class DataGenerator(keras.utils.PyDataset):

	def __init__(self, x, y, batch_size: int,
		dtype=None, process_data=None, const_batch_size: bool=True,
		cycles: int=1, seed: int=0, epoch_invariance: bool=False, **kwargs):

		super().__init__(**kwargs)
		assert len(x) == len(y), f"Incompatible data lengths: {len(x)} vs {len(y)}"
		self.x, self.y = np.array(x, dtype=dtype), np.array(y, dtype=dtype)
		self.batch_size = batch_size
		self.process_data = process_data
		self.seed = round(time.time()) if seed == 0 else seed
		self.epoch_invariance = epoch_invariance
		self.batch_number = len(self.x) // self.batch_size
		if not const_batch_size:
			self.batch_number = ceil(len(self.x) / self.batch_size)
		self.length = self.batch_number * cycles
		self.rng = None
		if process_data is None:
			print("DataGenerator: no process_data given.")

	# Returns the number of batches while cycling.
	def __len__(self):
		return self.length

	# Returns x, y for batch 'idx'.
	def __getitem__(self, idx):

		# Setting the RNG and resetting the data when needed:
		if self.rng is None or (self.epoch_invariance and idx % self.length == 0):
			if self.rng is not None:
				self.permut_comp = inverse_permutation(self.permut_comp)
				self.x = self.x[self.permut_comp]
				self.y = self.y[self.permut_comp]
			self.permut_comp = np.arange(len(self.x))
			self.rng = np.random.default_rng(self.seed)
			# Creating a new random generator instead of np.random, the static numpy RNG.

		if idx % self.batch_number == 0: # shuffling the data at each cycle start.
			permut = self.rng.permutation(len(self.x))
			self.x = self.x[permut]
			self.y = self.y[permut]
			if self.epoch_invariance:
				self.permut_comp = self.permut_comp[permut]

		low = (idx % self.batch_number) * self.batch_size
		high = min(low + self.batch_size, len(self.x))
		batch_x, batch_y = self.x[low:high], self.y[low:high]
		if self.process_data is not None:
			batch_x, batch_y = self.process_data(batch_x, batch_y, rng=self.rng)
		return batch_x, batch_y


if __name__ == "__main__":

	def addNoise(x, y, rng=None):
		if rng is None:
			rng = np.random # static numpy RNG, best not to use it here.
		noise = rng.normal(size=x.shape, loc=0., scale=np.full(x.shape, 0.1))
		return x + noise, y

	np.random.seed(42)
	x = np.random.randint(low=0, high=10, size=(6, 2))
	y = np.random.randint(low=0, high=3, size=(6,))

	dag = DataGenerator(x, y, 2, process_data=addNoise, cycles=2, seed=123, epoch_invariance=True)

	for epoch in range(3):
		for i in range(dag.__len__()):
			batch_x, batch_y = dag.__getitem__(i)
			print(batch_x, batch_y)
		print()

# TODO:
# - Enable to load only a part of the dataset at a given time, and iterate over it all.
# - Enable to load data from files or directories.
