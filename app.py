import streamlit as st
import os
import tempfile
from core.downloader import download_youtube_video
from core.video_processor import extract_frames_from_video
from core.ocr_engine import extract_text_from_image
from core.ppt_generator import create_ppt_from_texts
from core.pdf_processor import extract_half_texts_from_pdf
from core.translator import translate_text
from core.word_generator import create_translated_word_doc

st.set_page_config(page_title="AI Productivity Tools", page_icon="⚡", layout="centered")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
service_mode = st.sidebar.radio("Select a Service:", ("🎥 YouTube to PPT", "📄 PDF 반반 번역기"))

st.sidebar.write("---")
st.sidebar.subheader("🔑 API 설정 (API Settings)")
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key", 
    type="password", 
    placeholder="sk-...", 
    help="OpenAI API 키를 입력해 주세요. (시스템 환경 변수 'OPENAI_API_KEY'가 설정되어 있다면 비워두셔도 됩니다.)"
)

if service_mode == "🎥 YouTube to PPT":
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
    
    use_ai_ocr = st.checkbox("✨ AI OCR 자동 교정 사용 (추천)", value=True, help="gpt-4o-mini를 사용하여 OCR로 추출된 텍스트의 오타(예: ies -> ¿es, g0 -> go)를 문맥에 맞게 완벽히 교정합니다.")

    if st.button("Convert to PPT"):
        if not youtube_url:
            st.warning("Please enter a valid YouTube URL.")
        else:
            api_key = openai_api_key.strip()
            if use_ai_ocr and not api_key and not os.environ.get("OPENAI_API_KEY"):
                st.error("🔑 AI OCR 교정을 사용하려면 사이드바에 OpenAI API Key를 입력해 주세요.")
            else:
                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        with st.spinner("Downloading video... (This might take a while for long videos)"):
                            video_dir = os.path.join(tmpdir, "video")
                            video_path = download_youtube_video(youtube_url, output_dir=video_dir)
                        st.success("✅ Video downloaded.")

                        with st.spinner("Detecting scenes and extracting frames... (This might take a while depending on threshold)"):
                            frames_dir = os.path.join(tmpdir, "frames")
                            frame_paths = extract_frames_from_video(video_path, output_dir=frames_dir, threshold=threshold)
                        
                        if not frame_paths:
                            st.error("No scenes detected in the video.")
                        else:
                            st.success(f"✅ Extracted {len(frame_paths)} unique scene frames.")

                            progress_text = "Extracting text from frames (OCR)..."
                            my_bar = st.progress(0, text=progress_text)
                            
                            extracted_texts = []
                            total_frames = len(frame_paths)
                            for i, frame_path in enumerate(frame_paths):
                                text = extract_text_from_image(frame_path)
                                
                                if use_ai_ocr and text.strip():
                                    from core.ocr_engine import correct_ocr_text_with_ai
                                    text = correct_ocr_text_with_ai(text, api_key)
                                    
                                extracted_texts.append(text)
                                progress = (i + 1) / total_frames
                                my_bar.progress(progress, text=f"{progress_text} ({i+1}/{total_frames})")
                            
                            st.success("✅ Text extraction complete.")

                            with st.spinner("Generating PowerPoint presentation..."):
                                ppt_output_path = os.path.join(tmpdir, "output.pptx")
                                create_ppt_from_texts(extracted_texts, output_path=ppt_output_path)
                            
                            st.success("✅ PPT successfully generated!")

                            with open(ppt_output_path, "rb") as file:
                                st.download_button(
                                    label="Download PPTX",
                                    data=file,
                                    file_name="converted_presentation.pptx",
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                                )
                    except Exception as e:
                        st.error(f"An error occurred during processing: {e}")

elif service_mode == "📄 PDF 반반 번역기":
    st.title("📄 PDF 반반 번역기")
    st.write("PDF의 왼쪽 50% 텍스트를 한국어로 번역하여, 원문(우측)과 나란히 워드(.docx) 파일로 만들어줍니다.")
    st.write("*(참고: 하단 4.6%의 광고/꼬리말 영역은 자동으로 제외됩니다.)*")
    
    uploaded_pdf = st.file_uploader("Upload your PDF file:", type=["pdf"])
    
    if st.button("Translate & Convert to Word"):
        if not uploaded_pdf:
            st.warning("Please upload a PDF file first.")
        else:
            api_key = openai_api_key.strip()
            if not api_key and not os.environ.get("OPENAI_API_KEY"):
                st.error("🔑 OpenAI API Key가 필요합니다. 사이드바에 API Key를 입력하거나 시스템 환경 변수에 설정해 주세요.")
            else:
                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        pdf_path = os.path.join(tmpdir, "uploaded.pdf")
                        with open(pdf_path, "wb") as f:
                            f.write(uploaded_pdf.getbuffer())
                            
                        with st.spinner("Extracting text from PDF (ignoring right half and bottom 4.6%)..."):
                            pages_data = extract_half_texts_from_pdf(pdf_path)
                        st.success(f"✅ Extracted text from {len(pages_data)} pages.")
                        
                        with st.spinner("Translating left-side text to Korean..."):
                            translated_pages = []
                            my_bar = st.progress(0, text="Translating pages...")
                            total_pages = len(pages_data)
                            
                            for i, (left_text, right_text) in enumerate(pages_data):
                                translated_left = translate_text(left_text, api_key=api_key) if left_text else ""
                                translated_pages.append((translated_left, right_text))
                                my_bar.progress((i + 1) / total_pages, text=f"Translating pages... ({i+1}/{total_pages})")
                                
                        st.success("✅ Translation complete.")
                        
                        with st.spinner("Generating Word document..."):
                            docx_output_path = os.path.join(tmpdir, "translated_output.docx")
                            create_translated_word_doc(translated_pages, output_path=docx_output_path)
                        
                        st.success("✅ Word document successfully generated!")
                        
                        with open(docx_output_path, "rb") as file:
                            st.download_button(
                                label="Download Word (.docx)",
                                data=file,
                                file_name="translated_document.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    except Exception as e:
                        st.error(f"An error occurred during PDF processing: {e}")

