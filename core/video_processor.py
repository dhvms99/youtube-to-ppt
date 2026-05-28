import os
import cv2
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

def extract_frames_from_video(video_path: str, output_dir: str = "frames", threshold: float = 30.0) -> list[str]:
    """
    Detects scene changes in a video and extracts one frame per scene.
    Returns a list of paths to the extracted frame images.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    
    # ContentDetector uses a threshold for detecting cuts between scenes
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    base_timecode = video_manager.get_base_timecode()
    video_manager.set_downscale_factor()
    video_manager.start()

    print("Detecting scenes...")
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list(base_timecode)
    
    print(f"Found {len(scene_list)} scenes.")

    cap = cv2.VideoCapture(video_path)
    frame_paths = []
    prev_frame = None

    for i, scene in enumerate(scene_list):
        # scene is a tuple of (start_time, end_time)
        start_frame = scene[0].get_frames()
        end_frame = scene[1].get_frames()
        
        # Capture the exact middle of the scene to avoid fade/transition blurs
        target_frame = start_frame + (end_frame - start_frame) // 2
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        
        if ret:
            # Deduplication: convert to grayscale to check for identical slides
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_frame is not None:
                # Calculate mean absolute difference
                diff = cv2.absdiff(gray, prev_frame).mean()
                # If difference is extremely small, it's essentially the same slide
                if diff < 1.0:
                    continue
            
            prev_frame = gray.copy()
            frame_path = os.path.join(output_dir, f"scene_{len(frame_paths):04d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)

    cap.release()
    return frame_paths
