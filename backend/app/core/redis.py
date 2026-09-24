"""Provide redis components for the application."""

import os

import redis
from dotenv import load_dotenv

load_dotenv()


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_CACHE_DB = int(os.getenv("REDIS_CACHE_DB", "1"))


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_CACHE_DB,
    decode_responses=True,
)
