import shlex

from .cli import execute
from .store import MiniRedis


def main() -> None:
    """Run the interactive command loop."""
    store = MiniRedis()
    while True:
        try:
            line = input("mini-redis> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            continue
        try:
            words = shlex.split(line)
        except ValueError:
            print("(error) ERR syntax error")
            continue
        if not words:
            continue
        if len(words) == 1 and words[0].lower() in ("exit", "quit"):
            return
        print(execute(store, words))


if __name__ == "__main__":
    main()
