from .linked_list import LinkedList


class _Entry:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class HashMap:
    """String-keyed hash map using separate chaining."""

    def __init__(self, capacity=8):
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self._buckets = [None] * capacity
        self._size = 0

    def _hash(self, key):
        """Compute an FNV-1a hash from the UTF-8 bytes of a key."""
        value = 2166136261
        for byte in key.encode("utf-8"):
            value ^= byte
            value = (value * 16777619) & 0xFFFFFFFF
        return value

    def _find_node(self, key, bucket):
        if bucket is not None:
            for node in bucket.iter_nodes():
                if node.data.key == key:
                    return node
        return None

    def put(self, key, value):
        index = self._hash(key) % len(self._buckets)
        bucket = self._buckets[index]
        node = self._find_node(key, bucket)
        if node is not None:
            old = node.data.value
            node.data.value = value
            return old

        if bucket is None:
            bucket = LinkedList()
            self._buckets[index] = bucket
        bucket.insert_back(_Entry(key, value))
        self._size += 1
        if self._size * 4 > len(self._buckets) * 3:
            self._resize()
        return None

    def _resize(self):
        old_buckets = self._buckets
        self._buckets = [None] * (len(old_buckets) * 2)
        self._size = 0
        for bucket in old_buckets:
            if bucket is not None:
                for entry in bucket:
                    self.put(entry.key, entry.value)

    def get(self, key):
        index = self._hash(key) % len(self._buckets)
        node = self._find_node(key, self._buckets[index])
        return None if node is None else node.data.value

    def remove(self, key):
        index = self._hash(key) % len(self._buckets)
        bucket = self._buckets[index]
        node = self._find_node(key, bucket)
        if node is None:
            return None
        value = bucket.remove_node(node).value
        self._size -= 1
        if bucket.size() == 0:
            self._buckets[index] = None
        return value

    def contains(self, key):
        index = self._hash(key) % len(self._buckets)
        return self._find_node(key, self._buckets[index]) is not None

    def keys(self):
        result = []
        for bucket in self._buckets:
            if bucket is not None:
                for entry in bucket:
                    result.append(entry.key)
        return result

    def size(self):
        return self._size
