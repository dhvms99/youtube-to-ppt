import pdfplumber

def extract_half_texts_from_pdf(pdf_path: str) -> list[tuple[str, str]]:
    """
    Extracts text from a PDF, ignoring the bottom 4.6%.
    Splits each page into left 50% and right 50%.
    Returns a list of tuples: (left_text, right_text) per page.
    """
    extracted_pages = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            width = page.width
            height = page.height
            
            # The bottom 4.6% is ignored. 
            # In pdfplumber, y0 is top, y1 is bottom (actually it depends on coordinate system, 
            # but usually (x0, top, x1, bottom) is used for cropping).
            # pdfplumber bbox: (x0, top, x1, bottom)
            bottom_cut = height * (1.0 - 0.046)
            
            # Left bounding box: (0, 0, width/2, bottom_cut)
            left_bbox = (0, 0, width / 2, bottom_cut)
            # Right bounding box: (width/2, 0, width, bottom_cut)
            right_bbox = (width / 2, 0, width, bottom_cut)
            
            # Crop pages
            left_crop = page.within_bbox(left_bbox)
            right_crop = page.within_bbox(right_bbox)
            
            # Extract text
            left_text = left_crop.extract_text() or ""
            right_text = right_crop.extract_text() or ""
            
            # Clean up newlines if necessary, but PDF newlines might be structural.
            # We will keep them as is.
            extracted_pages.append((left_text.strip(), right_text.strip()))
            
    return extracted_pages
