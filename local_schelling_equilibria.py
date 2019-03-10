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
		self.max_type = "Red" if n_red >= n_blue else "Blue"
		self.min_type = "Red" if self.max_type == "Blue" else "Blue"

		seed = self.graph.GetRndNId()
		self.assignment[seed] = self.max_type
		print("Seed node is ID #{}".format(seed))

		hop_counts = snap.TIntPrV()
		snap.GetNodesAtHops(self.graph, seed, hop_counts, False)
		nodes_reachable = np.cumsum([item.GetVal2() for item in hop_counts])
		min_hop = np.min(np.where(nodes_reachable >= max(n_red, n_blue))) + 1

		n_assigned, cur_hop = 1, 0
		max_type_neighbors = snap.TIntV()

		# Drop red nodes on BFS tree
		while n_assigned < max(n_red, n_blue):
			cur_hop += 1
			candidates = snap.TIntV()
			snap.GetNodesAtHop(self.graph, seed, cur_hop, candidates, False)
			for node in candidates:
				self.assignment[node] = self.max_type
				n_assigned += 1
				neighbors = snap.TIntV()
				snap.GetNodesAtHop(self.graph, node, 1, neighbors, False)
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

		# No neighbors --> no happiness...
		if (friends + enemies) == 0:
			return 0

		return(1.0 * friends/(friends + enemies))

	# Entertain a deviation from old_nid --> new_nid; returns True if the agent in old_nid is... happier deviating
	def is_happier_deviating(self, old_nid, new_nid):
		assert(old_nid in self.assignment.keys() and new_nid not in self.assignment.keys())
		cur_happiness = self.get_happiness_ratio(old_nid)
		self.assignment[new_nid] = self.assignment.pop(old_nid)
		new_happiness = self.get_happiness_ratio(new_nid)
		self.assignment[old_nid] = self.assignment.pop(new_nid)
		return (new_happiness > cur_happiness)

	def check_equilibrium(self):
		all_nodes = list(range(self.graph.GetNodes()))
		empty_nodes = list(set(all_nodes) - set(self.assignment.keys()))

		# We only need to make sure that no neighboring max_type agents would deviate
		# to each empty node; min_type agents won't deviate by construction of the algorithm
		for empty_node in empty_nodes:
			neighbors = snap.TIntV()
			snap.GetNodesAtHop(self.graph, empty_node, 1, neighbors, False)
			for node in neighbors:
				node_is_max_type = (node in self.assignment.keys()) and (self.assignment[node] == self.max_type)
				if node_is_max_type and self.is_happier_deviating(node, empty_node):
					print("{}-type node #{} would like to deviate to {}. Not an equilibrium!".format(self.max_type, node, empty_node))
					return

		print("This assignment is an equilibrium!")

	def save_graph(self):
		labels = snap.TIntStrH()
		filled_nodes = self.assignment.keys()
		# assert(len(filled_nodes) > 0)
		for i in range(self.graph.GetNodes()):
			if i in filled_nodes:
				labels[i] = str(i) + ": " + self.assignment[i]
			else:
				labels[i] = str(i) + ": "
		snap.DrawGViz(self.graph, snap.gvlDot, "assignment.png", " ", labels)

if __name__ == "__main__":
	schell = SchellingGame(15, 30)
	schell.init_placement(6, 6)
	schell.check_equilibrium()
	schell.save_graph()
