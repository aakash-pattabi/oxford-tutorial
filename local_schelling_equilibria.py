import numpy as np
import snap
import graphviz

class SchellingGame(object):
	def __init__(self, nodes, edges, edge_list = None):
		if edge_list is None:
			G = snap.GenRndGnm(snap.PUNGraph, nodes, edges)
			self.graph = snap.GetMxWcc(G)
		else:
			self.graph = snap.LoadEdgeList(snap.PUNGraph, edge_list, 0, 1)
		self.assignment = {}
		self.max_type, self.min_type = None, None

	def init_placement(self, n_red, n_blue):
		assert(n_red + n_blue < self.graph.GetNodes())
		self.max_type = "Red" if n_red > n_blue else "Blue"
		self.min_type = "Red" if self.max_type == "Blue" else "Blue"
		seed = self.graph.GetRndNId()
		bfs_tree = snap.GetBfsTree(self.graph, seed, True, False)

		n_assigned = 0
		max_type_neighbors = snap.TIntV()

		# Drop red nodes on BFS tree
		for node in bfs_tree.Nodes():
			nid = node.GetId()
			self.assignment[nid] = self.max_type
			n_assigned += 1
			neighbors = snap.TIntV()
			snap.GetNodesAtHop(self.graph, nid, 1, neighbors, False)
			max_type_neighbors.Union(neighbors)
			if n_assigned == max(n_red, n_blue):
				break

		# Drop blue nodes on nodes in graph with no neighboring red nodes
		n_assigned = 0
		max_type_neighbors.Merge()
		for node in self.graph.Nodes():
			nid = node.GetId()
			if nid not in max_type_neighbors:
				self.assignment[nid] = self.min_type
				n_assigned += 1
				if n_assigned == min(n_red, n_blue):
					break 

		# If we've assigned all agents, we're done. Else, look for the "middle path"
		# where some nodes border (current) red and blue placements
		if n_assigned < min(n_red, n_blue):
			occupied = snap.TIntV()
			for key in self.assignment.keys():
				occupied.Add(key)

			middle_path = snap.TIntV()
			for node in self.graph.Nodes():
				middle_path.Add(node.GetId())

			middle_path.Diff(occupied)
			minority_happiness = {}
			for node in middle_path:
				minority_happiness[node] = self.get_happiness_ratio(node, hypothetical_type = self.min_type)

			empty_nodes = minority_happiness.keys()
			hypothetical_happiness = [minority_happiness[node] for node in empty_nodes]
			sorted_nodes = [node for __, node in sorted(zip(hypothetical_happiness, empty_nodes))]

			n_to_assign = min(n_red, n_blue) - n_assigned
			for i in range(n_to_assign):
				self.assignment[sorted_nodes[i]] = self.min_type

	def get_happiness_ratio(self, nid, hypothetical_type = None):
		own_type = hypothetical_type if hypothetical_type is not None else self.assignment[nid]
		neighbors = snap.TIntV()
		snap.GetNodesAtHop(self.graph, nid, 1, neighbors, False)
		friends, enemies = 0, 0
		for neighbor in neighbors:
			if neighbor in self.assignment.keys():
				if self.assignment[neighbor] == own_type:
					friends += 1
				else:
					enemies += 1
		return(1.0*friends/(friends + enemies))

	def check_equilibrium(self):
		all_nodes = list(range(self.graph.GetNodes()))
		empty_nodes = list(set(all_nodes) - set(self.assignment.keys()))

		# We only need to make sure that no neighboring max_type agents would deviate
		# to each empty node; min_type agents won't deviate by construction of the algorithm
		for node in empty_nodes:
			neighbors = snap.TIntV()
			snap.GetNodesAtHop(self.graph, node, 1, neighbors, False)
			max_type_happiness_at_empty = self.get_happiness_ratio(node, hypothetical_type = self.max_type)
			neighboring_max_type_happiness = [self.get_happiness_ratio(neighb) for neighb in neighbors \
				if (neighb in self.assignment.keys() and self.assignment[neighb] == self.max_type)]
			if np.min(neighboring_max_type_happiness) < max_type_happiness_at_empty:
				print("Some [red] neighbor to the middle path would deviate! This is not an equilibrium")
				return 

		print("This assignment is an equilibrium!")

	def save_graph(self):
		labels = snap.TIntStrH()
		filled_nodes = self.assignment.keys()
		assert(len(filled_nodes) > 0)
		for i in range(self.graph.GetNodes()):
			if i in filled_nodes:
				labels[i] = str(i) + ": " + self.assignment[i]
			else:
				labels[i] = str(i) + ": "
		snap.DrawGViz(self.graph, snap.gvlDot, "assignment.png", " ", labels)

if __name__ == "__main__":
	schell = SchellingGame(20, 30)
	schell.init_placement(8, 8)
	schell.check_equilibrium()
	schell.save_graph()
