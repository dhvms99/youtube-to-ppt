import streamlit as st
import os
import shutil
import tempfile
from core.downloader import download_youtube_video
from core.video_processor import extract_frames_from_video
from core.ocr_engine import extract_text_from_image
from core.ppt_generator import create_ppt_from_texts

st.set_page_config(page_title="YouTube to Editable PPT", page_icon="🎥", layout="centered")

st.title("🎥 YouTube to Editable PPT")
st.write("Convert YouTube videos (e.g., lecture slides) into editable PowerPoint presentations.")

youtube_url = st.text_input("Enter YouTube URL:")

st.write("---")
st.subheader("⚙️ 고급 설정 (Advanced Settings)")
st.write("동영상의 성격에 따라 텍스트 인식(장면 전환) 민감도를 조절할 수 있습니다.")
threshold = st.slider(
    "장면 전환 감지 임계값 (Threshold)", 
    min_value=1.0, 
    max_value=30.0, 
    value=5.0, 
    step=1.0,
    help="값이 낮을수록 작은 변화(예: 텍스트 변경)에도 장면 전환으로 인식합니다. 배경이 동일하고 텍스트만 바뀌는 영상은 3~8 사이를 추천합니다."
)

if st.button("Convert to PPT"):
    if not youtube_url:
        st.warning("Please enter a valid YouTube URL.")
    else:
        # Create a temporary directory for processing
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                # Step 1: Download Video
                with st.spinner("Downloading video... (This might take a while for long videos)"):
                    video_dir = os.path.join(tmpdir, "video")
                    video_path = download_youtube_video(youtube_url, output_dir=video_dir)
                st.success("✅ Video downloaded.")

                # Step 2: Scene Detection and Frame Extraction
                with st.spinner("Detecting scenes and extracting frames... (This might take a while depending on threshold)"):
                    frames_dir = os.path.join(tmpdir, "frames")
                    frame_paths = extract_frames_from_video(video_path, output_dir=frames_dir, threshold=threshold)
                
                if not frame_paths:
                    st.error("No scenes detected in the video.")
                else:
                    st.success(f"✅ Extracted {len(frame_paths)} unique scene frames.")

                    # Step 3: OCR Text Extraction
                    progress_text = "Extracting text from frames (OCR)..."
                    my_bar = st.progress(0, text=progress_text)
                    
                    extracted_texts = []
                    total_frames = len(frame_paths)
                    for i, frame_path in enumerate(frame_paths):
                        text = extract_text_from_image(frame_path)
                        extracted_texts.append(text)
                        
                        # Update progress bar
                        progress = (i + 1) / total_frames
                        my_bar.progress(progress, text=f"{progress_text} ({i+1}/{total_frames})")
                    
                    st.success("✅ Text extraction complete.")

                    # Step 4: PPT Generation
                    with st.spinner("Generating PowerPoint presentation..."):
                        ppt_output_path = os.path.join(tmpdir, "output.pptx")
                        create_ppt_from_texts(extracted_texts, output_path=ppt_output_path)
                    
                    st.success("✅ PPT successfully generated!")

                    # Step 5: Provide Download Button
                    with open(ppt_output_path, "rb") as file:
                        btn = st.download_button(
                            label="Download PPTX",
                            data=file,
                            file_name="converted_presentation.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
