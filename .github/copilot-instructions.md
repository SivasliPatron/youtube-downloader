# YouTube Downloader - AI Coding Agent Instructions

## Project Overview
Single-page YouTube video/audio downloader using Flask backend + vanilla JavaScript frontend. Downloads via `yt-dlp`, serves static HTML from Flask, stores files in `downloads/` directory.

## Architecture
- **Backend**: Flask (`app.py`) - serves both API endpoints and static HTML
- **Frontend**: Single HTML file (`index.html`) with embedded CSS/JS
- **Core Dependency**: `yt-dlp` for YouTube download functionality
- **File Flow**: Downloads → `downloads/` folder → served via Flask's `send_file()`

## Critical Patterns

### Two-Stage Download Flow
The app uses a **preview-then-download** pattern:
1. POST `/download` - extracts video metadata (title, thumbnail, duration) without downloading
2. GET `/download-file` - performs actual download with yt-dlp and streams file to user

This prevents long-running POST requests and enables showing video preview before download.

### Filename Sanitization
Always use `sanitize_filename()` when processing video titles:
```python
def sanitize_filename(filename):
    return re.sub(r'[^\w\s-]', '', filename).replace(' ', '_')
```
Special characters in YouTube titles will break file operations.

### yt-dlp Configuration
- **Audio (MP3)**: Uses `FFmpegExtractAudio` postprocessor, requires FFmpeg installed
- **Video**: Quality mapped explicitly (`720p` → `bestvideo[height<=720]+bestaudio`)
- **Output Template**: `outtmpl` sets download location; for MP3, extension is added by postprocessor

### Error Handling Convention
User-facing errors in German (`"Keine URL angegeben"`, `"Fehlende Parameter"`). Backend uses German error messages - maintain this for consistency.

## Development Workflow

### Running the App
```bash
python app.py
# Server starts on http://localhost:3000
# NOT using npm despite README mention - README is outdated
```

### Dependencies
Install from `requirements.txt`:
```bash
pip install -r requirements.txt
```
**External requirement**: FFmpeg must be installed system-wide for MP3 conversion.

### Local Testing
Frontend makes requests to `http://localhost:3000` (hardcoded in `index.html`). No CORS issues during development due to `CORS(app)`.

## Common Modifications

### Adding Video Quality
1. Add format button in `index.html` format selector
2. Update `quality_map` dict in `app.py` with yt-dlp format string
3. Example: `'240p': 'bestvideo[height<=240]+bestaudio/best[height<=240]'`

### Changing Download Directory
Update `DOWNLOAD_FOLDER = 'downloads'` constant. Directory is auto-created on startup.

### API Response Structure
`/download` returns:
```json
{
  "info": {"title": "...", "channel": "...", "duration": 123, "thumbnail": "..."},
  "downloadUrl": "/download-file?url=...&format=...&filename=...",
  "filename": "sanitized_title.mp4"
}
```

## Key Files
- `app.py` - All backend logic, API routes, yt-dlp integration
- `index.html` - Complete frontend (HTML/CSS/JS in one file)
- `downloads/` - Temporary storage for downloaded files (not version controlled)

## Language Note
UI and error messages are in **German** - maintain this convention when adding features or error handling.
