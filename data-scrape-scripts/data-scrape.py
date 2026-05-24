import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def download_pdfs(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links that end with .pdf
    pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]
    
    for link in pdf_links:
        # Convert relative links to absolute URLs
        full_url = urljoin(url, link)
        filename = os.path.join(dest_folder, os.path.basename(urlparse(full_url).path))
        
        print(f"Downloading: {full_url}")
        try:
            pdf_response = requests.get(full_url)
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)
        except Exception as e:
            print(f"Failed to download {full_url}: {e}")

if __name__ == "__main__":
    target_url = "https://dtu.ac.in/"
    save_path = "campus-assistant/data"
    download_pdfs(target_url, save_path)