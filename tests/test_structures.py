import unittest

from mini_redis.hash_map import HashMap
from mini_redis.linked_list import LinkedList
from mini_redis.min_heap import MinHeap


class LinkedListTest(unittest.TestCase):
    def test_empty_list(self):
        linked = LinkedList()
        self.assertEqual(linked.size(), 0)
        self.assertIsNone(linked.remove_front())
        self.assertIsNone(linked.remove_back())
        self.assertEqual(list(linked), [])

    def test_insert_move_and_remove(self):
        linked = LinkedList()
        first = linked.insert_back("first")
        middle = linked.insert_back("middle")
        linked.insert_front("front")
        self.assertEqual(list(linked), ["front", "first", "middle"])

        linked.move_to_front(middle)
        self.assertEqual(list(linked), ["middle", "front", "first"])
        self.assertEqual(linked.size(), 3)
        linked.move_to_front(middle)
        self.assertEqual(linked.size(), 3)
        self.assertEqual(linked.remove_node(first), "first")
        self.assertEqual(linked.remove_front(), "middle")
        self.assertEqual(linked.remove_back(), "front")
        self.assertEqual(linked.size(), 0)
        with self.assertRaises(ValueError):
            linked.remove_node(first)

    def test_remove_middle_node(self):
        linked = LinkedList()
        linked.insert_back(1)
        middle = linked.insert_back(2)
        linked.insert_back(3)
        self.assertEqual(linked.remove_node(middle), 2)
        self.assertEqual(list(linked), [1, 3])
        with self.assertRaises(ValueError):
            linked.move_to_front(middle)

    def test_reject_node_from_another_list(self):
        first = LinkedList()
        second = LinkedList()
        node = first.insert_back("first")
        second.insert_back("second")
        with self.assertRaises(ValueError):
            second.remove_node(node)
        with self.assertRaises(ValueError):
            second.move_to_front(node)
        self.assertEqual(list(first), ["first"])
        self.assertEqual(list(second), ["second"])


class HashMapTest(unittest.TestCase):
    def test_put_get_update_and_remove(self):
        mapping = HashMap()
        self.assertIsNone(mapping.get("missing"))
        self.assertFalse(mapping.contains("missing"))
        self.assertIsNone(mapping.put("key", "old"))
        self.assertEqual(mapping.put("key", "new"), "old")
        self.assertEqual(mapping.size(), 1)
        self.assertEqual(mapping.get("key"), "new")
        self.assertEqual(mapping.keys(), ["key"])
        self.assertEqual(mapping.remove("key"), "new")
        self.assertIsNone(mapping.remove("key"))
        self.assertFalse(mapping.contains("key"))
        self.assertEqual(mapping.size(), 0)

    def test_colliding_keys_share_a_bucket(self):
        mapping = HashMap(capacity=4)
        first = "a"
        second = next(
            "key{}".format(i)
            for i in range(100)
            if mapping._hash("key{}".format(i)) % 4 == mapping._hash(first) % 4
        )
        mapping.put(first, 1)
        mapping.put(second, 2)
        self.assertEqual(len(mapping._buckets), 4)
        self.assertEqual(mapping.get(first), 1)
        self.assertEqual(mapping.get(second), 2)
        mapping.remove(first)
        self.assertEqual(mapping.get(second), 2)

    def test_resize_only_above_threshold_and_preserve_entries(self):
        mapping = HashMap(capacity=4)
        for i in range(3):
            mapping.put("key{}".format(i), i)
        self.assertEqual(len(mapping._buckets), 4)
        mapping.put("key3", 3)
        self.assertEqual(len(mapping._buckets), 8)
        for i in range(4):
            self.assertEqual(mapping.get("key{}".format(i)), i)
        self.assertEqual(mapping.size(), 4)

    def test_many_keys_and_utf8_hash(self):
        mapping = HashMap(capacity=2)
        for i in range(100):
            mapping.put("키:{}".format(i), i)
        self.assertEqual(mapping.size(), 100)
        self.assertEqual(len(mapping.keys()), 100)
        for i in range(100):
            self.assertEqual(mapping.remove("키:{}".format(i)), i)
        self.assertEqual(mapping.size(), 0)
        self.assertEqual(mapping.keys(), [])

    def test_none_value_is_distinct_from_missing_key(self):
        mapping = HashMap()
        mapping.put("nil", None)
        self.assertTrue(mapping.contains("nil"))
        self.assertIsNone(mapping.get("nil"))
        mapping.remove("nil")
        self.assertFalse(mapping.contains("nil"))


class MinHeapTest(unittest.TestCase):
    def test_empty_heap(self):
        heap = MinHeap()
        self.assertIsNone(heap.peek())
        self.assertIsNone(heap.pop())
        self.assertEqual(heap.size(), 0)

    def test_expiration_order_and_ties(self):
        heap = MinHeap()
        items = [(10, "c"), (3, "b"), (7, "a"), (3, "a"), (15, "z")]
        for item in items:
            heap.push(item)
        self.assertEqual(heap.size(), 5)
        self.assertEqual(heap.peek(), (3, "a"))
        self.assertEqual([heap.pop() for _ in items], sorted(items))
        self.assertIsNone(heap.pop())

    def test_interleaved_push_and_pop(self):
        heap = MinHeap()
        for value in (8, 2, 6, 1, 4):
            heap.push(value)
        self.assertEqual(heap.pop(), 1)
        heap.push(0)
        self.assertEqual([heap.pop() for _ in range(heap.size())], [0, 2, 4, 6, 8])


if __name__ == "__main__":
    unittest.main()
