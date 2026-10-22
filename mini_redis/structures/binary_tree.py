from .linked_list import LinkedList


class BinaryTreeNode:
    """A node with at most two children."""

    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right


class BinaryTree:
    """A binary tree with depth-first and level-order traversals."""

    def __init__(self, root=None):
        self.root = root

    def preorder(self):
        result = []

        def visit(node):
            if node is None:
                return
            result.append(node.data)
            visit(node.left)
            visit(node.right)

        visit(self.root)
        return result

    def inorder(self):
        result = []

        def visit(node):
            if node is None:
                return
            visit(node.left)
            result.append(node.data)
            visit(node.right)

        visit(self.root)
        return result

    def postorder(self):
        result = []

        def visit(node):
            if node is None:
                return
            visit(node.left)
            visit(node.right)
            result.append(node.data)

        visit(self.root)
        return result

    def level_order(self):
        if self.root is None:
            return []

        result = []
        queue = LinkedList()
        queue.insert_back(self.root)
        while queue.size():
            node = queue.remove_front()
            result.append(node.data)
            if node.left is not None:
                queue.insert_back(node.left)
            if node.right is not None:
                queue.insert_back(node.right)
        return result
