import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import argparse

A = 1
B = -1

class SwapSchellingGame(object):
	def __init__(self, dim, tau, pct_A, max_iter = 200):
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
		self.take_snapshot()

	def init_locations(self, pct_A):
		self.grid = np.random.choice([A, B], (self.dim, self.dim), p = [pct_A, 1-pct_A])

	def compute_grid_happiness(self):
		for row in range(self.dim):
			for column in range(self.dim):
				h = self.compute_agent_happiness(row, column)
				if h <= self.tau:
					self.unhappy_agents[self.grid[(row, column)]].append((row, column))

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

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("dim", type=int)
	parser.add_argument("tau", type=float)
	parser.add_argument("pct_A", type=float)
	args = parser.parse_args()

	model = SwapSchellingGame(args.dim, args.tau, args.pct_A)
	model.find_equilibrium()
	model.animate()

if __name__ == "__main__":
	main()