import json
import os
import time
import random
import shelve
from datetime import datetime, timedelta
import hashlib
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

# Persistent request history storage
REQUEST_HISTORY = shelve.open('api_request_history.db', writeback=True)
CACHE_DIR = "api_cache"
CACHE_EXPIRY_HOURS = 24
MAX_RETRIES = 2
BASE_DELAY = 5.0  # Increased base delay
MAX_DELAY = 60.0  # Increased max delay
RATE_LIMIT_WINDOW = 60  # 60 second window
MAX_REQUESTS_PER_WINDOW = 10  # Conservative limit

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

def get_request_count():
    """Get current request count in the rate limit window"""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    return sum(1 for t in REQUEST_HISTORY.values() if t > window_start)

def record_request():
    """Record a new API request with current timestamp"""
    request_id = hashlib.md5(str(time.time()).encode()).hexdigest()
    REQUEST_HISTORY[request_id] = time.time()
    REQUEST_HISTORY.sync()

def enforce_rate_limit():
    """Enforce rate limiting with adaptive delays"""
    while get_request_count() >= MAX_REQUESTS_PER_WINDOW:
        wait_time = random.uniform(5.0, 15.0)
        print(f"Rate limit approaching, waiting {wait_time:.1f}s...")
        time.sleep(wait_time)

def cached_api_call(url):
    # Check cache first
    cached = read_from_cache(url)
    if cached is not None:
        return cached
        
    # Enforce rate limiting
    enforce_rate_limit()
    
    # Exponential backoff with retries
    retry_count = 0
    last_exception = None
    
    while retry_count < MAX_RETRIES:
        try:
            # Adaptive delay based on system load
            current_load = get_request_count() / MAX_REQUESTS_PER_WINDOW
            base_delay = BASE_DELAY * (1 + current_load)
            delay = min(base_delay * (2 ** retry_count), MAX_DELAY)
            delay += random.uniform(0, 2.0)  # Increased jitter
            
            print(f"Attempt {retry_count+1}, waiting {delay:.1f}s...")
            time.sleep(delay)
            
            # Make the API call
            response = urlopen(url, timeout=15)  # Increased timeout
            record_request()  # Track successful request
            
            # Verify response
            if response.status != 200:
                raise HTTPError(url, response.status, response.reason, response.headers, None)
                
            response_data = response.read().decode('utf-8')
            if not response_data:
                raise Exception("Empty response from API")
                
            data = json.loads(response_data)
            
            if not isinstance(data, (list, dict)):
                raise Exception("Invalid API response format")
            
            # Store in cache
            write_to_cache(url, data)
            return data
            
        except (HTTPError, URLError) as e:
            if isinstance(e, HTTPError) and e.code == 429:
                # On rate limit, increase our backoff
                BASE_DELAY = min(BASE_DELAY * 1.5, 30.0)
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    raise Exception("API rate limit exceeded. Please try again later.")
            elif isinstance(e, HTTPError) and e.code >= 500:
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    raise Exception("Server error occurred. Please try again later.")
            else:
                raise
                
    raise last_exception if last_exception else Exception("API request failed")
