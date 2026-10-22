from .binary_tree import BinaryTree, BinaryTreeNode


class BinarySearchTree(BinaryTree):
    """Binary search tree with unique, orderable values."""

    def insert(self, value):
        """Insert a new value and return whether it was added."""
        if self.root is None:
            self.root = BinaryTreeNode(value)
            return True

        node = self.root
        while True:
            if value == node.data:
                return False
            if value < node.data:
                if node.left is None:
                    node.left = BinaryTreeNode(value)
                    return True
                node = node.left
            else:
                if node.right is None:
                    node.right = BinaryTreeNode(value)
                    return True
                node = node.right

    def search(self, value):
        """Return whether a value exists in the tree."""
        node = self.root
        while node is not None:
            if value == node.data:
                return True
            node = node.left if value < node.data else node.right
        return False

    def delete(self, value):
        """Remove a value and return whether it existed."""
        def remove(node, target):
            if node is None:
                return None, False
            if target < node.data:
                node.left, removed = remove(node.left, target)
                return node, removed
            if target > node.data:
                node.right, removed = remove(node.right, target)
                return node, removed

            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True

            successor = node.right
            while successor.left is not None:
                successor = successor.left
            node.data = successor.data
            node.right, _ = remove(node.right, successor.data)
            return node, True

        self.root, removed = remove(self.root, value)
        return removed
