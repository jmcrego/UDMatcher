#!/usr/bin/env python3
"""
Quick health check and index management script for UDMatcher.

Usage:
    python scripts/health_check.py                  - Show health status
    python scripts/health_check.py --list           - List all indices
    python scripts/health_check.py --stats          - Show statistics only
"""

import requests
import json
import sys


BASE_URL = "http://localhost:8000"


def check_server():
    """Check if server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        print("✗ Server not running at {BASE_URL}")
        print("  Start server: uvicorn app.main:app --reload")
        return False, None
    except Exception as e:
        print(f"✗ Error: {e}")
        return False, None


def show_full_health(data):
    """Show complete health information."""
    print("\n" + "=" * 70)
    print("  UDMatcher Health Check")
    print("=" * 70)
    
    # Indices
    indices = data.get('indices', [])
    print(f"\nLoaded Indices: {len(indices)}")
    for idx in indices:
        print(f"  • {idx['name']}: {idx['size']} entries")
    
    # Cache
    cache = data.get('cache', {})
    print(f"\nCache Configuration:")
    print(f"  • Status: {'Enabled' if cache.get('enabled') else 'Disabled'}")
    print(f"  • Backend: {cache.get('type', 'N/A')}")
    print(f"  • Size: {cache.get('size', 0)}/{cache.get('max_size', 0)}")
    
    # Statistics
    stats = data.get('statistics', {})
    print(f"\nService Statistics:")
    print(f"  • Total Requests: {stats.get('total_requests', 0)}")
    print(f"  • Successful: {stats.get('successful_requests', 0)}")
    print(f"  • Errors: {stats.get('total_errors', 0)}")
    print(f"  • Cache Hits: {stats.get('cache_hits', 0)}")
    print(f"  • Cache Misses: {stats.get('cache_misses', 0)}")
    print(f"  • Hit Rate: {stats.get('cache_hit_rate_percent', 0):.2f}%")
    print(f"  • Avg Runtime: {stats.get('average_runtime_ms', 0):.2f}ms")
    
    print("\n" + "=" * 70 + "\n")


def list_indices(data):
    """List indices only."""
    indices = data.get('indices', [])
    if not indices:
        print("No indices loaded")
    else:
        print(f"Loaded Indices ({len(indices)}):")
        for idx in indices:
            print(f"  • {idx['name']}: {idx['size']} entries")


def show_stats(data):
    """Show statistics only."""
    stats = data.get('statistics', {})
    print("\nService Statistics:")
    print(f"  Total Requests:    {stats.get('total_requests', 0)}")
    print(f"  Successful:        {stats.get('successful_requests', 0)}")
    print(f"  Errors:            {stats.get('total_errors', 0)}")
    print(f"  Cache Hits:        {stats.get('cache_hits', 0)}")
    print(f"  Cache Misses:      {stats.get('cache_misses', 0)}")
    print(f"  Hit Rate:          {stats.get('cache_hit_rate_percent', 0):.2f}%")
    print(f"  Avg Runtime:       {stats.get('average_runtime_ms', 0):.2f}ms")
    print(f"  Min Runtime:       {stats.get('min_runtime_ms', 0):.2f}ms")
    print(f"  Max Runtime:       {stats.get('max_runtime_ms', 0):.2f}ms")


def main():
    """Main entry point."""
    running, data = check_server()
    if not running:
        return
    
    print("✓ Server is running")
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--list', '-l']:
            list_indices(data)
        elif arg in ['--stats', '-s']:
            show_stats(data)
        else:
            print(f"Unknown option: {arg}")
    else:
        show_full_health(data)


if __name__ == "__main__":
    main()
