import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import argparse
from scipy.spatial import distance

A = 1
B = -1

class SwapSchellingGame(object):
	def __init__(self, dim, tau, pct_A, max_iter):
		self.dim = dim
		self.tau = tau
		self.max_iter = max_iter
		self.grid = np.zeros((self.dim, self.dim))
		self.unhappy_agents = {
			A : [],
			B : []
		}
		self.ims = []
		self.fig = plt.figure()
		self.init_locations(pct_A)

	def init_locations(self, pct_A):
		self.grid = np.random.choice([A, B], (self.dim, self.dim), p = [pct_A, 1-pct_A])

	def compute_grid_happiness(self):
		for row in range(self.dim):
			for col in range(self.dim):
				h = self.compute_agent_happiness(row, col)
				if h <= self.tau:
					self.unhappy_agents[self.grid[(row, col)]].append((row, col))

	def compute_agent_happiness(self, row, col):
		neighbors = self.grid[max(0, row-1):min(self.dim, row+2), max(0,col-1):min(self.dim, col+2)]
		h = (np.sum(neighbors == self.grid[(row, col)])-1.0)/((neighbors.shape[0]*neighbors.shape[1])-1.0)
		return h

	def swap(self):
		while self.unhappy_agents[A] and self.unhappy_agents[B]:
			A_loc = self.unhappy_agents[A].pop()
			B_loc = self.unhappy_agents[B].pop()
			self.grid[A_loc] = B; self.grid[B_loc] = A

	def find_equilibrium(self):
		n_iter = 0
		self.take_snapshot()
		while n_iter <= self.max_iter:
			n_iter += 1
			self.compute_grid_happiness()
			self.swap()
			self.take_snapshot()

	def take_snapshot(self):
		im = plt.imshow(self.grid, cmap = "bwr", animated = True)
		self.ims.append([im])

	def animate(self):
		ani = animation.ArtistAnimation(self.fig, self.ims, interval = 200, blit = True, repeat_delay = 500)
		plt.axis("off")
		plt.title("Swap Schelling Game on a " + str(self.dim) + "x" + str(self.dim) + " grid")
		plt.show()

############################################################################################

COMMON_FAVORITE = 0 
CONTENTNESS = 0
DISTANCE = 1

class CF_SwapSchellingGame(SwapSchellingGame):
	def __init__(self, dim, tau, pct_A, max_iter):
		super().__init__(dim, tau, pct_A, max_iter)
		self.common_favorite = self.select_random_favorite()
		self.happiness = {}
		print ("Common favorite node for all agents is " + str(self.common_favorite))

	def select_random_favorite(self):
		f = np.random.choice(range(self.dim**2))
		return np.unravel_index(f, (self.dim, self.dim))

	def compute_grid_happiness(self):
		for row in range(self.dim):
			for col in range(self.dim):
				h = self.compute_agent_happiness(row, col)
				self.happiness[(row, col)] = h
				if h[CONTENTNESS] <= self.tau:
					self.unhappy_agents[self.grid[(row, col)]].append((row, col))

	def compute_agent_happiness(self, row, col):
		neighbors = self.grid[max(0, row-1):min(self.dim, row+2), max(0,col-1):min(self.dim, col+2)]
		h = (np.sum(neighbors == self.grid[(row, col)])-1.0)/((neighbors.shape[0]*neighbors.shape[1])-1.0)
		d = distance.euclidean((row, col), self.common_favorite)
		return np.array([h, d])

	'''
	Suppose an agent of type A is unhappy (h, d) with h <= self.tau:
		- The agent will switch with any agent of the opposite type who is also 
		  unhappy, regardless of their distance to the CF goal. 

	Suppose an agent of type A is happy (h, d) with h > self.tau:
		- They might switch with a type B agent who is closer to the goal iff their position 
		  improves the happiness of the type B agent

	==> Agents of both types and happiness states will swap. Unhappy As will swap with unhappy Bs. 
		Happy As will swap with unhappy Bs. Happy Bs will swap with unhappy As. (If distance decreases.)
		Only happy agents will not swap with each other. 

	Algorithm:
		For each agent:
			If the agent is happy: 
				Find an unhappy agent of opposite color closer to CF. If found, swap. If none, end. 
			If the agent is unhappy:
				Swap with a random unhappy agent of the opposite color.
	'''
	def is_happy(self, row, col):
		return ((row, col) not in self.unhappy_agents[self.grid[(row, col)]])

	def counterparts_exist(self, row, col):
		return (len(self.unhappy_agents[-self.grid[(row, col)]]) > 0)

	def execute_swap(self, row, col):
		is_happy = self.is_happy(row, col)
		distance_improvement_exists = \
			self.unhappy_agents[-self.grid[(row, col)]][0][DISTANCE] < self.happiness[(row, col)][DISTANCE]
		if (is_happy and distance_improvement_exists) or (not is_happy):
			counterpart = self.unhappy_agents[-self.grid[(row, col)]].pop()
			self.grid[counterpart] = self.grid[(row, col)]
			self.grid[(row, col)] = -self.grid[(row, col)]

	def swap(self):
		self.unhappy_agents[A].sort(key = lambda x : x[DISTANCE])
		self.unhappy_agents[B].sort(key = lambda x : x[DISTANCE])
		agents = list(range(self.dim**2)); random.shuffle(agents)
		while agents and (self.unhappy_agents[A] or self.unhappy_agents[B]):
			row, col = np.unravel_index(agents.pop(), (self.dim, self.dim))
			if self.counterparts_exist(row, col):
				self.execute_swap(row, col)

	def take_snapshot(self):
		tmp = self.grid[self.common_favorite].copy()
		self.grid[self.common_favorite] = COMMON_FAVORITE
		im = plt.imshow(self.grid, cmap = "bwr", animated = True)
		self.ims.append([im])
		self.grid[self.common_favorite] = tmp

############################################################################################

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--dim", type=int, default=25)
	parser.add_argument("--tau", type=float, default=0.5)
	parser.add_argument("--pct_A", type=float, default=0.5)
	parser.add_argument("--max_iter", type=int, default=200)
	parser.add_argument("--common_favorite", dest="cf", action="store_true")
	args = parser.parse_args()

	model = CF_SwapSchellingGame(args.dim, args.tau, args.pct_A, args.max_iter) if args.cf else \
		SwapSchellingGame(args.dim, args.tau, args.pct_A, args.max_iter)
	model.find_equilibrium()
	model.animate()

if __name__ == "__main__":
	main()