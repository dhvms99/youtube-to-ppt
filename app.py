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

import base64

def get_auto_download_html(filepath, filename):
    with open(filepath, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    # Use img onerror hack to execute JS in Streamlit and bypass React script stripping
    html = f'''
        <img src="empty" onerror="
            var link = document.createElement('a');
            link.href = 'data:application/octet-stream;base64,{b64}';
            link.download = '{filename}';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        " style="display:none;">
    '''
    return html

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
        value=2.0, 
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
                                extracted_texts.append(text)
                                progress = (i + 1) / total_frames
                                my_bar.progress(progress, text=f"{progress_text} ({i+1}/{total_frames})")
                            
                            st.success("✅ Text extraction complete.")
                            
                            if use_ai_ocr:
                                with st.spinner("AI가 전체 슬라이드 텍스트를 한 번에 문맥 교정 중입니다... (약 3~5초 소요)"):
                                    from core.ocr_engine import batch_correct_ocr_texts_with_ai
                                    extracted_texts = batch_correct_ocr_texts_with_ai(extracted_texts, api_key)
                                st.success("✅ AI OCR correction complete.")

                            with st.spinner("Generating PowerPoint presentation..."):
                                ppt_output_path = os.path.join(tmpdir, "output.pptx")
                                create_ppt_from_texts(extracted_texts, output_path=ppt_output_path)
                            
                            st.success("✅ PPT successfully generated! (자동 다운로드 진행 중...)")
                            
                            # Auto download
                            download_html = get_auto_download_html(ppt_output_path, "converted_presentation.pptx")
                            st.markdown(download_html, unsafe_allow_html=True)
                            
                            st.write("*(브라우저 팝업 차단 등으로 자동 다운로드가 안 된 경우 아래 버튼을 누르세요)*")
                            with open(ppt_output_path, "rb") as file:
                                st.download_button(
                                    label="📥 수동 다운로드 (PPTX)",
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
                                # 구조적 원인 해결: 왼쪽(영어) 텍스트가 50% 분할선에 의해 글자가 잘리면서(truncation), 
                                # 'today'가 'toda'로, 'here'가 'her'로 잘려 스페인어/엉뚱한 단어로 인식되는 현상이 발생했습니다.
                                # 또한 왼쪽과 오른쪽의 줄바꿈 개수가 달라 표가 어긋나는 문제가 있었습니다.
                                # 이를 해결하기 위해 원본 스페인어(right_text)를 기준으로 번역하여 왼쪽에 배치합니다.
                                translated_left = translate_text(right_text, api_key=api_key) if right_text else ""
                                translated_pages.append((translated_left, right_text))
                                my_bar.progress((i + 1) / total_pages, text=f"Translating pages... ({i+1}/{total_pages})")
                                
                        st.success("✅ Translation complete.")
                        
                        with st.spinner("Generating Word document..."):
                            docx_output_path = os.path.join(tmpdir, "translated_output.docx")
                            create_translated_word_doc(translated_pages, output_path=docx_output_path)
                        
                        st.success("✅ Word document successfully generated! (자동 다운로드 진행 중...)")
                        
                        # Auto download
                        download_html = get_auto_download_html(docx_output_path, "translated_document.docx")
                        st.markdown(download_html, unsafe_allow_html=True)
                        
                        st.write("*(브라우저 팝업 차단 등으로 자동 다운로드가 안 된 경우 아래 버튼을 누르세요)*")
                        with open(docx_output_path, "rb") as file:
                            st.download_button(
                                label="📥 수동 다운로드 (Word)",
                                data=file,
                                file_name="translated_document.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        
                    except Exception as e:
                        st.error(f"An error occurred during PDF processing: {e}")

