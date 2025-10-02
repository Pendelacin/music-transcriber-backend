import yt_dlp
import os
from pathlib import Path

class VideoDownloader:
    def __init__(self, output_dir='downloads'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def download_audio(self, url):
        """Download audio from YouTube URL"""
        try:
            output_template = str(self.output_dir / '%(id)s.%(ext)s')
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_file = str(self.output_dir / f"{info['id']}.mp3")
                
                return {
                    'success': True,
                    'file_path': audio_file,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0)
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup(self, file_path):
        """Delete downloaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Cleanup error: {e}")