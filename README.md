# 🎥 YouTube Downloader

Ein einfacher, moderner YouTube Video- und Audio-Downloader mit Flask-Backend und modernem Web-Frontend.

## ✨ Features

- ✅ YouTube Videos herunterladen (360p, 480p, 720p, 1080p)
- ✅ Audio als MP3 extrahieren
- ✅ Video-Vorschau mit Thumbnail, Titel, Kanal und Dauer
- ✅ Modernes, responsives Design
- ✅ Automatische Datei-Bereinigung
- ✅ Detaillierte Fehlerbehandlung
- ✅ Echtzeit-Download-Status

## 📋 Voraussetzungen

- **Python 3.8 oder höher**
- **FFmpeg** (für MP3-Konvertierung)

### FFmpeg Installation

#### Windows (mit Chocolatey):
```powershell
choco install ffmpeg
```

#### Windows (manuell):
1. Download von https://ffmpeg.org/download.html
2. Entpacken und zum PATH hinzufügen

#### Überprüfen:
```bash
ffmpeg -version
```

## 🚀 Installation

1. **Repository klonen/herunterladen**

2. **In das Projektverzeichnis wechseln**
   ```powershell
   cd "C:\Users\Ebube\Desktop\Neuer Ordner"
   ```

3. **Virtuelle Umgebung erstellen (empfohlen)**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

4. **Dependencies installieren**
   ```powershell
   pip install -r requirements.txt
   ```

## ▶️ Anwendung starten

```powershell
python app.py
```

Die Anwendung ist dann verfügbar unter: **http://localhost:3000**

## 📖 Verwendung

1. Öffne den Browser und navigiere zu `http://localhost:3000`
2. Gib eine YouTube-URL ein
3. Wähle das gewünschte Format:
   - **MP3** - Audio-Download
   - **360p bis 1080p** - Video-Download in verschiedenen Qualitäten
4. Klicke auf "Download starten"
5. Die Datei wird automatisch heruntergeladen

## 📁 Projektstruktur

```
.
├── app.py              # Flask Backend
├── index.html          # Frontend
├── requirements.txt    # Python Dependencies
├── downloads/          # Temporärer Download-Ordner (wird automatisch erstellt)
└── README.md          # Diese Datei
```

## 🔧 API-Endpunkte

### GET `/`
Serviert die HTML-Oberfläche

### POST `/api/info`
Ruft Video-Informationen ab
```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

### POST `/api/download`
Lädt Video/Audio herunter
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "format": "720p"
}
```

## ⚠️ Fehlerbehebung

### "ModuleNotFoundError"
→ Installiere alle Dependencies: `pip install -r requirements.txt`

### "FFmpeg not found" beim MP3-Download
→ FFmpeg muss installiert und im PATH sein

### Server startet nicht
→ Port 3000 könnte belegt sein. Ändere in `app.py` den Port:
```python
app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
```

### Download schlägt fehl
- Überprüfe die YouTube-URL
- Prüfe deine Internetverbindung
- Manche Videos sind möglicherweise regional gesperrt
- Private oder altersbeschränkte Videos können nicht heruntergeladen werden

## 🛠️ Technologien

- **Backend:** Flask, yt-dlp
- **Frontend:** Vanilla JavaScript, CSS3
- **Media Processing:** FFmpeg

## 📝 Hinweise

- Die Anwendung ist nur für den **lokalen Gebrauch** gedacht
- Heruntergeladene Dateien werden automatisch nach dem Download gelöscht
- Respektiere Urheberrechte und YouTube's Nutzungsbedingungen
- Debug-Modus ist aktiviert - für Produktion deaktivieren!

## 🐛 Logging

Der Server gibt detaillierte Logs aus:
- Video-Info-Anfragen
- Download-Status
- Fehler und Warnungen
- Datei-Operationen

## 📄 Lizenz

Dieses Projekt ist für Bildungszwecke erstellt.

---

**Erstellt mit ❤️ und Python**
