# Deployment auf Render.com - Schritt-für-Schritt Anleitung

## Vorbereitung (bereits erledigt ✓)
- ✓ Render.com Account erstellt
- ✓ GitHub Account verbunden
- ✓ `render.yaml` erstellt
- ✓ `build.sh` erstellt
- ✓ `requirements.txt` aktualisiert
- ✓ `app.py` für Production vorbereitet

## Deployment-Schritte

### 1. Code zu GitHub pushen
Öffne ein Terminal und führe folgende Befehle aus:

```bash
# Falls noch nicht initialisiert:
git init
git add .
git commit -m "Render deployment ready"

# Mit deinem GitHub Repository verbinden (ersetze USERNAME/REPO):
git remote add origin https://github.com/USERNAME/REPO.git
git branch -M main
git push -u origin main
```

### 2. Neuen Web Service auf Render erstellen

1. Gehe zu [Render Dashboard](https://dashboard.render.com/)
2. Klicke auf **"New +"** → **"Web Service"**
3. Wähle dein GitHub Repository aus
4. Render erkennt automatisch die `render.yaml` Datei

### 3. Service-Konfiguration (wird automatisch aus render.yaml geladen)

Falls manuelle Konfiguration nötig ist:
- **Name**: youtube-downloader (oder eigener Name)
- **Environment**: Python 3
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn app:app`
- **Plan**: Free (oder nach Bedarf)

### 4. Environment Variables (optional)
Die wichtigsten Variablen sind bereits in `render.yaml` gesetzt:
- `PORT`: 10000 (wird automatisch von Render gesetzt)
- `PYTHON_VERSION`: 3.11.0

### 5. Deploy starten
1. Klicke auf **"Create Web Service"**
2. Render startet automatisch:
   - Installation von Python Dependencies
   - Installation von FFmpeg
   - Build-Prozess
   - App-Start

### 6. Deployment verfolgen
- Im Dashboard siehst du Live-Logs
- Der erste Build dauert ~3-5 Minuten
- Status: "Building" → "Live"

### 7. App aufrufen
Nach erfolgreichem Deployment:
- URL: `https://youtube-downloader-XXXX.onrender.com`
- Die URL findest du oben im Dashboard

## Wichtige Hinweise

### ⚠️ Render Free Tier Limitierungen
- Nach 15 Minuten Inaktivität wird der Service "eingeschlafen"
- Erster Request nach dem Aufwachen dauert ~30-60 Sekunden
- 750 Stunden/Monat kostenlos

### 🔄 Auto-Deploy
Bei jedem `git push` zu GitHub:
- Render startet automatisch ein neues Deployment
- Kein manuelles Triggern nötig

### 📊 Monitoring
Im Render Dashboard:
- **Logs**: Echtzeit-Logs der App
- **Metrics**: CPU, Memory, Response Time
- **Events**: Deployment-History

## Troubleshooting

### Build schlägt fehl?
1. Prüfe die Build-Logs im Dashboard
2. Häufige Probleme:
   - `build.sh` nicht ausführbar → Render setzt automatisch Permissions
   - FFmpeg-Installation fehlgeschlagen → Logs prüfen

### App startet nicht?
1. Prüfe die Service-Logs
2. Stelle sicher, dass Port korrekt gesetzt ist: `PORT=10000`

### Downloads funktionieren nicht?
1. Prüfe FFmpeg-Installation in den Build-Logs
2. `yt-dlp` Version aktualisieren wenn YouTube-Fehler auftreten

## Nächste Schritte

1. **Push zu GitHub**:
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push
   ```

2. **Render Service erstellen** (siehe oben)

3. **Testen**:
   - URL öffnen
   - YouTube-Link einfügen
   - Download testen

## Support-Links
- [Render Dokumentation](https://render.com/docs)
- [yt-dlp Dokumentation](https://github.com/yt-dlp/yt-dlp)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
