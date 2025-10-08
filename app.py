from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import re
import logging
from pathlib import Path
import time
import hashlib
import threading
import json
import tempfile

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_FOLDER = Path('downloads')
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Track downloads in progress
downloads_status = {}

# Setup cookies if provided via environment variable
COOKIES_FILE = None
if os.environ.get('YOUTUBE_COOKIES'):
    try:
        # Create temporary cookie file
        COOKIES_FILE = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        # Decode base64 cookies if needed, or use raw
        cookies_data = os.environ.get('YOUTUBE_COOKIES')
        COOKIES_FILE.write(cookies_data)
        COOKIES_FILE.close()
        logger.info(f"Cookies loaded from environment variable: {COOKIES_FILE.name}")
    except Exception as e:
        logger.error(f"Failed to load cookies: {e}")
        COOKIES_FILE = None

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
        
        # Use yt-dlp with cookies if available
        ydl_opts = {
            'quiet': False,
            'no_warnings': False, 
            'skip_download': True,
            'socket_timeout': 30,
            'extractor_retries': 3,
            'noplaylist': True,
            'nocheckcertificate': True,
            # Use iOS client as fallback
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android'],
                }
            },
        }
        
        # Add cookies if available
        if COOKIES_FILE:
            ydl_opts['cookiefile'] = COOKIES_FILE.name
            logger.info("Using cookies for authentication")
        else:
            logger.warning("No cookies available - may encounter bot detection")
        
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
    """Start async download and return download ID"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        format_type = data.get('format', '360p')
        
        if not url:
            return jsonify({'error': 'No URL'}), 400
        
        # Create unique download ID
        download_id = hashlib.md5(f"{url}{format_type}{time.time()}".encode()).hexdigest()
        
        logger.info(f"Starting download {download_id}: {format_type} from {url}")
        
        # Initialize status
        downloads_status[download_id] = {
            'status': 'starting',
            'progress': 0,
            'filename': None,
            'filepath': None
        }
        
        # Start download in background thread
        thread = threading.Thread(target=_download_worker, args=(download_id, url, format_type))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'download_id': download_id,
            'status': 'started'
        })
        
    except Exception as e:
        logger.error(f"Error starting download: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def _download_worker(download_id, url, format_type):
    """Background worker to download video"""
    try:
        downloads_status[download_id]['status'] = 'fetching_info'
        
        # Use yt-dlp with cookies if available
        ydl_opts_info = {
            'quiet': True,
            'socket_timeout': 60,
            'nocheckcertificate': True,
            'noplaylist': True,
            'extractor_retries': 3,
            # Use iOS/Android clients
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android'],
                }
            },
        }
        
        if COOKIES_FILE:
            ydl_opts_info['cookiefile'] = COOKIES_FILE.name
        
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'video'))
        
        downloads_status[download_id]['status'] = 'downloading'
        
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
                'socket_timeout': 120,
                'noplaylist': True,
                'no_abort_on_error': True,
                'nocheckcertificate': True,
                'extractor_retries': 3,
                # Use iOS client (most reliable)
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android'],
                    }
                },
            }
            
            if COOKIES_FILE:
                ydl_opts['cookiefile'] = COOKIES_FILE.name
        else:
            filename = f"{title}_{format_type}.mp4"
            filepath = DOWNLOAD_FOLDER / filename
            
            quality_map = {
                '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
                '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
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
                'quiet': True,
                'socket_timeout': 120,
                'noplaylist': True,
                'no_abort_on_error': True,
                'nocheckcertificate': True,
                'extractor_retries': 3,
                # Use iOS client (most reliable)
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android'],
                    }
                },
            }
            
            if COOKIES_FILE:
                ydl_opts['cookiefile'] = COOKIES_FILE.name
        
        logger.info(f"Downloading {download_id}: {filename}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if not filepath.exists():
            downloads_status[download_id]['status'] = 'error'
            downloads_status[download_id]['error'] = 'Download failed'
            return
        
        downloads_status[download_id].update({
            'status': 'completed',
            'filename': filename,
            'filepath': str(filepath),
            'progress': 100
        })
        
        logger.info(f"Download {download_id} completed: {filename}")
        
    except Exception as e:
        logger.error(f"Error in download worker {download_id}: {e}", exc_info=True)
        downloads_status[download_id]['status'] = 'error'
        downloads_status[download_id]['error'] = str(e)

@app.route('/api/status/<download_id>', methods=['GET'])
def check_status(download_id):
    """Check download status"""
    if download_id not in downloads_status:
        return jsonify({'error': 'Download not found'}), 404
    
    return jsonify(downloads_status[download_id])

@app.route('/api/file/<download_id>', methods=['GET'])
def get_file(download_id):
    """Download the completed file"""
    try:
        if download_id not in downloads_status:
            return jsonify({'error': 'Download not found'}), 404
        
        status = downloads_status[download_id]
        
        if status['status'] != 'completed':
            return jsonify({'error': 'Download not ready', 'status': status['status']}), 400
        
        filepath = Path(status['filepath'])
        filename = status['filename']
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        mimetype = 'audio/mpeg' if filename.endswith('.mp3') else 'video/mp4'
        response = send_file(filepath, as_attachment=True, download_name=filename, mimetype=mimetype)
        
        @response.call_on_close
        def cleanup():
            try:
                time.sleep(2)
                if filepath.exists():
                    filepath.unlink()
                if download_id in downloads_status:
                    del downloads_status[download_id]
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error serving file: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"YouTube Downloader Started - http://localhost:{port}")
    cleanup_old_files()
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
