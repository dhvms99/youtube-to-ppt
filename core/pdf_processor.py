import pdfplumber

def get_dynamic_split_x(page, width, bottom_cut):
    """
    Dynamically finds the vertical split line by searching for a vertical gap
    where no text bounding boxes cross.
    Searches between 35% and 65% of the page width.
    """
    search_start = width * 0.35
    search_end = width * 0.65
    
    # Extract words. We only consider words that are above the bottom_cut
    words = page.extract_words()
    valid_words = [w for w in words if w['bottom'] <= bottom_cut]
    
    valid_gaps = []
    # Check X coordinates in the center region
    for x in range(int(search_start), int(search_end)):
        crosses = False
        for w in valid_words:
            # If word's left bound is before X and right bound is after X
            if w['x0'] < x < w['x1']:
                crosses = True
                break
        if not crosses:
            valid_gaps.append(x)
            
    if valid_gaps:
        # If there are multiple valid gap coordinates, we take the average (middle of the gap)
        return sum(valid_gaps) / len(valid_gaps)
        
    return None  # No clear gap found (e.g. title page or full-width intro text)

def extract_half_texts_from_pdf(pdf_path: str) -> list[tuple[str, str]]:
    """
    Extracts text from a PDF, ignoring the bottom 4.6%.
    Dynamically splits each page into left and right halves based on text gaps.
    Skips pages that do not have a clear two-column structure.
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
            
            # Dynamically detect split line
            split_x = get_dynamic_split_x(page, width, bottom_cut)
            
            if split_x is None:
                # Skip pages that don't have a clear two-column gap
                continue
            
            # Left bounding box: (0, 0, split_x, bottom_cut)
            left_bbox = (0, 0, split_x, bottom_cut)

            # Right bounding box: (split_x, 0, width, bottom_cut)
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
