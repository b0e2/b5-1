import unittest

from mini_redis.dynamic_array import DynamicArray
from mini_redis.min_heap import MinHeap
from mini_redis.store import MiniRedis


class DynamicArrayTest(unittest.TestCase):
    def test_capacity_doubles_only_when_full(self):
        array = DynamicArray(capacity=2)
        self.assertEqual(array.capacity, 2)
        self.assertEqual(array.size(), 0)
        array.append("a")
        array.append("b")
        self.assertEqual(array.capacity, 2)
        array.append("c")
        self.assertEqual(array.capacity, 4)
        array.append("d")
        array.append("e")
        self.assertEqual(array.capacity, 8)
        self.assertEqual([array.get(i) for i in range(array.size())],
                         ["a", "b", "c", "d", "e"])

    def test_set_remove_and_append_after_shift(self):
        array = DynamicArray(capacity=2)
        for value in ("a", "b", "c", "d"):
            array.append(value)
        array.set(1, "B")
        self.assertEqual(array[1], "B")
        array[2] = "C"
        self.assertEqual(array.remove(0), "a")
        self.assertEqual(array.remove(1), "C")
        self.assertEqual([array.get(i) for i in range(len(array))], ["B", "d"])
        array.append("e")
        self.assertEqual(array.pop(), "e")
        self.assertEqual(array.pop(), "d")
        self.assertEqual(array.pop(), "B")
        self.assertEqual(len(array), 0)
        self.assertEqual(array.capacity, 4)

    def test_none_value_and_cleared_slot(self):
        array = DynamicArray(capacity=1)
        array.append(None)
        self.assertEqual(len(array), 1)
        self.assertIsNone(array.get(0))
        self.assertIsNone(array.remove(0))
        self.assertEqual(len(array), 0)
        self.assertIsNone(array._items[0])
        array.append("again")
        self.assertEqual(array.pop(), "again")

    def test_invalid_capacity_and_indices(self):
        for capacity in (0, -1, "4"):
            with self.assertRaises(ValueError):
                DynamicArray(capacity=capacity)
        array = DynamicArray()
        with self.assertRaises(IndexError):
            array.pop()
        array.append("a")
        for index in (-1, 1):
            with self.assertRaises(IndexError):
                array.get(index)
            with self.assertRaises(IndexError):
                array.set(index, "x")
            with self.assertRaises(IndexError):
                array.remove(index)
        self.assertEqual(array.get(0), "a")


class HeapDynamicArrayTest(unittest.TestCase):
    def test_heap_uses_dynamic_array_through_growth_and_reuse(self):
        heap = MinHeap()
        self.assertIsInstance(heap._items, DynamicArray)
        for value in range(100, 0, -1):
            heap.push(value)
        self.assertEqual(heap._items.capacity, 128)
        self.assertEqual(heap.size(), 100)
        self.assertEqual([heap.pop() for _ in range(100)], list(range(1, 101)))
        self.assertIsNone(heap.pop())
        heap.push(3)
        heap.push(1)
        self.assertEqual(heap.pop(), 1)
        self.assertEqual(heap.pop(), 3)

    def test_ttl_cleanup_after_heap_growth(self):
        now = [100.0]
        store = MiniRedis(clock=lambda: now[0])
        for i in range(20):
            key = "k{}".format(i)
            store.set(key, "v")
            store.expire(key, 20 - i)
        self.assertIsInstance(store._expirations._items, DynamicArray)
        self.assertEqual(store.dbsize(), 20)
        now[0] += 10
        self.assertEqual(store.dbsize(), 10)
        self.assertEqual(store.evicted_keys, 0)
        now[0] += 10
        self.assertEqual(store.dbsize(), 0)
        self.assertEqual(store.used_memory, 0)


if __name__ == "__main__":
    unittest.main()
