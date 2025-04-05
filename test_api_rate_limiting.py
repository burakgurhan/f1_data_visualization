import time
from api_cache import cached_api_call

TEST_URL = "https://api.openf1.org/v1/drivers"  # Example endpoint

def test_concurrent_calls():
    print("Testing API rate limiting...")
    for i in range(10):  # Simulate burst of 10 calls
        start_time = time.time()
        try:
            print(f"Call {i+1}: ", end="")
            data = cached_api_call(TEST_URL)
            duration = time.time() - start_time
            print(f"Success! ({duration:.2f}s)")
        except Exception as e:
            duration = time.time() - start_time
            print(f"Failed: {str(e)} ({duration:.2f}s)")
        time.sleep(0.1)  # Small delay between test iterations

if __name__ == "__main__":
    test_concurrent_calls()
