import json
from typing import Optional


INTEGER_ERROR = "(error) ERR value is not an integer or out of range"
OOM_ERROR = "(error) OOM command not allowed when used_memory > 'maxmemory'"


def _integer(value) -> str:
    return "(integer) {}".format(value)


def _parse_integer(value) -> Optional[int]:
    try:
        number = int(value)
    except (ValueError, OverflowError):
        return None
    if number < -(1 << 63) or number > (1 << 63) - 1:
        return None
    return number


def _set(store, words) -> str:
    return "OK" if store.set(words[1], words[2]) else OOM_ERROR


def _get(store, words) -> str:
    value = store.get(words[1])
    return "(nil)" if value is None else json.dumps(value, ensure_ascii=False)


def _delete(store, words) -> str:
    return _integer(store.delete(words[1]))


def _exists(store, words) -> str:
    return _integer(int(store.exists(words[1])))


def _dbsize(store, words) -> str:
    return _integer(store.dbsize())


def _keys(store, words) -> str:
    keys = store.keys()
    if not keys:
        return "(empty array)"
    return "\n".join("{}. {}".format(i, json.dumps(key, ensure_ascii=False))
                     for i, key in enumerate(keys, 1))


def _config(store, words) -> str:
    if words[1].upper() != "SET" or words[2].lower() != "maxmemory":
        return "(error) ERR syntax error"
    limit = _parse_integer(words[3])
    if limit is None or limit < 0:
        return INTEGER_ERROR
    store.config_set_maxmemory(limit)
    return "OK"


def _info(store, words) -> str:
    if words[1].lower() != "memory":
        return "(error) ERR syntax error"
    used, limit, evicted = store.info_memory()
    return "used_memory:{}\nmaxmemory:{}\nevicted_keys:{}".format(
        used, limit, evicted
    )


def _expire(store, words) -> str:
    seconds = _parse_integer(words[2])
    if seconds is None:
        return INTEGER_ERROR
    return _integer(store.expire(words[1], seconds))


def _ttl(store, words) -> str:
    return _integer(store.ttl(words[1]))


def _subscribe(store, words) -> str:
    return _integer(store.subscribe(words[1], words[2]))


def _publish(store, words) -> str:
    return _integer(store.publish(words[1], words[2]))


def _poll(store, words) -> str:
    message = store.poll(words[1])
    if message is None:
        return "(nil)"
    channel, value = message
    return "1. {}\n2. {}".format(json.dumps(channel, ensure_ascii=False),
                                 json.dumps(value, ensure_ascii=False))


_COMMANDS = {
    "SET": (3, _set),
    "GET": (2, _get),
    "DEL": (2, _delete),
    "EXISTS": (2, _exists),
    "DBSIZE": (1, _dbsize),
    "KEYS": (1, _keys),
    "CONFIG": (4, _config),
    "INFO": (2, _info),
    "EXPIRE": (3, _expire),
    "TTL": (2, _ttl),
    "SUBSCRIBE": (3, _subscribe),
    "PUBLISH": (3, _publish),
    "POLL": (2, _poll),
}


def execute(store, words) -> str:
    """Execute one parsed command and return its printable result."""
    command = words[0].upper()
    entry = _COMMANDS.get(command)
    if entry is None:
        return "(error) ERR unknown command '{}'".format(words[0])
    expected, handler = entry
    if len(words) != expected:
        return "(error) ERR wrong number of arguments for '{}' command".format(command)
    return handler(store, words)
