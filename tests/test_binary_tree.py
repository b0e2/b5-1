import unittest

from mini_redis.binary_tree import BinaryTree, BinaryTreeNode


class BinaryTreeTest(unittest.TestCase):
    def test_empty_tree(self):
        tree = BinaryTree()
        self.assertEqual(tree.preorder(), [])
        self.assertEqual(tree.inorder(), [])
        self.assertEqual(tree.postorder(), [])
        self.assertEqual(tree.level_order(), [])

    def test_single_node_with_none_data(self):
        tree = BinaryTree(BinaryTreeNode(None))
        for traverse in (tree.preorder, tree.inorder, tree.postorder,
                         tree.level_order):
            self.assertEqual(traverse(), [None])

    def test_asymmetric_tree(self):
        root = BinaryTreeNode("A",
                              BinaryTreeNode("B", BinaryTreeNode("D"),
                                             BinaryTreeNode("E")),
                              BinaryTreeNode("C", right=BinaryTreeNode("F")))
        tree = BinaryTree(root)
        self.assertEqual(tree.preorder(), ["A", "B", "D", "E", "C", "F"])
        self.assertEqual(tree.inorder(), ["D", "B", "E", "A", "C", "F"])
        self.assertEqual(tree.postorder(), ["D", "E", "B", "F", "C", "A"])
        self.assertEqual(tree.level_order(), ["A", "B", "C", "D", "E", "F"])
        root.left.data = "BB"
        self.assertEqual(tree.level_order(), ["A", "BB", "C", "D", "E", "F"])

    def test_left_and_right_skewed_trees(self):
        left = BinaryTree(BinaryTreeNode(3, BinaryTreeNode(
            2, BinaryTreeNode(1))))
        right = BinaryTree(BinaryTreeNode(1, right=BinaryTreeNode(
            2, right=BinaryTreeNode(3))))
        self.assertEqual(left.preorder(), [3, 2, 1])
        self.assertEqual(left.inorder(), [1, 2, 3])
        self.assertEqual(left.postorder(), [1, 2, 3])
        self.assertEqual(left.level_order(), [3, 2, 1])
        self.assertEqual(right.preorder(), [1, 2, 3])
        self.assertEqual(right.inorder(), [1, 2, 3])
        self.assertEqual(right.postorder(), [3, 2, 1])
        self.assertEqual(right.level_order(), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
