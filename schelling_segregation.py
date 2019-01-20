import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.animation as animation

## Let the two types of agents be represented by +1 (A) and -1 (B) on the gridworld map
A = 1
B = -1

## Schelling swap model where the arbitrarily sized gridworld is completely occupied
class SchellingSegregationModel(object):
	def __init__(self, dim, tau, max_iter = 100):
		self.dim = dim
		self.tau = tau
		self.max_iter = max_iter

		self.gridworld = np.zeros((dim + 2, dim + 2))
		self.happiness = np.zeros((dim + 2, dim + 2))
		self.unhappy_As = []
		self.unhappy_Bs = []

		self.ims = []
		self.__initialize_types()
		self.__take_snapshot()

	def __initialize_types(self):
		types = np.array([A, B])
		positions = np.random.choice(types, (self.dim, self.dim))
		self.gridworld[1:(self.dim+1),1:(self.dim+1)] = positions

	def __compute_happiness(self):
		for row in range(self.dim):
			for column in range(self.dim):
				neighborhood = self.gridworld[row:(row+3),column:(column+3)]
				current_happiness = \
					(1.0)*(np.sum(neighborhood == neighborhood[1,1]) - 1)/ \
					(np.sum(neighborhood == A) + np.sum(neighborhood == B) - 1)
				self.happiness[row+1,column+1] = current_happiness

		self.unhappy_As += list(np.argwhere((self.gridworld == A) & (self.happiness <= self.tau)))
		self.unhappy_Bs += list(np.argwhere((self.gridworld == B) & (self.happiness <= self.tau)))

	def __take_snapshot(self):
		im = plt.imshow(self.gridworld, cmap = "bwr", animated = True)
		self.ims.append([im])

	def __iterate_swaps(self):
		for pair in range(min(len(self.unhappy_As), len(self.unhappy_Bs))):
			curr_A = self.unhappy_As.pop()
			curr_B = self.unhappy_Bs.pop()
			self.gridworld[tuple(curr_A)] = B
			self.gridworld[tuple(curr_B)] = A
		self.__take_snapshot()

	def find_equilibrium(self):
		n_iters = 0
		try:
			self.__compute_happiness()
			while (len(self.unhappy_As) > 0 or len(self.unhappy_Bs) > 0):
				n_iters += 1
				self.__iterate_swaps()
				self.__compute_happiness()
				if n_iters == self.max_iter:
					break
		except KeyboardInterrupt:
			pass

		print("Executed %d iterations of the Swap Schelling Game, tau = %f" % (n_iters, self.tau))

############################################################################################

def main():
	fig = plt.figure()
	model = SchellingSegregationModel(100, 0.5)
	model.find_equilibrium()
	ani = animation.ArtistAnimation(fig, model.ims, interval = 250, blit = True, repeat_delay = 1000)
	plt.tick_params(axis = "both", which = "both", bottom = False, top = False, labelbottom = False)
	plt.show()

if __name__ == "__main__":
	main()