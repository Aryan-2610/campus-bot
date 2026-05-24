import os
from pypdf import PdfReader

def cleanup_corrupted_pdfs(folder="data"):
    if not os.path.exists(folder):
        print(f"Folder '{folder}' does not exist.")
        return

    print(f"Scanning '{folder}' for corrupted files...")
    
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            filepath = os.path.join(folder, filename)
            try:
                # Attempt to read the PDF
                reader = PdfReader(filepath)
                # If we get here, the file is likely a valid PDF
            except Exception as e:
                print(f"[-] Deleting corrupted file: {filename} | Reason: {e}")
                os.remove(filepath)
            else:
                print(f"[+] Verified: {filename}")

if __name__ == "__main__":
    # Change 'data' to the path where your PDFs are stored
    cleanup_corrupted_pdfs("data")