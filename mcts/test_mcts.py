import unittest
from node import TreeNode
from mcts import MonteCarlo

class TestMonteCarlo(unittest.TestCase):

	def test_choice_is_correct(self):
		montecarlo = MonteCarlo(TreeNode(0))
		montecarlo.child_finder = self.child_finder
		montecarlo.node_evaluator = self.node_evaluator

		montecarlo.simulate(1, 1, 50)

		chosen_node = montecarlo.make_choice()
		self.assertIs(chosen_node.state, 1)

		exploratory_node = montecarlo.make_exploratory_choice()
		self.assertTrue(chosen_node != None)

	def child_finder(self, node, montecarlo):
		if node.state == 0:
			node.add_children([TreeNode(1), TreeNode(-1)])
		else:
			for i in range(2):
				modifier = (100 if i == 1 else 200) * (-1 if node.state < 0 else 1)
				node.add_child(TreeNode(node.state + modifier))

	def node_evaluator(self, node, montecarlo):
		if node.state > 1000:
			return 1
		elif node.state < -1000:
			return -1