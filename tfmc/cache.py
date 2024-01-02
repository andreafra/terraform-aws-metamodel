from importlib.resources import files
import json
import os
import shutil
import assets

cache_dir = files(assets) / "cache"

if not os.path.exists(cache_dir):
    print("Cache dir not found. Creating cache dir...")
    os.mkdir(cache_dir)


def cache(filename: str, encode_callback, decode_callback):
    """Caches to disk an expensive function result like a JSON file.
    - `filename` the key to access the cached data
    - `encode_callback` a function that wraps the expensive function and encodes it
    - `decode_callback` a function that decodes the cached value"""

    file = cache_dir / filename
    if not os.path.exists(file):
        print(f"Cache for '{filename}' does not exist. Saving to cache...")
        with open(file, "w") as fp:
            data = encode_callback()
            fp.write(data)
            return decode_callback(data)
    else:
        print(f"Cache for '{filename} found. Loading cache...'")
        with open(file) as fp:
            data = fp.read()
            return decode_callback(data)


def clear_cache():
    if os.path.exists(cache_dir):
        print("Clearing cache...")
        shutil.rmtree(cache_dir)
        os.mkdir(cache_dir)
