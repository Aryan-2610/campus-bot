import time
import ingest

def main():
    """
    Main loop for the ingestion service. Runs indefinitely.
    """
    print("--- Ingestion Service Started ---")
    print("Watching the 'data' folder for new documents...")
    while True:
        try:
            ingest.ingest()
            print(f"Check complete. Waiting for 60 seconds...")
        except Exception as e:
            print(f"!!! An error occurred during ingestion cycle: {e}")
        
        time.sleep(60)

if __name__ == '__main__':
    main()