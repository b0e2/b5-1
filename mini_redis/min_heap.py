class MinHeap:
    """Array-backed minimum heap for comparable items."""

    def __init__(self):
        self._items = []

    def size(self):
        return len(self._items)

    def peek(self):
        if not self._items:
            return None
        return self._items[0]

    def push(self, item):
        self._items.append(item)
        self._heapify_up(len(self._items) - 1)

    def pop(self):
        if not self._items:
            return None
        smallest = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._heapify_down(0)
        return smallest

    def _heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if not self._items[index] < self._items[parent]:
                break
            self._items[index], self._items[parent] = self._items[parent], self._items[index]
            index = parent

    def _heapify_down(self, index):
        size = len(self._items)
        while True:
            left = 2 * index + 1
            right = left + 1
            smallest = index
            if left < size and self._items[left] < self._items[smallest]:
                smallest = left
            if right < size and self._items[right] < self._items[smallest]:
                smallest = right
            if smallest == index:
                break
            self._items[index], self._items[smallest] = self._items[smallest], self._items[index]
            index = smallest
