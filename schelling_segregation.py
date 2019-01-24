import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

## Let the two types of agents be represented by +1 (A) and -1 (B) on the gridworld
A = 1
B = -1
NO_OCCUPANT = 0

class SchellingSegregationModel(object):
	def __init__(self, dim, tau, max_iter):
		self.dim = dim
		self.tau = tau
		self.max_iter = max_iter

		self.gridworld = np.zeros((dim + 2, dim + 2))
		self.happiness = np.zeros((dim + 2, dim + 2))
		self.unhappy_As = []
		self.unhappy_Bs = []

		self.ims = []

	def compute_happiness(self):
		for row in range(self.dim):
			for column in range(self.dim):
				## What's the more efficient way to do this?
				neighborhood = self.gridworld[row:(row+3),column:(column+3)].copy() 
				cell = neighborhood[1, 1]
				neighborhood[1, 1] = 0
				current_happiness = 0 if np.all(neighborhood == 0) else \
					(1.0)*(np.sum(neighborhood == cell))/(np.sum(neighborhood == A) + np.sum(neighborhood == B))
				self.happiness[row+1,column+1] = current_happiness

		self.unhappy_As += list(np.argwhere((self.gridworld == A) & (self.happiness <= self.tau)))
		self.unhappy_Bs += list(np.argwhere((self.gridworld == B) & (self.happiness <= self.tau)))

	def take_snapshot(self):
		im = plt.imshow(self.gridworld, cmap = "bwr", animated = True)
		self.ims.append([im])

	## Empty method redefined in subclasses
	def iterate_relocation(self):
		return

	def find_equilibrium(self):
		n_iters = 0
		try:
			self.compute_happiness()
			while self.unhappy_As or self.unhappy_Bs:
				n_iters += 1
				self.iterate_relocation()
				self.take_snapshot()
				self.compute_happiness()
				if n_iters == self.max_iter:
					break
		except KeyboardInterrupt:
			pass

		print("Executed %d iterations of the Schelling Game, tau = %f" % (n_iters, self.tau))

class SchellingSwapModel(SchellingSegregationModel):
	def __init__(self, dim, tau, max_iter = 100):
		SchellingSegregationModel.__init__(self, dim, tau, max_iter)
		self.__initialize_types()
		self.take_snapshot()

	def __initialize_types(self):
		types = np.array([A, B])
		positions = np.random.choice(types, (self.dim, self.dim))
		self.gridworld[1:(self.dim+1),1:(self.dim+1)] = positions

	def iterate_relocation(self):
		for pair in range(min(len(self.unhappy_As), len(self.unhappy_Bs))):
			curr_A = self.unhappy_As.pop()
			curr_B = self.unhappy_Bs.pop()
			self.gridworld[tuple(curr_A)] = B
			self.gridworld[tuple(curr_B)] = A

class SchellingJumpModel(SchellingSegregationModel):
	def __init__(self, dim, tau, pct_agents, pct_A, max_iter = 10):
		assert(pct_agents < 1)
		SchellingSegregationModel.__init__(self, dim, tau, max_iter)
		self.__initialize_types(pct_agents, pct_A)
		self.take_snapshot()

	def __initialize_types(self, pct_agents, pct_A):
		types = np.array([A, B, NO_OCCUPANT])
		pct_A = (1.0)*(pct_A)*(pct_agents)
		pct_B = (1.0 - pct_A)*(pct_agents)
		weights = [pct_A, pct_B, (1.0 - pct_A - pct_B)]
		positions = np.random.choice(types, (self.dim, self.dim), p = weights)
		self.gridworld[1:(self.dim+1),1:(self.dim+1)] = positions

	def iterate_relocation(self):
		es = np.argwhere(self.gridworld == NO_OCCUPANT)
		empty_spaces = es[(es[:,0] > 0) & (es[:,0] < (self.dim-1)) \
			& (es[:,1] > 0) & (es[:,1] < (self.dim-1))]
		np.random.shuffle(empty_spaces)
		empty_spaces = list(empty_spaces)
		print(self.gridworld)
		random.shuffle(self.unhappy_As); random.shuffle(self.unhappy_Bs)

		while (self.unhappy_As or self.unhappy_Bs) and empty_spaces:
			curr_agent = self.unhappy_As.pop() if len(self.unhappy_As) > 0 else \
				self.unhappy_Bs.pop()
			print(curr_agent)
			new_location = empty_spaces.pop()
			self.gridworld[tuple(new_location)] = self.gridworld[tuple(curr_agent)]
			self.gridworld[tuple(curr_agent)] = NO_OCCUPANT
			empty_spaces.append(curr_agent)

############################################################################################

def main():
	fig = plt.figure()
	model = SchellingSwapModel(100, 0.5)
	# model = SchellingJumpModel(10, 0.5, 0.75, 0.5)
	model.find_equilibrium()
	ani = animation.ArtistAnimation(fig, model.ims, interval = 200, blit = True, repeat_delay = 1000)
	plt.axis("off")
	plt.title("Schelling Jump Segregation Game on a " + str(model.dim) + "x" + str(model.dim) + " grid")
	plt.show()

if __name__ == "__main__":
	main()