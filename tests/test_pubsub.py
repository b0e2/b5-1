import subprocess
import sys
import unittest

from mini_redis.cli import execute
from mini_redis.pubsub import PubSub
from mini_redis.store import MiniRedis


class PubSubTest(unittest.TestCase):
    def test_channel_delivery_and_subscriber_order(self):
        pubsub = PubSub()
        self.assertEqual(pubsub.publish("news", "before"), 0)
        self.assertEqual(pubsub.subscribe("news", "alice"), 1)
        self.assertEqual(pubsub.subscribe("news", "bob"), 2)
        self.assertEqual(pubsub.subscribe("news", "alice"), 2)
        self.assertEqual(pubsub.subscribe("sports", "alice"), 1)
        self.assertEqual(pubsub.publish("news", "first"), 2)
        self.assertEqual(pubsub.publish("sports", "score"), 1)
        self.assertEqual(pubsub.publish("news", "second"), 2)
        self.assertEqual(pubsub.poll("alice"), ("news", "first"))
        self.assertEqual(pubsub.poll("alice"), ("sports", "score"))
        self.assertEqual(pubsub.poll("alice"), ("news", "second"))
        self.assertIsNone(pubsub.poll("alice"))
        self.assertEqual(pubsub.poll("bob"), ("news", "first"))
        self.assertEqual(pubsub.poll("bob"), ("news", "second"))
        self.assertIsNone(pubsub.poll("bob"))
        self.assertIsNone(pubsub.poll("missing"))

    def test_new_subscriber_does_not_receive_old_messages(self):
        pubsub = PubSub()
        pubsub.subscribe("updates", "first")
        pubsub.publish("updates", "old")
        pubsub.subscribe("updates", "second")
        pubsub.publish("updates", "new")
        self.assertEqual(pubsub.poll("first"), ("updates", "old"))
        self.assertEqual(pubsub.poll("first"), ("updates", "new"))
        self.assertEqual(pubsub.poll("second"), ("updates", "new"))
        self.assertIsNone(pubsub.poll("second"))

    def test_pubsub_is_independent_of_string_memory_and_ttl(self):
        now = [100.0]
        store = MiniRedis(clock=lambda: now[0])
        store.config_set_maxmemory(2)
        self.assertTrue(store.set("k", "v"))
        self.assertEqual(store.expire("k", 1), 1)
        self.assertEqual(store.subscribe("k", "listener"), 1)
        self.assertEqual(store.publish("k", "message"), 1)
        self.assertEqual(store.info_memory(), (2, 2, 0))
        now[0] += 2
        self.assertIsNone(store.get("k"))
        self.assertEqual(store.poll("listener"), ("k", "message"))
        self.assertEqual(store.info_memory(), (0, 2, 0))


class PubSubCliTest(unittest.TestCase):
    def test_commands_and_arity(self):
        store = MiniRedis()
        self.assertEqual(execute(store, ["subscribe", "news", "alice"]),
                         "(integer) 1")
        self.assertEqual(execute(store, ["PUBLISH", "news", "안녕 세상"]),
                         "(integer) 1")
        self.assertEqual(execute(store, ["PoLl", "alice"]),
                         '1. "news"\n2. "안녕 세상"')
        self.assertEqual(execute(store, ["POLL", "alice"]), "(nil)")
        for words, name in ((["SUBSCRIBE", "news"], "SUBSCRIBE"),
                            (["PUBLISH", "news"], "PUBLISH"),
                            (["POLL"], "POLL")):
            self.assertEqual(execute(store, words),
                             "(error) ERR wrong number of arguments for '{}' command".format(name))

    def test_repl_delivery(self):
        result = subprocess.run(
            [sys.executable, "-m", "mini_redis"],
            input='SUBSCRIBE news alice\nSUBSCRIBE news bob\n'
                  'PUBLISH news "hello world"\nPOLL alice\nPOLL bob\n'
                  'POLL alice\nquit\n',
            text=True, capture_output=True, timeout=5, check=True,
        )
        self.assertIn('(integer) 2', result.stdout)
        self.assertEqual(result.stdout.count('1. "news"\n2. "hello world"'), 2)
        self.assertIn('(nil)', result.stdout)


if __name__ == "__main__":
    unittest.main()
