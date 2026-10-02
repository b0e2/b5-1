class DynamicArray:
    """Resizable array backed by an explicitly sized list."""

    def __init__(self, capacity=4):
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self._capacity = capacity
        self._items = [None] * capacity
        self._size = 0

    @property
    def capacity(self):
        return self._capacity

    def size(self):
        return self._size

    def __len__(self):
        return self._size

    def _check_index(self, index):
        if not isinstance(index, int) or index < 0 or index >= self._size:
            raise IndexError("array index out of range")

    def _grow(self):
        new_capacity = self._capacity * 2
        items = [None] * new_capacity
        for index in range(self._size):
            items[index] = self._items[index]
        self._items = items
        self._capacity = new_capacity

    def append(self, value):
        if self._size == self._capacity:
            self._grow()
        self._items[self._size] = value
        self._size += 1

    def get(self, index):
        self._check_index(index)
        return self._items[index]

    def set(self, index, value):
        self._check_index(index)
        self._items[index] = value

    def remove(self, index):
        value = self.get(index)
        for position in range(index, self._size - 1):
            self._items[position] = self._items[position + 1]
        self._size -= 1
        self._items[self._size] = None
        return value

    def pop(self):
        if self._size == 0:
            raise IndexError("pop from empty array")
        return self.remove(self._size - 1)

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, index, value):
        self.set(index, value)
