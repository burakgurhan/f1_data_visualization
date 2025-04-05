import json
import os
from datetime import datetime, timedelta
import hashlib
from urllib.request import urlopen
CACHE_DIR = "api_cache"
CACHE_EXPIRY_HOURS = 24

def get_cache_key(url):
    return hashlib.md5(url.encode()).hexdigest()

def get_cache_file(url):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{get_cache_key(url)}.json")

def is_cache_valid(cache_file):
    if not os.path.exists(cache_file):
        return False
    mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    return datetime.now() - mod_time < timedelta(hours=CACHE_EXPIRY_HOURS)

def read_from_cache(url):
    cache_file = get_cache_file(url)
    if is_cache_valid(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def write_to_cache(url, data):
    cache_file = get_cache_file(url)
    with open(cache_file, 'w') as f:
        json.dump(data, f)

def cached_api_call(url):
    # Check cache first
    cached = read_from_cache(url)
    if cached is not None:
        return cached
        
    # Make API call if no cache
    response = urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    
    # Store in cache
    write_to_cache(url, data)
    return data
