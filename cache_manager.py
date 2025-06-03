import json
import os

CACHE_FILE = "output/cache.json"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {"gmail_ids": [], "drive_ids": []}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def update_cache(gmail_ids, drive_ids):
    cache = load_cache()
    cache["gmail_ids"] += [i for i in gmail_ids if i not in cache["gmail_ids"]]
    cache["drive_ids"] += [i for i in drive_ids if i not in cache["drive_ids"]]
    os.makedirs("output", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)