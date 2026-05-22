#!/usr/bin/env python3
"""
Example script demonstrating cache performance of UDMatcher.

This script:
1. Makes multiple identical queries to demonstrate cache hits
2. Tracks statistics before and after
3. Shows the performance improvement from caching
"""

import requests
import json
import time


BASE_URL = "http://localhost:8000"


def get_stats():
    """Get current statistics from server."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def demonstrate_cache_performance():
    """Demonstrate cache performance with repeated queries."""
    
    print("\n" + "=" * 70)
    print("  UDMatcher Cache Performance Demonstration")
    print("=" * 70)
    
    # Ensure we have a loaded index
    print("\n1. Checking for loaded indices...")
    data = get_stats()
    if not data or not data.get('indices'):
        print("   No indices loaded. Upload a glossary first using:")
        print("   python scripts/test_basic_functionality.py")
        return
    
    index_name = data['indices'][0]['name']
    print(f"   Using index: {index_name}")
    
    # Get baseline statistics
    print("\n2. Getting baseline statistics...")
    baseline = get_stats()
    baseline_stats = baseline.get('statistics', {})
    print(f"   - Cache Hits: {baseline_stats.get('cache_hits', 0)}")
    print(f"   - Cache Misses: {baseline_stats.get('cache_misses', 0)}")
    print(f"   - Total Requests: {baseline_stats.get('total_requests', 0)}")
    
    # Perform identical queries multiple times
    test_sentences = [
        "This is a test sentence for caching",
        "Another sample query to cache",
        "Third example for cache demonstration",
    ]
    
    print(f"\n3. Performing queries (2 times each for cache demonstration)...")
    
    for sentence in test_sentences:
        runtimes = []
        for attempt in range(2):
            payload = {"sentence": sentence, "indices": [index_name]}
            
            start = time.time()
            response = requests.post(f"{BASE_URL}/match", json=payload)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            runtimes.append(elapsed)
            
            if attempt == 0:
                print(f"\n   Query: \"{sentence}\"")
                print(f"   - 1st attempt (cache miss): {elapsed:.2f}ms")
            else:
                improvement = ((runtimes[0] - elapsed) / runtimes[0] * 100) if runtimes[0] > 0 else 0
                print(f"   - 2nd attempt (cache hit):  {elapsed:.2f}ms (↓ {improvement:.1f}% faster)")
    
    # Get final statistics
    print(f"\n4. Final Statistics:")
    final = get_stats()
    final_stats = final.get('statistics', {})
    
    print(f"   - Cache Hits: {final_stats.get('cache_hits', 0)}")
    print(f"   - Cache Misses: {final_stats.get('cache_misses', 0)}")
    print(f"   - Cache Hit Rate: {final_stats.get('cache_hit_rate_percent', 0):.2f}%")
    print(f"   - Total Requests: {final_stats.get('total_requests', 0)}")
    print(f"   - Avg Runtime: {final_stats.get('average_runtime_ms', 0):.2f}ms")
    print(f"   - Min Runtime: {final_stats.get('min_runtime_ms', 0):.2f}ms")
    print(f"   - Max Runtime: {final_stats.get('max_runtime_ms', 0):.2f}ms")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    print("Make sure the server is running: uvicorn app.main:app --reload")
    demonstrate_cache_performance()
