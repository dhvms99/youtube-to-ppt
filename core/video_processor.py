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

    for i, scene in enumerate(scene_list):
        # scene is a tuple of (start_time, end_time)
        # We will capture a frame slightly after the start to avoid transition blurs.
        start_frame = scene[0].get_frames()
        end_frame = scene[1].get_frames()
        
        # Capture middle of the scene or 5 frames after start
        target_frame = start_frame + min(5, (end_frame - start_frame) // 2)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        
        if ret:
            frame_path = os.path.join(output_dir, f"scene_{i:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)

    cap.release()
    return frame_paths
