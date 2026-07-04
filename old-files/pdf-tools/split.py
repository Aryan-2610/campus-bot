import os
from pypdf import PdfReader, PdfWriter

def split_pdf_in_pairs(input_pdf_path, output_dir="split_output"):
    """
    Splits a PDF into multiple PDFs of 2 pages each. 
    Files are saved sequentially as br1.pdf, br2.pdf, etc.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the PDF
    try:
        reader = PdfReader(input_pdf_path)
    except FileNotFoundError:
        print(f"❌ Error: The file '{input_pdf_path}' was not found.")
        return

    total_pages = len(reader.pages)
    
    print(f"📄 Processing '{input_pdf_path}' ({total_pages} pages)...")

    # Initialize a counter for our new file names
    pdf_counter = 1

    # Loop through the pages in steps of 2
    for i in range(0, total_pages, 2):
        writer = PdfWriter()
        
        # Add the first page of the current pair
        writer.add_page(reader.pages[i])
        
        # Add the second page ONLY if it exists (handles the odd-page leftover)
        if i + 1 < total_pages:
            writer.add_page(reader.pages[i + 1])
            
        # Format the new filename using the counter (e.g., "br1.pdf")
        output_filename = f"br{pdf_counter}.pdf"
        output_filepath = os.path.join(output_dir, output_filename)
        
        # Save the new split PDF
        with open(output_filepath, "wb") as output_file:
            writer.write(output_file)
            
        print(f"✅ Saved: {output_filename}")
        
        # Increment the counter for the next loop iteration
        pdf_counter += 1

    print("\n🎉 Splitting complete!")

# --- How to use it ---
if __name__ == "__main__":
    # Replace with the path to your actual PDF file
    target_pdf = "pdf-tools/Admission Brochue Ph_D__R12026-27 (1)_removed.pdf" 
    
    split_pdf_in_pairs(target_pdf)