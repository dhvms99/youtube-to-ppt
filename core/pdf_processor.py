import pdfplumber

# The source PDFs place the English and Spanish columns around the page center,
# separated by a narrow gutter.  The English text is right-aligned and extends
# slightly past the physical 50% point, so splitting at exactly ``width / 2``
# cuts off the final characters of each English line.
COLUMN_SPLIT_RATIO = 0.52

def extract_half_texts_from_pdf(pdf_path: str) -> list[tuple[str, str]]:
    """
    Extracts text from a PDF, ignoring the bottom 4.6%.
    Splits each page at the inter-column gutter.
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
            
            # These bilingual worksheets have a gutter just to the right of
            # the physical page center.  Use that gutter (52% of page width)
            # rather than the exact midpoint so English line endings remain
            # in the left column and Spanish begins cleanly in the right.
            split_x = width * COLUMN_SPLIT_RATIO
            left_bbox = (0, 0, split_x, bottom_cut)
            right_bbox = (split_x, 0, width, bottom_cut)
            
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
