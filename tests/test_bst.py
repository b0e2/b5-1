import unittest

from mini_redis.bst import BinarySearchTree


class BinarySearchTreeTest(unittest.TestCase):
    def test_empty_tree_and_unique_inserts(self):
        tree = BinarySearchTree()
        self.assertFalse(tree.search(3))
        self.assertFalse(tree.delete(3))
        self.assertEqual(tree.inorder(), [])
        self.assertTrue(tree.insert(3))
        self.assertFalse(tree.insert(3))
        self.assertTrue(tree.search(3))
        self.assertEqual(tree.inorder(), [3])
        self.assertTrue(tree.delete(3))
        self.assertFalse(tree.delete(3))
        self.assertEqual(tree.inorder(), [])

    def test_inorder_sorted_and_inherited_traversals(self):
        tree = BinarySearchTree()
        for value in (8, 3, 10, 1, 6, 14, 4, 7, 13):
            self.assertTrue(tree.insert(value))
        self.assertEqual(tree.inorder(), [1, 3, 4, 6, 7, 8, 10, 13, 14])
        self.assertEqual(tree.preorder(), [8, 3, 1, 6, 4, 7, 10, 14, 13])
        self.assertEqual(tree.level_order(), [8, 3, 10, 1, 6, 14, 4, 7, 13])
        self.assertTrue(tree.search(13))
        self.assertFalse(tree.search(12))

    def test_delete_leaf_one_child_and_two_children(self):
        tree = BinarySearchTree()
        for value in (8, 3, 10, 1, 6, 14, 4, 7, 13):
            tree.insert(value)
        self.assertTrue(tree.delete(1))
        self.assertEqual(tree.inorder(), [3, 4, 6, 7, 8, 10, 13, 14])
        self.assertTrue(tree.delete(14))
        self.assertEqual(tree.inorder(), [3, 4, 6, 7, 8, 10, 13])
        self.assertTrue(tree.delete(3))
        self.assertEqual(tree.inorder(), [4, 6, 7, 8, 10, 13])
        self.assertTrue(tree.delete(8))
        self.assertEqual(tree.inorder(), [4, 6, 7, 10, 13])
        for removed in (1, 3, 8, 14):
            self.assertFalse(tree.search(removed))
            self.assertFalse(tree.delete(removed))

    def test_delete_root_with_deep_successor(self):
        tree = BinarySearchTree()
        for value in (8, 3, 12, 10, 14, 9, 11):
            tree.insert(value)
        self.assertTrue(tree.delete(8))
        self.assertEqual(tree.inorder(), [3, 9, 10, 11, 12, 14])
        self.assertEqual(tree.root.data, 9)
        self.assertFalse(tree.search(8))
        self.assertTrue(tree.search(9))
        for value in (9, 12, 3, 10, 11, 14):
            self.assertTrue(tree.delete(value))
        self.assertEqual(tree.inorder(), [])
        self.assertIsNone(tree.root)

    def test_skewed_tree_and_negative_values(self):
        tree = BinarySearchTree()
        for value in (-2, -1, 0, 1):
            tree.insert(value)
        self.assertEqual(tree.inorder(), [-2, -1, 0, 1])
        self.assertTrue(tree.delete(-2))
        self.assertEqual(tree.inorder(), [-1, 0, 1])
        self.assertTrue(tree.delete(1))
        self.assertEqual(tree.inorder(), [-1, 0])


if __name__ == "__main__":
    unittest.main()
