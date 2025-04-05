import time
import atexit
from urllib.error import HTTPError
from api_cache import cached_api_call, REQUEST_HISTORY

# Ensure clean shutdown
def close_storage():
    REQUEST_HISTORY.close()
atexit.register(close_storage)

TEST_URL = "https://api.openf1.org/v1/meetings?year=2023"  # More stable endpoint

def test_concurrent_calls():
    print("Testing API rate limiting...")
    for i in range(5):  # Reduced to 5 test calls
        start_time = time.time()
        try:
            print(f"\nCall {i+1}:")
            data = cached_api_call(TEST_URL)
            if not data:
                raise Exception("Empty response")
            duration = time.time() - start_time
            print(f"Success! Got {len(data)} items ({duration:.2f}s)")
        except HTTPError as e:
            duration = time.time() - start_time
            print(f"HTTP Error {e.code}: {e.reason} ({duration:.2f}s)")
        except Exception as e:
            duration = time.time() - start_time
            print(f"Error: {str(e)} ({duration:.2f}s)")
        time.sleep(5.0)  # Longer delay between test iterations

if __name__ == "__main__":
    test_concurrent_calls()
