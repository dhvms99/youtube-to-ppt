import os
import cv2

def extract_frames_from_video(video_path: str, output_dir: str = "frames", threshold: float = 2.0) -> list[str]:
    """
    Detects presentation slide changes by finding stable frames that differ from the last saved slide.
    This works much better than traditional scene cut detectors for lecture videos.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or fps > 120:
        fps = 30.0
        
    # Process ~3 frames per second. Fast enough to catch everything, but skips unnecessary frames.
    frame_interval = max(1, int(fps / 3))
    
    frame_paths = []
    last_saved_gray = None
    prev_gray = None
    
    # Stability threshold: if the screen changes by less than 0.5 mean pixels between checks, it is "stable"
    stability_threshold = 0.5 
    
    frame_count = 0
    print("Detecting slide transitions...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # Resize image to a smaller resolution for extremely fast diff calculation (e.g., 640x360)
            # This also filters out minor video compression noise
            small_frame = cv2.resize(frame, (640, 360))
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            
            if prev_gray is None:
                prev_gray = gray
                frame_count += 1
                continue
                
            # 1. Check if the screen is stable (no fade transitions, animations, or scrolling)
            frame_diff = cv2.absdiff(gray, prev_gray).mean()
            is_stable = frame_diff < stability_threshold
            
            if is_stable:
                if last_saved_gray is None:
                    # Always save the very first stable frame
                    last_saved_gray = gray.copy()
                    frame_path = os.path.join(output_dir, f"scene_{len(frame_paths):04d}.jpg")
                    cv2.imwrite(frame_path, frame) # Save ORIGINAL high-res frame
                    frame_paths.append(frame_path)
                else:
                    # 2. If stable, check if it's a NEW slide compared to the last saved one
                    slide_diff = cv2.absdiff(gray, last_saved_gray).mean()
                    
                    # If difference exceeds the user threshold (e.g., 1.0 or 2.0), save it!
                    if slide_diff > threshold:
                        last_saved_gray = gray.copy()
                        frame_path = os.path.join(output_dir, f"scene_{len(frame_paths):04d}.jpg")
                        cv2.imwrite(frame_path, frame)
                        frame_paths.append(frame_path)
            
            prev_gray = gray.copy()
            
        frame_count += 1

    cap.release()
    print(f"Found {len(frame_paths)} unique slides.")
    return frame_paths
