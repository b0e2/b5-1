import subprocess
import sys
import unittest


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


if __name__ == "__main__":
    unittest.main()
