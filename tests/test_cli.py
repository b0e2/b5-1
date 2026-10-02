import subprocess
import sys
import unittest

from mini_redis.cli import execute
from mini_redis.store import MiniRedis


class CliSmokeTest(unittest.TestCase):
    def run_cli(self, commands):
        return subprocess.run(
            [sys.executable, "-m", "mini_redis"],
            input=commands,
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )

    def test_quit(self):
        result = self.run_cli("quit\n")
        self.assertEqual(result.stdout, "mini-redis> ")

    def test_unknown_command_and_exit(self):
        result = self.run_cli("HELLO\nexit\n")
        self.assertIn("(error) ERR unknown command 'HELLO'", result.stdout)
        self.assertEqual(result.stdout.count("mini-redis> "), 2)

    def test_string_commands_and_quoted_value(self):
        result = self.run_cli(
            'SET name "Alice Smith"\nGET name\nEXISTS name\nDBSIZE\nKEYS\nDEL name\nGET name\nquit\n'
        )
        for line in ('OK', '"Alice Smith"', '(integer) 1', '1. "name"', '(nil)'):
            self.assertIn(line, result.stdout)

    def test_memory_and_error_outputs(self):
        result = self.run_cli(
            'CONFIG SET maxmemory 5\nSET a 1234\nSET b 1\nINFO memory\n'
            'SET larger x\nCONFIG SET maxmemory abc\nGET\nSET a "broken\nquit\n'
        )
        for line in (
            'used_memory:2', 'maxmemory:5', 'evicted_keys:1',
            "(error) OOM command not allowed when used_memory > 'maxmemory'",
            '(error) ERR value is not an integer or out of range',
            "(error) ERR wrong number of arguments for 'GET' command",
            '(error) ERR syntax error',
        ):
            self.assertIn(line, result.stdout)

    def test_empty_keys(self):
        result = self.run_cli('KEYS\nquit\n')
        self.assertIn('(empty array)', result.stdout)


class CliCommandTest(unittest.TestCase):
    def test_ttl_and_case_insensitive_commands(self):
        now = [100.0]
        store = MiniRedis(clock=lambda: now[0])
        self.assertEqual(execute(store, ['set', 'k', 'v']), 'OK')
        self.assertEqual(execute(store, ['tTl', 'k']), '(integer) -1')
        self.assertEqual(execute(store, ['EXPIRE', 'k', '3']), '(integer) 1')
        now[0] += 1.1
        self.assertEqual(execute(store, ['TTL', 'k']), '(integer) 1')
        now[0] += 2
        self.assertEqual(execute(store, ['GET', 'k']), '(nil)')
        self.assertEqual(execute(store, ['TTL', 'k']), '(integer) -2')

    def test_invalid_integer_and_subcommand(self):
        store = MiniRedis()
        self.assertEqual(execute(store, ['EXPIRE', 'k', 'abc']),
                         '(error) ERR value is not an integer or out of range')
        self.assertEqual(execute(store, ['CONFIG', 'SET', 'maxmemory', '-1']),
                         '(error) ERR value is not an integer or out of range')
        self.assertEqual(execute(store, ['CONFIG', 'SET', 'maxmemory', str(1 << 63)]),
                         '(error) ERR value is not an integer or out of range')
        self.assertEqual(execute(store, ['EXPIRE', 'k', str(-(1 << 63) - 1)]),
                         '(error) ERR value is not an integer or out of range')
        self.assertEqual(execute(store, ['INFO', 'other']), '(error) ERR syntax error')


if __name__ == "__main__":
    unittest.main()
