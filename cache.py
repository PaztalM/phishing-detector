import os
import logging

import redis

log = logging.getLogger("phishing")

TTL_SECONDS = 300

_client = None


def get_client():
    global _client
    host = os.environ.get("REDIS_HOST")
    if not host:
        return None
    if _client is None:
        _client = redis.Redis(host=host, port=6379,
                              socket_timeout=0.5, socket_connect_timeout=0.5)
    return _client


def history_key(address):
    return f"history:{address}"


def cached_history(address, load):
    client = get_client()
    if client is None:
        return load(address)

    try:
        value = client.get(history_key(address))
        if value is not None:
            return int(value)
    except redis.RedisError as e:
        log.warning("cache read failed: %s", e)
        return load(address)

    count = load(address)
    try:
        client.set(history_key(address), count, ex=TTL_SECONDS)
    except redis.RedisError as e:
        log.warning("cache write failed: %s", e)
    return count


def forget_history(address):
    client = get_client()
    if client is None:
        return
    try:
        client.delete(history_key(address))
    except redis.RedisError as e:
        log.warning("cache delete failed: %s", e)