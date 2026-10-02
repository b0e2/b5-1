import unittest

from mini_redis.store import MiniRedis


class Clock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class MiniRedisTest(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.store = MiniRedis(clock=self.clock)

    def test_basic_commands_and_memory(self):
        self.assertEqual(self.store.dbsize(), 0)
        self.assertEqual(self.store.keys(), [])
        self.assertIsNone(self.store.get("missing"))
        self.assertEqual(self.store.delete("missing"), 0)
        self.assertFalse(self.store.exists("missing"))

        self.assertTrue(self.store.set("a", "one"))
        self.assertTrue(self.store.set("b", "two"))
        self.assertEqual(self.store.dbsize(), 2)
        self.assertEqual(sorted(self.store.keys()), ["a", "b"])
        self.assertTrue(self.store.exists("a"))
        self.assertEqual(self.store.get("a"), "one")
        self.assertEqual(self.store.info_memory(), (8, 0, 0))
        self.assertEqual(self.store.delete("a"), 1)
        self.assertEqual(self.store.info_memory(), (4, 0, 0))
        self.assertEqual(self.store.delete("a"), 0)

    def test_lru_evicts_least_recently_used(self):
        self.store.config_set_maxmemory(10)
        self.store.set("a", "1111")
        self.store.set("b", "2222")
        self.store.set("c", "3333")
        self.assertFalse(self.store.exists("a"))
        self.assertEqual(self.store.info_memory(), (10, 10, 1))

        self.assertEqual(self.store.get("b"), "2222")
        self.store.set("d", "4444")
        self.assertFalse(self.store.exists("c"))
        self.assertEqual(sorted(self.store.keys()), ["b", "d"])
        self.assertEqual(self.store.info_memory(), (10, 10, 2))

    def test_non_accessing_commands_do_not_refresh_lru(self):
        self.store.config_set_maxmemory(6)
        self.store.set("a", "11")
        self.store.set("b", "22")
        self.assertTrue(self.store.exists("a"))
        self.assertEqual(self.store.ttl("a"), -1)
        self.assertEqual(sorted(self.store.keys()), ["a", "b"])
        self.store.info_memory()
        self.store.set("c", "1")
        self.assertFalse(self.store.exists("a"))
        self.assertTrue(self.store.exists("b"))

    def test_overwrite_refreshes_lru(self):
        self.store.config_set_maxmemory(6)
        self.store.set("a", "11")
        self.store.set("b", "22")
        self.store.set("a", "11")
        self.store.set("c", "1")
        self.assertTrue(self.store.exists("a"))
        self.assertFalse(self.store.exists("b"))

    def test_oversized_entry_does_not_change_existing_value_or_ttl(self):
        self.store.config_set_maxmemory(6)
        self.store.set("a", "1111")
        self.store.expire("a", 10)
        self.assertFalse(self.store.set("a", "123456"))
        self.assertFalse(self.store.set("larger", "x"))
        self.assertEqual(self.store.get("a"), "1111")
        self.assertEqual(self.store.ttl("a"), 10)
        self.assertEqual(self.store.info_memory(), (5, 6, 0))

    def test_overwrite_resets_ttl_and_uses_utf8_bytes(self):
        self.store.set("한", "🙂")
        self.assertEqual(self.store.info_memory(), (7, 0, 0))
        self.store.expire("한", 2)
        self.assertTrue(self.store.set("한", "B"))
        self.assertEqual(self.store.info_memory(), (4, 0, 0))
        self.assertEqual(self.store.ttl("한"), -1)
        self.clock.advance(2)
        self.assertEqual(self.store.get("한"), "B")

    def test_expiration_cleans_data_lru_and_memory_without_eviction(self):
        self.store.set("a", "1")
        self.store.set("b", "2")
        self.store.expire("a", 3)
        self.store.expire("b", 10)
        self.clock.advance(3)
        self.assertIsNone(self.store.get("a"))
        self.assertEqual(self.store.ttl("a"), -2)
        self.assertEqual(self.store.dbsize(), 1)
        self.assertEqual(self.store.keys(), ["b"])
        self.assertEqual(self.store.info_memory(), (2, 0, 0))

    def test_global_commands_purge_without_get(self):
        self.store.set("a", "1")
        self.store.expire("a", 1)
        self.clock.advance(1)
        self.assertEqual(self.store.dbsize(), 0)
        self.assertEqual(self.store.keys(), [])
        self.assertEqual(self.store.info_memory(), (0, 0, 0))
        self.assertEqual(self.store.delete("a"), 0)

    def test_reexpire_ignores_earlier_heap_record(self):
        self.store.set("k", "v")
        self.store.expire("k", 3)
        self.store.expire("k", 8)
        self.clock.advance(3)
        self.assertTrue(self.store.exists("k"))
        self.assertEqual(self.store.ttl("k"), 5)
        self.clock.advance(5)
        self.assertFalse(self.store.exists("k"))

    def test_delete_and_recreate_ignores_old_expiration(self):
        self.store.set("k", "old")
        self.store.expire("k", 3)
        self.assertEqual(self.store.delete("k"), 1)
        self.store.set("k", "new")
        self.store.expire("k", 10)
        self.clock.advance(3)
        self.assertEqual(self.store.get("k"), "new")
        self.clock.advance(7)
        self.assertIsNone(self.store.get("k"))
        self.assertEqual(self.store.info_memory(), (0, 0, 0))

    def test_ttl_missing_persistent_and_immediate_expiration(self):
        self.assertEqual(self.store.ttl("missing"), -2)
        self.assertEqual(self.store.expire("missing", 3), 0)
        self.store.set("k", "v")
        self.assertEqual(self.store.ttl("k"), -1)
        self.assertEqual(self.store.expire("k", 0), 1)
        self.assertEqual(self.store.ttl("k"), -2)
        self.assertEqual(self.store.info_memory(), (0, 0, 0))

    def test_ttl_truncates_remaining_seconds(self):
        self.store.set("k", "v")
        self.store.expire("k", 3)
        self.clock.advance(0.5)
        self.assertEqual(self.store.ttl("k"), 2)
        self.clock.advance(2.5)
        self.assertEqual(self.store.ttl("k"), -2)

    def test_maxmemory_zero_is_unlimited_and_lower_limit_applies_on_set(self):
        for key in ("a", "b", "c"):
            self.store.set(key, "11")
        self.assertEqual(self.store.info_memory(), (9, 0, 0))
        self.store.config_set_maxmemory(5)
        self.assertEqual(self.store.info_memory(), (9, 5, 0))
        self.assertTrue(self.store.set("d", "1"))
        self.assertEqual(self.store.info_memory(), (5, 5, 2))
        self.store.config_set_maxmemory(0)
        self.assertTrue(self.store.set("large", "many bytes"))
        self.assertEqual(self.store.evicted_keys, 2)

    def test_invalid_memory_limit(self):
        with self.assertRaises(ValueError):
            self.store.config_set_maxmemory(-1)
        with self.assertRaises(ValueError):
            self.store.config_set_maxmemory("no")
        self.assertEqual(self.store.info_memory(), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
