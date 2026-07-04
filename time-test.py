import time
from rag_engine import CampusRAGEngine

def run_latency_benchmark(queries):
    if not queries:
        print("No queries provided.")
        return

    print("Initializing CampusRAGEngine (this time is not counted toward query latency)...")
    try:
        engine = CampusRAGEngine()
    except Exception as e:
        print(f"Failed to initialize engine: {e}")
        return

    print(f"\nStarting latency benchmark for {len(queries)} queries...\n")
    
    total_time = 0.0
    latencies = []

    for i, query in enumerate(queries, 1):
        # perf_counter is the most precise method for measuring code execution time
        start_time = time.perf_counter()
        
        try:
            # Using the specific method you requested
            response = engine.get_response(query)
        except Exception as e:
            print(f"Query {i}/{len(queries)} Failed: {e}")
            continue
            
        end_time = time.perf_counter()
        
        latency = end_time - start_time
        latencies.append(latency)
        total_time += latency
        
        print(f"Query {i}/{len(queries)}: {latency:.3f}s | '{query}'")

    if not latencies:
        print("\nBenchmark failed. No queries completed successfully.")
        return

    # Calculate statistics
    avg_latency = total_time / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)

    # Print final report
    print("\n" + "="*45)
    print(" ⚡ CAMPUSBOT LATENCY BENCHMARK")
    print("="*45)
    print(f"Total Queries Processed : {len(latencies)}")
    print(f"Total Execution Time    : {total_time:.3f} seconds")
    print("-" * 45)
    print(f"Average Latency         : {avg_latency:.3f} seconds/query")
    print(f"Fastest Query           : {min_latency:.3f} seconds")
    print(f"Slowest Query           : {max_latency:.3f} seconds")
    print("="*45)

if __name__ == "__main__":
    # Test queries tuned for DTU
    test_queries = [
        "Who is the Head of Training and Placement at DTU?",
        "Can a Placement Coordinator undertake a six-month internship if they secure a full-time job offer?",
        "What happens if a PC joins an internship without prior permission from T&P?",
        "Who is the Dean Academic (UG)?",
        "Who is the Registrar of DTU who signed the notification for faculty extension parameters?"
    ]
    
    run_latency_benchmark(test_queries)