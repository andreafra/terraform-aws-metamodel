from importlib.resources import files
import json
import os
import assets

def cache(filename: str, data_callback) -> any:
    """Caches to disk an expensive function result like a JSON file.
    - `filename` the key to access the cached data
    - `data_callback` should be a lambda function that wraps the expensive function."""
    
    cache_dir = files(assets) / 'cache'
    if not os.path.exists(cache_dir):
        print('Cache dir not found. Creating cache dir...')
        os.mkdir(cache_dir)
    file = cache_dir / filename
    if not os.path.exists(file):
        print(f'Cache for \'{filename}\' does not exist. Saving to cache...')
        with open(file, "w") as fp:
            data = data_callback()
            fp.write(json.dumps(data))
            return data
    else:
        print(f'Cache for \'{filename} found. Loading cache...\'')
        with open(file) as fp:
            return json.loads(fp.read())