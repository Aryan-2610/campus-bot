import shutil
import os
import chromadb

# --- A one-time-use script to guarantee a clean database ---

# Use the correct path relative to the backend folder
basedir = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(basedir, '..', 'db')
COLLECTION_NAME = "campus_docs"

def main():
    """
    Completely and safely deletes the entire database directory and the
    ChromaDB collection to ensure a true fresh start.
    """
    print("--- Starting Full Database Reset ---")
    
    if os.path.exists(DB_PATH):
        print(f"Found database directory at: {DB_PATH}")
        try:
            # First, try to gracefully delete the collection if the DB is not corrupted
            client = chromadb.PersistentClient(path=DB_PATH)
            collections = [c.name for c in client.list_collections()]
            if COLLECTION_NAME in collections:
                print(f"Deleting collection '{COLLECTION_NAME}'...")
                client.delete_collection(name=COLLECTION_NAME)
                print("Collection deleted.")
        except Exception as e:
            print(f"Could not connect to Chroma client (this is okay if DB is corrupted). Error: {e}")
        
        # Finally, delete the entire directory tree
        print("Deleting entire 'db' directory...")
        shutil.rmtree(DB_PATH)
        print("Directory 'db' removed successfully.")
    else:
        print(f"Database directory '{DB_PATH}' not found. Nothing to reset.")
        
    print("\n--- Database Reset Complete ---")
    print("You can now start the ingestion service with 'python run_ingestion.py'.")

if __name__ == '__main__':
    main()