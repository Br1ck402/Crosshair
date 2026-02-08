# Crosshair Overlay v6.0 - QUICK START GUIDE

## УСТАНОВКА / INSTALLATION

### Requirements:
- Windows 10+
- Python 3.8+

### Setup:
```bash
cd "c:\Users\ВаНя\Desktop\Crosshair"
pip install -r requirements.txt
# Or let the app auto-install dependencies on first run
```

### Run:
```bash
# Option 1: Via batch file (no console window)
crosshair_overlay_v6.bat

# Option 2: Direct Python
python crosshair_overlay_v6.pyw

# Option 3: Via pythonw.exe (hidden console)
pythonw.exe crosshair_overlay_v6.pyw
```

---

## ОСНОВНЫЕ ФУНКЦИИ / MAIN FEATURES

### Language & Theme (NEW)
- **Default UI Language:** Russian (Русский)
- **5 Themes:** Dark, Light, Solarized, Cyberpunk, Classic
- **Theme Selector:** Settings → ⚙️ СИСТЕМА → ТЕМА ПРИЛОЖЕНИЯ

### Crosshair Customization
- **Shapes:** Dot, Crosshair, T-Shape, Circle, Square, Diamond, Ring, Custom
- **Animations:** Breathing, Pulsing, Rotating, Wave, Flicker, Strobe
- **Effects:** RGB Rainbow, CHAOS MODE, Blink, Recoil React

### Gaming Features
- **Скрывать при прицеливании (ПКМ)** – Hide on Right-Click
- **Реакция на выстрел** – Flash on Click/Shoot
- **Слой центральной точки** – Center Dot (5 shapes)
- **Эффект мерцания** – Blink (hold RMB to trigger)

---

## HOTKEYS / ГОРЯЧИЕ КЛАВИШИ

| Зажим / Key | Функция / Function |
|------------|------------------|
| **F6**     | Показать/Скрыть оверлей (Toggle Overlay) |
| **F7**     | Открыть настройки (Show Settings) |
| **END**    | Экстренный выход (PANIC EXIT) |

**Customize hotkeys in Settings → ⚙️ СИСТЕМА → ГОРЯЧИЕ КЛАВИШИ**

---

## THEME COMPARISON

### Cyberpunk
- **Corner Radius:** 0° (sharp/aggressive)
- **Borders:** 2px thick (bold outlines)
- **Font:** Consolas (angular, monospace)
- **Colors:** Magenta, Cyan, Yellow neon
- **Feel:** Aggressive FPS gaming, retro-futuristic

### Light (Win11 Modern)
- **Corner Radius:** 15° (soft, rounded)
- **Borders:** None (clean, minimal)
- **Font:** Segoe UI (modern sans-serif)
- **Colors:** Blue, gray pastels
- **Feel:** Clean, professional, modern OS style

### Classic
- **Corner Radius:** 4° (balanced)
- **Borders:** 1px subtle
- **Font:** Segoe UI
- **Colors:** Green + Blue gaming colors
- **Feel:** Balanced, comfortable for long gaming sessions

---

## LANGUAGE SWITCHING

1. Open **Settings** (F7)
2. Go to **⚙️ СИСТЕМА** tab
3. Select **ЯЗЫК** (Language)
4. Choose: **en** (English) or **ru** (Русский)
5. Click **СОХРАНИТЬ** (Save)
6. UI updates immediately

### UI Labels in Russian:
- "Центральная точка" – Center Dot
- "Скрывать при прицеливании (ПКМ)" – Hide on ADS
- "Реакция на выстрел" – Click Response
- "Режим хаоса" – Chaos Mode
- "RGB Радуга" – RGB Chroma
- "Эффект мерцания" – Blink Effect

---

## ADVANCED: CUSTOMIZING THEMES

Edit `crosshair_overlay_v6.pyw` and modify `THEMES` dict:

```python
THEMES = {
    "MyCustomTheme": {
        # Colors
        "bg_primary": "#1a1a1a",
        "bg_secondary": "#2a2a2a",
        "fg_primary": "#ffffff",
        "accent_primary": "#ff00ff",
        
        # Geometry
        "corner_radius": 12,      # Smoothness (0-20)
        "border_width": 2,        # Border thickness (0-4)
        
        # Typography
        "font_family": "Consolas", # or "Segoe UI", "Arial", etc.
        
        # Style hint
        "button_style": "outlined", # or "flat"
    }
}
```

Save → Restart → Select "MyCustomTheme" from Theme selector

---

## TROUBLESHOOTING

### "ModuleNotFoundError: No module named 'customtkinter'"
→ App auto-installs. If not: `pip install customtkinter keyboard pystray Pillow pywin32`

### UI Text Not in Russian
→ Check Settings → ⚙️ СИСТЕМА → ЯЗЫК = **"ru"** → SAVE

### Theme Not Applying
→ Click **СОХРАНИТЬ** (Save) after theme selection
→ Or restart the app

### Crosshair Won't Show
→ Press **F6** to toggle visibility (Settings → ⚙️ СИСТЕМА → МОНИТОР = correct display)

### High CPU Usage
→ Disable "Реакция на выстрел" and "Эффект мерцания" if not needed

---

## FILE STRUCTURE

```
Crosshair/
├─ crosshair_overlay_v6.pyw       ← Main executable (2045 lines)
├─ crosshair_overlay_v6.bat       ← Windows batch launcher
├─ crosshair_config_v6.json       ← Settings saved here (auto-created)
├─ logs/                          ← Debug logs
├─ requirements.txt               ← Dependencies
└─ UPDATES_v6_FINALIZED.md        ← Full changelog
```

---

## PERFORMANCE

- **CPU:** ~2-5% (idle), ~10-15% (full effects)
- **RAM:** ~80-120 MB
- **FPS:** 60 FPS rendering (smooth animations)

**Lower CPU:**
- Disable RGB Rainbow + Blink
- Use "None" animation mode
- Disable CHAOS MODE

---

## CHANGELOG v6.0

### NEW in v6.0
✨ Complete Russian localization (gaming terminology)
🎨 5 visually distinct themes with geometry customization
⚙️ Theme parameters: corner_radius, border_width, font_family
🐛 Fixed animation threading → safe Tkinter .after() loop
💛 Blink effect now triggers only on RMB hold
🔧 Language switching without restart

### Fixed
- No more GUI thread crashes during animation
- RGB Chroma no longer conflicts with Click Response
- Blink melt doesn't flicker when disabled

---

## SUPPORT & CREDITS

**Platform:** Windows 10/11
**Author:** Elite Developer
**License:** MIT
**Python:** 3.8+

**Technologies:**
- CustomTkinter (modern GUI)
- Keyboard (hotkey detection)
- PyWin32 (Windows overlay)
- PIL/Pillow (image support)

---

**Status:** Ready for Production ✅

Enjoy your legendary crosshair! 🎯💫
