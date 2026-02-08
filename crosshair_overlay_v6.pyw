#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════════════════╗
║              CROSSHAIR OVERLAY v6.0 - LEGENDARY EDITION                   ║
║                  Elite Python GUI with Advanced Features                   ║
║                                                                            ║
║  ✨ Single-File Portable Architecture                                     ║
║  🖱️ Hide on ADS (Right-Click Detection)                                  ║
║  💥 Click Response & Recoil Simulation                                    ║
║  🖼️ Custom Image Support                                                 ║
║  🎯 Layered Crosshairs (Center Dot)                                      ║
║  🖥️ Multi-Monitor Support                                                ║
║  🎮 Game Detection & Auto-Profiles                                        ║
║  🌈 RGB Rainbow Chroma & Animations                                       ║
║  ⚡ 60 FPS High Performance                                               ║
╚════════════════════════════════════════════════════════════════════════════╝

Author: Elite Developer
License: MIT
Platform: Windows Only
Python: 3.8+
"""

import ctypes
import ctypes.wintypes
import sys
import os
import json
import threading
import time
import math
import random
import colorsys
import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable, Dict, Any, List, Tuple
import subprocess

# ═══════════════════════════════════════════════════════════════════════════
# AUTO-INSTALL DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def ensure_packages():
    """Auto-install missing packages with pip"""
    required = {
        "customtkinter": "customtkinter",
        "keyboard": "keyboard",
        "pystray": "pystray",
        "PIL": "Pillow",
        "win32api": "pywin32",
    }
    
    missing = []
    for import_name, package_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"[Setup] Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + missing)
            print(f"[Setup] ✓ Packages installed successfully")
        except Exception as e:
            print(f"[Setup] ✗ Failed to install packages: {e}")
            return False
    return True

if not ensure_packages():
    print("[ERROR] Cannot proceed without dependencies. Exiting.")
    sys.exit(1)

# ─── Now import the packages ───
import customtkinter as ctk
import keyboard
import pystray
from PIL import Image, ImageDraw, ImageTk
import win32api
import win32con
import win32gui
import win32process

# ─── High DPI Fix ───
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════════

import logging
import traceback

# Create logs directory if it doesn't exist
try:
    LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(LOGS_DIR, exist_ok=True)
except Exception as e:
    print(f"[ERROR] Failed to create logs directory: {e}")
    LOGS_DIR = os.getcwd()

# Automatic log cleanup: remove logs older than `max_age_days` or keep at most `max_count` files
def _cleanup_old_logs(logs_dir: str, max_age_days: int = 1, max_count: int = 100):
    try:
        now = time.time()
        max_age_seconds = max_age_days * 86400
        files = []
        for fn in os.listdir(logs_dir):
            if not fn.lower().startswith('crosshair_') or not fn.lower().endswith('.log'):
                continue
            path = os.path.join(logs_dir, fn)
            try:
                mtime = os.path.getmtime(path)
                files.append((path, mtime))
            except Exception:
                continue

        # Remove files older than max_age_days
        for path, mtime in files:
            try:
                if (now - mtime) > max_age_seconds:
                    os.remove(path)
            except Exception:
                pass

        # Rebuild list and ensure count < max_count by removing oldest
        files = []
        for fn in os.listdir(logs_dir):
            if not fn.lower().startswith('crosshair_') or not fn.lower().endswith('.log'):
                continue
            path = os.path.join(logs_dir, fn)
            try:
                mtime = os.path.getmtime(path)
                files.append((path, mtime))
            except Exception:
                continue

        files.sort(key=lambda x: x[1])  # oldest first
        while len(files) >= max_count:
            path, _ = files.pop(0)
            try:
                os.remove(path)
            except Exception:
                pass
    except Exception:
        pass

# Run cleanup once at startup
try:
    _cleanup_old_logs(LOGS_DIR, max_age_days=1, max_count=100)
except Exception:
    pass

# Setup logging to file and console
try:
    LOG_FILE = os.path.join(LOGS_DIR, f"crosshair_{time.strftime('%Y%m%d_%H%M%S')}.log")
    
    # Try to create/open the log file
    open(LOG_FILE, 'a', encoding='utf-8').close()
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    _logging_ok = True
except Exception as e:
    print(f"[ERROR] Failed to setup file logging: {e}")
    _logging_ok = False
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    LOG_FILE = None

logger = logging.getLogger(__name__)

def log(message, level="INFO"):
    """Log message to file and console"""
    if level == "DEBUG":
        logger.debug(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:
        logger.info(message)

if _logging_ok and LOG_FILE:
    log(f"✓ Crosshair v6.0 started, logging to: {LOG_FILE}")
else:
    log("✓ Crosshair v6.0 started (logging to console only)")

# ═══════════════════════════════════════════════════════════════════════════
# ADMIN ESCALATION
# ═══════════════════════════════════════════════════════════════════════════

def is_admin():
    """Check if running as admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def relaunch_as_admin():
    """Relaunch script with admin privileges"""
    try:
        print("[App] Requesting admin privileges...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        print("[App] Admin relaunch requested")
    except Exception as e:
        print(f"[ERROR] Failed to elevate privileges: {e}")
        sys.exit(1)

print("[App] Checking admin status...")
if not is_admin():
    print("[App] Not running as admin, relaunching...")
    relaunch_as_admin()
    print("[App] Original process exiting")
    sys.exit()


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION & DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════

SHAPES = ["Dot", "Crosshair", "T-Shape", "Circle", "Square", "Diamond", "Ring", "Crosshair+", "Custom", "Image"]
ANIMATION_MODES = ["None", "Breathing", "Pulsing", "Rotating", "Wave", "Flicker", "Strobe"]

DEFAULT_CROSSHAIR_SETTINGS = {
    "shape": "Crosshair",
    "size": 12,
    "thickness": 2,
    "gap": 4,
    "opacity": 100,
    "offset_x": 0,
    "offset_y": 0,
    "color": "#00FF00",
    "outline_color": "#000000",
    "outline_thickness": 1,
    "animation_mode": "None",
    "animation_speed": 50,
    "inner_size": 0,
    "rgb_chroma_enabled": False,
    "chroma_speed": 50,
    "chaos_enabled": False,
    # NEW: Hide on ADS
    "hide_on_ads": False,
    # NEW: Click Response
    "click_response_enabled": False,
    "click_response_color": "#FF0000",
    "click_response_bump_size": 5,
    "click_response_duration": 0.1,
    # NEW: Image Support
    "image_path": "",
    "image_scale": 1.0,
    # NEW: Center Dot
    "center_dot_enabled": False,
    "center_dot_color": "#FF0000",
    "center_dot_size": 4,
    "center_dot_opacity": 100,
    "center_dot_shape": "Circle",
    # NEW: Blink/Flash Effect
    "blink_enabled": False,
    "blink_speed": 50,  # 1-100, where 50 = 1 second cycle
}

DEFAULT_HOTKEYS = {
    "toggle_overlay": "f6",
    "toggle_settings": "f7",
    "panic": "end",
}

# ─── Theme Colors (Cyberpunk Gaming Dashboard) ───
THEME = {
    "bg_primary": "#0a0e27",
    "bg_secondary": "#151932",
    "fg_primary": "#e0e0ff",
    "fg_secondary": "#a0a0cc",
    "accent_primary": "#00ff88",
    "accent_secondary": "#ff006e",
    "accent_tertiary": "#00d9ff",
    "border": "#2a2d4a",
    "slider_accent": "#00ff88",
    "corner_radius": 8,
    "border_width": 1,
    "font_family": "Segoe UI",
    "button_style": "flat",
}

# ─── App Themes (predefined color sets + geometry) ───
THEMES = {
    "Dark": {
        "bg_primary": "#0a0e27",
        "bg_secondary": "#151932",
        "fg_primary": "#e0e0ff",
        "fg_secondary": "#a0a0cc",
        "accent_primary": "#00ff88",
        "accent_secondary": "#ff006e",
        "accent_tertiary": "#00d9ff",
        "border": "#2a2d4a",
        "slider_accent": "#00ff88",
        "corner_radius": 8,
        "border_width": 1,
        "font_family": "Segoe UI",
        "button_style": "flat",
    },
    "Light": {
        "bg_primary": "#f5f7fb",
        "bg_secondary": "#ffffff",
        "fg_primary": "#0b1220",
        "fg_secondary": "#334155",
        "accent_primary": "#2563eb",
        "accent_secondary": "#ef4444",
        "accent_tertiary": "#06b6d4",
        "border": "#d1d5db",
        "slider_accent": "#2563eb",
        "corner_radius": 15,
        "border_width": 0,
        "font_family": "Segoe UI",
        "button_style": "flat",
    },
    "Solarized": {
        "bg_primary": "#002b36",
        "bg_secondary": "#073642",
        "fg_primary": "#93a1a1",
        "fg_secondary": "#839496",
        "accent_primary": "#b58900",
        "accent_secondary": "#cb4b16",
        "accent_tertiary": "#2aa198",
        "border": "#073642",
        "slider_accent": "#b58900",
        "corner_radius": 6,
        "border_width": 1,
        "font_family": "Consolas",
        "button_style": "outlined",
    },
    "Cyberpunk": {
        "bg_primary": "#08060b",
        "bg_secondary": "#130925",
        "fg_primary": "#f1f0ff",
        "fg_secondary": "#c0bfe6",
        "accent_primary": "#ff00c8",
        "accent_secondary": "#00ffd5",
        "accent_tertiary": "#ffdd00",
        "border": "#2b1436",
        "slider_accent": "#ff00c8",
        "corner_radius": 0,
        "border_width": 2,
        "font_family": "Consolas",
        "button_style": "outlined",
    },
    "Classic": {
        "bg_primary": "#0f172a",
        "bg_secondary": "#111827",
        "fg_primary": "#e6edf3",
        "fg_secondary": "#9aa6b2",
        "accent_primary": "#10b981",
        "accent_secondary": "#6366f1",
        "accent_tertiary": "#06b6d4",
        "border": "#1f2937",
        "slider_accent": "#10b981",
        "corner_radius": 4,
        "border_width": 1,
        "font_family": "Segoe UI",
        "button_style": "flat",
    }
}

# ─── Translations ───
TRANSLATIONS = {
    "en": {
        "MONITOR": "MONITOR",
        "HOTKEYS": "HOTKEYS",
        "GAME_PROFILES": "GAME PROFILES",
        "Toggle Overlay": "Toggle Overlay",
        "Show Settings": "Show Settings",
        "PANIC Exit": "PANIC Exit",
        "Add Current Game Profile": "➕ Add Current Game Profile",
        "CENTER DOT LAYER": "CENTER DOT LAYER",
        "ANIMATION": "ANIMATION",
        "RGB Rainbow Chroma 🌈": "RGB Rainbow Chroma 🌈",
        "CHAOS MODE 🎲": "CHAOS MODE 🎲",
        "BLINK EFFECT": "BLINK EFFECT",
        "Enable Blink 💥": "Enable Blink 💥",
        "Blink Speed": "Blink Speed",
    },
    "ru": {
        "MONITOR": "МОНИТОР",
        "HOTKEYS": "ГОРЯЧИЕ КЛАВИШИ",
        "GAME_PROFILES": "ПРОФИЛИ ИГР",
        "Toggle Overlay": "Показать/Скрыть оверлей",
        "Show Settings": "Открыть настройки",
        "PANIC Exit": "PANИКА (Выход)",
        "Add Current Game Profile": "➕ Сохранить профиль для текущей игры",
        "CENTER DOT LAYER": "СЛОЙ ЦЕНТРАЛЬНОЙ ТОЧКИ",
        "ANIMATION": "АНИМАЦИЯ",
        "RGB Rainbow Chroma 🌈": "RGB Радуга 🌈",
        "CHAOS MODE 🎲": "РЕЖИМ ХАОСА 🎲",
        "BLINK EFFECT": "ЭФФЕКТ МЕРЦАНИЯ",
        "Enable Blink 💥": "Включить мерцание 💥",
        "Blink Speed": "Скорость мерцания",
    }
}

def translate(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# Extended translations (add many UI labels)
TRANSLATIONS["en"].update({
    "APP_TITLE": "⚙️ LEGENDARY v6.0",
    "Shape": "Shape",
    "Center Dot Shape": "Center Dot Shape",
    "HIDE ON ADS": "HIDE ON ADS",
    "CLICK RESPONSE": "CLICK RESPONSE",
    "Enable Click Response": "Реакция на зажим",
    "Size": "Размер",
    "Thickness": "Толщина",
    "Gap": "Зазор",
    "Opacity %": "Непрозрачность %",
    "Main Color": "Основной цвет",
    "Outline Color": "Цвет обводки",
    "Outline Width": "Толщина обводки",
    "Enable Center Dot": "Включить центральную точку",
    "Center Dot Color": "Цвет центральной точки",
    "Center Dot Size": "Размер центральной точки",
    "Center Dot Opacity": "Непрозрачность точки",
    "Animation Speed": "Скорость анимации",
    "Rainbow Speed": "Скорость радуги",
    "Enable Blink 💥": "Включить мерцание 💥",
    "Blink Speed": "Скорость мерцания",
    "Hide when Right-Click (ADS)": "Скрывать при зажатом ПКМ",
    "Flash Color": "Цвет реакции",
    "Size Bump": "Увеличение размера",
    "Image Scale": "Масштаб изображения",
    "Save": "СОХРАНИТЬ",
    "Close": "ЗАКРЫТЬ",
    "GENERAL": "ОСНОВНЫЕ",
    "LAYERS": "СЛОИ",
    "BEHAVIOR": "ПОВЕДЕНИЕ",
    "SYSTEM": "СИСТЕМА",
    "Offset X": "Смещение X",
    "Offset Y": "Смещение Y",
    "IMAGE SUPPORT": "IMAGE SUPPORT",
    "Image Scale": "Image Scale",
    "LANGUAGE": "LANGUAGE",
    "APP THEME": "APP THEME",
    "Save Success": "Settings saved!",
    "Success": "Success",
    "Warning": "Warning",
    "No game detected": "No game detected",
    "PANIC Exit": "PANIC Exit",
})

TRANSLATIONS["ru"].update({
    "APP_TITLE": "⚙️ ЛЕГЕНДАРНЫЙ v6.0",
    "Shape": "Форма",
    "Center Dot Shape": "Форма центральной точки",
    "HIDE ON ADS": "Скрывать при прицеливании (ПКМ)",
    "CLICK RESPONSE": "Реакция на выстрел",
    "IMAGE SUPPORT": "Поддержка изображения",
    "Image Scale": "Масштаб изображения",
    "LANGUAGE": "ЯЗЫК",
    "APP THEME": "ТЕМА ПРИЛОЖЕНИЯ",
    "Save Success": "Настройки сохранены!",
    "Success": "Готово",
    "Warning": "Внимание",
    "No game detected": "Игра не обнаружена",
    "PANIC Exit": "Экстренный выход",
})
# ─── Config file path ───
CONFIG_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_PATH = os.path.join(CONFIG_DIR, "crosshair_config_v6.json")


# ═══════════════════════════════════════════════════════════════════════════
# MONITOR DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def get_monitors():
    """Get list of monitors"""
    monitors = []
    def callback(hmonitor, hdc, lprect, lparam):
        monitors.append(hmonitor)
        return True
    
    try:
        win32api.EnumDisplayMonitors(None, None, callback, None)
    except Exception:
        pass
    
    return monitors if monitors else [None]

def get_monitor_info(hmonitor):
    """Get monitor resolution and position"""
    try:
        info = win32api.GetMonitorInfo(hmonitor)
        rc_monitor = info.get('Monitor', (0, 0, 1920, 1080))
        return {
            'left': rc_monitor[0],
            'top': rc_monitor[1],
            'width': rc_monitor[2] - rc_monitor[0],
            'height': rc_monitor[3] - rc_monitor[1]
        }
    except Exception:
        return {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}


# ═══════════════════════════════════════════════════════════════════════════
# GAME DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def get_foreground_process():
    """Get active process name"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = win32api.GetProcessImageFileName(win32process.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid))
        return os.path.basename(process).lower()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CrosshairSettings:
    shape: str = DEFAULT_CROSSHAIR_SETTINGS["shape"]
    size: int = DEFAULT_CROSSHAIR_SETTINGS["size"]
    thickness: int = DEFAULT_CROSSHAIR_SETTINGS["thickness"]
    gap: int = DEFAULT_CROSSHAIR_SETTINGS["gap"]
    opacity: int = DEFAULT_CROSSHAIR_SETTINGS["opacity"]
    offset_x: int = DEFAULT_CROSSHAIR_SETTINGS["offset_x"]
    offset_y: int = DEFAULT_CROSSHAIR_SETTINGS["offset_y"]
    color: str = DEFAULT_CROSSHAIR_SETTINGS["color"]
    outline_color: str = DEFAULT_CROSSHAIR_SETTINGS["outline_color"]
    outline_thickness: int = DEFAULT_CROSSHAIR_SETTINGS["outline_thickness"]
    animation_mode: str = DEFAULT_CROSSHAIR_SETTINGS["animation_mode"]
    animation_speed: int = DEFAULT_CROSSHAIR_SETTINGS["animation_speed"]
    inner_size: int = DEFAULT_CROSSHAIR_SETTINGS["inner_size"]
    rgb_chroma_enabled: bool = DEFAULT_CROSSHAIR_SETTINGS["rgb_chroma_enabled"]
    chroma_speed: int = DEFAULT_CROSSHAIR_SETTINGS["chroma_speed"]
    chaos_enabled: bool = DEFAULT_CROSSHAIR_SETTINGS["chaos_enabled"]
    hide_on_ads: bool = DEFAULT_CROSSHAIR_SETTINGS["hide_on_ads"]
    click_response_enabled: bool = DEFAULT_CROSSHAIR_SETTINGS["click_response_enabled"]
    click_response_color: str = DEFAULT_CROSSHAIR_SETTINGS["click_response_color"]
    click_response_bump_size: int = DEFAULT_CROSSHAIR_SETTINGS["click_response_bump_size"]
    click_response_duration: float = DEFAULT_CROSSHAIR_SETTINGS["click_response_duration"]
    image_path: str = DEFAULT_CROSSHAIR_SETTINGS["image_path"]
    image_scale: float = DEFAULT_CROSSHAIR_SETTINGS["image_scale"]
    center_dot_enabled: bool = DEFAULT_CROSSHAIR_SETTINGS["center_dot_enabled"]
    center_dot_color: str = DEFAULT_CROSSHAIR_SETTINGS["center_dot_color"]
    center_dot_size: int = DEFAULT_CROSSHAIR_SETTINGS["center_dot_size"]
    center_dot_opacity: int = DEFAULT_CROSSHAIR_SETTINGS["center_dot_opacity"]
    center_dot_shape: str = DEFAULT_CROSSHAIR_SETTINGS["center_dot_shape"]
    blink_enabled: bool = DEFAULT_CROSSHAIR_SETTINGS["blink_enabled"]
    blink_speed: int = DEFAULT_CROSSHAIR_SETTINGS["blink_speed"]


@dataclass
class AppConfig:
    crosshair: dict = field(default_factory=lambda: dict(asdict(CrosshairSettings())))
    hotkeys: dict = field(default_factory=lambda: dict(DEFAULT_HOTKEYS))
    overlay_visible: bool = True
    selected_monitor: int = 0
    profiles: dict = field(default_factory=dict)
    # UI language and app theme
    language: str = "ru"
    app_theme: str = "Dark"

    def save(self):
        """Save config to JSON"""
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=4)
        except Exception as e:
            print(f"[Config] Save error: {e}")

    @classmethod
    def load(cls):
        """Load config from JSON"""
        if not os.path.exists(CONFIG_PATH):
            return cls()
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(**data)
        except Exception as e:
            print(f"[Config] Load error: {e}, using defaults")
            return cls()


# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex color"""
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def get_rgb_chroma_color(speed: float = 1.0) -> str:
    """Get rainbow RGB color that cycles smoothly"""
    t = (time.time() * speed) % 1.0
    r, g, b = colorsys.hsv_to_rgb(t, 1.0, 1.0)
    hex_color = "#{:02x}{:02x}{:02x}".format(
        int(r * 255),
        int(g * 255),
        int(b * 255)
    )
    return hex_color

def load_image(path: str, size: int) -> Optional[Image.Image]:
    """Load and resize image"""
    try:
        if not os.path.exists(path):
            return None
        img = Image.open(path).convert("RGBA")
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        print(f"[Image] Load error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# OVERLAY WINDOW - TRANSPARENT, CLICK-THROUGH, TOP-MOST
# ═══════════════════════════════════════════════════════════════════════════

class OverlayWindow:
    """Transparent overlay window with crosshair rendering"""
    
    TRANSPARENT_COLOR = "#010101"

    def __init__(self, config: AppConfig, on_close: Optional[Callable] = None):
        self.config = config
        self.cs = CrosshairSettings(**config.crosshair)
        self._on_close = on_close
        self._visible = config.overlay_visible
        self._alive = True
        self._animation_frame = 0
        
        # Chaos mode
        self._chaos_params = {
            "shape": "Crosshair",
            "size": 12,
            "thickness": 2,
            "color": "#00FF00",
            "opacity": 100,
            "chaos_change_time": time.time(),
        }
        
        # Click response
        self._click_response_active = False
        self._click_response_time = 0.0
        self._last_mouse_state = False

        # Monitor setup
        self.monitors = get_monitors()
        monitor_idx = min(config.selected_monitor, len(self.monitors) - 1)
        self.current_monitor = self.monitors[monitor_idx]
        monitor_info = get_monitor_info(self.current_monitor)
        
        self.screen_w = monitor_info['width']
        self.screen_h = monitor_info['height']
        self.monitor_x = monitor_info['left']
        self.monitor_y = monitor_info['top']

        self.root = tk.Tk()
        self.root.title("Crosshair Overlay v6.0")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+{self.monitor_x}+{self.monitor_y}")
        
        self.root.configure(bg=self.TRANSPARENT_COLOR)
        self.root.attributes("-transparentcolor", self.TRANSPARENT_COLOR)

        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_w,
            height=self.screen_h,
            bg=self.TRANSPARENT_COLOR,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

        self.root.update_idletasks()
        self.hwnd = self._get_hwnd()
        if self.hwnd:
            self._apply_win32_styles()

        self.draw_crosshair()

        if not self._visible:
            self.root.withdraw()

        self._topmost_thread = threading.Thread(target=self._keep_topmost, daemon=True)
        self._topmost_thread.start()

        # Use Tkinter .after loop for GUI animations instead of background thread
        self.root.after(16, self._animation_tick)
        
        self._game_detection_thread = threading.Thread(target=self._game_detection_loop, daemon=True)
        self._game_detection_thread.start()

    def _get_hwnd(self):
        """Get window handle using multiple methods"""
        try:
            hwnd = int(self.root.wm_frame(), 16) if self.root.wm_frame() else None
            if not hwnd:
                hwnd = win32gui.FindWindow(None, "Crosshair Overlay v6.0")
            if not hwnd:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            return hwnd if hwnd else None
        except Exception:
            return None

    def _apply_win32_styles(self):
        """Apply WinAPI styles for click-through and transparency"""
        try:
            ex_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
            ex_style |= (
                win32con.WS_EX_TRANSPARENT
                | win32con.WS_EX_LAYERED
                | win32con.WS_EX_TOOLWINDOW
                | win32con.WS_EX_TOPMOST
            )
            ex_style &= ~win32con.WS_EX_APPWINDOW
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, ex_style)

            r = int(self.TRANSPARENT_COLOR[1:3], 16)
            g = int(self.TRANSPARENT_COLOR[3:5], 16)
            b = int(self.TRANSPARENT_COLOR[5:7], 16)
            color_key = r | (g << 8) | (b << 16)
            win32gui.SetLayeredWindowAttributes(
                self.hwnd, color_key, 0, win32con.LWA_COLORKEY
            )

            win32gui.SetWindowPos(
                self.hwnd,
                win32con.HWND_TOPMOST,
                0, 0, self.screen_w, self.screen_h,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE,
            )
        except Exception as e:
            print(f"[Overlay] WinAPI error: {e}")

    def _keep_topmost(self):
        """Background thread: keep window on top"""
        while self._alive:
            try:
                if self.hwnd and self._visible:
                    win32gui.SetWindowPos(
                        self.hwnd,
                        win32con.HWND_TOPMOST,
                        0, 0, 0, 0,
                        win32con.SWP_NOMOVE
                        | win32con.SWP_NOSIZE
                        | win32con.SWP_NOACTIVATE
                        | win32con.SWP_NOOWNERZORDER,
                    )
            except Exception:
                pass
            time.sleep(2.5)

    def _game_detection_loop(self):
        """Background thread: detect active game and load profile"""
        last_check = 0
        while self._alive:
            now = time.time()
            if now - last_check > 1.0:  # Check every 1 second
                try:
                    process_name = get_foreground_process()
                    if process_name and process_name in self.config.profiles:
                        profile = self.config.profiles[process_name]
                        self.cs = CrosshairSettings(**profile)
                        print(f"[Game Detection] Loaded profile for {process_name}")
                except Exception:
                    pass
                last_check = now
            time.sleep(0.5)

    def _animation_loop(self):
        """Background thread: redraw for animations"""
        # Kept for compatibility but not used; animation handled via _animation_tick on main thread
        return

    def _animation_tick(self):
        """Main-thread animation tick using .after"""
        try:
            if self._visible:
                has_animation = (
                    self.cs.animation_mode != "None"
                    or self.cs.rgb_chroma_enabled
                    or self.cs.chaos_enabled
                    or self.cs.click_response_enabled
                    or self.cs.hide_on_ads
                )
                if has_animation:
                    # Update chaos parameters
                    if self.cs.chaos_enabled:
                        now = time.time()
                        if now - self._chaos_params["chaos_change_time"] > 0.3:
                            self._randomize_chaos_params()
                            self._chaos_params["chaos_change_time"] = now

                    # Update click response (left mouse)
                    if self.cs.click_response_enabled:
                        try:
                            mouse_pressed = bool(win32api.GetAsyncKeyState(0x01) & 0x8000)
                            if mouse_pressed and not self._last_mouse_state:
                                self._click_response_active = True
                                self._click_response_time = time.time()
                            self._last_mouse_state = mouse_pressed
                            if (time.time() - self._click_response_time) > self.cs.click_response_duration:
                                self._click_response_active = False
                        except Exception:
                            pass

                try:
                    self.draw_crosshair()
                except Exception:
                    pass

            self._animation_frame += 1
        except Exception:
            pass
        finally:
            # schedule next tick (approx 60 FPS)
            try:
                self.root.after(16, self._animation_tick)
            except Exception:
                pass

    def draw_crosshair(self):
        """Render crosshair on canvas"""
        self.canvas.delete("all")

        cs = self.cs
        
        # Check Blink effect (only while holding Right Mouse Button)
        if cs.blink_enabled:
            try:
                rmd_pressed = bool(win32api.GetAsyncKeyState(0x02) & 0x8000)
                if rmd_pressed:
                    blink_cycle = (time.time() * cs.blink_speed / 50.0) % 1.0
                    if blink_cycle >= 0.5:
                        return  # Don't draw - invisible part of blink cycle
            except Exception:
                pass
        
        # Check Hide on ADS
        if cs.hide_on_ads:
            try:
                rmd_pressed = bool(win32api.GetAsyncKeyState(0x02) & 0x8000)
                if rmd_pressed:
                    return  # Don't draw anything
            except Exception:
                pass
        
        # Use chaos parameters if enabled
        if cs.chaos_enabled:
            shape = self._chaos_params["shape"]
            size = self._chaos_params["size"]
            thickness = self._chaos_params["thickness"]
            color = self._chaos_params["color"]
            opacity = self._chaos_params["opacity"]
        else:
            shape = cs.shape
            size = cs.size
            thickness = cs.thickness
            color = cs.color
            opacity = cs.opacity
        
        cx = self.screen_w // 2 + cs.offset_x
        cy = self.screen_h // 2 + cs.offset_y

        # Apply click response effects
        try:
            lmb_pressed = bool(win32api.GetAsyncKeyState(0x01) & 0x8000)
        except Exception:
            lmb_pressed = False

        # If left mouse is held down and click response is enabled, blink red every 1s (0.5s on/off)
        if lmb_pressed and cs.click_response_enabled:
            try:
                if (time.time() % 1.0) < 0.5:
                    color = "#FF0000"
                # keep bump size when a click response event was triggered
                if self._click_response_active:
                    size = size + cs.click_response_bump_size
            except Exception:
                pass
        else:
            if self._click_response_active and cs.click_response_enabled:
                color = cs.click_response_color
                size = size + cs.click_response_bump_size

        # Set transparency
        if self.hwnd and opacity < 100:
            alpha_byte = max(10, int(opacity * 255 / 100))
            r = int(self.TRANSPARENT_COLOR[1:3], 16)
            g = int(self.TRANSPARENT_COLOR[3:5], 16)
            b = int(self.TRANSPARENT_COLOR[5:7], 16)
            color_key = r | (g << 8) | (b << 16)
            win32gui.SetLayeredWindowAttributes(
                self.hwnd, color_key, alpha_byte,
                win32con.LWA_COLORKEY | win32con.LWA_ALPHA,
            )
        elif self.hwnd:
            r = int(self.TRANSPARENT_COLOR[1:3], 16)
            g = int(self.TRANSPARENT_COLOR[3:5], 16)
            b = int(self.TRANSPARENT_COLOR[5:7], 16)
            color_key = r | (g << 8) | (b << 16)
            win32gui.SetLayeredWindowAttributes(
                self.hwnd, color_key, 255, win32con.LWA_COLORKEY | win32con.LWA_ALPHA,
            )

        # Get animated color
        mc = self._get_animated_color(color, cs)
        s = self._get_animated_size(size, cs)
        t = self._get_animated_thickness(thickness, cs)
        
        oc = cs.outline_color
        ot = cs.outline_thickness
        g = cs.gap

        # Draw main shape
        try:
            if shape != "Image":
                self._draw_shape(shape, cx, cy, s, t, g, mc, oc, ot)
            else:
                self._draw_image(cx, cy, s, cs.image_path)
        except Exception as e:
            print(f"[Draw] Shape error: {e}")

        # Draw center dot on top
        try:
            if cs.center_dot_enabled:
                dot_size = cs.center_dot_size
                dot_color = cs.center_dot_color
                dot_shape = getattr(cs, 'center_dot_shape', 'Circle')
                # Draw center dot with selected shape
                if dot_shape == "Circle":
                    r = max(dot_size, 2)
                    self.canvas.create_oval(
                        cx - r, cy - r, cx + r, cy + r,
                        outline=dot_color, width=2
                    )
                elif dot_shape == "Dot":
                    r = max(dot_size // 2, 1)
                    self.canvas.create_oval(
                        cx - r, cy - r, cx + r, cy + r,
                        fill=dot_color, outline=""
                    )
                elif dot_shape == "Square":
                    half = dot_size // 2
                    self.canvas.create_rectangle(
                        cx - half, cy - half, cx + half, cy + half,
                        outline=dot_color, width=2
                    )
                elif dot_shape == "Diamond":
                    points = [cx, cy - dot_size, cx + dot_size, cy, cx, cy + dot_size, cx - dot_size, cy]
                    self.canvas.create_polygon(
                        points, outline=dot_color, fill="", width=2
                    )
                elif dot_shape == "Ring":
                    r = dot_size
                    self.canvas.create_oval(
                        cx - r, cy - r, cx + r, cy + r,
                        outline=dot_color, width=2
                    )
        except Exception as e:
            print(f"[Draw] Center dot error: {e}")

        # Force canvas update
        try:
            self.canvas.update()
        except Exception:
            pass

    def _get_animated_color(self, base_color: str, cs: CrosshairSettings) -> str:
        """Apply color animations"""
        # Click Response has highest priority
        if self._click_response_active and cs.click_response_enabled:
            return base_color  # Return click response color as-is
        
        # CHAOS MODE disables other color effects
        if cs.chaos_enabled:
            return base_color  # CHAOS already randomizes color
        
        if cs.rgb_chroma_enabled:
            speed = cs.chroma_speed / 50.0
            return get_rgb_chroma_color(speed)
        
        if cs.animation_mode == "Breathing":
            return self._animate_breathing(base_color, cs)
        elif cs.animation_mode == "Pulsing":
            return self._animate_pulsing(base_color, cs)
        elif cs.animation_mode == "Rotating":
            return self._animate_rotating(base_color, cs)
        elif cs.animation_mode == "Wave":
            return self._animate_wave(base_color, cs)
        elif cs.animation_mode == "Flicker":
            return self._animate_flicker(base_color, cs)
        elif cs.animation_mode == "Strobe":
            return self._animate_strobe(base_color, cs)
        
        return base_color

    def _get_animated_size(self, base_size: int, cs: CrosshairSettings) -> int:
        """Apply size animation"""
        if cs.animation_mode == "None":
            return base_size
        
        speed = cs.animation_speed / 50.0
        
        if cs.animation_mode == "Breathing":
            t = (time.time() * speed) % 1.0
            scale = 0.7 + 0.3 * math.sin(t * math.pi * 2)
            return max(1, int(base_size * scale))
        
        elif cs.animation_mode == "Pulsing":
            t = (time.time() * speed) % 1.0
            scale = 1.0 if t < 0.5 else 0.6
            return max(1, int(base_size * scale))
        
        elif cs.animation_mode == "Rotating":
            return base_size
        
        elif cs.animation_mode == "Wave":
            t = (time.time() * speed) % 1.0
            scale = 0.6 + 0.4 * math.sin(t * math.pi * 4)
            return max(1, int(base_size * scale))
        
        elif cs.animation_mode == "Flicker":
            if int(time.time() * speed * 10) % 2 == 0:
                scale = random.uniform(0.6, 1.0)
            else:
                scale = 1.0
            return max(1, int(base_size * scale))
        
        elif cs.animation_mode == "Strobe":
            t = (time.time() * speed * 2) % 1.0
            scale = 1.0 if t < 0.3 else 0.5
            return max(1, int(base_size * scale))
        
        return base_size

    def _get_animated_thickness(self, base_thickness: int, cs: CrosshairSettings) -> int:
        """Apply thickness animation"""
        if cs.animation_mode == "None":
            return base_thickness
        
        speed = cs.animation_speed / 50.0
        
        if cs.animation_mode == "Breathing":
            t = (time.time() * speed) % 1.0
            scale = 0.7 + 0.3 * math.sin(t * math.pi * 2)
            return max(1, int(base_thickness * scale))
        
        elif cs.animation_mode == "Pulsing":
            t = (time.time() * speed) % 1.0
            scale = 1.0 if t < 0.5 else 0.6
            return max(1, int(base_thickness * scale))
        
        elif cs.animation_mode == "Rotating":
            return base_thickness
        
        elif cs.animation_mode == "Wave":
            t = (time.time() * speed) % 1.0
            scale = 0.6 + 0.4 * math.sin(t * math.pi * 4)
            return max(1, int(base_thickness * scale))
        
        elif cs.animation_mode == "Flicker":
            if int(time.time() * speed * 10) % 2 == 0:
                scale = random.uniform(0.6, 1.0)
            else:
                scale = 1.0
            return max(1, int(base_thickness * scale))
        
        elif cs.animation_mode == "Strobe":
            t = (time.time() * speed * 2) % 1.0
            scale = 1.0 if t < 0.3 else 0.5
            return max(1, int(base_thickness * scale))
        
        return base_thickness

    def _animate_breathing(self, base_color: str, cs: CrosshairSettings) -> str:
        """Breathing effect"""
        speed = cs.animation_speed / 50.0
        t = (time.time() * speed) % 1.0
        brightness = 0.6 + 0.4 * math.sin(t * math.pi * 2)
        r, g, b = hex_to_rgb(base_color)
        return rgb_to_hex(int(r * brightness), int(g * brightness), int(b * brightness))

    def _animate_pulsing(self, base_color: str, cs: CrosshairSettings) -> str:
        """Pulsing effect"""
        speed = cs.animation_speed / 50.0
        t = (time.time() * speed) % 1.0
        brightness = 1.0 if t < 0.5 else 0.4
        r, g, b = hex_to_rgb(base_color)
        return rgb_to_hex(int(r * brightness), int(g * brightness), int(b * brightness))

    def _animate_rotating(self, base_color: str, cs: CrosshairSettings) -> str:
        """Rotating effect"""
        speed = cs.animation_speed / 50.0
        t = (time.time() * speed) % 1.0
        r, g, b = colorsys.hsv_to_rgb(t, 1.0, 1.0)
        return rgb_to_hex(int(r*255), int(g*255), int(b*255))

    def _animate_wave(self, base_color: str, cs: CrosshairSettings) -> str:
        """Wave effect"""
        speed = cs.animation_speed / 50.0
        t = (time.time() * speed) % 1.0
        brightness = 0.5 + 0.5 * math.sin(t * math.pi * 4)
        r, g, b = hex_to_rgb(base_color)
        return rgb_to_hex(int(r * brightness), int(g * brightness), int(b * brightness))

    def _animate_flicker(self, base_color: str, cs: CrosshairSettings) -> str:
        """Flicker effect"""
        speed = cs.animation_speed / 50.0
        t = time.time() * speed
        if int(t * 10) % 2 == 0:
            brightness = random.uniform(0.3, 1.0)
        else:
            brightness = 1.0
        r, g, b = hex_to_rgb(base_color)
        return rgb_to_hex(int(r * brightness), int(g * brightness), int(b * brightness))

    def _animate_strobe(self, base_color: str, cs: CrosshairSettings) -> str:
        """Strobe effect"""
        speed = cs.animation_speed / 50.0
        t = (time.time() * speed * 2) % 1.0
        brightness = 1.0 if t < 0.3 else 0.1
        r, g, b = hex_to_rgb(base_color)
        return rgb_to_hex(int(r * brightness), int(g * brightness), int(b * brightness))

    def _randomize_chaos_params(self):
        """Randomize chaos mode parameters"""
        self._chaos_params["shape"] = random.choice(SHAPES[:-1])  # Exclude "Image"
        self._chaos_params["size"] = random.randint(5, 40)
        self._chaos_params["thickness"] = random.randint(1, 8)
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        self._chaos_params["color"] = rgb_to_hex(r, g, b)
        self._chaos_params["opacity"] = random.randint(50, 100)

    def _draw_shape(self, shape: str, cx: int, cy: int, size: int, thickness: int, 
                    gap: int, color: str, oc: str, ot: int):
        """Draw crosshair shape"""
        if shape == "Dot":
            self._draw_dot(cx, cy, size, thickness, color, oc, ot)
        elif shape == "Crosshair":
            self._draw_cross(cx, cy, size, thickness, gap, color, oc, ot)
        elif shape == "T-Shape":
            self._draw_tshape(cx, cy, size, thickness, gap, color, oc, ot)
        elif shape == "Circle":
            self._draw_circle(cx, cy, size, thickness, color, oc, ot)
        elif shape == "Square":
            self._draw_square(cx, cy, size, thickness, color, oc, ot)
        elif shape == "Diamond":
            self._draw_diamond(cx, cy, size, thickness, color, oc, ot)
        elif shape == "Ring":
            self._draw_ring(cx, cy, size, thickness, color, oc, ot)
        elif shape == "Crosshair+":
            self._draw_crosshair_plus(cx, cy, size, thickness, gap, color, oc, ot)
        elif shape == "Custom":
            self._draw_custom_crosshair(cx, cy, size, thickness, gap, color, oc, ot)

    def _draw_line_with_outline(self, x1: int, y1: int, x2: int, y2: int, 
                                thickness: int, color: str, oc: str, ot: int):
        """Draw line with optional outline"""
        if ot > 0:
            self.canvas.create_line(
                x1, y1, x2, y2,
                width=thickness + ot * 2, fill=oc, capstyle=tk.BUTT
            )
        self.canvas.create_line(
            x1, y1, x2, y2,
            width=thickness, fill=color, capstyle=tk.BUTT
        )

    def _draw_dot(self, cx, cy, size, thickness, color, oc, ot):
        r = max(size // 2, 1)
        if ot > 0:
            self.canvas.create_oval(
                cx - r - ot, cy - r - ot, cx + r + ot, cy + r + ot,
                fill=oc, outline=""
            )
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=color, outline=""
        )

    def _draw_cross(self, cx, cy, length, thickness, gap, color, oc, ot):
        self._draw_line_with_outline(cx, cy - gap, cx, cy - gap - length, thickness, color, oc, ot)
        self._draw_line_with_outline(cx, cy + gap, cx, cy + gap + length, thickness, color, oc, ot)
        self._draw_line_with_outline(cx - gap, cy, cx - gap - length, cy, thickness, color, oc, ot)
        self._draw_line_with_outline(cx + gap, cy, cx + gap + length, cy, thickness, color, oc, ot)

    def _draw_tshape(self, cx, cy, length, thickness, gap, color, oc, ot):
        self._draw_line_with_outline(cx - gap, cy, cx - gap - length, cy, thickness, color, oc, ot)
        self._draw_line_with_outline(cx + gap, cy, cx + gap + length, cy, thickness, color, oc, ot)
        self._draw_line_with_outline(cx, cy + gap, cx, cy + gap + length, thickness, color, oc, ot)

    def _draw_circle(self, cx, cy, size, thickness, color, oc, ot):
        r = max(size, 2)
        if ot > 0:
            self.canvas.create_oval(
                cx - r - ot, cy - r - ot, cx + r + ot, cy + r + ot,
                outline=oc, width=thickness + ot * 2
            )
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=color, width=thickness
        )

    def _draw_square(self, cx, cy, size, thickness, color, oc, ot):
        half = size // 2
        if ot > 0:
            self.canvas.create_rectangle(
                cx - half - ot, cy - half - ot, cx + half + ot, cy + half + ot,
                outline=oc, width=thickness + ot * 2
            )
        self.canvas.create_rectangle(
            cx - half, cy - half, cx + half, cy + half,
            outline=color, width=thickness
        )

    def _draw_diamond(self, cx, cy, size, thickness, color, oc, ot):
        points = [cx, cy - size, cx + size, cy, cx, cy + size, cx - size, cy]
        if ot > 0:
            self.canvas.create_polygon(
                points, outline=oc, width=thickness + ot * 2, fill=""
            )
        self.canvas.create_polygon(
            points, outline=color, width=thickness, fill=""
        )

    def _draw_ring(self, cx, cy, size, thickness, color, oc, ot):
        r = size
        if ot > 0:
            self.canvas.create_oval(
                cx - r - ot, cy - r - ot, cx + r + ot, cy + r + ot,
                outline=oc, width=thickness + ot * 2
            )
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=color, width=thickness
        )

    def _draw_crosshair_plus(self, cx, cy, length, thickness, gap, color, oc, ot):
        # Horizontal
        self._draw_line_with_outline(cx - gap - length, cy, cx - gap, cy, thickness, color, oc, ot)
        self._draw_line_with_outline(cx + gap, cy, cx + gap + length, cy, thickness, color, oc, ot)
        # Vertical
        self._draw_line_with_outline(cx, cy - gap - length, cx, cy - gap, thickness, color, oc, ot)
        self._draw_line_with_outline(cx, cy + gap, cx, cy + gap + length, thickness, color, oc, ot)
        # Diagonals
        diag_len = int(length * 0.7)
        self._draw_line_with_outline(cx - gap - diag_len, cy - gap - diag_len, cx - gap, cy - gap, thickness, color, oc, ot)
        self._draw_line_with_outline(cx + gap, cy + gap, cx + gap + diag_len, cy + gap + diag_len, thickness, color, oc, ot)
        self._draw_line_with_outline(cx + gap + diag_len, cy - gap - diag_len, cx + gap, cy - gap, thickness, color, oc, ot)
        self._draw_line_with_outline(cx - gap, cy + gap, cx - gap - diag_len, cy + gap + diag_len, thickness, color, oc, ot)

    def _draw_custom_crosshair(self, cx, cy, length, thickness, gap, color, oc, ot):
        # Custom crosshair (combination)
        self._draw_cross(cx, cy, length, thickness, gap, color, oc, ot)
        r = max(length // 3, 2)
        if ot > 0:
            self.canvas.create_oval(
                cx - r - ot, cy - r - ot, cx + r + ot, cy + r + ot,
                fill=oc, outline=""
            )
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=color, outline=""
        )

    def _draw_image(self, cx, cy, size, image_path):
        """Draw custom image"""
        img = load_image(image_path, int(size * 2))
        if not img:
            return
        
        # Convert to PhotoImage
        try:
            photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(cx, cy, image=photo)
            self.canvas.image = photo  # Keep a reference
        except Exception as e:
            print(f"[Image] Draw error: {e}")

    def update_settings(self, cs: CrosshairSettings):
        """Update crosshair settings"""
        self.cs = cs
        self.draw_crosshair()

    def toggle_visibility(self):
        """Toggle overlay visibility"""
        self._visible = not self._visible
        if self._visible:
            self.root.deiconify()
        else:
            self.root.withdraw()

    def set_monitor(self, monitor_idx: int):
        """Switch to different monitor"""
        if 0 <= monitor_idx < len(self.monitors):
            self.current_monitor = self.monitors[monitor_idx]
            monitor_info = get_monitor_info(self.current_monitor)
            self.screen_w = monitor_info['width']
            self.screen_h = monitor_info['height']
            self.monitor_x = monitor_info['left']
            self.monitor_y = monitor_info['top']
            self.root.geometry(f"{self.screen_w}x{self.screen_h}+{self.monitor_x}+{self.monitor_y}")
            self.config.selected_monitor = monitor_idx

    def destroy(self):
        """Cleanup"""
        self._alive = False
        try:
            self.root.destroy()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════
# SETTINGS WINDOW - TABBED UI
# ═══════════════════════════════════════════════════════════════════════════

class SettingsWindow:
    def __init__(self, config: AppConfig, overlay: OverlayWindow, on_apply: Callable, on_save: Callable):
        self.config = config
        self.overlay = overlay
        self.on_apply = on_apply
        self.on_save = on_save
        self._win = None
        self._alive = True
        self._hotkey_vars = {}
        self._vars = {}

    # Theme helpers for SettingsWindow widgets
    def _theme_corner(self):
        return int(THEME.get("corner_radius", 8))

    def _theme_border(self):
        return int(THEME.get("border_width", 1))

    def _theme_font(self, size: int = 12, weight: str = "normal"):
        fam = THEME.get("font_family", "Segoe UI")
        try:
            return (fam, int(size), weight)
        except Exception:
            return (fam, size)

    def _button_style(self):
        return THEME.get("button_style", "flat")

    def show(self):
        """Show settings window"""
        if self._win and self._win.winfo_exists():
            self._win.focus()
            return
        
        try:
            ctk.set_appearance_mode("Dark")
            ctk.set_default_color_theme("dark-blue")
            
            self._win = ctk.CTkToplevel()
            self._win.title("CROSSHAIR v6.0 // НАСТРОЙКИ")
            self._win.geometry("600x800")
            self._win.configure(fg_color=THEME["bg_primary"])
            self._win.attributes("-topmost", True)
            
            # Header
            header = ctk.CTkFrame(self._win, fg_color=THEME["bg_secondary"], corner_radius=self._theme_corner(), height=50,
                                   border_width=self._theme_border())
            header.pack(fill="x")
            ctk.CTkLabel(header, text=translate("APP_TITLE", self.config.language), font=self._theme_font(18, "bold"), 
                         text_color=THEME["accent_primary"]).pack(side="left", padx=20, pady=10)
            
            # Tabs
            self.tabs = ctk.CTkTabview(self._win, fg_color=THEME["bg_secondary"],
                                       text_color=THEME["fg_primary"])
            self.tabs.pack(fill="both", expand=True, padx=15, pady=15)
            
            t_general = self.tabs.add("🎯 " + translate("GENERAL", self.config.language))
            t_layers = self.tabs.add("🎨 " + translate("LAYERS", self.config.language))
            t_behavior = self.tabs.add("🎮 " + translate("BEHAVIOR", self.config.language))
            t_system = self.tabs.add("⚙️ " + translate("SYSTEM", self.config.language))
            
            cs = CrosshairSettings(**self.config.crosshair)
            
            # ═══ GENERAL TAB ═══
            print("[Settings] Creating GENERAL tab...")
            self._create_general_tab(t_general, cs)
            
            # ═══ LAYERS TAB ═══
            print("[Settings] Creating LAYERS tab...")
            self._create_layers_tab(t_layers, cs)
            
            # ═══ BEHAVIOR TAB ═══
            print("[Settings] Creating BEHAVIOR tab...")
            self._create_behavior_tab(t_behavior, cs)
            
            # ═══ SYSTEM TAB ═══
            print("[Settings] Creating SYSTEM tab...")
            self._create_system_tab(t_system, cs)
            
            # Footer
            footer = ctk.CTkFrame(self._win, fg_color="transparent", height=50)
            footer.pack(fill="x", padx=15, pady=10)
            ctk.CTkButton(footer, text="💾 " + translate("Save", self.config.language), fg_color=THEME["accent_primary"],
                          text_color="#000000", font=self._theme_font(12, "bold"),
                          hover_color=THEME["accent_secondary"],
                          command=self._save_click).pack(side="right", fill="x", expand=True, padx=(5,0))
            ctk.CTkButton(footer, text="✕ " + translate("Close", self.config.language), fg_color="transparent",
                          border_color=THEME["border"], border_width=1,
                          text_color=THEME["fg_secondary"],
                          command=self._win.destroy).pack(side="left", fill="x", expand=True, padx=(0,5))
            
            print("[Settings] ✓ Settings window created successfully")
        except Exception as e:
            print(f"[Settings] Error creating window: {e}")
            import traceback
            traceback.print_exc()


    def _create_general_tab(self, parent, cs):
        """General settings tab"""
        try:
            frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
            frame.pack(fill="both", expand=True)
            
            # Shape
            ctk.CTkLabel(frame, text=translate("Shape", self.config.language), text_color=THEME["fg_primary"]).pack(anchor="w", padx=10, pady=(10,0))
            var = ctk.StringVar(value=cs.shape)
            ctk.CTkOptionMenu(frame, variable=var, values=SHAPES, fg_color=THEME["bg_secondary"],
                             command=lambda x: self._live_apply()).pack(fill="x", padx=10, pady=5)
            self._vars["shape"] = var
            
            # Size
            self._create_slider(frame, translate("Size", self.config.language), "size", 1, 80, cs.size)
            # Thickness
            self._create_slider(frame, translate("Thickness", self.config.language), "thickness", 0.5, 15, cs.thickness)
            # Gap
            self._create_slider(frame, translate("Gap", self.config.language), "gap", 0, 30, cs.gap)
            # Opacity
            self._create_slider(frame, translate("Opacity %", self.config.language), "opacity", 10, 100, cs.opacity)
            
            # Color
            self._create_color_picker(frame, translate("Main Color", self.config.language), "color", cs.color)
            # Outline color
            self._create_color_picker(frame, translate("Outline Color", self.config.language), "outline_color", cs.outline_color)
            # Outline thickness
            self._create_slider(frame, translate("Outline Width", self.config.language), "outline_thickness", 0, 8, cs.outline_thickness)
        except Exception as e:
            print(f"[UI] General tab error: {e}")
            import traceback
            traceback.print_exc()

    def _create_layers_tab(self, parent, cs):
        """Layers settings tab"""
        try:
            frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
            frame.pack(fill="both", expand=True)
            
            # Center Dot
            ctk.CTkLabel(frame, text=translate("CENTER DOT LAYER", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(10,5))

            self._create_switch(frame, translate("Enable Center Dot", self.config.language), "center_dot_enabled", cs.center_dot_enabled)
            self._create_color_picker(frame, translate("Center Dot Color", self.config.language), "center_dot_color", cs.center_dot_color)
            self._create_slider(frame, translate("Center Dot Size", self.config.language), "center_dot_size", 1, 30, cs.center_dot_size)
            self._create_slider(frame, translate("Center Dot Opacity", self.config.language), "center_dot_opacity", 10, 100, cs.center_dot_opacity)
            
            var = ctk.StringVar(value=cs.center_dot_shape)
            ctk.CTkLabel(frame, text=translate("Center Dot Shape", self.config.language), text_color=THEME["fg_primary"]).pack(anchor="w", padx=10, pady=(10,2))
            ctk.CTkOptionMenu(frame, variable=var, values=["Circle", "Dot", "Square", "Diamond", "Ring"],
                             fg_color=THEME["bg_secondary"],
                             command=lambda x: self._live_apply()).pack(fill="x", padx=10, pady=5)
            self._vars["center_dot_shape"] = var
            
            # Animation
            ctk.CTkLabel(frame, text=translate("ANIMATION", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(20,5))
            
            var = ctk.StringVar(value=cs.animation_mode)
            ctk.CTkOptionMenu(frame, variable=var, values=ANIMATION_MODES, fg_color=THEME["bg_secondary"],
                             command=lambda x: self._live_apply()).pack(fill="x", padx=10, pady=5)
            self._vars["animation_mode"] = var
            
            self._create_slider(frame, translate("Animation Speed", self.config.language), "animation_speed", 10, 200, cs.animation_speed)
            
            # RGB Chroma
            self._create_switch(frame, translate("RGB Rainbow Chroma 🌈", self.config.language), "rgb_chroma_enabled", cs.rgb_chroma_enabled)
            self._create_slider(frame, translate("Rainbow Speed", self.config.language), "chroma_speed", 10, 200, cs.chroma_speed)
            
            # Chaos
            self._create_switch(frame, translate("CHAOS MODE 🎲", self.config.language), "chaos_enabled", cs.chaos_enabled)
            
            # Blink/Flash Effect
            ctk.CTkLabel(frame, text=translate("BLINK EFFECT", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(20,5))
            
            self._create_switch(frame, translate("Enable Blink 💥", self.config.language), "blink_enabled", cs.blink_enabled)
            self._create_slider(frame, translate("Blink Speed", self.config.language), "blink_speed", 10, 200, cs.blink_speed)
        except Exception as e:
            print(f"[UI] Layers tab error: {e}")
            import traceback
            traceback.print_exc()

    def _create_behavior_tab(self, parent, cs):
        """Behavior settings tab"""
        try:
            frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
            frame.pack(fill="both", expand=True)
            
            # Hide on ADS
            ctk.CTkLabel(frame, text=translate("HIDE ON ADS", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(10,5))
            
            self._create_switch(frame, translate("Hide when Right-Click (ADS)", self.config.language), "hide_on_ads", cs.hide_on_ads)
            
            # Click Response
            ctk.CTkLabel(frame, text=translate("CLICK RESPONSE", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(20,5))
            
            self._create_switch(frame, translate("Enable Click Response", self.config.language), "click_response_enabled", cs.click_response_enabled)
            self._create_color_picker(frame, translate("Flash Color", self.config.language), "click_response_color", cs.click_response_color)
            self._create_slider(frame, translate("Size Bump", self.config.language), "click_response_bump_size", 0, 20, cs.click_response_bump_size)
            
            # Image Support
            ctk.CTkLabel(frame, text=translate("IMAGE SUPPORT", self.config.language) if translate("IMAGE SUPPORT", self.config.language) else "IMAGE SUPPORT", text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(20,5))
            
            def load_image_file():
                path = filedialog.askopenfilename(filetypes=[("PNG images", "*.png"), ("All files", "*.*")])
                if path:
                    self._vars["image_path"].set(path)
                    self._live_apply()
            
            img_frame = ctk.CTkFrame(frame, fg_color="transparent")
            img_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkButton(img_frame, text="📁 Load Image", command=load_image_file,
                         fg_color=THEME["accent_primary"], text_color="#000000",
                         width=100).pack(side="left")
            
            var = ctk.StringVar(value=cs.image_path)
            ctk.CTkLabel(img_frame, text=cs.image_path[:40], text_color=THEME["fg_secondary"],
                        font=self._theme_font(9)).pack(side="left", padx=10)
            self._vars["image_path"] = var
            
            self._create_slider(frame, translate("Image Scale", self.config.language), "image_scale", 0.1, 3.0, cs.image_scale)
        except Exception as e:
            print(f"[UI] Behavior tab error: {e}")
            import traceback
            traceback.print_exc()

    def _create_system_tab(self, parent, cs):
        """System settings tab"""
        try:
            frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
            frame.pack(fill="both", expand=True)
            
            # Monitors
            ctk.CTkLabel(frame, text=translate("MONITOR", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(10,5))
            
            monitors = [f"Monitor {i+1}" for i in range(len(self.overlay.monitors))]
            var = ctk.StringVar(value=monitors[self.config.selected_monitor])
            
            def on_monitor_change(choice):
                try:
                    idx = monitors.index(choice)
                    self.overlay.set_monitor(idx)
                except Exception as e:
                    print(f"[UI] Monitor change error: {e}")
            
            ctk.CTkOptionMenu(frame, variable=var, values=monitors,
                             fg_color=THEME["bg_secondary"], command=on_monitor_change).pack(fill="x", padx=10, pady=5)
            
            # Hotkeys
            ctk.CTkLabel(frame, text=translate("HOTKEYS", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(20,5))
            
            for key, label in [("toggle_overlay", "Toggle Overlay"), ("toggle_settings", "Show Settings"), ("panic", "PANIC Exit")]:
                hk_frame = ctk.CTkFrame(frame, fg_color="transparent")
                hk_frame.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(hk_frame, text=translate(label, self.config.language), text_color=THEME["fg_primary"]).pack(side="left")
                
                var = ctk.StringVar(value=self.config.hotkeys.get(key, ""))
                self._hotkey_vars[key] = var
                
                btn = ctk.CTkButton(hk_frame, textvariable=var, width=100,
                                   fg_color=THEME["bg_secondary"], border_color=THEME["border"],
                                   border_width=1, command=lambda v=var: self._record_hotkey(v))
                btn.pack(side="right")
            
            # Game Profiles
            ctk.CTkLabel(frame, text=translate("GAME_PROFILES", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(20,5))
            
            def add_current_game():
                process = get_foreground_process()
                if process:
                    self.config.profiles[process] = self.config.crosshair
                    messagebox.showinfo(translate("Success", self.config.language), f"{translate('Success', self.config.language)}: {process}")
                    self.on_save()
                else:
                    messagebox.showwarning(translate("Warning", self.config.language), translate("No game detected", self.config.language))
            
            ctk.CTkButton(frame, text=translate("Add Current Game Profile", self.config.language), command=add_current_game,
                         fg_color=THEME["accent_primary"], text_color="#000000").pack(fill="x", padx=10, pady=5)

            # Language & Theme
            ctk.CTkLabel(frame, text=translate("LANGUAGE", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(20,5))
            lang_var = ctk.StringVar(value=getattr(self.config, 'language', 'en'))
            ctk.CTkOptionMenu(frame, variable=lang_var, values=["en", "ru"],
                             fg_color=THEME["bg_secondary"], command=lambda x: self._live_apply()).pack(fill="x", padx=10, pady=5)
            self._vars["language"] = lang_var

            ctk.CTkLabel(frame, text=translate("APP THEME", self.config.language), text_color=THEME["accent_primary"],
                        font=self._theme_font(12, "bold")).pack(anchor="w", padx=10, pady=(10,5))
            theme_var = ctk.StringVar(value=getattr(self.config, 'app_theme', 'Dark'))
            ctk.CTkOptionMenu(frame, variable=theme_var, values=list(THEMES.keys()),
                             fg_color=THEME["bg_secondary"], command=lambda x: self._apply_theme(x)).pack(fill="x", padx=10, pady=5)
            self._vars["app_theme"] = theme_var
            
            # helper to apply theme selection
            def apply_theme_local(choice):
                try:
                    if choice in THEMES:
                        THEME.update(THEMES[choice])
                        # update basic UI background
                        try:
                            self._win.configure(fg_color=THEME["bg_primary"])
                        except Exception:
                            pass
                        # reapply overlay colors
                        try:
                            self.on_apply(CrosshairSettings(**self.config.crosshair))
                        except Exception:
                            pass
                except Exception as e:
                    print(f"[UI] Apply theme error: {e}")
            # expose for OptionMenu callback
            self._apply_theme = apply_theme_local
        except Exception as e:
            print(f"[UI] System tab error: {e}")
            import traceback
            traceback.print_exc()

    def _create_slider(self, parent, label, var_name, from_val, to_val, default):
        """Create slider with numeric input"""
        label_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=self._theme_corner(), border_width=self._theme_border())
        label_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(label_frame, text=label, text_color=THEME["fg_primary"], font=self._theme_font(11)).pack(side="left")
        
        entry = ctk.CTkEntry(label_frame, width=50, height=25, font=self._theme_font(11),
                            fg_color=THEME["bg_secondary"], border_width=self._theme_border(),
                            border_color=THEME["accent_primary"], text_color=THEME["accent_primary"])
        entry.insert(0, str(int(default)))
        entry.pack(side="right", padx=5)
        
        var = ctk.DoubleVar(value=default)
        var._entry_widget = entry
        
        def on_slider_change(v):
            entry.delete(0, "end")
            entry.insert(0, str(int(float(v))))
            self._live_apply()
        
        def on_entry_change(event=None):
            try:
                val = float(entry.get())
                val = max(from_val, min(to_val, val))
                var.set(val)
                slider.set(val)
                entry.delete(0, "end")
                entry.insert(0, str(int(val)))
                self._live_apply()
            except ValueError:
                entry.delete(0, "end")
                entry.insert(0, str(int(var.get())))
        
        slider = ctk.CTkSlider(parent, from_=from_val, to=to_val, variable=var,
                      progress_color=THEME["accent_primary"],
                      button_color=THEME["accent_primary"],
                      button_hover_color=THEME["accent_secondary"],
                      fg_color=THEME["bg_secondary"], height=16,
                      command=on_slider_change)
        slider.pack(fill="x", padx=10, pady=2)
        
        entry.bind("<Return>", on_entry_change)
        entry.bind("<FocusOut>", on_entry_change)
        
        self._vars[var_name] = var

    def _create_color_picker(self, parent, label, var_name, default):
        """Create color picker"""
        frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=self._theme_corner(), border_width=self._theme_border())
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame, text=label, text_color=THEME["fg_primary"], font=self._theme_font(11)).pack(side="left")
        
        var = ctk.StringVar(value=default)
        
        btn = ctk.CTkButton(frame, text="", width=40, height=25, fg_color=default,
                           hover_color=default, border_color=THEME["border"],
                           border_width=self._theme_border(), command=lambda: self._pick_color(var, btn))
        btn.pack(side="right", padx=5)
        
        hex_label = ctk.CTkLabel(frame, text=default, text_color=THEME["accent_tertiary"],
                                font=self._theme_font(9), width=70)
        hex_label.pack(side="right", padx=5)
        
        var._color_button = btn
        var._hex_label = hex_label
        self._vars[var_name] = var

    def _pick_color(self, var, btn):
        """Color picker dialog"""
        color = colorchooser.askcolor(color=var.get(), title="Choose Color")[1]
        if color:
            var.set(color)
            btn.configure(fg_color=color, hover_color=color)
            var._hex_label.configure(text=color)
            self._live_apply()

    def _create_switch(self, parent, label, var_name, default):
        """Create toggle switch"""
        frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=self._theme_corner(), border_width=self._theme_border())
        frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(frame, text=label, text_color=THEME["fg_primary"], font=self._theme_font(11)).pack(side="left")
        
        var = ctk.BooleanVar(value=default)
        switch = ctk.CTkSwitch(frame, variable=var, text="",
                              button_color=THEME["accent_primary"],
                              button_hover_color=THEME["accent_secondary"],
                              fg_color=THEME["bg_secondary"],
                              progress_color=THEME["accent_primary"],
                              command=lambda: self._live_apply())
        switch.pack(side="right", padx=10)
        
        self._vars[var_name] = var

    def _record_hotkey(self, var):
        """Record hotkey from keyboard"""
        var.set("...")
        def handler(event):
            var.set(event.name)
            keyboard.unhook(hook)
        hook = keyboard.on_press(handler)

    def _collect_settings(self):
        """Collect all settings with safe defaults"""
        try:
            def get_var(name, default):
                if name in self._vars:
                    try:
                        val = self._vars[name].get()
                        return val
                    except Exception:
                        return default
                return default
            
            return CrosshairSettings(
                shape=get_var('shape', 'Crosshair'),
                size=int(get_var('size', 12)),
                thickness=int(get_var('thickness', 2)),
                gap=int(get_var('gap', 4)),
                opacity=int(get_var('opacity', 100)),
                offset_x=int(get_var('offset_x', 0)),
                offset_y=int(get_var('offset_y', 0)),
                color=get_var('color', '#00FF00'),
                outline_color=get_var('outline_color', '#000000'),
                outline_thickness=int(get_var('outline_thickness', 1)),
                animation_mode=get_var('animation_mode', 'None'),
                animation_speed=int(get_var('animation_speed', 50)),
                inner_size=int(get_var('inner_size', 0)),
                rgb_chroma_enabled=get_var('rgb_chroma_enabled', False),
                chroma_speed=int(get_var('chroma_speed', 50)),
                chaos_enabled=get_var('chaos_enabled', False),
                hide_on_ads=get_var('hide_on_ads', False),
                click_response_enabled=get_var('click_response_enabled', False),
                click_response_color=get_var('click_response_color', '#FF0000'),
                click_response_bump_size=int(get_var('click_response_bump_size', 5)),
                click_response_duration=0.1,
                image_path=get_var('image_path', ''),
                image_scale=float(get_var('image_scale', 1.0)),
                center_dot_enabled=get_var('center_dot_enabled', False),
                center_dot_color=get_var('center_dot_color', '#FF0000'),
                center_dot_size=int(get_var('center_dot_size', 4)),
                center_dot_opacity=int(get_var('center_dot_opacity', 100)),
                center_dot_shape=get_var('center_dot_shape', 'Circle'),
                blink_enabled=get_var('blink_enabled', False),
                blink_speed=int(get_var('blink_speed', 50)),
            )
        except Exception as e:
            print(f"[Settings] Collect error: {e}")
            return CrosshairSettings(**self.config.crosshair)

    def _live_apply(self):
        """Apply changes in real-time"""
        try:
            if self._win and self._win.winfo_exists():
                cs = self._collect_settings()
                # apply UI language/theme if changed
                if "language" in self._vars:
                    try:
                        self.config.language = self._vars["language"].get()
                    except Exception:
                        pass
                if "app_theme" in self._vars:
                    try:
                        choice = self._vars["app_theme"].get()
                        self.config.app_theme = choice
                        if choice in THEMES:
                            THEME.update(THEMES[choice])
                    except Exception:
                        pass
                self.on_apply(cs)
        except Exception as e:
            print(f"[Settings] Apply error: {e}")

    def _save_click(self):
        """Save configuration"""
        try:
            cs = self._collect_settings()
            self.config.crosshair = asdict(cs)
            for key, var in self._hotkey_vars.items():
                self.config.hotkeys[key] = var.get()
            # Save language/theme if present in UI
            if "language" in self._vars:
                self.config.language = self._vars["language"].get()
            if "app_theme" in self._vars:
                self.config.app_theme = self._vars["app_theme"].get()
                # apply immediately
                theme_choice = self.config.app_theme
                if theme_choice in THEMES:
                    THEME.update(THEMES[theme_choice])
            self.on_save()
            messagebox.showinfo(translate("Success", self.config.language), translate("Save Success", self.config.language))
        except Exception as e:
            print(f"[Settings] Save error: {e}")
            messagebox.showerror("Error", f"Failed to save: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# TRAY ICON
# ═══════════════════════════════════════════════════════════════════════════

class TrayIcon:
    """System tray integration"""

    def __init__(self, on_show_settings, on_toggle_overlay, on_quit):
        self._on_show = on_show_settings
        self._on_toggle = on_toggle_overlay
        self._on_quit = on_quit
        self._icon: Optional[pystray.Icon] = None

    def start(self):
        """Start tray icon"""
        image = self._create_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("🎯 Toggle", lambda: self._on_toggle()),
            pystray.MenuItem("⚙️ Settings", lambda: self._on_show()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("✕ Quit", lambda: self._on_quit()),
        )
        self._icon = pystray.Icon("CrosshairOverlay", image, "Crosshair v6.0", menu)
        threading.Thread(target=self._icon.run, daemon=True).start()

    def _create_icon_image(self) -> Image.Image:
        """Create tray icon image"""
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((10, 10, 54, 54), outline="#00FF88", width=5)
        d.ellipse((28, 28, 36, 36), fill="#00FF88")
        return img

    def stop(self):
        """Stop tray icon"""
        if self._icon:
            self._icon.stop()


# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION - MAIN CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════

class Application:
    """Main application controller"""

    def __init__(self):
        print("╔════════════════════════════════════════════════════════════╗")
        print("║     CROSSHAIR OVERLAY v6.0 - LEGENDARY EDITION            ║")
        print("╚════════════════════════════════════════════════════════════╝")
        
        try:
            print("[App] Loading configuration...")
            self.config = AppConfig.load()
            print("[App] ✓ Configuration loaded")
        except Exception as e:
            print(f"[FATAL] Failed to load config: {e}")
            traceback.print_exc()
            raise
        
        try:
            print("[App] Creating overlay window...")
            self.overlay = OverlayWindow(self.config, on_close=self.quit)
            print("[App] ✓ Overlay created")
        except Exception as e:
            print(f"[FATAL] Failed to create overlay: {e}")
            traceback.print_exc()
            raise
        
        try:
            print("[App] Creating settings window...")
            self.settings = SettingsWindow(
                self.config,
                self.overlay,
                on_apply=self._on_apply,
                on_save=self._on_save
            )
            print("[App] ✓ Settings created")
        except Exception as e:
            print(f"[FATAL] Failed to create settings: {e}")
            traceback.print_exc()
            raise
        
        try:
            print("[App] Setting up system tray...")
            self._setup_tray()
            print("[App] ✓ Tray setup complete")
        except Exception as e:
            print(f"[FATAL] Failed to setup tray: {e}")
            traceback.print_exc()
            raise
        
        try:
            print("[App] Registering hotkeys...")
            self._register_hotkeys()
            print("[App] ✓ Hotkeys registered")
        except Exception as e:
            print(f"[FATAL] Failed to register hotkeys: {e}")
            traceback.print_exc()
            raise

    def _setup_tray(self):
        """Setup system tray icon"""
        try:
            log("[Tray] Initializing system tray...", "DEBUG")
            self.tray = TrayIcon(
                on_show_settings=self.show_settings,
                on_toggle_overlay=self.toggle_overlay,
                on_quit=self.quit
            )
            self.tray.start()
            log("[Tray] ✓ System tray ready", "DEBUG")
        except Exception as e:
            log(f"[Tray] Error: {e}", "ERROR")
            print(f"[Tray] Error: {e}")
            traceback.print_exc()

    def _register_hotkeys(self):
        """Register global hotkeys"""
        hk = self.config.hotkeys
        try:
            keyboard.add_hotkey(hk["toggle_overlay"], self.toggle_overlay)
            keyboard.add_hotkey(hk["toggle_settings"], self.toggle_settings)
            keyboard.add_hotkey(hk["panic"], self.quit)
            log("[Hotkeys] ✓ Registered successfully")
            print("[Hotkeys] ✓ Registered successfully")
        except Exception as e:
            log(f"[Hotkeys] Error: {e}", "ERROR")
            print(f"[Hotkeys] Error: {e}")

    def show_settings(self):
        """Show settings window"""
        self.settings.show()

    def toggle_settings(self):
        """Toggle the settings window (F7) - show or destroy if visible"""
        try:
            win = getattr(self.settings, '_win', None)
            if win and hasattr(win, 'winfo_exists') and win.winfo_exists():
                try:
                    win.destroy()
                except Exception:
                    pass
            else:
                # create/show settings
                try:
                    self.settings.show()
                except Exception:
                    pass
        except Exception as e:
            print(f"[App] toggle_settings error: {e}")

    def toggle_overlay(self):
        """Toggle overlay visibility"""
        self.overlay.toggle_visibility()

    def _on_apply(self, cs):
        """Apply settings to overlay"""
        self.overlay.update_settings(cs)

    def _on_save(self):
        """Save configuration"""
        try:
            self.config.save()
            log("[App] ✓ Configuration saved")
            print("[App] ✓ Configuration saved")
            # Reload hotkeys with new values
            print("[App] Reloading hotkeys...")
            keyboard.remove_all_hotkeys()
            self._register_hotkeys()
            print("[App] ✓ Hotkeys reloaded")
        except Exception as e:
            log(f"[App] Save config error: {e}", "ERROR")
            print(f"[App] Save config error: {e}")

    def quit(self):
        """Cleanup and exit"""
        log("[App] Initiating shutdown...", "INFO")
        print("[App] Initiating shutdown...")
        
        try:
            log("[App] Removing hotkeys...", "DEBUG")
            keyboard.remove_all_hotkeys()
            print("[App] Hotkeys removed")
        except Exception as e:
            log(f"[App] Hotkey removal error: {e}", "ERROR")
            print(f"[App] Hotkey error: {e}")
        
        try:
            log("[App] Saving configuration...", "DEBUG")
            self._on_save()
        except Exception as e:
            log(f"[App] Save error: {e}", "ERROR")
            print(f"[App] Save error: {e}")
            traceback.print_exc()
        
        try:
            log("[App] Stopping tray...", "DEBUG")
            self.tray.stop()
            print("[App] Tray stopped")
            time.sleep(0.3)
        except Exception as e:
            log(f"[App] Tray stop error: {e}", "ERROR")
            print(f"[App] Tray error: {e}")
            traceback.print_exc()
        
        try:
            log("[App] Destroying overlay...", "DEBUG")
            self.overlay._alive = False
            self.overlay.destroy()
            print("[App] Overlay destroyed")
            time.sleep(0.2)
        except Exception as e:
            log(f"[App] Overlay destroy error: {e}", "ERROR")
            print(f"[App] Overlay error: {e}")
            traceback.print_exc()
        
        try:
            log("[App] Destroying settings window...", "DEBUG")
            self.settings._alive = False
            self.settings.destroy()
            print("[App] Settings destroyed")
            time.sleep(0.2)
        except Exception as e:
            log(f"[App] Settings destroy error: {e}", "ERROR")
            print(f"[App] Settings error: {e}")
            traceback.print_exc()
        
        log("[App] ✓ Cleanup complete, exiting...", "INFO")
        print("[App] ✓ Shutdown complete")
        
        time.sleep(0.3)
        try:
            self.overlay.root.quit()
            self.overlay.root.destroy()
        except Exception as e:
            log(f"[App] Root destroy error: {e}", "ERROR")
            pass
        
        time.sleep(0.5)
        log("[App] Process exit via sys.exit()", "INFO")
        print("[App] Exiting...")
        sys.exit(0)


    def run(self):
        """Run application"""
        try:
            log("[App] Starting main application loop...", "INFO")
            print("[App] Application running. Press F7 to open settings, END to panic exit.")
            self.overlay.root.mainloop()
        except KeyboardInterrupt:
            log("[App] Keyboard interrupt detected", "INFO")
            self.quit()
        except Exception as e:
            log(f"[ERROR] Unexpected error: {e}", "ERROR")
            print(f"[ERROR] {e}")
            traceback.print_exc()
            self.quit()


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        log("="*80, "INFO")
        log("CROSSHAIR OVERLAY v6.0 STARTING", "INFO")
        log("="*80, "INFO")
        app = Application()
        log("[Main] Application initialized successfully", "INFO")
        app.run()
    except Exception as e:
        log(f"[FATAL] Application crashed: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        print(f"FATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
