import time

from .hash_map import HashMap
from .linked_list import LinkedList
from .min_heap import MinHeap
from .pubsub import PubSub


class _Record:
    def __init__(self, value, lru_node):
        self.value = value
        self.lru_node = lru_node
        self.expires_at = None
        self.expiry_id = None


class MiniRedis:
    """In-memory string store with LRU eviction and lazy TTL cleanup."""

    def __init__(self, clock=None):
        self._clock = clock if clock is not None else time.monotonic
        self._data = HashMap()
        self._lru = LinkedList()
        self._expirations = MinHeap()
        self._next_expiry_id = 0
        self._pubsub = PubSub()
        self.used_memory = 0
        self.maxmemory = 0
        self.evicted_keys = 0

    def _entry_size(self, key, value):
        return len(key.encode("utf-8")) + len(value.encode("utf-8"))

    def _remove(self, key, evicted=False):
        record = self._data.remove(key)
        self._lru.remove_node(record.lru_node)
        self.used_memory -= self._entry_size(key, record.value)
        if evicted:
            self.evicted_keys += 1

    def _purge_expired(self, now):
        while self._expirations.peek() is not None:
            expires_at, key, expiry_id = self._expirations.peek()
            if expires_at > now:
                break
            self._expirations.pop()
            record = self._data.get(key)
            if record is not None and record.expiry_id == expiry_id:
                self._remove(key)

    def set(self, key, value):
        """Store a value, returning False without changing it if it cannot fit."""
        self._purge_expired(self._clock())
        new_size = self._entry_size(key, value)
        if self.maxmemory and new_size > self.maxmemory:
            return False

        record = self._data.get(key)
        if record is None:
            node = self._lru.insert_front(key)
            self._data.put(key, _Record(value, node))
            self.used_memory += new_size
        else:
            self.used_memory += new_size - self._entry_size(key, record.value)
            record.value = value
            record.expires_at = None
            record.expiry_id = None
            self._lru.move_to_front(record.lru_node)

        while self.maxmemory and self.used_memory > self.maxmemory:
            self._remove(self._lru.peek_back(), evicted=True)
        return True

    def get(self, key):
        self._purge_expired(self._clock())
        record = self._data.get(key)
        if record is None:
            return None
        self._lru.move_to_front(record.lru_node)
        return record.value

    def delete(self, key):
        self._purge_expired(self._clock())
        if not self._data.contains(key):
            return 0
        self._remove(key)
        return 1

    def exists(self, key):
        self._purge_expired(self._clock())
        return self._data.contains(key)

    def dbsize(self):
        self._purge_expired(self._clock())
        return self._data.size()

    def keys(self):
        self._purge_expired(self._clock())
        return self._data.keys()

    def config_set_maxmemory(self, limit):
        self._purge_expired(self._clock())
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("maxmemory must be a non-negative integer")
        self.maxmemory = limit

    def info_memory(self):
        self._purge_expired(self._clock())
        return self.used_memory, self.maxmemory, self.evicted_keys

    def expire(self, key, seconds):
        now = self._clock()
        self._purge_expired(now)
        record = self._data.get(key)
        if record is None:
            return 0
        if seconds <= 0:
            self._remove(key)
            return 1

        self._next_expiry_id += 1
        record.expires_at = now + seconds
        record.expiry_id = self._next_expiry_id
        self._expirations.push((record.expires_at, key, record.expiry_id))
        return 1

    def ttl(self, key):
        now = self._clock()
        self._purge_expired(now)
        record = self._data.get(key)
        if record is None:
            return -2
        if record.expires_at is None:
            return -1
        return int(record.expires_at - now)

    def subscribe(self, channel, subscriber):
        return self._pubsub.subscribe(channel, subscriber)

    def publish(self, channel, message):
        return self._pubsub.publish(channel, message)

    def poll(self, subscriber):
        return self._pubsub.poll(subscriber)
