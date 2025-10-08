from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import re
import logging
from pathlib import Path
import time

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_FOLDER = Path('downloads')
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

def sanitize_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename[:200]

def cleanup_old_files():
    try:
        for file in DOWNLOAD_FOLDER.glob('*'):
            if file.is_file():
                file.unlink()
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "index.html not found", 404

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/info', methods=['POST'])
def get_video_info():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'No URL'}), 400
        
        logger.info(f"Info request: {url}")
        
        # Simplified options to avoid hanging
        ydl_opts = {
            'quiet': False,
            'no_warnings': False, 
            'skip_download': True,
            'socket_timeout': 15,
            'extractor_retries': 2,
            'legacy_server_connect': True,
            'noplaylist': True,  # Only download single video, not playlist
        }
        
        logger.info("Starting yt-dlp extraction...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            logger.info("Extraction successful!")
            
            if not info:
                return jsonify({'error': 'Not found'}), 404
            
            result = {
                'title': info.get('title', 'Unknown'),
                'channel': info.get('uploader', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'view_count': info.get('view_count', 0),
            }
            
            logger.info(f"Returning info for: {result['title']}")
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Error in get_video_info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        format_type = data.get('format', '360p')
        
        if not url:
            return jsonify({'error': 'No URL'}), 400
        
        logger.info(f"Download request: {format_type} from {url}")
        
        ydl_opts_info = {
            'quiet': True,
            'socket_timeout': 30,
            'no_check_certificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'noplaylist': True,  # Only download single video
        }
        
        logger.info("Fetching video title...")
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'video'))
        
        logger.info(f"Title: {title}")
        
        if format_type == 'mp3':
            filename = f"{title}.mp3"
            filepath = DOWNLOAD_FOLDER / filename
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(filepath.with_suffix('')),
                'quiet': True,
                'socket_timeout': 30,
                'noplaylist': True,
                'no_abort_on_error': True,
            }
        else:
            # Eindeutiger Dateiname mit Qualität, um Cache-Probleme zu vermeiden
            filename = f"{title}_{format_type}.mp4"
            filepath = DOWNLOAD_FOLDER / filename
            
            # Flexiblere Format-Spezifikation für zuverlässige Downloads
            quality_map = {
                '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                '720p': 'bestvideo[height<=720][height>=720]+bestaudio/bestvideo[height<=720]+bestaudio/best[height<=720]',
                '480p': 'bestvideo[height<=480][height>=480]+bestaudio/bestvideo[height<=480]+bestaudio/best[height<=480]',
                '360p': 'bestvideo[height<=360][height>=360]+bestaudio/bestvideo[height<=360]+bestaudio/best[height<=360]',
            }
            
            ydl_opts = {
                'format': quality_map.get(format_type, 'best'),
                'outtmpl': str(filepath),
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'prefer_free_formats': False,
                'quiet': False,  # Temporär auf False für besseres Debugging
                'verbose': True,  # Zeigt welches Format heruntergeladen wird
                'socket_timeout': 30,
                'noplaylist': True,
                'no_abort_on_error': True,
            }
        
        logger.info(f"Downloading: {filename}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if not filepath.exists():
            return jsonify({'error': 'Download failed'}), 500
        
        logger.info(f"Success: {filename}")
        
        mimetype = 'audio/mpeg' if format_type == 'mp3' else 'video/mp4'
        response = send_file(filepath, as_attachment=True, download_name=filename, mimetype=mimetype)
        
        @response.call_on_close
        def cleanup():
            try:
                time.sleep(2)
                if filepath.exists():
                    filepath.unlink()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in download_video: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"YouTube Downloader Started - http://localhost:{port}")
    cleanup_old_files()
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
