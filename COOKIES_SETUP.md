# YouTube Cookies Setup für Render.com

## Problem
YouTube blockiert Server-IPs von Render.com. Die Lösung: Cookies von einem echten Browser verwenden.

## Schritt 1: Cookies aus deinem Browser exportieren

### Option A: Mit Browser-Extension (Empfohlen)

1. **Installiere "Get cookies.txt LOCALLY" Extension:**
   - Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

2. **Gehe zu YouTube und melde dich an:**
   - Öffne https://www.youtube.com
   - Melde dich mit deinem Google-Konto an

3. **Exportiere die Cookies:**
   - Klicke auf die Extension (Puzzle-Icon → "Get cookies.txt LOCALLY")
   - Klicke auf "Export" → "Current Site"
   - Speichere die Datei als `youtube_cookies.txt`

### Option B: Mit yt-dlp (fortgeschritten)

Öffne Terminal/PowerShell und führe aus:
```bash
yt-dlp --cookies-from-browser chrome --cookies youtube_cookies.txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```
Ersetze `chrome` mit deinem Browser: `firefox`, `edge`, `opera`, `brave`

## Schritt 2: Cookies zu Render hinzufügen

1. **Öffne die Cookie-Datei:**
   - Öffne `youtube_cookies.txt` mit Notepad/Editor
   - Kopiere den **GESAMTEN** Inhalt

2. **Gehe zu Render Dashboard:**
   - https://dashboard.render.com/
   - Wähle deinen `youtube-downloader` Service

3. **Füge Environment Variable hinzu:**
   - Gehe zu **"Environment"** Tab
   - Klicke **"Add Environment Variable"**
   - **Key:** `YOUTUBE_COOKIES`
   - **Value:** Füge den GESAMTEN Cookie-Inhalt ein
   - Klicke **"Save Changes"**

4. **Service neu starten:**
   - Render startet automatisch neu
   - Warte 2-3 Minuten
   - Teste einen Download!

## Schritt 3: Cookies aktualisieren (alle 6 Monate)

YouTube Cookies laufen ab. Wenn Downloads wieder fehlschlagen:
1. Wiederhole Schritt 1 (neue Cookies exportieren)
2. Aktualisiere die `YOUTUBE_COOKIES` Variable in Render
3. Service wird automatisch neu gestartet

## Troubleshooting

### "Still getting bot errors"
- Stelle sicher, dass du die **GESAMTE** Cookie-Datei kopiert hast
- Die Datei muss mit `# Netscape HTTP Cookie File` beginnen
- Cookies müssen von einem **angemeldeten** YouTube Account stammen

### "Cookies not loading"
- Prüfe die Render Logs: sollte "Cookies loaded from environment variable" zeigen
- Stelle sicher, keine Leerzeichen vor/nach dem Cookie-Text
- Cookie-Format muss Netscape-Format sein

### "Invalid cookie format"
- Nutze die Browser-Extension Methode (Option A)
- Stelle sicher, die Datei endet mit `.txt`

## Wichtig
- **Teile deine Cookies NIE öffentlich** (sie gewähren Zugriff auf deinen YouTube Account)
- Verwende einen **Test-Account** wenn möglich
- Cookies sind nur in Render gespeichert (Environment Variables sind privat)
