#!/usr/bin/env python3
"""
PathForm Benchmark Tool

Benchmarks parsing and conversion performance.
"""

import time
import sys
from pathform import parse_pathform, from_json, to_json

# Large test data
LARGE_PATHFORM = """
# Large PathForm test data
""" + "\n".join([
    f"config.servers[{i}].host = server{i}.example.com"
    f"\nconfig.servers[{i}].port = {8000 + i}"
    f"\nconfig.servers[{i}].enabled = true"
    for i in range(1000)
]) + "\n" + "\n".join([
    f"data.items[{i}].id = {i}"
    f"\ndata.items[{i}].name = item{i}"
    f"\ndata.items[{i}].value = {i * 1.5}"
    for i in range(1000)
])


def benchmark_parse(iterations=100):
    """Benchmark parsing performance."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        parse_pathform(LARGE_PATHFORM)
        end = time.perf_counter()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Parse benchmark ({iterations} iterations):")
    print(f"  Average: {avg_time*1000:.2f} ms")
    print(f"  Min: {min_time*1000:.2f} ms")
    print(f"  Max: {max_time*1000:.2f} ms")
    print(f"  Throughput: {len(LARGE_PATHFORM) / avg_time / 1024:.2f} KB/s")
    print()


def benchmark_round_trip(iterations=100):
    """Benchmark round-trip conversion."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        obj = parse_pathform(LARGE_PATHFORM)
        pathform = from_json(obj)
        reparsed = parse_pathform(pathform)
        end = time.perf_counter()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    
    print(f"Round-trip benchmark ({iterations} iterations):")
    print(f"  Average: {avg_time*1000:.2f} ms")
    print(f"  Throughput: {len(LARGE_PATHFORM) / avg_time / 1024:.2f} KB/s")
    print()


def benchmark_json_conversion(iterations=100):
    """Benchmark JSON conversion."""
    obj = parse_pathform(LARGE_PATHFORM)
    
    # To JSON
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        to_json(LARGE_PATHFORM)
        end = time.perf_counter()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    print(f"PathForm to JSON ({iterations} iterations):")
    print(f"  Average: {avg_time*1000:.2f} ms")
    print()
    
    # From JSON
    import json
    json_str = json.dumps(obj)
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        from_json(obj)
        end = time.perf_counter()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    print(f"JSON to PathForm ({iterations} iterations):")
    print(f"  Average: {avg_time*1000:.2f} ms")
    print()


def main():
    parser = argparse.ArgumentParser(description='Benchmark PathForm performance')
    parser.add_argument(
        '--iterations',
        type=int,
        default=100,
        help='Number of iterations (default: 100)'
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("PathForm Benchmark")
    print("=" * 50)
    print(f"Test data size: {len(LARGE_PATHFORM)} bytes")
    print()
    
    benchmark_parse(args.iterations)
    benchmark_round_trip(args.iterations)
    benchmark_json_conversion(args.iterations)


if __name__ == '__main__':
    main()

