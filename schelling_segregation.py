import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.animation as animation

A = 1
B = -1

## Initially work with a Schelling swap model where the entire gridworld is occupied
## by agents of two types
class SchellingSegregationModel(object):
	def __init__(self, dim, tau):
		self.dim = dim
		self.tau = tau
		self.gridworld = np.zeros((dim + 2, dim + 2))
		self.happiness = np.zeros((dim + 2, dim + 2))
		self.unhappy_As = []
		self.unhappy_Bs = []
		self.terminate = False
		self.im = None

		self.__initialize_types()

	## Let the two types be represented by +1 (A) and -1 (B)
	## on the gridworld map
	def __initialize_types(self):
		types = np.array([A, B])
		positions = np.random.choice(types, (self.dim, self.dim))
		self.gridworld[1:(self.dim+1),1:(self.dim+1)] = positions

	def __compute_happiness(self):
		for row in range(self.dim):
			for column in range(self.dim):
				neighborhood = self.gridworld[row:(row+2),column:(column+2)]
				current_happiness = (1.0)*len(neighborhood == neighborhood[1,1])/(len(neighborhood[neighborhood == A]) + \
					len(neighborhood[neighborhood == B]))
				self.happiness[row+1,column+1] = current_happiness

		no_As_unhappy = len(self.unhappy_As)
		no_Bs_unhappy = len(self.unhappy_Bs)

		self.unhappy_As += list(np.argwhere((self.gridworld == A) & (self.happiness <= self.tau)))
		self.unhappy_Bs +=  list(np.argwhere((self.gridworld == B) & (self.happiness <= self.tau)))

		if (no_As_unhappy == len(self.unhappy_As) and no_Bs_unhappy == len(self.unhappy_Bs)):
			self.terminate = True 

	def __iterate_swaps(self):
		for pair in range(min(len(self.unhappy_As), len(self.unhappy_Bs))):
			curr_A = self.unhappy_As.pop()
			curr_B = self.unhappy_Bs.pop()

			print(curr_A)

			self.gridworld[tuple(curr_A)] = B
			self.gridworld[tuple(curr_B)] = A

	def find_equilibrium(self):
		n_iters = 0

		try:
			self.__compute_happiness()
			while (len(self.unhappy_As) > 0 or len(self.unhappy_Bs) > 0):
				n_iters += 1
				self.__iterate_swaps()
				# self.__plot_positions()
				self.__compute_happiness()
				# plt.show()

				if self.terminate:
					break

		except KeyboardInterrupt:
		 	print("Executed %d iterations of the Swap Schelling Game, tau = %f" % (n_iters, self.tau))

############################################################################################

def main():
	fig = plt.figure()
	model = SchellingSegregationModel(10, 0.5)
	model.find_equilibrium()


if __name__ == "__main__":
	main()