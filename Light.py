#=========== All The Rights to The Creator: Mohammed Boulifa =================================================================#

import ctypes
import tkinter as tk
from tkinter import filedialog, Label, Frame, Canvas, Entry, Scrollbar

import numpy as np
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps

import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource — works for dev and PyInstaller."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

class RoundSlider(tk.Canvas):
    """
    A horizontal slider drawn entirely on a Canvas with:
    - rounded filled track (progress bar to the left of thumb)
    - circular thumb
    - smooth drag + click
    """
    TRACK_H  = 4
    THUMB_R  = 8
    TROUGH   = "#484848"
    FILL     = "#888888"
    THUMB_C  = "#ffffff"
    THUMB_HOV= "#dddddd"
    HEIGHT   = 24

    def __init__(self, master, from_=0.0, to=10.0, resolution=0.1,
                 initial=0.0, command=None, bg="#2c2c2c", **kw):
        super().__init__(master, height=self.HEIGHT, bg=bg,
                         highlightthickness=0, bd=0, **kw)
        self._from   = from_
        self._to     = to
        self._res    = resolution
        self._val    = initial
        self._cmd    = command
        self._bg     = bg
        self._dragging = False

        self.bind("<Configure>",      self._draw)
        self.bind("<ButtonPress-1>",  self._on_press)
        self.bind("<B1-Motion>",      self._on_drag)
        self.bind("<ButtonRelease-1>",self._on_release)
        self.bind("<Enter>",          lambda e: self._draw(hover=True))
        self.bind("<Leave>",          lambda e: self._draw(hover=False))

    # ── value helpers ────────────────────────────────────────────────────────
    def get(self):
        return self._val

    def set(self, val, trigger=False):
        self._val = max(self._from, min(self._to,
                        round(round(val / self._res) * self._res, 10)))
        self._draw()
        if trigger and self._cmd:
            self._cmd(str(self._val))

    def config(self, **kw):
        if "command" in kw:
            self._cmd = kw.pop("command")
        super().config(**kw)

    # ── geometry helpers ─────────────────────────────────────────────────────
    def _track_x(self):
        """(x_start, x_end) of the track line."""
        r = self.THUMB_R
        return r + 2, self.winfo_width() - r - 2

    def _val_to_x(self, val):
        x0, x1 = self._track_x()
        t = (val - self._from) / (self._to - self._from)
        return x0 + t * (x1 - x0)

    def _x_to_val(self, x):
        x0, x1 = self._track_x()
        t = max(0.0, min(1.0, (x - x0) / max(1, x1 - x0)))
        raw = self._from + t * (self._to - self._from)
        return round(round(raw / self._res) * self._res, 10)

    # ── drawing ──────────────────────────────────────────────────────────────
    def _draw(self, event=None, hover=False):
        w = self.winfo_width()
        if w < 4:
            return
        h   = self.HEIGHT
        cy  = h // 2
        x0, x1 = self._track_x()
        tx  = self._val_to_x(self._val)

        self.delete("all")

        # Background track
        self._rr(x0, cy - self.TRACK_H//2,
                 x1, cy + self.TRACK_H//2,
                 r=self.TRACK_H//2, fill=self.TROUGH, outline="")

        # Filled track (left of thumb)
        if tx > x0:
            self._rr(x0, cy - self.TRACK_H//2,
                     tx, cy + self.TRACK_H//2,
                     r=self.TRACK_H//2, fill=self.FILL, outline="")

        # Thumb circle
        tc = self.THUMB_HOV if hover or self._dragging else self.THUMB_C
        r  = self.THUMB_R
        self.create_oval(tx-r, cy-r, tx+r, cy+r, fill=tc, outline="")

    def _rr(self, x1, y1, x2, y2, r=2, **kw):
        """Mini round-rect on self."""
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
               x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
               x1,y2, x1,y2-r, x1,y1+r, x1,y1, x1+r,y1]
        self.create_polygon(pts, smooth=True, **kw)

    # ── interaction ──────────────────────────────────────────────────────────
    def _on_press(self, e):
        self._dragging = True
        self._update_from_x(e.x)

    def _on_drag(self, e):
        if self._dragging:
            self._update_from_x(e.x)

    def _on_release(self, e):
        self._dragging = False
        self._draw()

    def _update_from_x(self, x):
        new_val = self._x_to_val(x)
        if new_val != self._val:
            self._val = new_val
            self._draw(hover=True)
            if self._cmd:
                self._cmd(str(self._val))


def _detect_os_dark_mode():
    """Return True if the OS is currently in dark mode."""
    import sys, subprocess
    try:
        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return val == 0          # 0 = dark, 1 = light
        elif sys.platform == "darwin":
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True)
            return result.stdout.strip().lower() == "dark"
        else:  # Linux / freedesktop
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True)
            return "dark" in result.stdout.lower()
    except Exception:
        return True   # default to dark on failure


THEMES = {
    "dark": {
        "BG_ROOT":    "#1a1a1a",
        "BG_PANEL":   "#1a1a1a",
        "BG_CARD":    "#2c2c2c",
        "BG_CANVAS":  "#141414",
        "BG_BAR":     "#111111",
        "BG_BTN":     "#3c3c3c",
        "BG_BTN_HOV": "#4a4a4a",
        "BG_BTN_DIS": "#2a2a2a",
        "BG_VAL":     "#383838",
        "BG_SEP":     "#3a3a3a",
        "FG_TEXT":    "#ffffff",
        "FG_SUB":     "#aaaaaa",
        "FG_DIS":     "#555555",
        "SLIDER_TROUGH": "#484848",
        "SLIDER_FILL":   "#888888",
        "SLIDER_THUMB":  "#ffffff",
        "SLIDER_HOV":    "#dddddd",
        "ZOOM_TROUGH":   "#2a2a2a",
        "ZOOM_FILL":     "#555555",
        "ZOOM_THUMB":    "#cccccc",
        "DWM_DARK": 1,
        "DWM_COLOR": 0x00000000,   # black title bar
    },
    "light": {
        "BG_ROOT":    "#f0f0f0",
        "BG_PANEL":   "#f0f0f0",
        "BG_CARD":    "#ffffff",
        "BG_CANVAS":  "#d8d8d8",
        "BG_BAR":     "#e0e0e0",
        "BG_BTN":     "#d0d0d0",
        "BG_BTN_HOV": "#c0c0c0",
        "BG_BTN_DIS": "#e8e8e8",
        "BG_VAL":     "#e4e4e4",
        "BG_SEP":     "#cccccc",
        "FG_TEXT":    "#1a1a1a",
        "FG_SUB":     "#555555",
        "FG_DIS":     "#aaaaaa",
        "SLIDER_TROUGH": "#cccccc",
        "SLIDER_FILL":   "#888888",
        "SLIDER_THUMB":  "#333333",
        "SLIDER_HOV":    "#111111",
        "ZOOM_TROUGH":   "#cccccc",
        "ZOOM_FILL":     "#888888",
        "ZOOM_THUMB":    "#333333",
        "DWM_DARK": 0,
        "DWM_COLOR": 0x00f0f0f0,   # light title bar (0x00BBGGRR)
    },
}


class SimplePhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Light - Photo Editor")
        self.root.geometry("1600x900")
        self.root.iconphoto(False, tk.PhotoImage(file=resource_path("Icon.png")))

        # ── Black window title bar (Windows only) ───────────────────────────
        try:
            import ctypes
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            # DWMWA_CAPTION_COLOR  = 35  (Windows 11)
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_CAPTION_COLOR = 35
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
            black = ctypes.c_int(0x00000000)   # COLORREF: 0x00BBGGRR
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_CAPTION_COLOR,
                ctypes.byref(black), ctypes.sizeof(black))
        except Exception:
            pass  # non-Windows or older Windows — silently skip

        # ── Font setup — prefer Inter, fall back to Segoe UI then Arial ──
        from tkinter import font as tkfont
        _available = tkfont.families()
        if "Inter" in _available:
            self.FONT = "Inter"
        elif "Inter Bold" in _available:
            self.FONT = "Inter Bold"
        elif "Segoe UI" in _available:
            self.FONT = "Segoe UI"
        else:
            self.FONT = "Arial"
        # Variables
        self.original_image = None
        self.current_image = None
        self.displayed_image = None
        self.filename = None
        self.last_x = 0
        self.last_y = 0
        self.layers = []
        self.current_layer = None
        self.mask = None

        # Zoom & pan state
        self._zoom        = 1.0
        self._zoom_min    = 0.1
        self._zoom_max    = 10.0
        self._pan_x       = 0
        self._pan_y       = 0
        self._pan_start_x = 0
        self._pan_start_y = 0
        self._panning     = False
        self._fit_pending = False   # True when a new image needs fit-to-canvas

        # Undo / Redo history (stores slider states)
        self._history = []        # list of slider-state dicts
        self._redo_stack = []     # list of slider-state dicts
        self._max_history = 50    # maximum undo steps
        self._is_undoing = False  # guard to avoid pushing during undo/redo restore
        
        # ── Theme ───────────────────────────────────────────────────────────
        self._theme_name = "dark" if _detect_os_dark_mode() else "light"
        self._themed_widgets = []   # list of (widget, role) for live retheming
        self._apply_theme_palette()   # sets self.BG_ROOT, FG_TEXT, etc.
        self.root.configure(bg=self.BG_ROOT)

        # ── Left panel (scrollable) ─────────────────────────────────────────
        self.left_container = Frame(root, width=260, bg=self.BG_PANEL)
        self.left_container.pack(side=tk.LEFT, fill=tk.Y)
        self.left_container.pack_propagate(False)

        self.left_scrollbar = Scrollbar(self.left_container, orient=tk.VERTICAL,
                                        bg=self.BG_PANEL, troughcolor=self.BG_PANEL,
                                        width=14)
        self.left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.left_scroll_canvas = Canvas(
            self.left_container, bg=self.BG_PANEL,
            yscrollcommand=self.left_scrollbar.set,
            highlightthickness=0, width=254
        )
        self.left_scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_scrollbar.config(command=self.left_scroll_canvas.yview)

        self.left_frame = Frame(self.left_scroll_canvas, bg=self.BG_PANEL, padx=10, pady=10)
        self.left_frame_id = self.left_scroll_canvas.create_window(
            (0, 0), window=self.left_frame, anchor="nw"
        )

        def _on_frame_configure(event):
            self.left_scroll_canvas.configure(
                scrollregion=self.left_scroll_canvas.bbox("all")
            )
        self.left_frame.bind("<Configure>", _on_frame_configure)

        def _on_canvas_configure(event):
            self.left_scroll_canvas.itemconfig(self.left_frame_id, width=event.width)
        self.left_scroll_canvas.bind("<Configure>", _on_canvas_configure)

        # Panel scroll via mouse wheel — works wherever the pointer is in the panel
        def _panel_scroll(event):
            self.left_scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_scroll(widget):
            """Recursively bind <MouseWheel> to widget and all its descendants."""
            widget.bind("<MouseWheel>", _panel_scroll, add="+")
            for child in widget.winfo_children():
                _bind_scroll(child)

        # Bind existing widgets now, then re-bind whenever the frame layout changes
        # so widgets added later (cards, sliders, buttons) are covered automatically.
        self.left_scroll_canvas.bind("<MouseWheel>", _panel_scroll)
        self.left_frame.bind("<Configure>", lambda e: _bind_scroll(self.left_frame), add="+")
        _bind_scroll(self.left_frame)

        # ── Right panel ─────────────────────────────────────────────────────
        self.right_frame = Frame(root, bg=self.BG_CANVAS)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas_frame = Frame(self.right_frame, bg=self.BG_CANVAS)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = Canvas(self.canvas_frame, bg=self.BG_CANVAS,
                             cursor="hand2", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Zoom with Ctrl+scroll OR plain scroll on canvas
        self.canvas.bind("<MouseWheel>",        self._on_canvas_scroll)
        self.canvas.bind("<Control-MouseWheel>", self._on_canvas_scroll)

        # Pan with left-button drag
        self.canvas.bind("<ButtonPress-1>",   self._pan_start)
        self.canvas.bind("<B1-Motion>",       self._pan_move)
        self.canvas.bind("<ButtonRelease-1>", self._pan_end)

        # ── Zoom bar (bottom of right panel) ────────────────────────────────
        zoom_bar = Frame(self.right_frame, bg=self.BG_BAR, pady=4)
        zoom_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._zoom_bar_frame = zoom_bar   # ref for apply_theme

        zl = Label(zoom_bar, text="Zoom", bg=self.BG_BAR, fg=self.FG_SUB,
              font=(self.FONT, 8), width=5)
        zl.pack(side=tk.LEFT, padx=(10, 2))
        self._zoom_lbl = zl

        self._zoom_var = tk.DoubleVar(value=1.0)
        self._zoom_slider = RoundSlider(
            zoom_bar, from_=self._zoom_min, to=self._zoom_max,
            resolution=0.01, initial=1.0,
            command=self._on_zoom_slider,
            bg=self.BG_BAR,
        )
        T = THEMES[self._theme_name]
        self._zoom_slider.TROUGH    = T["ZOOM_TROUGH"]
        self._zoom_slider.FILL      = T["ZOOM_FILL"]
        self._zoom_slider.THUMB_C   = T["ZOOM_THUMB"]
        self._zoom_slider.THUMB_HOV = T["FG_TEXT"]
        self._zoom_slider.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=False)

        # Zoom % — clickable canvas pill
        zoom_val_cv = Canvas(zoom_bar, width=52, height=22, bg=self.BG_BAR,
                             highlightthickness=0, bd=0, cursor="xterm")
        zoom_val_cv.pack(side=tk.LEFT, padx=(4, 0))
        self._zoom_val_cv = zoom_val_cv  # ref for theme

        zoom_entry = Entry(zoom_bar, width=6, justify="center",
                           bg=self.BG_VAL, fg=self.FG_TEXT,
                           insertbackground=self.FG_TEXT,
                           relief=tk.FLAT, font=(self.FONT, 8))

        def _draw_zoom_pill(text):
            T = THEMES[self._theme_name]
            zoom_val_cv.delete("all")
            zoom_val_cv.configure(bg=T["BG_BAR"])
            self._round_rect(zoom_val_cv, 1, 1, 51, 21, r=5,
                             fill=T["BG_VAL"], outline="")
            zoom_val_cv.create_text(26, 11, text=text,
                                    fill=T["FG_TEXT"], font=(self.FONT, 8))

        _draw_zoom_pill("100%")
        self._zoom_label = zoom_val_cv   # keep reference for updates
        self._zoom_pill_draw = _draw_zoom_pill

        def _show_zoom_entry(e=None):
            zoom_val_cv.pack_forget()
            zoom_entry.delete(0, tk.END)
            zoom_entry.insert(0, str(int(self._zoom * 100)))
            zoom_entry.pack(side=tk.LEFT, padx=(4, 0), ipady=2)
            zoom_entry.focus_set()
            zoom_entry.select_range(0, tk.END)

        def _commit_zoom_entry(e=None):
            try:
                pct = float(zoom_entry.get())
                new_zoom = max(self._zoom_min, min(self._zoom_max, pct / 100.0))
                cw = self.canvas.winfo_width()  or 800
                ch = self.canvas.winfo_height() or 600
                cx, cy = cw / 2, ch / 2
                self._pan_x = cx - (cx - self._pan_x) * (new_zoom / self._zoom)
                self._pan_y = cy - (cy - self._pan_y) * (new_zoom / self._zoom)
                self._zoom  = new_zoom
                self._zoom_slider.set(round(self._zoom, 2))
                _draw_zoom_pill(f"{int(self._zoom * 100)}%")
                self._render_zoom()
            except ValueError:
                pass
            zoom_entry.pack_forget()
            zoom_val_cv.pack(side=tk.LEFT, padx=(4, 0))

        zoom_val_cv.bind("<Button-1>", _show_zoom_entry)
        zoom_entry.bind("<Return>",    _commit_zoom_entry)
        zoom_entry.bind("<KP_Enter>",  _commit_zoom_entry)
        zoom_entry.bind("<FocusOut>",  _commit_zoom_entry)
        zoom_entry.bind("<Escape>",    lambda e: (zoom_entry.pack_forget(),
                                                   zoom_val_cv.pack(side=tk.LEFT, padx=(4,0))))

        # Reset zoom button
        def _reset_zoom():
            if not self.current_image:
                return
            cw = self.canvas.winfo_width()  or 800
            ch = self.canvas.winfo_height() or 600
            iw, ih = self.current_image.size
            fit_zoom = min(cw / iw, ch / ih)
            self._zoom  = fit_zoom
            self._pan_x = (cw - iw * fit_zoom) / 2
            self._pan_y = (ch - ih * fit_zoom) / 2
            self._zoom_slider.set(round(self._zoom, 2))
            self._zoom_pill_draw(f"{int(self._zoom * 100)}%")
            self._render_zoom()
        Label(zoom_bar, text="  ", bg=self.BG_BAR).pack(side=tk.LEFT)
        reset_cv = Canvas(zoom_bar, width=46, height=20, bg=self.BG_BAR,
                          highlightthickness=0, cursor="hand2")
        reset_cv.pack(side=tk.LEFT, padx=4)
        self._reset_cv = reset_cv

        def _draw_reset_btn(hov=False):
            T = THEMES[self._theme_name]
            bg = T["BG_BTN_HOV"] if hov else T["BG_BTN"]
            reset_cv.delete("all")
            reset_cv.configure(bg=T["BG_BAR"])
            self._round_rect(reset_cv, 1, 1, 45, 19, r=5, fill=bg, outline="")
            reset_cv.create_text(23, 10, text="Reset", fill=T["FG_SUB"],
                                 font=(self.FONT, 8))

        self._draw_reset_btn = _draw_reset_btn
        reset_cv.bind("<Configure>", lambda e: _draw_reset_btn())
        reset_cv.bind("<Enter>",     lambda e: _draw_reset_btn(True))
        reset_cv.bind("<Leave>",     lambda e: _draw_reset_btn(False))
        reset_cv.bind("<Button-1>",  lambda e: _reset_zoom())

        # Status bar
        self.status_bar = Label(
            self.right_frame, text="Ready — Open an image to start",
            bg=self.BG_BAR, fg=self.FG_SUB, anchor=tk.W, padx=10, pady=3,
            font=(self.FONT, 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # ── Build toolbar & bind shortcuts ──────────────────────────────────
        self.create_toolbar()
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-Z>", lambda e: self.undo())
        self.root.bind("<Control-Y>", lambda e: self.redo())
        
       
    # ── Rounded-rect helper ──────────────────────────────────────────────────
    def _round_rect(self, canvas, x1, y1, x2, y2, r=12, **kwargs):
        """Draw a rounded rectangle on a Canvas widget."""
        pts = [
            x1+r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r,
            x2,   y2-r, x2,   y2,
            x2-r, y2,   x1+r, y2,
            x1,   y2,   x1,   y2-r,
            x1,   y1+r, x1,   y1,
            x1+r, y1,
        ]
        return canvas.create_polygon(pts, smooth=True, **kwargs)

    # ── Theme palette ────────────────────────────────────────────────────────
    def _apply_theme_palette(self):
        """Copy the current theme dict values onto self.* colour attributes."""
        T = THEMES[self._theme_name]
        self.BG_ROOT     = T["BG_ROOT"]
        self.BG_PANEL    = T["BG_PANEL"]
        self.BG_CARD     = T["BG_CARD"]
        self.BG_CANVAS   = T["BG_CANVAS"]
        self.BG_BAR      = T["BG_BAR"]
        self.BG_BTN      = T["BG_BTN"]
        self.BG_BTN_HOV  = T["BG_BTN_HOV"]
        self.BG_BTN_DIS  = T["BG_BTN_DIS"]
        self.BG_VAL      = T["BG_VAL"]
        self.BG_SEP      = T["BG_SEP"]
        self.FG_TEXT     = T["FG_TEXT"]
        self.FG_SUB      = T["FG_SUB"]
        self.FG_DIS      = T["FG_DIS"]
        # keep legacy names used in older code paths
        self.BG_SLIDER   = T["BG_CARD"]
        self.ACCENT      = T["SLIDER_FILL"]

    def apply_theme(self, theme_name=None):
        """Switch to 'dark' or 'light' (or toggle if None) and repaint everything."""
        if theme_name is None:
            theme_name = "light" if self._theme_name == "dark" else "dark"
        self._theme_name = theme_name
        self._apply_theme_palette()
        T = THEMES[theme_name]

        # ── DWM title bar ───────────────────────────────────────────────────
        try:
            import ctypes
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20,
                ctypes.byref(ctypes.c_int(T["DWM_DARK"])),
                ctypes.sizeof(ctypes.c_int))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 35,
                ctypes.byref(ctypes.c_int(T["DWM_COLOR"])),
                ctypes.sizeof(ctypes.c_int))
        except Exception:
            pass

        # ── Root & main frames ──────────────────────────────────────────────
        self.root.configure(bg=T["BG_ROOT"])
        self.left_container.configure(bg=T["BG_PANEL"])
        self.left_scrollbar.configure(bg=T["BG_PANEL"], troughcolor=T["BG_PANEL"])
        self.left_scroll_canvas.configure(bg=T["BG_PANEL"])
        self.left_frame.configure(bg=T["BG_PANEL"])
        self.right_frame.configure(bg=T["BG_CANVAS"])
        self.canvas_frame.configure(bg=T["BG_CANVAS"])
        self.canvas.configure(bg=T["BG_CANVAS"])
        self.status_bar.configure(bg=T["BG_BAR"], fg=T["FG_SUB"])
        self._zoom_bar_frame.configure(bg=T["BG_BAR"])
        self._zoom_lbl.configure(bg=T["BG_BAR"], fg=T["FG_SUB"])
        self._zoom_slider.configure(bg=T["BG_BAR"])
        self._zoom_slider.TROUGH    = T["ZOOM_TROUGH"]
        self._zoom_slider.FILL      = T["ZOOM_FILL"]
        self._zoom_slider.THUMB_C   = T["ZOOM_THUMB"]
        self._zoom_slider.THUMB_HOV = T["FG_TEXT"]
        self._zoom_slider._draw()
        self._zoom_val_cv.configure(bg=T["BG_BAR"])
        self._zoom_pill_draw(f"{int(self._zoom * 100)}%")
        self._reset_cv.configure(bg=T["BG_BAR"])
        self._draw_reset_btn()

        # ── Theme toggle button ─────────────────────────────────────────────
        self._theme_btn.configure(bg=T["BG_CARD"])
        self._draw_theme_btn()

        # ── Walk all registered themed widgets ──────────────────────────────
        self._repaint_widgets()

        # ── Redraw all slider pills ─────────────────────────────────────────
        for name, _ in self.SLIDER_NAMES:
            pill_draw = getattr(self, f"{name}_pill_draw", None)
            slider    = getattr(self, f"{name}_slider",    None)
            if pill_draw and slider:
                pill_draw(f"{slider.get():.1f}")
            s = getattr(self, f"{name}_slider", None)
            if s:
                s.configure(bg=T["BG_CARD"])
                s.TROUGH    = T["SLIDER_TROUGH"]
                s.FILL      = T["SLIDER_FILL"]
                s.THUMB_C   = T["SLIDER_THUMB"]
                s.THUMB_HOV = T["SLIDER_HOV"]
                s._draw()

    def _repaint_widgets(self):
        """Walk all widgets in the left panel and repaint by type."""
        T = THEMES[self._theme_name]

        def _walk(widget):
            cls = widget.winfo_class()
            try:
                if cls == "Frame":
                    bg = widget.cget("bg")
                    # Map old dark colours → new theme colours
                    if bg in ("#1a1a1a", "#f0f0f0", T["BG_PANEL"],
                              THEMES["dark"]["BG_PANEL"], THEMES["light"]["BG_PANEL"]):
                        widget.configure(bg=T["BG_PANEL"])
                    elif bg in ("#2c2c2c", "#ffffff", T["BG_CARD"],
                                THEMES["dark"]["BG_CARD"], THEMES["light"]["BG_CARD"]):
                        widget.configure(bg=T["BG_CARD"])
                    elif bg in ("#111111", "#e0e0e0", T["BG_BAR"],
                                THEMES["dark"]["BG_BAR"], THEMES["light"]["BG_BAR"]):
                        widget.configure(bg=T["BG_BAR"])
                elif cls == "Label":
                    widget.configure(fg=T["FG_SUB"])
                    bg = widget.cget("bg")
                    if bg in ("#2c2c2c", "#ffffff", T["BG_CARD"],
                              THEMES["dark"]["BG_CARD"], THEMES["light"]["BG_CARD"]):
                        widget.configure(bg=T["BG_CARD"])
                    elif bg in ("#1a1a1a", "#f0f0f0", T["BG_PANEL"],
                                THEMES["dark"]["BG_PANEL"], THEMES["light"]["BG_PANEL"]):
                        widget.configure(bg=T["BG_PANEL"])
                    elif bg in ("#111111", "#e0e0e0", T["BG_BAR"],
                                THEMES["dark"]["BG_BAR"], THEMES["light"]["BG_BAR"]):
                        widget.configure(bg=T["BG_BAR"])
                elif cls == "Canvas":
                    bg = widget.cget("bg")
                    if bg in ("#2c2c2c", "#ffffff", T["BG_CARD"],
                              THEMES["dark"]["BG_CARD"], THEMES["light"]["BG_CARD"]):
                        widget.configure(bg=T["BG_CARD"])
                    elif bg in ("#1a1a1a", "#f0f0f0", T["BG_PANEL"],
                                THEMES["dark"]["BG_PANEL"], THEMES["light"]["BG_PANEL"]):
                        widget.configure(bg=T["BG_PANEL"])
                elif cls == "Entry":
                    widget.configure(bg=T["BG_VAL"], fg=T["FG_TEXT"],
                                     insertbackground=T["FG_TEXT"],
                                     highlightbackground=T["BG_VAL"])
            except Exception:
                pass
            for child in widget.winfo_children():
                _walk(child)

        _walk(self.left_frame)
        _walk(self._zoom_bar_frame)

        # Cards: redraw rounded backgrounds
        for cv, inner, inner_win, wrapper in self._card_refs:
            self._repaint_card(cv, inner, inner_win, wrapper, T)

        # Buttons: redraw rounded backgrounds
        for cv_ref in self._btn_refs:
            cv_ref["T"] = T
            cv_ref["redraw"]()

    def _repaint_card(self, cv, inner, inner_win, wrapper, T):
        CARD_R   = 14
        CARD_PAD = 12
        w = wrapper.winfo_width()
        h = inner.winfo_reqheight() + CARD_PAD * 2
        if w < 10:
            return
        cv.configure(bg=T["BG_PANEL"])
        inner.configure(bg=T["BG_CARD"])
        cv.delete("bg_rect")
        self._round_rect(cv, 2, 2, w-2, h-2, r=CARD_R,
                         fill=T["BG_CARD"], outline=T["BG_SEP"], tags="bg_rect")
        cv.tag_lower("bg_rect")
        # repaint title label and separator inside card
        for child in inner.winfo_children():
            cls = child.winfo_class()
            if cls == "Label":
                child.configure(bg=T["BG_CARD"], fg=T["FG_TEXT"])
            elif cls == "Frame":
                child.configure(bg=T["BG_SEP"] if child.cget("height") == 1
                                else T["BG_CARD"])

    # ── Card ─────────────────────────────────────────────────────────────────
    def _make_card(self, title):
        CARD_R   = 14
        CARD_PAD = 12
        CARD_BG  = self.BG_CARD
        SEP_BG   = self.BG_SEP

        wrapper = Frame(self.left_frame, bg=self.BG_PANEL)
        wrapper.pack(fill=tk.X, pady=(0, 10))

        cv = Canvas(wrapper, bg=self.BG_PANEL, highlightthickness=0,
                    bd=0, relief=tk.FLAT)
        cv.pack(fill=tk.X)

        inner = Frame(cv, bg=CARD_BG)
        inner_win = cv.create_window(CARD_PAD, CARD_PAD,
                                     window=inner, anchor="nw")

        Label(inner, text=title, bg=CARD_BG, fg=self.FG_TEXT,
              font=(self.FONT, 11, "bold"),
              anchor="center", pady=6).pack(fill=tk.X)

        Frame(inner, bg=SEP_BG, height=1).pack(fill=tk.X, pady=(0, 6))

        def _resize(event=None):
            w = wrapper.winfo_width()
            if w < 10:
                return
            h = inner.winfo_reqheight() + CARD_PAD * 2
            cv.config(width=w, height=h)
            cv.delete("bg_rect")
            self._round_rect(cv, 2, 2, w-2, h-2, r=CARD_R,
                             fill=inner["bg"], outline=self.BG_SEP, tags="bg_rect")
            cv.tag_lower("bg_rect")
            cv.itemconfig(inner_win, width=w - CARD_PAD * 2)

        inner.bind("<Configure>",   lambda e: wrapper.after(1, _resize))
        wrapper.bind("<Configure>", lambda e: wrapper.after(1, _resize))
        cv.bind("<Configure>",      lambda e: wrapper.after(1, _resize))

        def _fwd_scroll(event):
            self.left_scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        cv.bind("<MouseWheel>",    _fwd_scroll)
        inner.bind("<MouseWheel>", _fwd_scroll)

        # Register for theme repainting
        if not hasattr(self, "_card_refs"):
            self._card_refs = []
        self._card_refs.append((cv, inner, inner_win, wrapper))

        return inner

    # ── Rounded button ───────────────────────────────────────────────────────
    def _make_btn(self, parent, text, command, col=0):
        BTN_H   = 38
        BTN_R   = 10

        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        cv = Canvas(parent, height=BTN_H, bg=parent["bg"],
                    highlightthickness=0, bd=0, cursor="hand2")
        cv.grid(row=0, column=col, sticky="ew", padx=3, pady=3)

        enabled = [True]
        # mutable so _repaint_widgets can swap them
        colors = {"bg": self.BG_BTN, "hov": self.BG_BTN_HOV, "dis": self.BG_BTN_DIS}

        def _draw(bg=None):
            if bg is None:
                bg = colors["bg"]
            w = cv.winfo_width() or 100
            cv.delete("all")
            self._round_rect(cv, 1, 1, w-1, BTN_H-1, r=BTN_R, fill=bg, outline="")
            cv.create_text(w//2, BTN_H//2, text=text,
                           fill=self.FG_TEXT if enabled[0] else self.FG_DIS,
                           font=(self.FONT, 10, "bold"))

        def _on_enter(e):
            if enabled[0]: _draw(colors["hov"])
        def _on_leave(e):
            if enabled[0]: _draw(colors["bg"])
        def _on_click(e):
            if enabled[0]: command()

        cv.bind("<Configure>",  lambda e: _draw())
        cv.bind("<Enter>",      _on_enter)
        cv.bind("<Leave>",      _on_leave)
        cv.bind("<Button-1>",   _on_click)

        def _config(state=None, fg=None):
            if state == tk.DISABLED:
                enabled[0] = False
                _draw(colors["dis"])
            elif state == tk.NORMAL:
                enabled[0] = True
                _draw(colors["bg"])
        cv.config_btn = _config

        def _repaint():
            colors["bg"]  = self.BG_BTN
            colors["hov"] = self.BG_BTN_HOV
            colors["dis"] = self.BG_BTN_DIS
            cv.configure(bg=cv.master["bg"] if cv.master.winfo_class() == "Frame"
                         else self.BG_CARD)
            _draw(colors["dis"] if not enabled[0] else colors["bg"])

        cv.bind("<MouseWheel>",
                lambda e: self.left_scroll_canvas.yview_scroll(
                    int(-1*(e.delta/120)), "units"))

        if not hasattr(self, "_btn_refs"):
            self._btn_refs = []
        self._btn_refs.append({"redraw": _repaint, "T": None})

        return cv

    # ── Toolbar builder ──────────────────────────────────────────────────────
    def create_toolbar(self):
        # ── File Operation ──────────────────────────────────────────────────
        file_card = self._make_card("File Operation")

        row1 = Frame(file_card, bg=file_card["bg"])
        row1.pack(fill=tk.X, pady=(0, 4))
        self._make_btn(row1, "Open", self.open_image, col=0)
        self._make_btn(row1, "Save", self.save_image, col=1)

        row2 = Frame(file_card, bg=file_card["bg"])
        row2.pack(fill=tk.X, pady=(0, 4))
        self.undo_btn = self._make_btn(row2, "Undo", self.undo, col=0)
        self.redo_btn = self._make_btn(row2, "Redo", self.redo, col=1)
        self.undo_btn.config_btn(state=tk.DISABLED)
        self.redo_btn.config_btn(state=tk.DISABLED)

        # ── Theme toggle ─────────────────────────────────────────────────────
        theme_row = Frame(file_card, bg=file_card["bg"])
        theme_row.pack(fill=tk.X)
        self._theme_btn = Canvas(theme_row, height=32, bg=file_card["bg"],
                                 highlightthickness=0, bd=0, cursor="hand2")
        self._theme_btn.pack(fill=tk.X, padx=3, pady=(0, 3))

        def _draw_theme_btn(bg=None):
            if bg is None:
                bg = self.BG_BTN
            w = self._theme_btn.winfo_width() or 230
            self._theme_btn.delete("all")
            self._round_rect(self._theme_btn, 1, 1, w-1, 31, r=10,
                             fill=bg, outline="")
            icon = "🔆 Light Mode" if self._theme_name == "dark" else "🌙 Dark Mode"
            self._theme_btn.create_text(w//2, 16, text=icon,
                                        fill=self.FG_TEXT,
                                        font=(self.FONT, 10))

        self._draw_theme_btn = _draw_theme_btn
        self._theme_btn.bind("<Configure>", lambda e: _draw_theme_btn())
        self._theme_btn.bind("<Enter>",     lambda e: _draw_theme_btn(self.BG_BTN_HOV))
        self._theme_btn.bind("<Leave>",     lambda e: _draw_theme_btn())
        self._theme_btn.bind("<Button-1>",  lambda e: self.apply_theme())
        self._theme_btn.bind("<MouseWheel>",
            lambda e: self.left_scroll_canvas.yview_scroll(
                int(-1*(e.delta/120)), "units"))

        # ── Basic Adjustments ───────────────────────────────────────────────
        adj_card = self._make_card("Basic Adjustments")
        self.create_slider_with_entry(adj_card, "Brightness", 0.0, 10.0, 1.0, self.adjust_brightness)
        self.create_slider_with_entry(adj_card, "Contrast",   -10.0, 10.0, 1.0, self.adjust_contrast)
        self.create_slider_with_entry(adj_card, "Saturation", -10.0, 10.0, 1.0, self.adjust_saturation)
        self.create_slider_with_entry(adj_card, "Vibrancy",   -10.0, 10.0, 1.0, self.adjust_vibrancy)
        self.create_slider_with_entry(adj_card, "Texture",    -10.0, 10.0, 1.0, self.adjust_texture)

        # ── Color Adjustments ───────────────────────────────────────────────
        color_card = self._make_card("Color Adjustments")
        self.create_slider_with_entry(color_card, "Red",   -10.0, 10.0, 1.0, self.adjust_colors)
        self.create_slider_with_entry(color_card, "Green", -10.0, 10.0, 1.0, self.adjust_colors)
        self.create_slider_with_entry(color_card, "Blue",  -10.0, 10.0, 1.0, self.adjust_colors)

        # ── Effects ─────────────────────────────────────────────────────────
        effects_card = self._make_card("Effects")
        self.create_slider_with_entry(effects_card, "Blur",          0.0, 10.0, 0.0, self.apply_blur)
        self.create_slider_with_entry(effects_card, "Sharpen",       0.0, 10.0, 0.0, self.apply_sharpen)
        self.create_slider_with_entry(effects_card, "Black & White", 0.0,  1.0, 0.0, self.convert_bw)
        self.create_slider_with_entry(effects_card, "Invert",        0.0,  1.0, 0.0, self.invert_colors)

    # ── Slider row ───────────────────────────────────────────────────────────
    def create_slider_with_entry(self, parent, label, from_, to, initial, command):
        CARD_BG = parent["bg"]
        VAL_W   = 46
        VAL_H   = 22
        VAL_R   = 7

        frame = Frame(parent, bg=CARD_BG)
        frame.pack(fill=tk.X, pady=(2, 6))

        # ── Label row ────────────────────────────────────────────────────────
        Label(frame, text=label, bg=CARD_BG, fg="#aaaaaa",
              font=(self.FONT, 9), anchor="w").pack(fill=tk.X)

        # ── Slider + pill row (grid so pill width is guaranteed) ─────────────
        row = Frame(frame, bg=CARD_BG)
        row.pack(fill=tk.X, pady=(2, 0))
        row.columnconfigure(0, weight=1)          # slider expands
        row.columnconfigure(1, minsize=VAL_W + 8) # pill column fixed

        slider = RoundSlider(row, from_=from_, to=to, resolution=0.1,
                             initial=initial, command=None, bg=CARD_BG)
        slider.grid(row=0, column=0, sticky="ew", pady=2)

        # ── Pill canvas (always in col 1) ─────────────────────────────────
        pill = Canvas(row, width=VAL_W, height=VAL_H, bg=CARD_BG,
                      highlightthickness=0, bd=0, cursor="xterm")
        pill.grid(row=0, column=1, padx=(6, 0))

        # ── Hidden entry (replaces pill while editing) ────────────────────
        entry = Entry(row, width=5, justify="center",
                      bg=self.BG_VAL, fg=self.FG_TEXT,
                      insertbackground=self.FG_TEXT,
                      relief=tk.FLAT, font=(self.FONT, 8),
                      highlightthickness=1,
                      highlightcolor="#777777",
                      highlightbackground=self.BG_VAL)

        _display_text = [f"{initial:.1f}"]   # mutable cell so _draw can read latest

        def _draw_pill(text=None):
            if text is not None:
                _display_text[0] = text
            pill.delete("all")
            self._round_rect(pill, 1, 1, VAL_W-1, VAL_H-1, r=VAL_R,
                             fill=self.BG_VAL, outline="")
            pill.create_text(VAL_W//2, VAL_H//2,
                             text=_display_text[0],
                             fill=self.FG_TEXT,
                             font=(self.FONT, 8))

        # Draw on first layout AND any resize
        pill.bind("<Configure>", lambda e: _draw_pill())

        # ── Wrapped command: slider drag → redraw pill + call real command ──
        def _wrapped_command(val, _cmd=command):
            v = float(val)
            _draw_pill(f"{v:.1f}")
            entry.delete(0, tk.END)
            entry.insert(0, f"{v:.1f}")
            _cmd(str(v))

        slider.config(command=_wrapped_command)

        # ── Pill click → show entry in same grid cell ─────────────────────
        def _show_entry(e=None):
            pill.grid_remove()
            entry.delete(0, tk.END)
            entry.insert(0, _display_text[0])
            entry.grid(row=0, column=1, padx=(6, 0), ipady=2, sticky="e")
            entry.focus_set()
            entry.select_range(0, tk.END)

        def _commit_entry(e=None):
            try:
                raw   = float(entry.get())
                val   = max(from_, min(to, raw))
                slider.set(val)
                _wrapped_command(str(val))
            except ValueError:
                _draw_pill()        # restore last good value
            entry.grid_remove()
            pill.grid(row=0, column=1, padx=(6, 0))

        def _cancel_entry(e=None):
            entry.grid_remove()
            pill.grid(row=0, column=1, padx=(6, 0))

        pill.bind("<Button-1>",  _show_entry)
        entry.bind("<Return>",   _commit_entry)
        entry.bind("<KP_Enter>", _commit_entry)
        entry.bind("<FocusOut>", _commit_entry)
        entry.bind("<Escape>",   _cancel_entry)

        # ── Mouse wheel: adjust value ─────────────────────────────────────
        def _on_wheel(event, s=slider, f=from_, t=to):
            delta   = 0.1 if event.delta > 0 else -0.1
            new_val = round(min(t, max(f, s.get() + delta)), 1)
            s.set(new_val)
            _wrapped_command(str(new_val))

        slider.bind("<MouseWheel>", _on_wheel)
        pill.bind("<MouseWheel>",   _on_wheel)
        entry.bind("<MouseWheel>",  _on_wheel)

        # Forward wheel from frame label area to panel scroller
        def _fwd(e):
            self.left_scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        frame.bind("<MouseWheel>", _fwd)

        # ── Store references ──────────────────────────────────────────────
        key = label.lower().replace("black & white", "b&w")
        setattr(self, f"{key}_slider",    slider)
        setattr(self, f"{key}_entry",     entry)
        setattr(self, f"{key}_pill_draw", _draw_pill)  # for reset_sliders

        return slider, entry
    
    def update_slider_from_entry(self, slider, entry, min_val, max_val):
        try:
            value = float(entry.get())
            if value < min_val:
                value = min_val
                entry.delete(0, tk.END)
                entry.insert(0, str(min_val))
            elif value > max_val:
                value = max_val
                entry.delete(0, tk.END)
                entry.insert(0, str(max_val))
            slider.set(value)
            # Trigger the slider's command
            slider.event_generate("<ButtonRelease-1>")
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, str(slider.get()))
    
    def open_image(self):
        self.filename = filedialog.askopenfilename(title="Select Image",
                                                  filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                                                             ("All files", "*.*")))
        if self.filename:
            try:
                self.original_image = Image.open(self.filename).convert("RGB")
                self.current_image = self.original_image.copy()
                self.layers = [self.current_image.copy()]
                self.current_layer = 0
                # Reset zoom & pan for new image
                self._zoom  = 1.0
                self._pan_x = 0
                self._pan_y = 0
                self._fit_pending = True
                self.display_image()
                self.status_bar.config(text=f"Image loaded: {self.filename}")

                # Reset all sliders and clear history
                self.reset_sliders()
                self._history.clear()
                self._redo_stack.clear()
                self._push_history()   # baseline state
                self._update_undo_redo_buttons()
            except Exception as e:
                self.status_bar.config(text=f"Error: {str(e)}")
    
    def reset_sliders(self):
        sliders = [
            ('brightness', 1.0), ('contrast', 1.0), ('saturation', 1.0),
            ('vibrancy',   1.0), ('texture',  1.0), ('red',        1.0),
            ('green',      1.0), ('blue',     1.0), ('blur',       0.0),
            ('sharpen',    0.0), ('b&w',      0.0), ('invert',     0.0),
        ]
        for name, value in sliders:
            slider    = getattr(self, f"{name}_slider",    None)
            entry     = getattr(self, f"{name}_entry",     None)
            pill_draw = getattr(self, f"{name}_pill_draw", None)
            if slider:
                slider.set(value)
            if entry:
                entry.delete(0, tk.END)
                entry.insert(0, f"{value:.1f}")
            if pill_draw:
                pill_draw(f"{value:.1f}")
    
    def save_image(self):
        if self.current_image:
            save_filename = filedialog.asksaveasfilename(defaultextension=".png",
                                                        filetypes=(("PNG files", "*.png"),("PDF files", "*.pdf"),("WebP files", "*.webp"),("Gif files", "*.gif"),
                                                                   ("JPEG files", "*.jpg *.jpeg"),
                                                                   ("All files", "*.*")))
            if save_filename:
                try:
                    self.current_image.save(save_filename)
                    self.status_bar.config(text=f"Image saved as: {save_filename}")
                except Exception as e:
                    self.status_bar.config(text=f"Error saving image: {str(e)}")
    
    def reset_image(self):
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.layers = [self.current_image.copy()]
            self.current_layer = 0
            self.display_image()
            self.reset_sliders()
            self.status_bar.config(text="Image reset to original")
    
    # ── Zoom & pan ───────────────────────────────────────────────────────────
    def _on_canvas_scroll(self, event):
        """Zoom in/out centred on the mouse pointer."""
        if not self.current_image:
            return
        factor = 1.1 if event.delta > 0 else 0.9
        new_zoom = max(self._zoom_min, min(self._zoom_max, self._zoom * factor))

        # Keep the pixel under the cursor stationary
        mx, my = event.x, event.y
        self._pan_x = mx - (mx - self._pan_x) * (new_zoom / self._zoom)
        self._pan_y = my - (my - self._pan_y) * (new_zoom / self._zoom)

        self._zoom = new_zoom
        self._zoom_slider.set(round(self._zoom, 2))
        self._zoom_pill_draw(f"{int(self._zoom * 100)}%")
        self._render_zoom()

    def _on_zoom_slider(self, val):
        """Sync zoom when the bottom slider is dragged."""
        if not self.current_image:
            return
        new_zoom = float(val)
        cw = self.canvas.winfo_width()  or 800
        ch = self.canvas.winfo_height() or 600
        # Scale around canvas centre
        cx, cy = cw / 2, ch / 2
        self._pan_x = cx - (cx - self._pan_x) * (new_zoom / self._zoom)
        self._pan_y = cy - (cy - self._pan_y) * (new_zoom / self._zoom)
        self._zoom = new_zoom
        self._zoom_pill_draw(f"{int(self._zoom * 100)}%")
        self._render_zoom()

    def _pan_start(self, event):
        self._panning     = True
        self._pan_start_x = event.x - self._pan_x
        self._pan_start_y = event.y - self._pan_y
        self.canvas.config(cursor="fleur")

    def _pan_move(self, event):
        if self._panning and self.current_image:
            self._pan_x = event.x - self._pan_start_x
            self._pan_y = event.y - self._pan_start_y
            self._render_zoom()

    def _pan_end(self, event):
        self._panning = False
        self.canvas.config(cursor="hand2")

    def _render_zoom(self):
        """Render the current image at self._zoom, offset by pan."""
        if not self.current_image:
            return
        cw = self.canvas.winfo_width()  or 800
        ch = self.canvas.winfo_height() or 600

        iw, ih = self.current_image.size
        new_w = max(1, int(iw * self._zoom))
        new_h = max(1, int(ih * self._zoom))

        resized = self.current_image.resize((new_w, new_h), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)

        cx = self._pan_x + new_w / 2
        cy = self._pan_y + new_h / 2

        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, cw, ch))
        self.canvas.create_image(cx, cy, image=self.tk_image, anchor="center")

    def display_image(self):
        """Called after adjustments — fits image on first load, preserves zoom on edits."""
        if not self.current_image:
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if self._fit_pending:
            # Canvas not ready yet — defer until it's laid out
            if cw <= 1 or ch <= 1:
                self.root.after(30, self.display_image)
                return
            # Canvas is ready — compute fit zoom
            iw, ih = self.current_image.size
            fit_zoom = min(cw / iw, ch / ih)   # fit whole image, allow upscale for small images
            self._zoom  = fit_zoom
            self._pan_x = (cw - iw * fit_zoom) / 2
            self._pan_y = (ch - ih * fit_zoom) / 2
            self._zoom_slider.set(round(self._zoom, 2))
            self._zoom_pill_draw(f"{int(self._zoom * 100)}%")
            self._fit_pending = False

        self._render_zoom()
    
    def adjust_brightness(self, value):
        if self.original_image:
            value = float(value)
            getattr(self, "brightness_entry", None).delete(0, tk.END)
            getattr(self, "brightness_entry", None).insert(0, str(value))
            self.apply_all_adjustments()
            self.status_bar.config(text=f"Brightness: {value:.1f}")
    
    def adjust_contrast(self, value):
        if self.original_image:
            value = float(value)
            getattr(self, "contrast_entry", None).delete(0, tk.END)
            getattr(self, "contrast_entry", None).insert(0, str(value))
            self.apply_all_adjustments()
            self.status_bar.config(text=f"Contrast: {value:.1f}")
    
    def adjust_saturation(self, value):
        if self.original_image:
            value = float(value)
            getattr(self, "saturation_entry", None).delete(0, tk.END)
            getattr(self, "saturation_entry", None).insert(0, str(value))
            self.apply_all_adjustments()
            self.status_bar.config(text=f"Saturation: {value:.1f}")
    
    def adjust_vibrancy(self, value):
        if self.original_image:
            value = float(value)
            getattr(self, "vibrancy_entry", None).delete(0, tk.END)
            getattr(self, "vibrancy_entry", None).insert(0, str(value))
            self.apply_all_adjustments()
            self.status_bar.config(text=f"Vibrancy: {value:.1f}")
    
    def adjust_texture(self, value):
        if self.original_image:
            value = float(value)
            getattr(self, "texture_entry", None).delete(0, tk.END)
            getattr(self, "texture_entry", None).insert(0, str(value))
            
            # Texture adjustment (simulated with sharpness and grain)
            self.apply_all_adjustments()
            self.status_bar.config(text=f"Texture: {value:.1f}")
    
    def adjust_colors(self, value):
        if self.original_image:
            self.apply_all_adjustments()
            self.status_bar.config(text="Color adjustments applied")
    
    def apply_all_adjustments(self):
        if not self.original_image:
            return
            
        # Start with original image
        img = self.original_image.copy()
        
        # Apply basic adjustments
        brightness = float(getattr(self, "brightness_slider", None).get())
        contrast = float(getattr(self, "contrast_slider", None).get())
        saturation = float(getattr(self, "saturation_slider", None).get())
        vibrancy = float(getattr(self, "vibrancy_slider", None).get())
        
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img = ImageEnhance.Color(img).enhance(saturation)
        
        # Apply vibrancy (simulated with additional saturation for vibrant colors)
        if vibrancy != 1.0:
            hsv = img.convert('HSV')
            h, s, v = hsv.split()
            s = s.point(lambda x: min(255, x * vibrancy))
            img = Image.merge('HSV', (h, s, v)).convert('RGB')
        
        # Apply color adjustments (ROYGBIV)
        color_adjustments = {
            'red': float(getattr(self, "red_slider", None).get()),
            
     
            'green': float(getattr(self, "green_slider", None).get()),
            'blue': float(getattr(self, "blue_slider", None).get()),
        }
        
        if any(v != 1.0 for v in color_adjustments.values()):
            img = self.adjust_individual_colors(img, color_adjustments)
        
        # Apply texture
        texture = float(getattr(self, "texture_slider", None).get())
        if texture != 1.0:
            if texture > 1.0:
                # Sharpen effect
                img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=int((texture-1)*100), threshold=3))
            else:
                # Smooth effect
                img = img.filter(ImageFilter.GaussianBlur(radius=(1-texture)*2))
        
        # Apply Blur
        blur = float(getattr(self, "blur_slider", None).get())
        if blur > 0.0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur))

        # Apply Sharpen
        sharpen = float(getattr(self, "sharpen_slider", None).get())
        if sharpen > 0.0:
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=int(sharpen * 50), threshold=3))

        # Apply B&W (blend grayscale over original based on slider)
        bw = float(getattr(self, "b&w_slider", None).get())
        if bw > 0.0:
            gray = ImageOps.grayscale(img).convert("RGB")
            img = Image.blend(img, gray, alpha=bw)

        # Apply Invert (blend inverted over original based on slider)
        invert = float(getattr(self, "invert_slider", None).get())
        if invert > 0.0:
            inverted = ImageOps.invert(img)
            img = Image.blend(img, inverted, alpha=invert)

        # Update current image
        self.current_image = img
        self.display_image()
        self._push_history()
    
    def adjust_individual_colors(self, img, adjustments):
        """Adjust individual color channels based on the adjustments dictionary"""
        # Convert to numpy array for faster processing
        arr = np.array(img)
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        
        # Define color ranges (approximate)
        # Red
        if adjustments['red'] != 1.0:
            red_mask = (r > 120) & (g < 100) & (b < 100)
            r[red_mask] = np.clip(r[red_mask] * adjustments['red'], 0, 255)
        
        
        # Green
        if adjustments['green'] != 1.0:
            green_mask = (g > 100) & (r < g) & (b < g)
            g[green_mask] = np.clip(g[green_mask] * adjustments['green'], 0, 255)
        
        # Blue
        if adjustments['blue'] != 1.0:
            blue_mask = (b > 100) & (r < b) & (g < b)
            b[blue_mask] = np.clip(b[blue_mask] * adjustments['blue'], 0, 255)
        
        
        return Image.fromarray(np.clip(np.stack([r, g, b], axis=2), 0, 255))
    
    def apply_blur(self, value):
        if self.original_image:
            value = float(value)
            getattr(self, "blur_entry", None).delete(0, tk.END)
            getattr(self, "blur_entry", None).insert(0, str(value))
            self.apply_all_adjustments()
            self.status_bar.config(text=f"Blur: {value:.1f}")

    def apply_sharpen(self, value):
        if self.original_image:
            value = float(value)
            getattr(self, "sharpen_entry", None).delete(0, tk.END)
            getattr(self, "sharpen_entry", None).insert(0, str(value))
            self.apply_all_adjustments()
            self.status_bar.config(text=f"Sharpen: {value:.1f}")

    def convert_bw(self, value):
        if self.original_image:
            value = float(value)
            getattr(self, "b&w_entry", None).delete(0, tk.END)
            getattr(self, "b&w_entry", None).insert(0, str(value))
            self.apply_all_adjustments()
            self.status_bar.config(text=f"B&W: {value:.1f}")

    def invert_colors(self, value):
        if self.original_image:
            value = float(value)
            getattr(self, "invert_entry", None).delete(0, tk.END)
            getattr(self, "invert_entry", None).insert(0, str(value))
            self.apply_all_adjustments()
            self.status_bar.config(text=f"Invert: {value:.1f}")
    
    
    
    # ── Undo / Redo ──────────────────────────────────────────────────────────

    SLIDER_NAMES = [
        ('brightness', 1.0), ('contrast', 1.0), ('saturation', 1.0),
        ('vibrancy', 1.0),   ('texture', 1.0),  ('red', 1.0),
        ('green', 1.0),      ('blue', 1.0),      ('blur', 0.0),
        ('sharpen', 0.0),    ('b&w', 0.0),       ('invert', 0.0),
    ]

    def _get_slider_state(self):
        """Capture current values of all sliders into a dict."""
        return {name: float(getattr(self, f"{name}_slider").get())
                for name, _ in self.SLIDER_NAMES
                if getattr(self, f"{name}_slider", None)}

    def _restore_slider_state(self, state):
        """Silently restore all sliders to a saved state and re-render."""
        self._is_undoing = True
        for name, default in self.SLIDER_NAMES:
            slider    = getattr(self, f"{name}_slider",    None)
            entry     = getattr(self, f"{name}_entry",     None)
            pill_draw = getattr(self, f"{name}_pill_draw", None)
            value     = state.get(name, default)
            if slider:
                slider.set(value)
            if entry:
                entry.delete(0, tk.END)
                entry.insert(0, str(round(value, 1)))
            if pill_draw:
                pill_draw(f"{round(value, 1):.1f}")
        self._is_undoing = False
        self.apply_all_adjustments()

    def _push_history(self):
        """Push current slider state onto the undo stack."""
        if self._is_undoing:
            return
        state = self._get_slider_state()
        # Avoid duplicate consecutive entries
        if self._history and self._history[-1] == state:
            return
        self._history.append(state)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        # Any new action clears redo
        self._redo_stack.clear()
        self._update_undo_redo_buttons()

    def undo(self):
        """Restore previous slider state (Ctrl+Z)."""
        if not self.original_image or len(self._history) < 2:
            return
        # Push current state onto redo stack before undoing
        self._redo_stack.append(self._history.pop())
        self._restore_slider_state(self._history[-1])
        self._update_undo_redo_buttons()
        self.status_bar.config(text=f"Undo  ({len(self._history)} steps left)")

    def redo(self):
        """Re-apply undone slider state (Ctrl+Y)."""
        if not self._redo_stack:
            return
        state = self._redo_stack.pop()
        self._history.append(state)
        self._restore_slider_state(state)
        self._update_undo_redo_buttons()
        self.status_bar.config(text=f"Redo  ({len(self._redo_stack)} steps ahead)")

    def _update_undo_redo_buttons(self):
        """Enable / disable the toolbar buttons based on stack sizes."""
        self.undo_btn.config_btn(state=tk.NORMAL if len(self._history) >= 2 else tk.DISABLED)
        self.redo_btn.config_btn(state=tk.NORMAL if self._redo_stack else tk.DISABLED)

    # ─────────────────────────────────────────────────────────────────────────

    def create_layer(self):
        if self.current_image:
            new_layer = self.current_image.copy()
            self.layers.append(new_layer)
            self.current_layer = len(self.layers) - 1
            self.status_bar.config(text=f"Created new layer ({self.current_layer + 1}/{len(self.layers)})")
    
    def apply_mask(self):
        if len(self.layers) > 1 and self.current_layer > 0:
            # Simple masking - blend current layer with previous one
            mask = Image.new("L", self.layers[self.current_layer].size, 128)  # 50% opacity
            self.layers[self.current_layer - 1] = Image.composite(
                self.layers[self.current_layer],
                self.layers[self.current_layer - 1],
                mask
            )
            self.layers.pop(self.current_layer)
            self.current_layer = max(0, self.current_layer - 1)
            self.current_image = self.layers[self.current_layer].copy()
            self.display_image()
            self.status_bar.config(text=f"Applied mask (Layers: {len(self.layers)})")
    
    def clear_mask(self):
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.layers = [self.current_image.copy()]
            self.current_layer = 0
            self.display_image()
            self.reset_sliders()
            self.status_bar.config(text="Cleared all layers and masks")

# Main application
if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myapp.uniqueid")
    root = tk.Tk()
    app = SimplePhotoEditor(root)
    icon = ImageTk.PhotoImage(Image.open(resource_path("Icon.png")))
    root.iconphoto(True, icon)
    root.mainloop()