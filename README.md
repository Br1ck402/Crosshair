# Crosshair Overlay v6.0

Crosshair Overlay v6 is a lightweight, single-file Windows overlay that displays a customizable crosshair on top of applications and games.

Highlights:
- Russian and English UI (default: Russian)
- 5 built-in themes with geometry and typography options
- Click response (flash), blink, RGB chroma, chaos mode
- Safe Tkinter animations (`root.after`) to avoid GUI thread issues
- Single-file distribution: `crosshair_overlay_v6.pyw`

Quick start
-----------
Prerequisites:
- Windows 10+
- Python 3.8+

Install dependencies (optional):

```bash
pip install -r requirements.txt
```

Run (no console):

```powershell
# Use batch launcher (recommended)
crosshair_overlay_v6.bat

# Or run with pythonw.exe to hide console
pythonw.exe crosshair_overlay_v6.pyw
```

Hotkeys
-------
- F6 — Toggle overlay
- F7 — Toggle settings window
- END — Panic exit (close app)

How to push to GitHub
---------------------
1. Create a new repository on GitHub.
2. In your local folder (`Crosshair`), run:

```bash
git init
git add .
git commit -m "Add Crosshair Overlay v6"
# add your remote e.g.:
# git remote add origin git@github.com:youruser/yourrepo.git
git branch -M main
git push -u origin main
```

Files to include
----------------
- `crosshair_overlay_v6.pyw` (main)
- `crosshair_overlay_v6.bat` (launcher)
- `requirements.txt`
- `README.md`
- `LICENSE`

Ignore
------
Add these to `.gitignore`: `logs/`, `crosshair_config_v6.json`, `.venv/`, `__pycache__/`.

License
-------
This project is licensed under MIT (see `LICENSE`).
