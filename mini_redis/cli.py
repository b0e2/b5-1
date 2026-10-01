def main():
    """Run the interactive command loop."""
    while True:
        try:
            line = input("mini-redis> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not line:
            continue

        command = line.split(maxsplit=1)[0]
        if command.lower() in ("exit", "quit") and line.lower() == command.lower():
            return

        print("(error) ERR unknown command '{}'".format(command))
