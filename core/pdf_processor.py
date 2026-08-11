import pdfplumber

def get_dynamic_split_x(page, width, bottom_cut):
    """
    Dynamically finds the vertical split line by searching for a vertical gap
    where no text bounding boxes cross.
    Searches between 35% and 65% of the page width.

    The source PDFs place the English and Spanish columns around the page
    center, separated by a narrow gutter. The English text is right-aligned
    and extends slightly past the physical 50% point, so splitting at exactly
    ``width / 2`` cuts off the final characters of each English line. The
    gutter is not at a fixed offset either, so it is located per page instead
    of being hardcoded to a ratio.
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
        # Group continuous gaps into segments to find the true column divider
        segments = []
        current_segment = [valid_gaps[0]]
        for x in valid_gaps[1:]:
            if x == current_segment[-1] + 1:
                current_segment.append(x)
            else:
                segments.append(current_segment)
                current_segment = [x]
        segments.append(current_segment)
        
        # Find the segment closest to the center of the page
        center = width / 2.0
        best_segment = min(segments, key=lambda seg: abs(sum(seg)/len(seg) - center))
        
        return sum(best_segment) / len(best_segment)
        
    return None  # No clear gap found (e.g. title page or full-width intro text)

def extract_half_texts_from_pdf(pdf_path: str) -> list[tuple[str, str]]:
    """
    Extracts text from a PDF, ignoring the bottom 4.6%.
    Splits each page at the inter-column gutter, located dynamically from the
    text gaps. Skips pages that do not have a clear two-column structure.
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
            
            # Locate the gutter for this page so English line endings stay in
            # the left column and Spanish begins cleanly in the right.
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
