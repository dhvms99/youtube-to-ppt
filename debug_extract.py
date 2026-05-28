from core.pdf_processor import extract_half_texts_from_pdf

def debug_pdf_text():
    pages_data = extract_half_texts_from_pdf("mini-course-1.pdf")
    if not pages_data:
        print("No data extracted.")
        return
        
    for i, (left_text, right_text) in enumerate(pages_data[:3]): # Check first 3 pages
        print(f"--- PAGE {i+1} LEFT ---")
        print(repr(left_text[:200]))
        print(f"--- PAGE {i+1} RIGHT ---")
        print(repr(right_text[:200]))
        print("-------------------")

if __name__ == "__main__":
    debug_pdf_text()
