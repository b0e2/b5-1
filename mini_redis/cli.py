import json
import shlex

from .store import MiniRedis


INTEGER_ERROR = "(error) ERR value is not an integer or out of range"
OOM_ERROR = "(error) OOM command not allowed when used_memory > 'maxmemory'"


def _integer(value):
    return "(integer) {}".format(value)


def _parse_integer(value):
    try:
        number = int(value)
    except (ValueError, OverflowError):
        return None
    if number < -(1 << 63) or number > (1 << 63) - 1:
        return None
    return number


def execute(store, words):
    """Execute one parsed command and return its printable result."""
    command = words[0].upper()
    counts = (
        ("SET", 3), ("GET", 2), ("DEL", 2), ("EXISTS", 2),
        ("DBSIZE", 1), ("KEYS", 1), ("CONFIG", 4), ("INFO", 2),
        ("EXPIRE", 3), ("TTL", 2),
        ("SUBSCRIBE", 3), ("PUBLISH", 3), ("POLL", 2),
    )
    expected = None
    for name, count in counts:
        if command == name:
            expected = count
            break
    if expected is None:
        return "(error) ERR unknown command '{}'".format(words[0])
    if len(words) != expected:
        return "(error) ERR wrong number of arguments for '{}' command".format(command)

    if command == "SET":
        return "OK" if store.set(words[1], words[2]) else OOM_ERROR
    if command == "GET":
        value = store.get(words[1])
        return "(nil)" if value is None else json.dumps(value, ensure_ascii=False)
    if command == "DEL":
        return _integer(store.delete(words[1]))
    if command == "EXISTS":
        return _integer(int(store.exists(words[1])))
    if command == "DBSIZE":
        return _integer(store.dbsize())
    if command == "KEYS":
        keys = store.keys()
        if not keys:
            return "(empty array)"
        return "\n".join("{}. {}".format(i, json.dumps(key, ensure_ascii=False))
                         for i, key in enumerate(keys, 1))
    if command == "CONFIG":
        if words[1].upper() != "SET" or words[2].lower() != "maxmemory":
            return "(error) ERR syntax error"
        limit = _parse_integer(words[3])
        if limit is None or limit < 0:
            return INTEGER_ERROR
        store.config_set_maxmemory(limit)
        return "OK"
    if command == "INFO":
        if words[1].lower() != "memory":
            return "(error) ERR syntax error"
        used, limit, evicted = store.info_memory()
        return "used_memory:{}\nmaxmemory:{}\nevicted_keys:{}".format(
            used, limit, evicted
        )
    if command == "EXPIRE":
        seconds = _parse_integer(words[2])
        if seconds is None:
            return INTEGER_ERROR
        return _integer(store.expire(words[1], seconds))
    if command == "SUBSCRIBE":
        return _integer(store.subscribe(words[1], words[2]))
    if command == "PUBLISH":
        return _integer(store.publish(words[1], words[2]))
    if command == "POLL":
        message = store.poll(words[1])
        if message is None:
            return "(nil)"
        channel, value = message
        return "1. {}\n2. {}".format(json.dumps(channel, ensure_ascii=False),
                                     json.dumps(value, ensure_ascii=False))
    return _integer(store.ttl(words[1]))


def main():
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
