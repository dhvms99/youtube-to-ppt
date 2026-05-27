import os
import yt_dlp

def download_youtube_video(url: str, output_dir: str = "downloads") -> str:
    """
    Downloads a YouTube video to the specified output directory.
    Returns the path to the downloaded video file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # We use a specific format that gives us a good resolution for OCR but not too huge.
    # bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best
    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_id = info_dict.get("id", None)
        ext = info_dict.get("ext", "mp4")
        
        # In case yt-dlp merges into mp4
        final_ext = "mp4" if ydl_opts.get('merge_output_format') == 'mp4' else ext
        file_path = os.path.join(output_dir, f"{video_id}.{final_ext}")
        
        return file_path
