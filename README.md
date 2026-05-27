# YouTube to PPT Service

A service that extracts text from YouTube videos (using scene detection) and converts them into editable PowerPoint (.pptx) presentations.

## Prerequisites

1.  **Python 3.9+**
2.  **CUDA (Optional but recommended):** Since you have an RTX 5060, using CUDA will make text extraction significantly faster.

## Installation

1.  **Install PyTorch with CUDA support:**
    Before installing the requirements, you should install a version of PyTorch that supports your GPU. Open your terminal and run:
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    ```
    *(Note: adjust `cu118` to `cu121` etc. if you have a newer CUDA toolkit installed).*

2.  **Install project dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install System Dependencies:**
    -   You might need to install `ffmpeg` and ensure it's in your system's PATH, as `yt-dlp` relies on it to merge video and audio in some cases. You can download it from [ffmpeg.org](https://ffmpeg.org/download.html).

## How to Run

Run the Streamlit application:

```bash
cd c:\Projects\youtube-to-ppt
streamlit run app.py
```

This will open a web browser tab where you can paste a YouTube URL and click "Convert to PPT".
