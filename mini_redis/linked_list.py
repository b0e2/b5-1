class Node:
    """A doubly linked list node."""

    def __init__(self, data):
        self.prev = None
        self.next = None
        self.data = data
        self._owner = None


class LinkedList:
    """Doubly linked list with constant-time changes at a known node."""

    def __init__(self):
        self._head = Node(None)
        self._tail = Node(None)
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    def size(self):
        return self._size

    def _insert_between(self, node, before, after):
        node.prev = before
        node.next = after
        node._owner = self
        before.next = node
        after.prev = node

    def insert_front(self, data):
        node = Node(data)
        self._insert_between(node, self._head, self._head.next)
        self._size += 1
        return node

    def insert_back(self, data):
        node = Node(data)
        self._insert_between(node, self._tail.prev, self._tail)
        self._size += 1
        return node

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        node._owner = None

    def remove_node(self, node):
        if node._owner is not self:
            raise ValueError("node is not in this list")
        self._unlink(node)
        self._size -= 1
        return node.data

    def remove_front(self):
        if self._size == 0:
            return None
        return self.remove_node(self._head.next)

    def remove_back(self):
        if self._size == 0:
            return None
        return self.remove_node(self._tail.prev)

    def move_to_front(self, node):
        if node._owner is not self:
            raise ValueError("node is not in this list")
        if node.prev is self._head:
            return
        self._unlink(node)
        self._insert_between(node, self._head, self._head.next)

    def iter_nodes(self):
        node = self._head.next
        while node is not self._tail:
            yield node
            node = node.next

    def __iter__(self):
        for node in self.iter_nodes():
            yield node.data
