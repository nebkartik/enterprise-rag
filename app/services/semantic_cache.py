import hashlib
import os
import json
import numpy as np
import redis
import logfire

CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
REDIDS_HOST = os.getenv("REDIS_HOST", "localhost")
KEY_PREFIX = "sem_cache:"


_client = None

def get_client():
    global _client 
    if _client is not None:
        return _client
    _client = redis.Redis(
        host = REDIDS_HOST,
        port = int(os.getenv("REDIS_PORT", "6379")),
        socket_connect_timeout=2,
        socket_timeout=2,
        decode_responses=False
    )
    return _client

def _cosine_distance(a, b) -> float:
    a, b = np.array(a, dtype=np.float32), np.array(b, dtype=np.float32)
    norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return float(1.0 - np.dot(a, b) / (norm_a * norm_b))

def check_cache(query: str):
    client = get_client()
    try:
        from app.services.embeddinigs import embed_query
        query_vec = embed_query(query)
        for key in client.scan_iter(f"{KEY_PREFIX}*"):
            raw = client.get(key)
            if raw is None:
                continue
            entry = json.loads(raw)
            cached_vec = entry.get("embedding")
            if cached_vec is None:
                continue
            cos_dist = _cosine_distance(query_vec, cached_vec)
            if cos_dist < float(os.getenv("CACHE_DISTANCE_THRESHOLD", "0.15")):
                logfire.info(f"Semantic cache hit for query: {query} with distance: {cos_dist}")
                return entry.get("answer")
    except Exception as e:
        logfire.error(f"Error checking semantic cache: {e}")
    return None        

def set_cache(query: str, answer:str):
    client = get_client()
    try:
        from app.services.embeddinigs import embed_query
        query_vec = embed_query(query)
        cache_entry = {
            "query": query,
            "answer": answer,
            "embedding": query_vec
        }
        key = f"{KEY_PREFIX}{hashlib.md5(query.encode()).hexdigest()}"
        client.set(key, json.dumps(cache_entry), ex=CACHE_TTL)
        logfire.info(f"💾 Cached answer for: {query[:60]}")
        
    except Exception as e:
        logfire.warning(f"⚠️ Semantic cache set failed (non-fatal): {e}")



