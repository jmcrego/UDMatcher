#!/usr/bin/env python3
"""
Example test script demonstrating UDMatcher basic functionality.
Run the server first: uvicorn app.main:app --reload

This script demonstrates:
1. Health check
2. Uploading a sample translation glossary
3. Performing matches
4. Viewing cache and statistics
"""

import requests
import json
import time
from pathlib import Path
import tempfile


BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def test_health_check():
    """Test the /health endpoint."""
    print_section("1. HEALTH CHECK")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Indices loaded: {len(data.get('indices', []))}")
        
        if data.get('cache'):
            cache = data['cache']
            print(f"\nCache Status:")
            print(f"  - Enabled: {cache.get('enabled')}")
            print(f"  - Type: {cache.get('type')}")
            print(f"  - Size: {cache.get('size')}/{cache.get('max_size')}")
        
        if data.get('statistics'):
            stats = data['statistics']
            print(f"\nService Statistics:")
            print(f"  - Total Requests: {stats.get('total_requests')}")
            print(f"  - Cache Hit Rate: {stats.get('cache_hit_rate_percent', 0):.1f}%")
            print(f"  - Average Runtime: {stats.get('average_runtime_ms', 0):.2f}ms")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        print(f"Make sure server is running: uvicorn app.main:app --reload --port 8000")
        return False


def test_upload():
    """Test uploading a sample glossary."""
    print_section("2. UPLOAD SAMPLE GLOSSARY")
    
    # Create a sample TSV file
    sample_data = """hello;hi\tBonjour;Salut
world\tMonde
good morning\tBon matin
thank you\tMerci
please\tS'il vous plaît
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
        f.write(sample_data)
        temp_file = f.name
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': f}
            data = {'name': 'en_fr_sample'}
            
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
            response.raise_for_status()
            result = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_match():
    """Test matching functionality."""
    print_section("3. TEST MATCHING")
    
    test_queries = [
        "I say hello to the world",
        "Good morning, thank you",
        "Please say hello",
        "I say hello to the world",  # Duplicate to test caching
    ]
    
    try:
        for i, query in enumerate(test_queries, 1):
            print(f"\nQuery {i}: \"{query}\"")
            
            payload = {
                "sentence": query,
                "indices": ["en_fr_sample"]
            }
            
            response = requests.post(f"{BASE_URL}/match", json=payload)
            response.raise_for_status()
            result = response.json()
            
            print(f"Runtime: {result.get('runtime_ms', 0):.2f}ms")
            matches = result.get('matches', [])
            
            if matches:
                print(f"Found {len(matches)} match(es):")
                for match in matches:
                    print(f"  - '{match['source']}' → '{match['target']}' at [{match['start']}, {match['end']}]")
            else:
                print("No matches found")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_statistics():
    """Display updated statistics."""
    print_section("4. UPDATED STATISTICS")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        
        if data.get('statistics'):
            stats = data['statistics']
            print("\nFinal Statistics:")
            print(f"  - Total Requests: {stats.get('total_requests')}")
            print(f"  - Successful: {stats.get('successful_requests')}")
            print(f"  - Errors: {stats.get('total_errors')}")
            print(f"  - Cache Hits: {stats.get('cache_hits')}")
            print(f"  - Cache Misses: {stats.get('cache_misses')}")
            print(f"  - Cache Hit Rate: {stats.get('cache_hit_rate_percent', 0):.2f}%")
            print(f"  - Avg Runtime: {stats.get('average_runtime_ms', 0):.2f}ms")
            print(f"  - Min Runtime: {stats.get('min_runtime_ms', 0):.2f}ms")
            print(f"  - Max Runtime: {stats.get('max_runtime_ms', 0):.2f}ms")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  UDMatcher Functionality Test Suite")
    print("=" * 70)
    
    tests = [
        ("Health Check", test_health_check),
        ("Upload Glossary", test_upload),
        ("Perform Matches", test_match),
        ("View Statistics", test_statistics),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} passed")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
