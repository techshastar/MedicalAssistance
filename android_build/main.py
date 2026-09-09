"""
main.py (ANDROID / Kivy) — Medicine Assistant APK v0.5
======================================================
Professional health-suite UI (teal + mint theme), SIH build.

New in v0.5:
  * Home dashboard: greeting, dose status pill, suggestion search bar,
    upcoming dose card (Take Now / Snooze), quick actions grid,
    bottom navigation + Add/Scan button
  * Medicine Cabinet: quantity, dosage, expiry, storage place per medicine
  * Reminders: daily dose times per family member, SPOKEN voice reminders
    while the app is open (Take Now / Snooze 15m)
  * Family Care: manage whose medicines you look after
  * Expiry dashboard: active / expiring soon / expired, with voice summary
  * Authenticity checklist + Storage guide (education only)
  * Explanation levels on the details page: simple / normal / detailed
  * Voice search (Android SpeechRecognizer, graceful fallback)
  * Dark mode, user name, language — saved locally on-device

Same honest backend: 100% offline, no accounts, no tracking, photos
never stored, and the app NEVER guesses medicines.
"""

import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse, Line
from kivy.graphics import PushMatrix, PopMatrix, Scale

# =====================================================================
# Platform detection (jnius bridges exist only inside the real APK)
# =====================================================================
IS_ANDROID = False
try:
    from kivy.utils import platform as _kivy_platform
    IS_ANDROID = _kivy_platform == "android"
except Exception:
    pass

_JNI_OK = False
if IS_ANDROID:
    try:
        from jnius import autoclass, PythonJavaClass, java_method  # noqa
        from android import activity as _android_activity          # noqa
        _JNI_OK = True
    except Exception:
        _JNI_OK = False

# Runtime mic permission helper (p4a provides this on-device only)
_PERMISSIONS_OK = False
if IS_ANDROID:
    try:
        from android.permissions import request_permissions, Permission  # noqa
        _PERMISSIONS_OK = True
    except Exception:
        _PERMISSIONS_OK = False

# =====================================================================
# Font: one file that covers Latin + Devanagari (bundled in APK)
# =====================================================================
FONT = "Roboto"
try:
    _f = os.path.join(os.path.dirname(__file__), "assets", "Lohit-Devanagari.ttf")
    if os.path.isfile(_f):
        LabelBase.register(name="LohitDev", fn_regular=_f, fn_bold=_f,
                           fn_italic=_f, fn_bolditalic=_f)
        FONT = "LohitDev"
except Exception:
    pass

# =====================================================================
# Backend (pure python, shared with desktop)
# =====================================================================
import database.database as db_module
from database.database import get_connection, initialize_database, fetch_all_medicines
from database.seed_data import seed_demo_data
from database import database as db
from medicine.search import search_medicines, find_medicines_in_ocr_text, EXACT
from medicine.information import (format_details_page,
                                  format_packaging_info_section,
                                  format_age_suitability,
                                  format_storage_card,
                                  format_authenticity_checklist,
                                  build_spoken_summary,
                                  build_reminder_spoken,
                                  build_cabinet_spoken_summary)
from utils.languages import t, EN, HI
from utils.date_utils import extract_packaging_info
from utils.suggestions import get_suggestions

# =====================================================================
# PALETTES - teal health theme (light + dark)
# =====================================================================
_LIGHT = {
    "bg":          (0.937, 0.965, 0.969, 1),   # #EFF7F7 app background
    "card":        (1, 1, 1, 1),
    "primary":     (0.043, 0.361, 0.388, 1),   # #0B5C63 dark teal
    "primary_dk":  (0.031, 0.267, 0.290, 1),
    "mint":        (0.725, 0.910, 0.847, 1),   # #B9E8D8 mint
    "mint_soft":   (0.870, 0.953, 0.925, 1),
    "teal_soft":   (0.839, 0.925, 0.929, 1),   # soft teal (search bar etc)
    "ink":         (0.055, 0.086, 0.094, 1),
    "muted":       (0.380, 0.478, 0.490, 1),
    "warn":        (0.83, 0.48, 0.03, 1),
    "warn_soft":   (0.996, 0.945, 0.780, 1),
    "danger":      (0.80, 0.16, 0.16, 1),
    "danger_soft": (0.992, 0.898, 0.898, 1),
    "ok":          (0.10, 0.55, 0.36, 1),
    "ok_soft":     (0.878, 0.957, 0.918, 1),
    "border":      (0.796, 0.878, 0.882, 1),
    "white":       (1, 1, 1, 1),
    "track":       (0.878, 0.906, 0.910, 1),
    "nav":         (1, 1, 1, 1),
}
_DARK = {
    "bg":          (0.059, 0.086, 0.094, 1),
    "card":        (0.098, 0.137, 0.145, 1),
    "primary":     (0.302, 0.749, 0.741, 1),
    "primary_dk":  (0.725, 0.910, 0.847, 1),
    "mint":        (0.180, 0.322, 0.286, 1),
    "mint_soft":   (0.137, 0.239, 0.220, 1),
    "teal_soft":   (0.125, 0.192, 0.200, 1),
    "ink":         (0.909, 0.945, 0.941, 1),
    "muted":       (0.560, 0.639, 0.643, 1),
    "warn":        (0.93, 0.63, 0.25, 1),
    "warn_soft":   (0.25, 0.20, 0.10, 1),
    "danger":      (0.94, 0.45, 0.45, 1),
    "danger_soft": (0.30, 0.13, 0.13, 1),
    "ok":          (0.45, 0.82, 0.62, 1),
    "ok_soft":     (0.12, 0.22, 0.17, 1),
    "border":      (0.208, 0.286, 0.294, 1),
    "white":       (0.98, 0.99, 0.99, 1),
    "track":       (0.188, 0.259, 0.267, 1),
    "nav":         (0.078, 0.114, 0.122, 1),
}
PAL = dict(_LIGHT)


def apply_theme(dark: bool):
    """Switch the live palette; screens re-read PAL on refresh()."""
    PAL.clear()
    PAL.update(_DARK if dark else _LIGHT)
    Window.clearcolor = PAL["bg"]


def _darken(rgba, k=0.85):
    return (rgba[0] * k, rgba[1] * k, rgba[2] * k, rgba[3])


RESULT_OK = -1
_PICK_IMAGE_REQUEST = 9101
APP_VERSION = "v0.5"


# =====================================================================
# Small drawing helpers + custom widgets
# =====================================================================
def txt(s, fs=13, color=None, bold=False, wrap=False, halign="left",
        valign="middle", **kw):
    """Themed label. fs = font size; wrap=True wraps text to widget width.

    text_size is ALWAYS tied to the widget width so `halign` really works
    (Kivy ignores halign without text_size). Single-line labels shorten with
    an ellipsis instead of spilling out of their box.
    """
    color = color or PAL["ink"]
    lbl = Label(text=s, font_size=dp(fs * 1.22), color=color, bold=bold,
                font_name=FONT, halign=halign, valign=valign, **kw)
    if not wrap:
        lbl.shorten = True
        lbl.shorten_from = "right"
    lbl.bind(width=lambda w, v: setattr(lbl, "text_size", (v, None)))
    return lbl


def chip(text, fg, bg, height=None):
    """Small rounded pill with a status word."""
    h = height or dp(30)
    box = BoxLayout(size_hint=(None, None), height=h, padding=(dp(12), 0))
    l = Label(text=text, font_size=dp(12), color=fg, bold=True, font_name=FONT,
              size_hint=(None, None), height=h - dp(4))
    l.bind(texture_size=lambda _l, s: setattr(box, "width", s[0] + dp(22)))
    l.bind(texture_size=lambda _l, s: setattr(l, "width", s[0]))
    box.add_widget(l)
    with box.canvas.before:
        Color(rgba=bg)
        rr = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(13)])
    box.bind(pos=lambda w, _v: setattr(rr, "pos", w.pos),
             size=lambda w, _v: setattr(rr, "size", w.size))
    return box


class RoundedButton(Button):
    """Canvas-drawn rounded button (replaces ugly default Kivy texture)."""

    def __init__(self, text, bg=None, fg=None, radius=15, fs=14, bold=True,
                 border=None, **kw):
        self._bg = bg if bg is not None else PAL["primary"]
        self._border = border
        super().__init__(text=text, font_name=FONT, font_size=dp(fs * 1.15),
                         color=fg if fg is not None else PAL["white"],
                         bold=bold, **kw)
        self.background_normal = ""
        self.background_down = ""
        self.background_disabled_normal = ""
        self.background_disabled_down = ""
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self._c = Color(rgba=self._shown_bg())
            self._rr = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[dp(radius)])
            if self._border:
                Color(rgba=self._border)
                self._ln = Line(rounded_rectangle=(
                    self.x, self.y, self.width, self.height, dp(radius)), width=1.2)
            else:
                self._ln = None
        self.bind(pos=self._sync, size=self._sync,
                  state=lambda *_: self._repaint(),
                  disabled=lambda *_: self._repaint())

    def _shown_bg(self):
        if self.disabled:
            return PAL["track"]
        return _darken(self._bg, 0.88) if self.state == "down" else self._bg

    def _repaint(self):
        self._c.rgba = self._shown_bg()
        if self.disabled:
            self.color = PAL["muted"]

    def _sync(self, *_):
        self._rr.pos, self._rr.size = self.pos, self.size
        if self._ln:
            self._ln.rounded_rectangle = (self.x, self.y, self.width,
                                          self.height, dp(15))


class Card(BoxLayout):
    """White rounded card with soft border."""

    def __init__(self, radius=16, **kw):
        super().__init__(**kw)
        self._radius = radius
        with self.canvas.before:
            Color(rgba=PAL["card"])
            self._rr = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[dp(radius)])
            Color(rgba=PAL["border"])
            self._ln = Line(rounded_rectangle=(
                self.x, self.y, self.width, self.height, dp(radius)), width=1.1)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._rr.pos, self._rr.size = self.pos, self.size
        self._ln.rounded_rectangle = (self.x, self.y, self.width,
                                      self.height, dp(self._radius))

    def repaint(self):
        """Cards are always rebuilt by refresh(), so a live repaint of the
        same widget is never needed - update the rect in place if called."""
        self._rr.pos, self._rr.size = self.pos, self.size


class TintCard(Card):
    """A Card with an explicit background colour (no / custom border)."""

    def __init__(self, bg=None, radius=16, border=None, **kw):
        self._bg = bg if bg is not None else PAL["card"]
        self._border_c = border
        super().__init__(radius=radius, **kw)
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self._bg)
            self._rr = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[dp(radius)])
            if self._border_c:
                Color(rgba=self._border_c)
                self._ln = Line(rounded_rectangle=(
                    self.x, self.y, self.width, self.height, dp(radius)),
                    width=1.3)
            else:
                self._ln = None

    def _sync(self, *_):
        self._rr.pos, self._rr.size = self.pos, self.size
        if self._ln:
            self._ln.rounded_rectangle = (self.x, self.y, self.width,
                                          self.height, dp(self._radius))


class CardButton(ButtonBehavior, Card):
    """A card you can tap."""

    def __init__(self, text=None, **kw):
        super().__init__(**kw)


class Avatar(RelativeLayout):
    """Circle with a letter (user avatar, mint).

    Same canvas-safe pattern as Icon: the circle is drawn ONCE for a virtual
    100x100 box (canvas.before, local coords) and a Scale instruction tracks
    size changes; the letter Label fills the widget and centres its text via
    text_size. We never clear canvas.before once the widget is in the tree.
    """

    def __init__(self, letter="M", size=dp(40), bg=None, fg=None, **kw):
        super().__init__(size_hint=(None, None), size=(size, size), **kw)
        self.letter = (letter or "M").strip()[:1].upper() or "M"
        self._bg = bg if bg is not None else PAL["mint"]
        self._fg = fg if fg is not None else PAL["primary"]
        with self.canvas.before:
            PushMatrix()
            self._sc = Scale(1.0, 1.0, 1.0)
            Color(rgba=self._bg)
            Ellipse(pos=(0, 0), size=(100.0, 100.0))
            PopMatrix()
        self.lab = Label(text=self.letter, font_name=FONT, bold=True,
                         color=self._fg, halign="center", valign="middle")
        self.add_widget(self.lab)
        self.bind(size=self._sync)
        self._sync()

    def set_letter(self, letter):
        self.letter = (letter or "M").strip()[:1].upper() or "M"
        self.lab.text = self.letter

    def _sync(self, *_):
        s = min(self.width, self.height) / 100.0
        self._sc.x = self._sc.y = s
        self.lab.size = self.size
        self.lab.pos = (0, 0)
        self.lab.text_size = self.size
        self.lab.font_size = self.height * 0.42


class Icon(RelativeLayout):
    """Tiny vector icons drawn with shapes (no emoji/images needed).

    NOTE (canvas-safe pattern): RelativeLayout translates our canvas when the
    widget MOVES, and a Scale instruction handles SIZE changes. Shapes are
    drawn ONCE for a virtual 100x100 box (local coords) and then we only ever
    update `self._sc.x/.y` in-place. We NEVER clear canvas.before after the
    widget is in the tree - that corrupts Kivy's GL state stack (crash).
    """

    _VBOX = 100.0   # virtual drawing box (icons scale to real size)

    def __init__(self, kind, color=None, **kw):
        self.kind = kind
        self.color = color or PAL["primary"]
        self._built = False
        super().__init__(**kw)
        self.bind(size=self._rescale)
        self._draw()

    def _rescale(self, *_):
        if self._built:
            s = min(self.width, self.height) / self._VBOX
            self._sc.x = self._sc.y = s

    def _draw(self, *_):
        if self._built:
            return
        self._built = True
        u = self._VBOX / 22.0
        cx = cy = self._VBOX / 2.0          # centre of the virtual 100x100 box
        C = self.color
        with self.canvas.before:
            PushMatrix()
            self._sc = Scale(1.0, 1.0, 1.0)
            Color(rgba=C)
            if self.kind == "search":
                r = 6.2 * u
                Line(circle=(cx - 0.4 * u, cy + 0.8 * u, r), width=1.5 * u)
                Line(points=[cx + 4.0 * u, cy - 3.6 * u,
                             cx + 7.4 * u, cy - 7.0 * u], width=1.5 * u)
            elif self.kind == "scan":
                L = 4.2 * u
                m = 7 * u
                Line(points=[cx - m, cy - m + L, cx - m, cy - m, cx - m + L, cy - m], width=1.6 * u)
                Line(points=[cx + m - L, cy - m, cx + m, cy - m, cx + m, cy - m + L], width=1.6 * u)
                Line(points=[cx + m, cy + m - L, cx + m, cy + m, cx + m - L, cy + m], width=1.6 * u)
                Line(points=[cx - m + L, cy + m, cx - m, cy + m, cx - m, cy + m - L], width=1.6 * u)
                Color(rgba=PAL["mint"])
                Line(points=[cx - 5 * u, cy, cx + 5 * u, cy], width=1.4 * u)
            elif self.kind == "clock":
                Line(circle=(cx, cy, 7.6 * u), width=1.5 * u)
                Line(points=[cx, cy, cx, cy + 4.4 * u], width=1.5 * u)
                Line(points=[cx, cy, cx + 3.2 * u, cy - 1.6 * u], width=1.5 * u)
            elif self.kind == "cross":
                RoundedRectangle(pos=(cx - 2.1 * u, cy - 6.2 * u),
                                 size=(4.2 * u, 12.4 * u), radius=[1.6 * u])
                RoundedRectangle(pos=(cx - 6.2 * u, cy - 2.1 * u),
                                 size=(12.4 * u, 4.2 * u), radius=[1.6 * u])
            elif self.kind == "bell":
                # dome: top arc of a circle (25deg..155deg), then side walls,
                # flared base, top knob and clapper. circle=(cx, cy, r, a0, a1)
                Line(circle=(cx, cy + 0.2 * u, 5.0 * u, 25, 155), width=1.6 * u)
                Line(points=[cx - 4.5 * u, cy + 2.3 * u,
                             cx - 5.8 * u, cy - 3.4 * u], width=1.6 * u)
                Line(points=[cx + 4.5 * u, cy + 2.3 * u,
                             cx + 5.8 * u, cy - 3.4 * u], width=1.6 * u)
                Line(points=[cx - 7.2 * u, cy - 3.6 * u,
                             cx + 7.2 * u, cy - 3.6 * u], width=1.7 * u)
                Line(points=[cx, cy + 5.4 * u, cx, cy + 7.0 * u], width=1.6 * u)
                Line(circle=(cx, cy - 5.3 * u, 1.4 * u), width=1.4 * u)
            elif self.kind == "home":
                Line(points=[cx - 7 * u, cy - 1 * u, cx, cy + 6.4 * u,
                             cx + 7 * u, cy - 1 * u], width=1.7 * u)
                Line(points=[cx - 4.6 * u, cy - 6 * u, cx - 4.6 * u, cy - 0.4 * u],
                     width=1.7 * u)
                Line(points=[cx + 4.6 * u, cy - 6 * u, cx + 4.6 * u, cy - 0.4 * u],
                     width=1.7 * u)
                Line(points=[cx - 4.6 * u, cy - 6 * u, cx + 4.6 * u, cy - 6 * u],
                     width=1.7 * u)
            elif self.kind == "cal":
                Line(rounded_rectangle=(cx - 6.5 * u, cy - 6 * u, 13 * u, 12 * u,
                                        2 * u), width=1.6 * u)
                Line(points=[cx - 6.5 * u, cy + 1.6 * u, cx + 6.5 * u, cy + 1.6 * u],
                     width=1.6 * u)
                Line(points=[cx - 3 * u, cy + 8 * u, cx - 3 * u, cy + 4 * u], width=1.6 * u)
                Line(points=[cx + 3 * u, cy + 8 * u, cx + 3 * u, cy + 4 * u], width=1.6 * u)
            elif self.kind == "person":
                Line(circle=(cx, cy + 3.2 * u, 3.4 * u), width=1.6 * u)
                Line(circle=(cx, cy - 5.4 * u, 5.6 * u, 15, 165), width=1.6 * u)
            elif self.kind == "mic":
                RoundedRectangle(pos=(cx - 2.6 * u, cy - 1 * u),
                                 size=(5.2 * u, 9 * u), radius=[2.6 * u],
                                 width=1.6 * u)
                Line(circle=(cx, cy - 0.6 * u, 5.0 * u, 200, 340), width=1.6 * u)
                Line(points=[cx, cy - 5 * u, cx, cy - 8 * u], width=1.6 * u)
                Line(points=[cx - 3 * u, cy - 8 * u, cx + 3 * u, cy - 8 * u],
                     width=1.6 * u)
            elif self.kind == "camera":
                Line(rounded_rectangle=(cx - 7 * u, cy - 5 * u, 14 * u, 10 * u,
                                        2 * u), width=1.6 * u)
                Line(points=[cx - 3 * u, cy + 5 * u, cx - 1.6 * u, cy + 7.2 * u,
                             cx + 1.6 * u, cy + 7.2 * u, cx + 3 * u, cy + 5 * u],
                     width=1.6 * u)
                Line(circle=(cx, cy, 3 * u), width=1.6 * u)
            elif self.kind == "box":
                Line(points=[cx - 7 * u, cy - 2 * u, cx - 7 * u, cy + 5 * u,
                             cx, cy + 8.4 * u, cx + 7 * u, cy + 5 * u,
                             cx + 7 * u, cy - 2 * u, cx, cy - 5.4 * u, cx - 7 * u, cy - 2 * u],
                     width=1.5 * u)
                Line(points=[cx - 7 * u, cy + 1 * u, cx, cy + 4.4 * u,
                             cx + 7 * u, cy + 1 * u], width=1.5 * u)
                Line(points=[cx, cy + 4.4 * u, cx, cy - 5.4 * u], width=1.5 * u)
            elif self.kind == "family":
                Line(circle=(cx - 3.6 * u, cy + 2.6 * u, 2.8 * u), width=1.5 * u)
                Line(circle=(cx + 3.6 * u, cy + 2.6 * u, 2.8 * u), width=1.5 * u)
                Line(circle=(cx - 3.8 * u, cy - 4.4 * u, 4.0 * u, 15, 165),
                     width=1.5 * u)
                Line(circle=(cx + 3.8 * u, cy - 4.4 * u, 4.0 * u, 15, 165),
                     width=1.5 * u)
            elif self.kind == "shield":
                Line(points=[cx, cy + 7 * u, cx + 6 * u, cy + 4.4 * u,
                             cx + 6 * u, cy - 2 * u, cx, cy - 7 * u,
                             cx - 6 * u, cy - 2 * u, cx - 6 * u, cy + 4.4 * u,
                             cx, cy + 7 * u], width=1.6 * u)
                Line(points=[cx - 2.6 * u, cy, cx - 0.4 * u, cy - 2.4 * u,
                             cx + 3 * u, cy + 2.6 * u], width=1.6 * u)
            elif self.kind == "shelf":
                Line(points=[cx - 7 * u, cy + 2 * u, cx + 7 * u, cy + 2 * u],
                     width=1.7 * u)
                Line(points=[cx - 7 * u, cy - 4.4 * u, cx + 7 * u, cy - 4.4 * u],
                     width=1.7 * u)
                RoundedRectangle(pos=(cx - 5.4 * u, cy + 2.8 * u),
                                 size=(4 * u, 4.6 * u), radius=[0.8 * u], width=1.4 * u)
                RoundedRectangle(pos=(cx + 1.4 * u, cy + 2.8 * u),
                                 size=(4 * u, 4.6 * u), radius=[0.8 * u], width=1.4 * u)
                RoundedRectangle(pos=(cx - 2 * u, cy - 3.8 * u),
                                 size=(4 * u, 4 * u), radius=[0.8 * u], width=1.4 * u)
            elif self.kind == "trash":
                Line(points=[cx - 4.4 * u, cy - 5.6 * u, cx - 4.4 * u, cy + 3.6 * u,
                             cx + 4.4 * u, cy + 3.6 * u, cx + 4.4 * u, cy - 5.6 * u],
                     width=1.5 * u)
                Line(points=[cx - 6 * u, cy + 3.6 * u, cx + 6 * u, cy + 3.6 * u],
                     width=1.5 * u)
                Line(points=[cx - 2 * u, cy + 5.6 * u, cx + 2 * u, cy + 5.6 * u],
                     width=1.5 * u)
            elif self.kind == "sunmoon":
                # simple sun: disc + 4 rays
                Line(circle=(cx, cy, 4.0 * u), width=1.6 * u)
                Line(points=[cx - 6.4 * u, cy, cx - 8.2 * u, cy], width=1.5 * u)
                Line(points=[cx + 6.4 * u, cy, cx + 8.2 * u, cy], width=1.5 * u)
                Line(points=[cx, cy - 6.4 * u, cx, cy - 8.2 * u], width=1.5 * u)
                Line(points=[cx, cy + 6.4 * u, cx, cy + 8.2 * u], width=1.5 * u)
            elif self.kind == "plus":
                Line(points=[cx - 5 * u, cy, cx + 5 * u, cy], width=2 * u)
                Line(points=[cx, cy - 5 * u, cx, cy + 5 * u], width=2 * u)
            elif self.kind == "check":
                Line(points=[cx - 5.4 * u, cy, cx - 1 * u, cy - 4.6 * u,
                             cx + 6 * u, cy + 4.8 * u], width=2 * u)
            elif self.kind == "snooze":
                Line(circle=(cx, cy - 1 * u, 6.4 * u), width=1.6 * u)
                Line(points=[cx, cy - 1 * u, cx, cy + 3 * u], width=1.6 * u)
                Line(points=[cx, cy - 1 * u, cx + 2.6 * u, cy - 2 * u], width=1.6 * u)
                Line(points=[cx + 4 * u, cy + 7 * u, cx + 7 * u, cy + 7 * u],
                     width=1.5 * u)
                Line(points=[cx + 4 * u, cy + 7 * u, cx + 7 * u, cy + 4 * u],
                     width=1.5 * u)
                Line(points=[cx + 4 * u, cy + 4 * u, cx + 7 * u, cy + 4 * u],
                     width=1.5 * u)
            PopMatrix()
        self._rescale()


class IconButton(ButtonBehavior, FloatLayout):
    """Tappable icon (mic / bell / camera / avatar). FloatLayout centres it."""

    def __init__(self, kind=None, color=None, size_wh=(44, 44), icon_wh=(24, 24),
                 custom=None, **kw):
        super().__init__(size_hint=(None, None), size=(dp(size_wh[0]), dp(size_wh[1])), **kw)
        if custom is not None:
            inner = custom
        else:
            inner = Icon(kind, color=color or PAL["primary"])
        inner.size_hint = (None, None)
        inner.size = (dp(icon_wh[0]), dp(icon_wh[1]))
        inner.pos_hint = {"center_x": .5, "center_y": .5}
        self.add_widget(inner)
        self.inner = inner


class _NavBtn(ButtonBehavior, BoxLayout):
    """One bottom-nav item (clickable layout, children positioned correctly)."""

    def __init__(self, **kw):
        super().__init__(orientation="vertical", spacing=0, **kw)


class _Dot(Widget):
    """Small status dot, drawn fresh each time (canvas-safe)."""

    def __init__(self, color, d=10, **kw):
        super().__init__(size_hint=(None, None), **kw)
        self.size = (dp(d), dp(d))
        self._c = color
        with self.canvas:
            Color(rgba=self._c)
            self._el = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._fix, size=self._fix)

    def _fix(self, *_):
        self._el.pos = (self.x, self.center_y - self.height / 2.0)
        self._el.size = self.size


class ScreenBase(Screen):
    """Screen with themed background."""

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self._bgc = Color(rgba=PAL["bg"])
            self._bgr = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, _v: setattr(self._bgr, "pos", w.pos),
                  size=lambda w, _v: setattr(self._bgr, "size", w.size))

    def repaint_bg(self):
        """Update bg colour in place (clearing canvas.before while the
        widget is in the tree corrupts Kivy's GL state stack - crash)."""
        self._bgc.rgba = PAL["bg"]
        self._bgr.pos, self._bgr.size = self.pos, self.size


class RoundedInput(TextInput):
    """Pill / rounded text field."""

    def __init__(self, radius=14, fill=None, **kw):
        self._radius = radius
        self._fill = fill
        super().__init__(**kw)
        self.background_normal = ""
        self.background_active = ""
        self.background_disabled_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.cursor_color = PAL["primary"]
        self.foreground_color = PAL["ink"]
        self.hint_text_color = PAL["muted"]
        self.font_name = FONT
        self.padding = [dp(16), dp(13)] if not self.multiline \
            else [dp(16), dp(12)]
        with self.canvas.before:
            Color(rgba=self._fill if self._fill else PAL["white"])
            self._rr = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[dp(radius)])
            Color(rgba=PAL["border"])
            self._ln = Line(rounded_rectangle=(
                self.x, self.y, self.width, self.height, dp(radius)), width=1.2)
            # IMPORTANT: the LAST Color in canvas.before leaks into Kivy's
            # TextInput text-shader state. Reset it to the text colour or
            # typed text renders washed-out (found during v0.5 testing).
            Color(rgba=self.foreground_color)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._rr.pos, self._rr.size = self.pos, self.size
        self._ln.rounded_rectangle = (self.x, self.y, self.width,
                                      self.height, dp(self._radius))


class TopBar(BoxLayout):
    """Home-style top bar: logo + app name + bell + avatar."""

    def __init__(self, app, **kw):
        super().__init__(orientation="horizontal", size_hint_y=None,
                         height=dp(64), padding=(dp(16), dp(12)),
                         spacing=dp(10), **kw)
        self.app = app
        logo = TintCard(bg=PAL["primary"], size_hint=(None, None),
                        size=(dp(40), dp(40)), radius=12)
        logo.add_widget(Icon("cross", color=PAL["mint"]))
        self.add_widget(logo)
        col = BoxLayout(orientation="vertical", spacing=0)
        col.add_widget(txt("Medicine Assistant", 15.5, PAL["ink"], True))
        col.add_widget(txt("OFFLINE  •  PRIVATE  •  FREE", 8,
                           PAL["muted"], False))
        self.add_widget(col)

        def _tap_icon(kind, size_wh, icon_wh, color, custom=None):
            b = IconButton(kind, color=color, size_wh=size_wh,
                           icon_wh=icon_wh, custom=custom)
            b.size_hint = (None, None)
            b.size = (dp(size_wh[0]), dp(size_wh[1]))
            return b

        self.bell = _tap_icon("bell", (42, 42), (26, 26), PAL["ink"])
        self.bell.bind(on_release=lambda *_: setattr(app.sm, "current", "reminders"))
        self.add_widget(self.bell)
        self.avatar_btn = _tap_icon(None, (42, 42), (34, 34), PAL["primary"],
                                    custom=Avatar(app.avatar_letter(), size=dp(34)))
        self.avatar_btn.bind(on_release=lambda *_: app.open_profile())
        self.add_widget(self.avatar_btn)

    def refresh_avatar(self):
        self.avatar_btn.inner.set_letter(self.app.avatar_letter())


class BackBar(BoxLayout):
    """Sub-screen bar: back button + title."""

    def __init__(self, app, title, back="home", **kw):
        super().__init__(orientation="horizontal", size_hint_y=None,
                         height=dp(60), padding=(dp(14), dp(10)),
                         spacing=dp(10), **kw)
        b = RoundedButton("‹ " + ("वापस" if app.language == HI else "Back"),
                          bg=PAL["teal_soft"], fg=PAL["primary"], fs=11.5,
                          size_hint=(None, None), size=(dp(84), dp(40)),
                          radius=20)
        b.bind(on_release=lambda *_: setattr(app.sm, "current", back))
        self.add_widget(b)
        self.add_widget(txt(title, 16, PAL["ink"], True))


class BottomNav(BoxLayout):
    """Bottom navigation: Home | History | Reminders | Profile."""

    def __init__(self, app, active="home", **kw):
        super().__init__(orientation="horizontal", size_hint_y=None,
                         height=dp(64), padding=(dp(8), dp(6)),
                         spacing=dp(4), **kw)
        self.app = app
        with self.canvas.before:
            Color(rgba=PAL["nav"])
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(rgba=PAL["border"])
            self._top = Line(points=[self.x, self.top, self.right, self.top],
                             width=1.1)
        self.bind(pos=self._paint, size=self._paint)
        lang = app.language
        items = [
            ("home", "home", t("nav_home", lang)),
            ("history", "cal", t("nav_history", lang)),
            ("reminders", "clock", t("nav_reminders", lang)),
            ("profile", "person", t("nav_profile", lang)),
        ]
        for target, kind, label in items:
            self.add_widget(self._item(target, kind, label, active == target))

    def _paint(self, *_):
        self._bg.pos, self._bg.size = self.pos, self.size
        self._top.points = [self.x, self.top, self.right, self.top]

    def _item(self, target, kind, label, selected):
        col = _NavBtn()
        ind = Widget(size_hint_y=None, height=dp(3))
        if selected:
            with ind.canvas:
                Color(rgba=PAL["primary"])
                _r = RoundedRectangle(pos=ind.pos, size=ind.size, radius=[dp(2)])
            ind.bind(pos=lambda w, _v: setattr(_r, "pos", w.pos),
                     size=lambda w, _v: setattr(_r, "size", w.size))
        col.add_widget(ind)
        col.add_widget(Icon(kind, color=PAL["primary"] if selected
                            else PAL["muted"], size_hint_y=None, height=dp(26)))
        col.add_widget(txt(label, 9,
                           PAL["primary"] if selected else PAL["muted"],
                           selected, halign="center",
                           size_hint_y=None, height=dp(16)))
        if target == "profile":
            col.bind(on_release=lambda *_: self.app.open_profile())
        else:
            col.bind(on_release=lambda *_: setattr(self.app.sm, "current",
                                                   target))
        return col


def text_card(title, body_text, title_color=None, body_color=None):
    """Auto-height card: bold title + wrapped body text."""
    c = Card(orientation="vertical", size_hint_y=None, spacing=dp(4),
             padding=(dp(14), dp(12)))
    t1 = txt(title, 13, title_color or PAL["primary"], True,
             size_hint_y=None, height=dp(22))
    t2 = txt(body_text, 11.5, body_color or PAL["ink"], wrap=True,
             size_hint_y=None)
    t2.bind(texture_size=lambda _l, s: setattr(t2, "height", s[1] + dp(6)))
    t2.bind(texture_size=lambda _l, s: setattr(
        c, "height", s[1] + dp(24) + dp(22) + dp(10)))
    c.add_widget(t1)
    c.add_widget(t2)
    return c


# =====================================================================
# ANDROID BRIDGE 1 - TextToSpeech (built-in, offline)
# =====================================================================
if _JNI_OK:

    class _TTSInitListener(PythonJavaClass):
        __javainterfaces__ = ["android/speech/tts/TextToSpeech$OnInitListener"]
        __javacontext__ = "app"

        def __init__(self, callback):
            super().__init__()
            self._callback = callback

        @java_method("(I)V")
        def onInit(self, status):
            if self._callback:
                self._callback(status)


class Speaker:
    """android.speech.tts.TextToSpeech wrapper (offline device voices)."""

    QUEUE_FLUSH = 0
    SUCCESS = 0

    def __init__(self, status_cb=None):
        self._status_cb = status_cb or (lambda *_: None)
        self._tts = None
        self._ready = False
        self._pending = None
        self._pending_fallback = None
        if not _JNI_OK:
            return
        try:
            TTS = autoclass("android.speech.tts.TextToSpeech")
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            self._tts = TTS(activity, _TTSInitListener(self._on_init))
        except Exception as exc:
            self._tts = None
            self._status_cb(f"TTS init error: {exc}")

    def _on_init(self, status):
        if status != self.SUCCESS:
            self._status_cb("TTS is phone par available nahi mila.")
            return
        self._ready = True
        if self._pending:
            text, lang = self._pending
            fallback = self._pending_fallback
            self._pending = self._pending_fallback = None
            outcome = self._speak_now(text, lang)
            if outcome == "fallback_en" and fallback:
                self._speak_now(fallback, EN)

    def _speak_now(self, text, lang):
        try:
            Locale = autoclass("java.util.Locale")
            loc = Locale("hi", "IN") if lang == HI else Locale("en", "US")
            result = self._tts.setLanguage(loc)
            if result < 0:
                if lang == HI:
                    self._status_cb(
                        "Hindi voice install nahi hai (Settings > Text-to-"
                        "speech). English me suna raha hoon.")
                    return "fallback_en"
                self._status_cb(
                    "Voice data nahi mila - Google Speech Services update/"
                    "voice data install karo, phir dobara try karo.")
                return None
            code = self._tts.speak(text, self.QUEUE_FLUSH,
                                   autoclass("android.os.Bundle")(),
                                   "medassist")
            if code != 0:
                self._status_cb(
                    "Voice engine error (code %s) - Google 'Speech Services'"
                    " app update karo, ya Settings > Text-to-speech check karo."
                    % code)
                return None
            return "ok"
        except Exception as exc:
            self._status_cb(f"TTS error: {exc}")
            return None

    def speak(self, text, lang, fallback_text=None, status_cb=None):
        if status_cb is not None:
            self._status_cb = status_cb
        if not text:
            return
        if not _JNI_OK or not self._tts:
            self._status_cb("Listen sirf Android app me chalta hai.")
            return
        if not self._ready:
            self._pending = (text, lang)
            self._pending_fallback = fallback_text
            return
        outcome = self._speak_now(text, lang)
        if outcome == "fallback_en" and fallback_text:
            self._speak_now(fallback_text, EN)

    def stop(self):
        if self._tts:
            try:
                self._tts.stop()
            except Exception:
                pass


# =====================================================================
# ANDROID BRIDGE 2 - on-device OCR via ML Kit (no cloud, no key)
# =====================================================================
if _JNI_OK:

    class _OcrSuccess(PythonJavaClass):
        __javainterfaces__ = ["com/google/android/gms/tasks/OnSuccessListener"]
        __javacontext__ = "app"

        def __init__(self, callback):
            super().__init__()
            self._callback = callback

        @java_method("(Ljava/lang/Object;)V")
        def onSuccess(self, result):
            try:
                text = result.getText() or ""
            except Exception:
                text = ""
            self._callback(text)

    class _OcrFailure(PythonJavaClass):
        __javainterfaces__ = ["com/google/android/gms/tasks/OnFailureListener"]
        __javacontext__ = "app"

        def __init__(self, callback):
            super().__init__()
            self._callback = callback

        @java_method("(Ljava/lang/Exception;)V")
        def onFailure(self, error):
            self._callback(str(error))


def decode_bitmap(uri, max_side=2000):
    """Uri -> Bitmap (down-scaled, memory only). Returns (bmp, error)."""
    try:
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        BitmapFactory = autoclass("android.graphics.BitmapFactory")
        Options = autoclass("android.graphics.BitmapFactory$Options")
        resolver = activity.getContentResolver()

        opts = Options()
        opts.inJustDecodeBounds = True
        stream = resolver.openInputStream(uri)
        BitmapFactory.decodeStream(stream, None, opts)
        stream.close()
        w, h = int(opts.outWidth), int(opts.outHeight)
        if w <= 0 or h <= 0:
            return None, "photo decode nahi hui"

        sample = 1
        while max(w, h) // (sample * 2) >= max_side:
            sample *= 2
        opts = Options()
        opts.inSampleSize = sample
        stream = resolver.openInputStream(uri)
        bmp = BitmapFactory.decodeStream(stream, None, opts)
        stream.close()
        if bmp is None:
            return None, "photo decode nahi hui"
        return bmp, None
    except Exception as exc:
        return None, str(exc)


def share_text(text, chooser_title="Share via"):
    """Open the Android share sheet with plain text. Returns True if opened."""
    if not _JNI_OK or not text:
        return False
    try:
        Intent = autoclass("android.content.Intent")
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        send = Intent()
        send.setAction(Intent.ACTION_SEND)
        send.putExtra(autoclass("android.content.Intent").EXTRA_TEXT, text)
        send.setType("text/plain")
        chooser = Intent.createChooser(send, chooser_title)
        activity.startActivity(chooser)
        return True
    except Exception:
        return False


def recognize_text(bitmap, on_success, on_error):
    """ML Kit Latin-script OCR, fully on-device."""
    try:
        InputImage = autoclass("com.google.mlkit.vision.common.InputImage")
        TextRecognition = autoclass(
            "com.google.mlkit.vision.text.TextRecognition")
        RecognizerOptions = autoclass(
            "com.google.mlkit.vision.text.latin.TextRecognizerOptions")
        recognizer = TextRecognition.getClient(
            RecognizerOptions.DEFAULT_OPTIONS)
        image = InputImage.fromBitmap(bitmap, 0)
        recognizer.process(image) \
            .addOnSuccessListener(_OcrSuccess(on_success)) \
            .addOnFailureListener(_OcrFailure(on_error))
        return True
    except Exception as exc:
        on_error(str(exc))
        return False


# =====================================================================
# ANDROID BRIDGE 3 - voice search (SpeechRecognizer), graceful fallback
# =====================================================================
if _JNI_OK:

    class _RecogListener(PythonJavaClass):
        __javainterfaces__ = ["android/speech/RecognitionListener"]
        __javacontext__ = "app"

        def __init__(self, on_result, on_error):
            super().__init__()
            self._on_result = on_result
            self._on_error = on_error

        @java_method("(Landroid/os/Bundle;)V")
        def onResults(self, results):
            try:
                matches = results.getStringArrayList(
                    "android.speech.extra.RESULTS")
                text = matches.get(0) if matches and matches.size() else ""
            except Exception:
                text = ""
            Clock.schedule_once(lambda _dt: self._on_result(text or ""), 0)

        @java_method("(I)V")
        def onError(self, error):
            Clock.schedule_once(lambda _dt: self._on_error(int(error)), 0)

        @java_method("(Landroid/os/Bundle;)V")
        def onPartialResults(self, bundle):
            pass

        @java_method("(Landroid/os/Bundle;)V")
        def onReadyForSpeech(self, params):
            pass

        @java_method("(F)V")
        def onRmsChanged(self, rmsdB):
            pass

        @java_method("(I)V")
        def onBeginningOfSpeech(self):
            pass

        @java_method("()V")
        def onEndOfSpeech(self):
            pass

        @java_method("(I)V")
        def onBufferReceived(self, buffer):
            pass

        @java_method("(ILandroid/os/Bundle;)V")
        def onEvent(self, eventType, params):
            pass


class VoiceSearch:
    """One-shot speech-to-text. Falls back to honest messages off-device."""

    def __init__(self):
        self._recognizer = None

    def available(self):
        if not (_JNI_OK and _PERMISSIONS_OK):
            return False
        try:
            SpeechRecognizer = autoclass("android.speech.SpeechRecognizer")
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            return bool(SpeechRecognizer.isRecognitionAvailable(activity))
        except Exception:
            return False

    def start(self, lang, on_result, on_error):
        if not self.available():
            on_error("unavailable")
            return

        def _permitted(granted):
            if not granted:
                on_error("permission")
                return
            Clock.schedule_once(
                lambda _dt: self._begin(lang, on_result, on_error), 0)

        try:
            request_permissions([Permission.RECORD_AUDIO],
                                lambda perms, grants: _permitted(
                                    all(grants) if grants else False))
        except Exception:
            Clock.schedule_once(
                lambda _dt: self._begin(lang, on_result, on_error), 0)

    def _begin(self, lang, on_result, on_error):
        try:
            SpeechRecognizer = autoclass("android.speech.SpeechRecognizer")
            RecognizerIntent = autoclass("android.speech.RecognizerIntent")
            Intent = autoclass("android.content.Intent")
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            self._recognizer = SpeechRecognizer.createSpeechRecognizer(activity)
            self._recognizer.setRecognitionListener(
                _RecogListener(on_result, on_error))
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                            RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE,
                            "hi-IN" if lang == HI else "en-IN")
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
            activity.runOnUiThread(
                _Runnable(lambda: self._recognizer.startListening(intent)))
        except Exception:
            on_error("unavailable")

    def stop(self):
        if not self._recognizer:
            return
        try:
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            activity.runOnUiThread(
                _Runnable(lambda: self._recognizer.stopListening()))
        except Exception:
            pass


if _JNI_OK:

    class _Runnable(PythonJavaClass):
        __javainterfaces__ = ["java/lang/Runnable"]
        __javacontext__ = "app"

        def __init__(self, fn):
            super().__init__()
            self._fn = fn

        @java_method("()V")
        def run(self):
            try:
                self._fn()
            except Exception:
                pass


# =====================================================================
# APP
# =====================================================================
class MedicineAssistantApp(App):
    def build(self):
        self.title = "Medicine Assistant"
        os.makedirs(self.user_data_dir, exist_ok=True)
        db_module.DB_PATH = os.path.join(self.user_data_dir,
                                         "medicine_database.db")
        self.conn = get_connection(db_module.DB_PATH)
        initialize_database(self.conn)
        seed_demo_data(self.conn)

        # ---- persisted settings (local only) ----
        self.language = db.get_setting(self.conn, "language", EN) or EN
        dark = db.get_setting(self.conn, "dark_mode", "0") == "1"
        self.dark_mode = dark
        apply_theme(dark)
        self.explain_lv = db.get_setting(self.conn, "explain_level",
                                         "normal") or "normal"

        self.speaker = None
        self.voice = VoiceSearch()
        self._due_spoken_today = set()       # (reminder_id, time) already spoken
        self._last_seen_minute = ""

        self.sm = ScreenManager(transition=FadeTransition(duration=0.16))
        self.home = HomeScreen(self, name="home")
        self.search = SearchScreen(self, name="search")
        self.scan = ScanScreen(self, name="scan")
        self.details = DetailsScreen(self, name="details")
        self.history = HistoryScreen(self, name="history")
        self.reminder_scr = RemindersScreen(self, name="reminders")
        self.cabinet = CabinetScreen(self, name="cabinet")
        self.expiry_scr = ExpiryScreen(self, name="expiry")
        self.family = FamilyScreen(self, name="family")
        self.auth_scr = AuthScreen(self, name="auth")
        self.storage_scr = StorageScreen(self, name="storage")
        self.about = AboutScreen(self, name="about")
        for s in (self.home, self.search, self.scan, self.details,
                  self.history, self.reminder_scr, self.cabinet,
                  self.expiry_scr, self.family, self.auth_scr,
                  self.storage_scr, self.about):
            self.sm.add_widget(s)

        self.profile_sheet = ProfileSheet(self)
        self.add_sheet = AddSheet(self)
        self._reminder_evt = Clock.schedule_interval(self._tick_reminders, 20)
        Clock.schedule_once(lambda _dt: self._tick_reminders(0), 2)
        return self.sm

    # ---------------- settings helpers ----------------
    def user_name(self):
        return db.get_setting(self.conn, "user_name", "") or ""

    def avatar_letter(self):
        name = self.user_name().strip()
        return name[:1].upper() if name else "+"

    def save_name(self, name):
        db.set_setting(self.conn, "user_name", name.strip())
        self.home.refresh_avatar()

    def save_language(self, code):
        self.language = code
        db.set_setting(self.conn, "language", code)
        for s in (self.home, self.search, self.scan, self.history,
                  self.reminder_scr, self.cabinet, self.expiry_scr,
                  self.family, self.auth_scr, self.storage_scr, self.about):
            s.refresh()
        if self.details.medicine is not None:
            self.details.show(self.details.medicine, self.details.match_type,
                              self.details.packaging)

    def toggle_dark(self, dark):
        self.dark_mode = bool(dark)
        db.set_setting(self.conn, "dark_mode", "1" if dark else "0")
        apply_theme(self.dark_mode)
        self.save_language(self.language)   # full themed refresh

    def save_explain_level(self, lv):
        self.explain_lv = lv
        db.set_setting(self.conn, "explain_level", lv)
        if self.details.medicine is not None:
            self.details.show(self.details.medicine, self.details.match_type,
                              self.details.packaging)

    # ---------------- audio ----------------
    def get_speaker(self):
        if self.speaker is None:
            self.speaker = Speaker()
        return self.speaker

    def speak(self, text, status_cb=None):
        lang = self.language
        self.get_speaker().speak(
            text, lang, fallback_text=None, status_cb=status_cb)

    def stop_speaking(self):
        if self.speaker:
            self.speaker.stop()

    # ---------------- navigation helpers ----------------
    def show_details(self, medicine, match_type, source="search",
                     packaging=None):
        expiry_status = None
        if packaging is not None and packaging.expiry_status():
            expiry_status = packaging.expiry_status().lower()
        db.add_history_entry(self.conn, medicine, match_type,
                             expiry_status, source)
        self.details.show(medicine, match_type, packaging)
        self.sm.current = "details"

    def open_profile(self):
        self.profile_sheet.refresh_ui()
        self.profile_sheet.open()

    def open_add(self):
        self.add_sheet.refresh_ui()
        self.add_sheet.open()

    def run_suggestion(self, action):
        """Suggestion lines under the home search bar (one tap)."""
        if action == "tell_my_medicines":
            self.sm.current = "cabinet"
            summary = db.cabinet_expiry_summary(self.conn)
            self.speak(build_cabinet_spoken_summary(summary, self.language))
        elif action == "check_expiry":
            self.expiry_scr.refresh()
            self.sm.current = "expiry"
            summary = db.cabinet_expiry_summary(self.conn)
            self.speak(build_cabinet_spoken_summary(summary, self.language))
        elif action == "storage_tips":
            self.storage_scr.refresh()
            self.sm.current = "storage"
        elif action == "add_medicine":
            self.open_add()
        elif action == "family_routine":
            self.sm.current = "reminders"

    # ---------------- reminder engine (voice, in-app) ----------------
    def _tick_reminders(self, _dt):
        """
        Every 20 s: find doses that became due since the last check and
        SPEAK them once (voice-assistant style). Also refreshes the home
        upcoming-dose card. Runs only while the app is open - honestly
        labelled that way in Settings.
        """
        from datetime import datetime
        due = self.find_due_slots(datetime.now())
        for reminder, hhmm in due:
            key = (reminder.id, hhmm)
            if key in self._due_spoken_today:
                continue
            self._due_spoken_today.add(key)
            text = build_reminder_spoken(reminder.member_name,
                                         reminder.medicine_name,
                                         reminder.strength, self.language)
            self.speak(text)
            break                        # speak one at a time
        # reset spoken-set at midnight
        today = datetime.now().strftime("%Y-%m-%d")
        if getattr(self, "_spoken_day", today) != today:
            self._due_spoken_today.clear()
            self._spoken_day = today
        if self.sm.current == "home":
            self.home.refresh_dose_card()

    def find_due_slots(self, now):
        """
        [(Reminder, 'HH:MM')] that are due right now:
        time reached, not taken today, and not snoozed past now.
        """
        from datetime import datetime, timedelta
        today = now.strftime("%Y-%m-%d")
        now_txt = now.strftime("%Y-%m-%d %H:%M")
        due = []
        for r in db.fetch_reminders(self.conn, active_only=True):
            for hhmm in r.times():
                try:
                    slot = datetime.strptime(f"{today} {hhmm}",
                                             "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                if slot > now:
                    continue
                if slot < now - timedelta(hours=6):
                    continue                # too old - do not nag
                log = db.get_dose_log(self.conn, r.id, today, hhmm)
                if log and log.status == "taken":
                    continue
                if log and log.status == "snoozed" and log.snooze_until \
                        and log.snooze_until > now_txt:
                    continue
                due.append((r, hhmm))
        due.sort(key=lambda pair: pair[1])
        return due

    def next_slot_today(self):
        """Next future (reminder, 'HH:MM') today, for the upcoming card."""
        from datetime import datetime
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        upcoming = []
        for r in db.fetch_reminders(self.conn, active_only=True):
            for hhmm in r.times():
                try:
                    from datetime import datetime as _dt
                    slot = _dt.strptime(f"{today} {hhmm}", "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                if slot > now:
                    upcoming.append((slot, r, hhmm))
        upcoming.sort(key=lambda x: x[0])
        return upcoming[0] if upcoming else None


# =====================================================================
# HOME dashboard
# =====================================================================
class HomeScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.refresh()

    # ---------------- build ----------------
    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        self.topbar = TopBar(app)
        root.add_widget(self.topbar)

        scroll = ScrollView()
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(8),
                                                          dp(16), dp(8)),
                         spacing=dp(12), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))
        scroll.add_widget(body)
        root.add_widget(scroll)
        root.add_widget(BottomNav(app, active="home"))
        self.add_widget(root)
        self._body = body

        # ---- greeting ----
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 12:
            greet = t("greet_morning", lang)
        elif hour < 17:
            greet = t("greet_afternoon", lang)
        else:
            greet = t("greet_evening", lang)
        name = app.user_name()
        if name:
            greet = f"{greet}, {name}"
        body.add_widget(txt(greet, 22, PAL["ink"], True, wrap=True,
                            size_hint_y=None, height=dp(40)))

        # ---- status pill: today's doses ----
        from datetime import datetime as _dt
        taken, scheduled = db.count_today_doses(
            app.conn, _dt.now().strftime("%Y-%m-%d"))
        if scheduled == 0:
            s_txt, s_icon, s_col = t("status_none", lang), "clock", PAL["muted"]
        elif taken >= scheduled:
            s_txt, s_icon, s_col = t("status_all_done", lang), "check", PAL["ok"]
        else:
            s_txt = t("status_progress", lang, taken=taken, total=scheduled)
            s_icon, s_col = "clock", PAL["warn"]
        pill = TintCard(bg=PAL["ok_soft"] if s_icon == "check" else PAL["mint_soft"],
                        radius=20, size_hint_y=None, height=dp(44),
                        padding=(dp(12), 0))
        prow = BoxLayout(orientation="horizontal", spacing=dp(8))
        prow.add_widget(Icon(s_icon, color=s_col, size_hint=(None, None),
                             size=(dp(22), dp(22))))
        prow.add_widget(txt(s_txt, 12, s_col, True))
        pill.add_widget(prow)
        body.add_widget(pill)

        # ---- search bar (search + mic + camera) ----
        bar = Card(radius=24, size_hint_y=None, height=dp(52),
                   padding=(dp(10), 0))
        srow = BoxLayout(orientation="horizontal", spacing=dp(6))
        srow.add_widget(Icon("search", color=PAL["muted"],
                             size_hint=(None, None), size=(dp(26), dp(26)),
                             pos_hint={"center_y": .5}))
        self.input = RoundedInput(
            hint_text=t("search_hint", lang), font_size=dp(14),
            multiline=False, fill=(0, 0, 0, 0), radius=1)
        self.input._ln.width = 0.0001
        self.input.bind(on_text_validate=lambda *_: self._go_search())
        srow.add_widget(self.input)
        mic = IconButton("mic", color=PAL["primary"], size_wh=(40, 40),
                         icon_wh=(24, 24), pos_hint={"center_y": .5})
        mic.bind(on_release=lambda *_: self._voice())
        srow.add_widget(mic)
        cam = IconButton("camera", color=PAL["primary"], size_wh=(40, 40),
                         icon_wh=(24, 24), pos_hint={"center_y": .5})
        cam.bind(on_release=lambda *_: setattr(app.sm, "current", "scan"))
        srow.add_widget(cam)
        bar.add_widget(srow)
        body.add_widget(bar)

        self.status_lbl = txt("", 10, PAL["muted"], wrap=True,
                              size_hint_y=None, height=dp(18))
        body.add_widget(self.status_lbl)

        # ---- suggestion lines (elder-friendly, one tap) ----
        sug_row = BoxLayout(orientation="vertical", spacing=dp(6),
                            size_hint_y=None)
        for action, line in get_suggestions(lang)[:3]:
            b = RoundedButton(line, bg=PAL["teal_soft"], fg=PAL["primary"],
                              fs=11.5, radius=18, size_hint_y=None,
                              height=dp(38), bold=False)
            b.bind(on_release=lambda _x, a=action: app.run_suggestion(a))
            sug_row.add_widget(b)
        sug_row.bind(minimum_height=sug_row.setter("height"))
        body.add_widget(sug_row)

        # ---- upcoming dose card ----
        self.dose_holder = BoxLayout(orientation="vertical", size_hint_y=None)
        self.dose_holder.bind(minimum_height=self.dose_holder.setter("height"))
        body.add_widget(self.dose_holder)
        self.refresh_dose_card()

        # ---- quick actions grid ----
        body.add_widget(txt(t("quick_actions", lang), 15, PAL["ink"], True,
                            size_hint_y=None, height=dp(26)))
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        acts = [
            ("scan", "camera", t("qa_scan", lang), t("qa_scan_sub", lang),
             t("on_device_ai", lang)),
            ("reminders", "bell", t("qa_reminders", lang),
             t("qa_rem_sub", lang,
               n=len(db.fetch_reminders(app.conn, active_only=True))), None),
            ("cabinet", "box", t("qa_cabinet", lang),
             t("qa_cab_sub", lang, n=len(db.fetch_cabinet(app.conn))), None),
            ("family", "family", t("qa_family", lang),
             t("qa_fam_sub", lang,
               n=len(db.fetch_family_members(app.conn))), None),
            ("auth", "shield", t("qa_auth", lang), t("qa_auth_sub", lang), None),
            ("storage", "shelf", t("qa_storage", lang),
             t("qa_storage_sub", lang), None),
        ]
        for target, kind, title, sub, ctag in acts:
            grid.add_widget(self._qa_card(target, kind, title, sub, ctag))
        grid.bind(minimum_height=grid.setter("height"))
        grid.height = dp(3 * 118)              # explicit: 3 rows of cards
        body.add_widget(grid)

        # ---- add / scan big button ----
        addb = RoundedButton("+  " + t("add_scan", lang), fs=15,
                             size_hint_y=None, height=dp(54), radius=27)
        addb.bind(on_release=lambda *_: app.open_add())
        body.add_widget(addb)

        body.add_widget(txt("Medicine Assistant  •  " + APP_VERSION
                            + "  •  100% offline", 9.5, PAL["muted"],
                            halign="center", size_hint_y=None,
                            height=dp(24)))

    # ---------------- pieces ----------------
    def _qa_card(self, target, kind, title, sub, ctag):
        card = CardButton(orientation="vertical", padding=(dp(12), dp(10)),
                          spacing=dp(3), size_hint_y=None, height=dp(118))
        row = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(30))
        row.add_widget(Icon(kind, color=PAL["primary"], size_hint=(None, None),
                            size=(dp(28), dp(28))))
        if ctag:
            row.add_widget(chip(ctag, PAL["primary"], PAL["mint_soft"],
                                height=dp(22)))
        card.add_widget(row)
        card.add_widget(txt(title, 13, PAL["ink"], True, size_hint_y=None,
                            height=dp(20)))
        card.add_widget(txt(sub, 9.5, PAL["muted"], wrap=True))
        card.bind(on_release=lambda *_: setattr(self.app.sm, "current", target))
        return card

    def refresh_dose_card(self):
        """Rebuild only the upcoming-dose card (called every 20 s)."""
        app, lang = self.app, self.app.language
        holder = self.dose_holder
        holder.clear_widgets()

        from datetime import datetime
        due = app.find_due_slots(datetime.now())

        if due:
            reminder, hhmm = due[0]
            label_txt = t("due_now", lang)
            time_txt = hhmm
        else:
            nxt = app.next_slot_today()
            if not nxt:
                card = TintCard(bg=PAL["teal_soft"], size_hint_y=None,
                                height=dp(64), padding=(dp(14), dp(8)))
                card.add_widget(txt(t("no_doses_today", lang), 11,
                                    PAL["muted"], wrap=True))
                holder.add_widget(card)
                return
            _slot, reminder, hhmm = nxt
            label_txt = t("upcoming_dose", lang)
            time_txt = hhmm

        card = Card(size_hint_y=None, orientation="vertical",
                    padding=(dp(14), dp(10)), spacing=dp(6))
        top = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(24))
        dot = Widget(size_hint=(None, None), size=(dp(10), dp(10)),
                     pos_hint={"center_y": .5})
        with dot.canvas:
            Color(rgba=PAL["primary"])
            _d = Ellipse(pos=dot.pos, size=dot.size)
        dot.bind(pos=lambda w, _v: setattr(_d, "pos", (w.x, w.center_y - dp(5))))
        top.add_widget(dot)
        top.add_widget(txt(label_txt, 11, PAL["primary"], True))
        top.add_widget(txt(time_txt, 15, PAL["primary"], True,
                           halign="right", size_hint=(None, None),
                           size=(dp(90), dp(24))))
        card.add_widget(top)

        card.add_widget(txt(reminder.medicine_name, 17, PAL["ink"], True,
                            size_hint_y=None, height=dp(26)))
        sub = f"{reminder.strength or ''}  •  {t('daily', lang)}  •  " \
              f"{reminder.member_name}"
        card.add_widget(txt(sub, 11, PAL["muted"], size_hint_y=None,
                            height=dp(18)))
        card.add_widget(txt(t("alert_note", lang), 10, PAL["muted"],
                            wrap=True, size_hint_y=None, height=dp(20)))

        brow = BoxLayout(orientation="horizontal", spacing=dp(8),
                         size_hint_y=None, height=dp(46))
        take = RoundedButton(t("take_now", lang), fs=13)
        take.bind(on_release=lambda *_: self._take_dose(reminder, hhmm))
        brow.add_widget(take)
        snz = RoundedButton(t("snooze_15", lang), bg=PAL["track"],
                            fg=PAL["muted"], fs=12, size_hint_x=None,
                            width=dp(130))
        snz.bind(on_release=lambda *_: self._snooze_dose(reminder, hhmm))
        brow.add_widget(snz)
        card.add_widget(brow)
        card.height = dp(24 + 26 + 18 + 20 + 46 + 20 + 6 * 4)
        holder.add_widget(card)

    def _take_dose(self, reminder, hhmm):
        from datetime import datetime
        now = datetime.now()
        db.upsert_dose_log(self.app.conn, reminder.id,
                           now.strftime("%Y-%m-%d"), hhmm, "taken",
                           taken_at=now.strftime("%Y-%m-%d %H:%M"))
        self.status_lbl.text = t("dose_recorded", self.app.language)
        self.status_lbl.color = PAL["ok"]
        self.app.speak(build_reminder_spoken(
            reminder.member_name, reminder.medicine_name,
            reminder.strength, self.app.language).split(". ")[1]
            if False else t("dose_recorded", self.app.language))
        self.refresh()

    def _snooze_dose(self, reminder, hhmm):
        from datetime import datetime, timedelta
        now = datetime.now()
        until = now + timedelta(minutes=15)
        db.upsert_dose_log(self.app.conn, reminder.id,
                           now.strftime("%Y-%m-%d"), hhmm, "snoozed",
                           snooze_until=until.strftime("%Y-%m-%d %H:%M"))
        # allow re-speak after snooze ends
        self.app._due_spoken_today.discard((reminder.id, hhmm))
        self.status_lbl.text = t("snoozed_msg", self.app.language)
        self.status_lbl.color = PAL["warn"]
        self.refresh()

    def refresh_avatar(self):
        try:
            self.topbar.refresh_avatar()
        except Exception:
            pass

    def _go_search(self):
        q = self.input.text.strip()
        app = self.app
        app.sm.current = "search"
        app.search.set_query(q)

    def _voice(self):
        """Mic button: speech -> search (graceful fallback everywhere)."""
        lang = self.app.language
        if not IS_ANDROID:
            self.status_lbl.text = t("voice_desktop", lang)
            self.status_lbl.color = PAL["warn"]
            return
        self.status_lbl.text = t("voice_listening", lang)
        self.status_lbl.color = PAL["primary"]

        def on_result(text):
            text = (text or "").strip()
            if not text:
                self.status_lbl.text = t("voice_none", lang)
                self.status_lbl.color = PAL["warn"]
                return
            self.input.text = text
            self._go_search()

        def on_error(code):
            if code == "permission":
                self.status_lbl.text = t("voice_perm", lang)
            elif code == "unavailable":
                self.status_lbl.text = t("voice_fail", lang)
            else:
                self.status_lbl.text = t("voice_none", lang)
            self.status_lbl.color = PAL["warn"]

        self.app.voice.start(lang, on_result, on_error)


# =====================================================================
# ADD / SCAN sheet (bottom popup)
# =====================================================================
class AddSheet(ModalView):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.size_hint = (1, None)
        self.height = dp(360)
        self.background = ""
        self.anchor_y = "bottom"
        self.auto_dismiss = True

    def refresh_ui(self):
        self.clear_widgets()
        app, lang = self.app, self.app.language
        card = Card(radius=22, orientation="vertical",
                    padding=(dp(16), dp(14)), spacing=dp(8))
        head = BoxLayout(size_hint_y=None, height=dp(26))
        head.add_widget(txt(t("add_scan", lang), 15, PAL["ink"], True))
        x = RoundedButton("X", bg=PAL["track"], fg=PAL["muted"], fs=12,
                          size_hint=(None, None), size=(dp(34), dp(30)),
                          radius=15)
        x.bind(on_release=lambda *_: self.dismiss())
        head.add_widget(x)
        card.add_widget(head)

        options = [
            ("camera", t("sheet_scan", lang),
             lambda: (self.dismiss(), setattr(app.sm, "current", "scan"))),
            ("search", t("sheet_search", lang),
             lambda: (self.dismiss(), setattr(app.sm, "current", "search"))),
            ("box", t("sheet_cabinet", lang),
             lambda: (self.dismiss(), app.cabinet.open_form())),
            ("bell", t("sheet_reminder", lang),
             lambda: (self.dismiss(), app.reminder_scr.open_form())),
            ("family", t("sheet_member", lang),
             lambda: (self.dismiss(), app.family.open_form())),
        ]
        for kind, label, fn in options:
            b = CardButton(orientation="horizontal", size_hint_y=None,
                           height=dp(46), padding=(dp(12), 0), spacing=dp(10))
            b.add_widget(Icon(kind, color=PAL["primary"],
                              size_hint=(None, None), size=(dp(24), dp(24)),
                              pos_hint={"center_y": .5}))
            b.add_widget(txt(label, 13, PAL["ink"]))
            b.add_widget(txt("›", 18, PAL["muted"], size_hint=(None, None),
                             size=(dp(18), dp(40)), halign="center"))
            b.bind(on_release=lambda *_x, f=fn: f())
            card.add_widget(b)
        self.add_widget(card)


# =====================================================================
# PROFILE & SETTINGS sheet
# =====================================================================
class ProfileSheet(ModalView):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.size_hint = (1, None)
        self.height = dp(560)
        self.background = ""
        self.anchor_y = "bottom"
        self.auto_dismiss = True

    def refresh_ui(self):
        self.clear_widgets()
        app, lang = self.app, self.app.language
        from medicine.information import LV_SIMPLE

        card = Card(radius=22, orientation="vertical",
                    padding=(dp(16), dp(12)), spacing=dp(8))

        head = BoxLayout(size_hint_y=None, height=dp(28))
        head.add_widget(txt("MEDICINE ASSISTANT", 10, PAL["primary"], True))
        x = RoundedButton("X", bg=PAL["track"], fg=PAL["muted"], fs=12,
                          size_hint=(None, None), size=(dp(34), dp(30)),
                          radius=15)
        x.bind(on_release=lambda *_: self.dismiss())
        head.add_widget(x)
        card.add_widget(head)
        card.add_widget(txt(t("prof_title", lang), 17, PAL["ink"], True,
                            size_hint_y=None, height=dp(28)))

        # name row
        namecard = TintCard(bg=PAL["teal_soft"], radius=16,
                            size_hint_y=None, height=dp(64),
                            padding=(dp(10), 0))
        nrow = BoxLayout(orientation="horizontal", spacing=dp(10))
        self._av = Avatar(app.avatar_letter(), size=dp(42),
                          pos_hint={"center_y": .5})
        nrow.add_widget(self._av)
        ncol = BoxLayout(orientation="vertical")
        ncol.add_widget(txt(t("your_name", lang), 9, PAL["muted"], True))
        self.name_in = RoundedInput(text=app.user_name(), font_size=dp(15),
                                    multiline=False, size_hint_y=None,
                                    height=dp(36), fill=(0, 0, 0, 0))
        self.name_in._ln.width = 0.0001
        ncol.add_widget(self.name_in)
        nrow.add_widget(ncol)
        sv = RoundedButton(t("save", lang), fs=11, size_hint=(None, None),
                           size=(dp(70), dp(34)), radius=17,
                           pos_hint={"center_y": .5})
        sv.bind(on_release=lambda *_: self._save_name())
        nrow.add_widget(sv)
        namecard.add_widget(nrow)
        card.add_widget(namecard)

        # language row
        card.add_widget(self._setting_row(
            t("language", lang), "English · हिन्दी",
            self._lang_buttons()))
        # dark mode row
        card.add_widget(self._setting_row(
            t("dark_mode", lang),
            t("dark_app", lang) if app.dark_mode else t("light_app", lang),
            self._dark_buttons()))
        # explanation level row
        card.add_widget(self._setting_row(
            t("explain_lbl", lang),
            t({"simple": "lv_simple", "normal": "lv_normal"}.get(
                app.explain_lv, "lv_detailed"), lang),
            self._level_buttons()))
        # notif info row
        card.add_widget(self._setting_row(
            t("notif_row", lang), t("notif_sub", lang), None))
        # clear history row
        cl = CardButton(orientation="horizontal", size_hint_y=None,
                        height=dp(56), padding=(dp(12), 0), spacing=dp(8))
        cl.add_widget(Icon("trash", color=PAL["danger"],
                           size_hint=(None, None), size=(dp(22), dp(22)),
                           pos_hint={"center_y": .5}))
        clc = BoxLayout(orientation="vertical")
        clc.add_widget(txt(t("clear_hist", lang), 12.5, PAL["ink"], True))
        clc.add_widget(txt(t("clear_hist_sub", lang), 9.5, PAL["muted"]))
        cl.add_widget(clc)
        cl.bind(on_release=lambda *_: self._clear_all())
        card.add_widget(cl)

        # privacy footer
        foot = TintCard(bg=PAL["mint_soft"], radius=16, size_hint_y=None,
                        padding=(dp(12), dp(8)))
        fl = txt(t("privacy_footer", lang), 9.5, PAL["primary"], wrap=True,
                 size_hint_y=None)
        def _foot_h(_l, s):
            fl.height = s[1]
            foot.height = s[1] + dp(18)
        fl.bind(texture_size=_foot_h)
        foot.add_widget(fl)
        card.add_widget(foot)
        self.add_widget(card)

    # ---------------- row builders ----------------
    def _setting_row(self, title, subtitle, right_widget):
        row = TintCard(bg=PAL["teal_soft"], radius=16, size_hint_y=None,
                       height=dp(56), padding=(dp(12), 0))
        rr = BoxLayout(orientation="horizontal", spacing=dp(8))
        col = BoxLayout(orientation="vertical")
        col.add_widget(txt(title, 12.5, PAL["ink"], True))
        col.add_widget(txt(subtitle, 9.5, PAL["muted"]))
        rr.add_widget(col)
        if right_widget:
            rr.add_widget(right_widget)
        row.add_widget(rr)
        return row

    def _mini(self, label, active, fn):
        return RoundedButton(
            label, bg=PAL["primary"] if active else PAL["track"],
            fg=PAL["white"] if active else PAL["muted"], fs=10.5,
            size_hint=(None, None), size=(dp(66), dp(32)), radius=16,
            on_release=lambda *_: fn())

    def _lang_buttons(self):
        app = self.app
        box = BoxLayout(orientation="horizontal", spacing=dp(6),
                        size_hint=(None, None), size=(dp(140), dp(36)),
                        pos_hint={"center_y": .5})
        box.add_widget(self._mini("EN", app.language == EN,
                                  lambda: app.save_language(EN)))
        box.add_widget(self._mini("हिं", app.language == HI,
                                  lambda: app.save_language(HI)))
        return box

    def _dark_buttons(self):
        app = self.app
        lang = app.language
        box = BoxLayout(orientation="horizontal", spacing=dp(6),
                        size_hint=(None, None), size=(dp(140), dp(36)),
                        pos_hint={"center_y": .5})
        box.add_widget(self._mini(t("light_short", lang), not app.dark_mode,
                                  lambda: self._dark(False)))
        box.add_widget(self._mini(t("dark_short", lang), app.dark_mode,
                                  lambda: self._dark(True)))
        return box

    def _level_buttons(self):
        from medicine.information import LV_SIMPLE, LV_NORMAL, LV_DETAILED
        app = self.app
        box = BoxLayout(orientation="horizontal", spacing=dp(4),
                        size_hint=(None, None), size=(dp(190), dp(36)),
                        pos_hint={"center_y": .5})
        lang = app.language
        for lv, key in ((LV_SIMPLE, "lv_simple"), (LV_NORMAL, "lv_normal"),
                        (LV_DETAILED, "lv_detailed")):
            box.add_widget(RoundedButton(
                t(key, lang), bg=PAL["primary"] if app.explain_lv == lv
                else PAL["track"],
                fg=PAL["white"] if app.explain_lv == lv else PAL["muted"],
                fs=9.5, size_hint=(None, None), size=(dp(60), dp(32)),
                radius=16,
                on_release=lambda *_x, l=lv: self._level(l)))
        return box

    def _dark(self, dark):
        self.app.toggle_dark(dark)
        self.refresh_ui()

    def _level(self, lv):
        self.app.save_explain_level(lv)
        self.refresh_ui()

    def _save_name(self):
        self.app.save_name(self.name_in.text)
        self._av.set_letter(self.app.avatar_letter())
        self.app.home.refresh()
        self.refresh_ui()

    def _clear_all(self):
        app, lang = self.app, self.app.language
        db.clear_history(app.conn)
        db.clear_dose_logs(app.conn)
        app.home.status_lbl.text = t("clear_done", lang)
        app.home.status_lbl.color = PAL["ok"]
        self.dismiss()
        app.history.refresh()
        app.home.refresh()


# =====================================================================
# SEARCH
# =====================================================================
class SearchScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self._last_query = ""
        self.refresh()

    def set_query(self, query):
        self._last_query = query
        if hasattr(self, "input"):
            self.input.text = query
            self._do_search()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, t("opt_search", lang)))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(10)),
                         spacing=dp(10))
        root.add_widget(body)
        root.add_widget(BottomNav(app, active="home"))

        row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(8))
        self.input = RoundedInput(
            hint_text=t("search_hint", lang), font_size=dp(16),
            multiline=False, text=self._last_query)
        self.input.bind(on_text_validate=lambda *_: self._do_search())
        row.add_widget(self.input)
        go = RoundedButton(t("opt_search", lang), fs=12,
                           size_hint=(None, None), size=(dp(92), dp(54)))
        go.bind(on_release=lambda *_: self._do_search())
        row.add_widget(go)
        body.add_widget(row)

        # suggestion one-tap lines here too (elders)
        for action, line in get_suggestions(lang)[:2]:
            b = RoundedButton(line, bg=PAL["teal_soft"], fg=PAL["primary"],
                              fs=11, radius=17, size_hint_y=None,
                              height=dp(36), bold=False)
            b.bind(on_release=lambda _x, a=action: app.run_suggestion(a))
            body.add_widget(b)

        self.results = BoxLayout(orientation="vertical", spacing=dp(10),
                                 size_hint_y=None)
        self.results.bind(minimum_height=self.results.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.results)
        body.add_widget(scroll)
        self.add_widget(root)
        if self._last_query:
            self._do_search()

    def _do_search(self):
        lang = self.app.language
        query = self.input.text.strip()
        self._last_query = query
        self.results.clear_widgets()
        if not query:
            self.results.add_widget(text_card(
                t("opt_search", lang),
                t("type_name", lang)))
            return
        matches = search_medicines(self.app.conn, query)
        if not matches:
            self.results.add_widget(text_card(
                t("opt_search", lang),
                t("not_found", lang, q=query), title_color=PAL["warn"]))
            return
        for m in matches:
            self.results.add_widget(self._result_card(m, lang))

    def _result_card(self, m, lang):
        card = CardButton(orientation="horizontal", size_hint_y=None,
                          height=dp(72), padding=(dp(14), dp(8)), spacing=dp(8))
        col = BoxLayout(orientation="vertical", spacing=dp(1))
        col.add_widget(txt(m.medicine.medicine_name, 14.5, PAL["ink"], True,
                           size_hint_y=None, height=dp(22)))
        gen = m.medicine.generic_name or "-"
        col.add_widget(txt(f"{gen}  •  {m.medicine.strength or ''}", 10.5,
                           PAL["muted"]))
        card.add_widget(col)
        if m.match_type == EXACT:
            card.add_widget(chip(t("exact_tag", lang), PAL["primary"],
                                 PAL["mint_soft"]))
        else:
            card.add_widget(chip(t("possible_tag", lang), PAL["warn"],
                                 PAL["warn_soft"]))
        card.add_widget(txt("›", 22, PAL["muted"], size_hint=(None, None),
                            size=(dp(18), dp(46)), halign="center"))
        card.bind(on_release=lambda *_: self.app.show_details(
            m.medicine, m.match_type))
        return card


# =====================================================================
# SCAN (ML Kit OCR) + manual expiry check
# =====================================================================
class ScanScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.packaging = None
        self.refresh()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, t("opt_scan", lang)))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(10)),
                         spacing=dp(10))
        root.add_widget(body)
        root.add_widget(BottomNav(app, active="home"))

        pick = CardButton(orientation="vertical", size_hint_y=None,
                          height=dp(120), padding=(dp(14), dp(8)), spacing=dp(2))
        pick.add_widget(Icon("camera", color=PAL["primary"],
                             size_hint=(None, None), size=(dp(40), dp(40)),
                             pos_hint={"center_x": .5}))
        pick.add_widget(txt(t("sheet_scan", lang), 14, PAL["primary"], True,
                            halign="center", size_hint_y=None, height=dp(22)))
        pick.add_widget(txt(
            "Gallery se - photo kabhi save nahi hoti, on-device scan"
            if lang == HI else
            "From gallery - never saved, scanned fully on-device",
            9.5, PAL["muted"], halign="center"))
        pick.bind(on_release=lambda *_: self._pick_image())
        body.add_widget(pick)

        self.status = txt("", 10.5, PAL["muted"], wrap=True, size_hint_y=None,
                          height=dp(26), halign="center")
        body.add_widget(self.status)

        body.add_widget(txt("OR TYPE PACK TEXT" if lang == EN
                            else "या पैक का text लिखें", 10, PAL["muted"],
                            True, halign="center", size_hint_y=None,
                            height=dp(16)))
        self.manual = RoundedInput(
            hint_text="MFG 03/2025  EXP 02/2027  Paracetamol 500",
            font_size=dp(14), multiline=True, size_hint_y=None,
            height=dp(80))
        body.add_widget(self.manual)
        check = RoundedButton("CHECK EXPIRY" if lang == EN else "एक्सपायरी जाँचें",
                              fs=15, size_hint_y=None, height=dp(50))
        check.bind(on_release=lambda *_: self._handle_text(
            self.manual.text.strip()))
        body.add_widget(check)

        self.results = BoxLayout(orientation="vertical", spacing=dp(10),
                                 size_hint_y=None)
        self.results.bind(minimum_height=self.results.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.results)
        body.add_widget(scroll)
        self.add_widget(root)

    # ---- helpers ----
    def _set_status(self, msg, color=None):
        self.status.text = msg
        self.status.color = color or PAL["muted"]

    # ---- photo flow ----
    def _pick_image(self):
        lang = self.app.language
        if not _JNI_OK:
            self._set_status("Photo scan sirf Android app me chalta hai."
                             if lang == EN else
                             "फोटो स्कैन सिर्फ Android app में चलता है.",
                             PAL["danger"])
            return
        try:
            Intent = autoclass("android.content.Intent")
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("image/*")
            _android_activity.bind(on_activity_result=self._on_picked)
            activity.startActivityForResult(intent, _PICK_IMAGE_REQUEST)
        except Exception as exc:
            self._set_status(f"Gallery nahi khuli: {exc}", PAL["danger"])

    def _on_picked(self, request_code, result_code, data):
        try:
            _android_activity.unbind(on_activity_result=self._on_picked)
        except Exception:
            pass
        lang = self.app.language
        if request_code != _PICK_IMAGE_REQUEST:
            return
        if result_code != RESULT_OK or data is None:
            self._set_status("Cancelled." if lang == EN else "Cancel हुआ.")
            return
        self._set_status(t("processing", lang), PAL["primary"])
        Clock.schedule_once(lambda _dt: self._start_ocr(data.getData()), 0.1)

    def _start_ocr(self, uri):
        lang = self.app.language
        bmp, error = decode_bitmap(uri)
        if error or bmp is None:
            self._set_status(
                ("Photo padh nahi paye - seedhi/saaf photo dobara try karein."
                 if lang == EN else
                 "फोटो पढ नहीं पाए - सीधी/साफ फोटो दोबारा try करें.")
                + (f" ({error})" if error else ""), PAL["danger"])
            return
        recognize_text(bitmap=bmp, on_success=self._on_ocr_text,
                       on_error=self._on_ocr_error)

    def _on_ocr_error(self, message):
        lang = self.app.language
        self._set_status("Scan engine error - dobara try karein." if lang == EN
                         else "स्कैन engine error - दोबारा try करें.",
                         PAL["danger"])

    def _on_ocr_text(self, raw_text):
        lang = self.app.language
        raw_text = (raw_text or "").strip()
        if not raw_text:
            self._set_status(
                "Photo me koi text nahi mila. Seedhi, nikat ki photo try "
                "karein - ya neeche type karein." if lang == EN else
                "फोटो में कोई text नहीं मिला। सीधी, निकट की फोटो try करें "
                "- या नीचे type करें.", PAL["warn"])
            return
        self._handle_text(raw_text, source="scan")

    # ---- shared result handling ----
    def _handle_text(self, raw_text, source="manual"):
        lang = self.app.language
        self.results.clear_widgets()
        if not raw_text:
            self._set_status("Text khaali hai." if lang == EN
                             else "Text खाली है.")
            return

        self.packaging = extract_packaging_info(raw_text)
        self._set_status("OK - text mil gaya - results neeche." if lang == EN
                         else "OK - text मिल गया - results नीचे.",
                         PAL["primary"])

        section = format_packaging_info_section(self.packaging, None, lang)
        # card title already shows the header -> drop the section's own
        # ">> ..." heading line (and its dashes underline, plus blank pads)
        _lines = section.splitlines()
        while _lines and not _lines[0].strip():
            _lines.pop(0)
        if _lines and _lines[0].lstrip().startswith(">>"):
            _lines = _lines[1:]
            if _lines and set(_lines[0].strip()) <= {"-"}:
                _lines = _lines[1:]
            section = "\n".join(_lines).strip("\n")
        self.results.add_widget(text_card(
            t("pkg_hdr", lang), section))

        matches = find_medicines_in_ocr_text(self.app.conn, raw_text)
        if matches:
            for m in matches:
                self.results.add_widget(self._med_row(m, lang, source))
        else:
            self.results.add_widget(text_card(
                "NO KNOWN MEDICINE FOUND" if lang == EN
                else "कोई जानी दवा नहीं मिली",
                t("not_identified", lang), title_color=PAL["warn"]))

        shown = raw_text if len(raw_text) <= 400 else raw_text[:400] + " ..."
        self.results.add_widget(text_card(
            "TEXT THAT WAS READ" if lang == EN else "जो text पढ़ा गया",
            shown, body_color=PAL["muted"]))

    def _med_row(self, m, lang, source):
        card = CardButton(orientation="horizontal", size_hint_y=None,
                          height=dp(70), padding=(dp(14), dp(8)), spacing=dp(8))
        col = BoxLayout(orientation="vertical", spacing=dp(1))
        col.add_widget(txt(m.medicine.medicine_name, 14, PAL["ink"], True,
                           size_hint_y=None, height=dp(22)))
        col.add_widget(txt(m.medicine.generic_name or "-", 10.5, PAL["muted"]))
        card.add_widget(col)
        card.add_widget(chip("EXACT" if m.match_type == EXACT else "POSSIBLE",
                             PAL["primary"] if m.match_type == EXACT
                             else PAL["warn"],
                             PAL["mint_soft"] if m.match_type == EXACT
                             else PAL["warn_soft"]))
        card.add_widget(txt("›", 20, PAL["muted"], size_hint=(None, None),
                            size=(dp(16), dp(46)), halign="center"))
        card.bind(on_release=lambda *_: self.app.show_details(
            m.medicine, m.match_type, source=source,
            packaging=self.packaging))
        return card


# =====================================================================
# DETAILS (+ Listen / Stop / Share + explanation levels + new cards)
# =====================================================================
class DetailsScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.medicine = None
        self.match_type = None
        self.packaging = None

    def show(self, medicine, match_type, packaging=None):
        self.repaint_bg()
        self.clear_widgets()
        self.medicine, self.match_type, self.packaging = (medicine,
                                                          match_type, packaging)
        app, lang = self.app, self.app.language
        from medicine.information import LV_SIMPLE, LV_NORMAL, LV_DETAILED

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, medicine.medicine_name))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(10)),
                         spacing=dp(10))
        root.add_widget(body)

        # EXPIRED loud banner (safety-first)
        if packaging is not None and packaging.expiry_status() == "expired":
            ban = TintCard(bg=PAL["danger_soft"], border=PAL["danger"],
                           radius=16, orientation="vertical",
                           size_hint_y=None, height=dp(64),
                           padding=(dp(14), dp(8)))
            ban.add_widget(txt("EXPIRED - YE DAWA USE MAT KARO" if lang == HI
                               else "EXPIRED - DO NOT USE THIS MEDICINE",
                               15, PAL["danger"], True))
            ban.add_widget(txt("Nai dawa ke liye pharmacist/doctor se mile."
                               if lang == HI else
                               "Please get a fresh supply - ask a pharmacist/doctor.",
                               11, PAL["danger"]))
            body.add_widget(ban)

        # confidence + explanation-level chips
        row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(8))
        if match_type == EXACT:
            row.add_widget(chip(t("exact_tag", lang), PAL["primary"],
                                PAL["mint_soft"]))
        else:
            row.add_widget(chip(t("possible_tag", lang), PAL["warn"],
                                PAL["warn_soft"]))
        row.add_widget(Widget())
        for lv, key in ((LV_SIMPLE, "lv_simple"), (LV_NORMAL, "lv_normal"),
                        (LV_DETAILED, "lv_detailed")):
            b = RoundedButton(
                t(key, lang), bg=PAL["primary"] if app.explain_lv == lv
                else PAL["track"],
                fg=PAL["white"] if app.explain_lv == lv else PAL["muted"],
                fs=9.5, size_hint=(None, None), size=(dp(64), dp(30)),
                radius=15,
                on_release=lambda *_x, l=lv: app.save_explain_level(l))
            row.add_widget(b)
        body.add_widget(row)

        # action row: LISTEN + STOP + SHARE + ADD-TO-CABINET
        btnrow = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        listen = RoundedButton("LISTEN" if lang == EN else "सुनें", fs=13)
        listen.bind(on_release=lambda *_: self._listen())
        btnrow.add_widget(listen)
        stopb = RoundedButton("STOP" if lang == EN else "रोकें",
                              bg=PAL["track"], fg=PAL["muted"], fs=11,
                              size_hint_x=None, width=dp(74))
        stopb.bind(on_release=lambda *_: self._stop())
        btnrow.add_widget(stopb)
        share = RoundedButton("SHARE" if lang == EN else "शेयर",
                              bg=PAL["teal_soft"], fg=PAL["primary"], fs=11,
                              size_hint_x=None, width=dp(86))
        share.bind(on_release=lambda *_: self._share())
        btnrow.add_widget(share)
        cabadd = RoundedButton("+ " + t("qa_cabinet", lang),
                               bg=PAL["mint_soft"], fg=PAL["primary"], fs=10,
                               size_hint_x=None, width=dp(116))
        cabadd.bind(on_release=lambda *_: self._add_cab())
        btnrow.add_widget(cabadd)
        body.add_widget(btnrow)

        self.status = txt("", 10, PAL["warn"], wrap=True, size_hint_y=None,
                          height=dp(30), halign="center")
        body.add_widget(self.status)

        # ---- details text (level-aware) ----
        page = format_details_page(medicine, match_type, lang,
                                   level=app.explain_lv)
        content = txt(page, 12, PAL["ink"], wrap=True, size_hint_y=None,
                      valign="top")
        content.bind(texture_size=lambda _l, s: setattr(
            content, "height", s[1] + dp(8)))
        card = Card(padding=(dp(14), dp(12)), size_hint_y=None)
        card.add_widget(content)
        card.bind(minimum_height=card.setter("height"))

        inner = BoxLayout(orientation="vertical", spacing=dp(10),
                          size_hint_y=None)
        inner.bind(minimum_height=inner.setter("height"))
        inner.add_widget(card)

        # who-can-take + storage + authenticity cards (all levels, safety)
        inner.add_widget(text_card(t("who_card", lang),
                                   format_age_suitability(medicine, lang),
                                   title_color=PAL["primary"]))
        inner.add_widget(text_card(t("storage_card", lang),
                                   format_storage_card(medicine, lang),
                                   title_color=PAL["primary"]))
        auth = CardButton(orientation="horizontal", size_hint_y=None,
                          height=dp(48), padding=(dp(12), 0), spacing=dp(8))
        auth.add_widget(Icon("shield", color=PAL["primary"],
                             size_hint=(None, None), size=(dp(24), dp(24)),
                             pos_hint={"center_y": .5}))
        auth.add_widget(txt(t("auth_link", lang), 11.5, PAL["primary"], True,
                            wrap=True))
        auth.add_widget(txt("›", 18, PAL["muted"], size_hint=(None, None),
                            size=(dp(16), dp(40)), halign="center"))
        auth.bind(on_release=lambda *_: setattr(app.sm, "current", "auth"))
        inner.add_widget(auth)

        scroll = ScrollView()
        scroll.add_widget(inner)
        body.add_widget(scroll)
        self.add_widget(root)

    def _add_cab(self):
        if not self.medicine:
            return
        self.app.cabinet.open_form(prefill_name=self.medicine.medicine_name,
                                   prefill_strength=self.medicine.strength)

    def _listen(self):
        if not self.medicine:
            return
        lang = self.app.language
        cb = lambda msg: setattr(self.status, "text", msg)
        text = build_spoken_summary(self.medicine, self.packaging,
                                    self.match_type, lang)
        fallback = build_spoken_summary(self.medicine, self.packaging,
                                        self.match_type,
                                        EN) if lang == HI else None
        self.app.get_speaker().speak(text, lang, fallback_text=fallback,
                                     status_cb=cb)

    def _stop(self):
        self.app.stop_speaking()
        self.status.text = ""

    def _share(self):
        if not self.medicine:
            return
        lang = self.app.language
        page = format_details_page(self.medicine, self.match_type, lang,
                                   level="detailed")
        header = ("Shared from Medicine Assistant (offline app)\n"
                  "NOTE: General info only - not medical advice.\n\n"
                  if lang == EN else
                  "Medicine Assistant (offline app) se share kiya\n"
                  "NOTE: Sirf general jaankari - medical salah nahi.\n\n")
        if not share_text(header + page):
            self.status.text = "Share sirf Android app me chalta hai."


# =====================================================================
# HISTORY
# =====================================================================
class HistoryScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.refresh()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, t("opt_history", lang)))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(10)),
                         spacing=dp(10))
        root.add_widget(body)
        root.add_widget(BottomNav(app, active="history"))

        top = BoxLayout(size_hint_y=None, height=dp(30))
        top.add_widget(txt("Sirf text - photos kabhi save nahi hoti."
                           if lang == HI else
                           "Text only - photos are never stored.",
                           9.5, PAL["muted"]))
        clear = RoundedButton(t("clear_hist", lang), bg=PAL["danger_soft"],
                              fg=PAL["danger"], fs=9.5,
                              size_hint=(None, None), size=(dp(120), dp(30)),
                              radius=15, bold=True)
        clear.bind(on_release=lambda *_: (db.clear_history(self.app.conn),
                                          self.refresh()))
        top.add_widget(clear)
        body.add_widget(top)

        entries = db.fetch_history(self.app.conn)
        self.list_box = BoxLayout(orientation="vertical", spacing=dp(8),
                                  size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.list_box)
        body.add_widget(scroll)
        self.add_widget(root)

        if not entries:
            self.list_box.add_widget(text_card(t("opt_history", lang),
                                               t("history_empty", lang)))
            return
        for e in entries:
            self.list_box.add_widget(self._row(e))

    def _row(self, e):
        status = (e.expiry_status or "").lower()
        dot = {"valid": PAL["ok"], "expiring_soon": PAL["warn"],
               "expired": PAL["danger"]}.get(status, PAL["track"])
        card = CardButton(orientation="horizontal", size_hint_y=None,
                          height=dp(64), padding=(dp(12), dp(6)), spacing=dp(10))
        dotw = Widget(size_hint=(None, None), size=(dp(12), dp(12)),
                      pos_hint={"center_y": .5})
        with dotw.canvas:
            Color(rgba=dot)
            el = Ellipse(pos=dotw.pos, size=dotw.size)
        dotw.bind(pos=lambda w, _v: setattr(el, "pos", (w.x, w.center_y - dp(6))))
        card.add_widget(dotw)
        col = BoxLayout(orientation="vertical")
        col.add_widget(txt(e.medicine_name, 15, PAL["ink"], True,
                           size_hint_y=None, height=dp(22)))
        col.add_widget(txt(f"{e.searched_at}  •  {status or '-'}", 9.5,
                           PAL["muted"]))
        card.add_widget(col)
        card.add_widget(txt("›", 20, PAL["muted"], size_hint=(None, None),
                            size=(dp(16), dp(40)), halign="center"))
        card.bind(on_release=lambda *_: self._open(e))
        return card

    def _open(self, e):
        medicine = db.get_medicine_by_id(self.app.conn, e.medicine_id)
        if medicine:
            self.app.show_details(medicine, e.match_type)


# =====================================================================
# REMINDERS (list + add/edit sheet)
# =====================================================================
class RemindersScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.form = ReminderFormSheet(app)
        self.refresh()

    def open_form(self):
        self.form.refresh_ui()
        self.form.open()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, t("rem_title", lang)))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(8)),
                         spacing=dp(10))
        root.add_widget(body)
        root.add_widget(BottomNav(app, active="reminders"))

        add = RoundedButton("+  " + t("rem_add", lang), fs=13,
                            size_hint_y=None, height=dp(48), radius=24)
        add.bind(on_release=lambda *_: self.open_form())
        body.add_widget(add)

        box = BoxLayout(orientation="vertical", spacing=dp(8),
                        size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(box)
        body.add_widget(scroll)
        self.add_widget(root)

        reminders = db.fetch_reminders(app.conn)
        if not reminders:
            box.add_widget(text_card(t("rem_title", lang),
                                     t("rem_empty", lang)))
            return
        for r in reminders:
            box.add_widget(self._row(r))

    def _row(self, r):
        lang = self.app.language
        card = Card(orientation="vertical", size_hint_y=None,
                    padding=(dp(12), dp(8)), spacing=dp(4))
        top = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(30), spacing=dp(8))
        top.add_widget(txt(r.medicine_name
                           + (f"  •  {r.strength}" if r.strength else ""),
                           14, PAL["ink"], True))
        on = r.active == 1
        switch = RoundedButton(t("rem_on", lang) if on else t("rem_off", lang),
                               bg=PAL["ok"] if on else PAL["track"],
                               fg=PAL["white"] if on else PAL["muted"],
                               fs=9.5, size_hint=(None, None),
                               size=(dp(72), dp(30)), radius=15)
        switch.bind(on_release=lambda *_: self._toggle(r))
        top.add_widget(switch)
        card.add_widget(top)
        when = f"{t('daily', lang)}  {t('rem_at', lang)} " + ", ".join(r.times())
        card.add_widget(txt(when, 11, PAL["primary"], True, size_hint_y=None,
                            height=dp(20)))
        card.add_widget(txt(f"{r.member_name}", 10, PAL["muted"],
                            size_hint_y=None, height=dp(18)))
        delb = RoundedButton(t("cab_delete2", lang), bg=PAL["danger_soft"],
                             fg=PAL["danger"], fs=9.5, size_hint=(None, None),
                             size=(dp(90), dp(28)), radius=14)
        delb.bind(on_release=lambda *_:
                  (db.delete_reminder(self.app.conn, r.id), self.refresh()))
        card.add_widget(delb)
        card.height = dp(30 + 20 + 18 + 34 + 16 + 4 * 4)
        return card

    def _toggle(self, r):
        db.set_reminder_active(self.app.conn, r.id, r.active != 1)
        self.refresh()


class ReminderFormSheet(ModalView):
    """Add-a-reminder bottom sheet."""

    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.size_hint = (1, None)
        self.height = dp(470)
        self.background = ""
        self.anchor_y = "bottom"
        self.auto_dismiss = True
        self.member_choice = None

    def refresh_ui(self):
        self.clear_widgets()
        app, lang = self.app, self.app.language
        card = Card(radius=22, orientation="vertical",
                    padding=(dp(16), dp(12)), spacing=dp(8))

        head = BoxLayout(size_hint_y=None, height=dp(26))
        head.add_widget(txt(t("rem_add", lang), 16, PAL["ink"], True))
        x = RoundedButton("X", bg=PAL["track"], fg=PAL["muted"], fs=12,
                          size_hint=(None, None), size=(dp(34), dp(30)),
                          radius=15)
        x.bind(on_release=lambda *_: self.dismiss())
        head.add_widget(x)
        card.add_widget(head)

        # who takes it?
        card.add_widget(txt(t("rem_member", lang), 11, PAL["muted"], True,
                            size_hint_y=None, height=dp(18)))
        self.member_choice = None
        self._member_box = BoxLayout(orientation="horizontal", spacing=dp(6),
                                     size_hint_y=None, height=dp(36))
        card.add_widget(self._member_box)
        self._build_member_buttons()

        self.msg = txt("", 10, PAL["warn"], size_hint_y=None, height=dp(16))

        half = BoxLayout(orientation="horizontal", spacing=dp(8),
                         size_hint_y=None, height=dp(96))
        left = BoxLayout(orientation="vertical", spacing=dp(4))
        left.add_widget(txt(t("rem_med", lang), 10, PAL["muted"], True,
                            size_hint_y=None, height=dp(16)))
        self.med_in = RoundedInput(font_size=dp(14), multiline=False,
                                   size_hint_y=None, height=dp(44))
        left.add_widget(self.med_in)
        right = BoxLayout(orientation="vertical", spacing=dp(4),
                          size_hint_x=None, width=dp(120))
        right.add_widget(txt(t("rem_str", lang), 10, PAL["muted"], True,
                             size_hint_y=None, height=dp(16)))
        self.str_in = RoundedInput(font_size=dp(14), multiline=False,
                                   size_hint_y=None, height=dp(44))
        right.add_widget(self.str_in)
        half.add_widget(left)
        half.add_widget(right)
        card.add_widget(half)

        card.add_widget(txt(t("rem_times", lang), 10, PAL["muted"], True,
                            size_hint_y=None, height=dp(16)))
        self.times_in = RoundedInput(hint_text="08:00, 20:30",
                                     font_size=dp(14), multiline=False,
                                     size_hint_y=None, height=dp(44))
        card.add_widget(self.times_in)
        card.add_widget(self.msg)

        save = RoundedButton(t("rem_save", lang), fs=14, size_hint_y=None,
                             height=dp(48), radius=24)
        save.bind(on_release=lambda *_: self._save())
        card.add_widget(save)
        self.add_widget(card)

    def _build_member_buttons(self):
        app, lang = self.app, self.app.language
        self._member_box.clear_widgets()
        members = [None] + db.fetch_family_members(app.conn)
        for m in members:
            if m is None:
                label = t("self_member", lang)
            else:
                label = m.name
            sel = (self.member_choice is None and m is None) or \
                  (self.member_choice is not None and m is not None
                   and self.member_choice == m.id)
            b = RoundedButton(label, bg=PAL["primary"] if sel else PAL["track"],
                              fg=PAL["white"] if sel else PAL["muted"],
                              fs=10, size_hint=(None, None), radius=18,
                              height=dp(34))
            b.bind(texture_size=lambda _b, s: setattr(_b, "width",
                                                      s[0] + dp(24)))
            b.bind(on_release=lambda *_x, mm=m: self._pick_member(mm))
            self._member_box.add_widget(b)

    def _pick_member(self, member):
        self.member_choice = None if member is None else member.id
        self._build_member_buttons()

    def _save(self):
        app, lang = self.app, self.app.language
        med = self.med_in.text.strip()
        if not med:
            self.msg.text = t("rem_need_med", lang)
            return
        if self.member_choice is None:
            member_id = None
            member_name = app.user_name() or t("self_member", lang)
        else:
            member_id = self.member_choice
            found = [m for m in db.fetch_family_members(app.conn)
                     if m.id == member_id]
            member_name = found[0].name if found else t("self_member", lang)
        db.add_reminder(app.conn, member_id, member_name, med,
                        self.str_in.text.strip() or None,
                        self.times_in.text)
        app.reminder_scr.refresh()
        app.home.refresh()
        self.dismiss()
        app.reminder_scr.refresh()


# =====================================================================
# CABINET (medicine maintainer: quantity + dosage + expiry + place)
# =====================================================================
class CabinetScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.form = CabinetFormSheet(app)
        self.refresh()

    def open_form(self, prefill_name="", prefill_strength=""):
        self.form.refresh_ui(prefill_name, prefill_strength)
        self.form.open()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, t("cabinet_title", lang)))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(8)),
                         spacing=dp(10))
        root.add_widget(body)
        root.add_widget(BottomNav(app, active="home"))

        # expiry dashboard strip
        summary = db.cabinet_expiry_summary(app.conn)
        strip = Card(size_hint_y=None, height=dp(116), padding=(dp(12), dp(8)))
        ti = BoxLayout(orientation="vertical", spacing=dp(4))
        head = BoxLayout(orientation="horizontal", size_hint_y=None,
                         height=dp(24))
        head.add_widget(txt(t("exp_dash", lang), 13, PAL["ink"], True))
        spk = RoundedButton(t("speak_summary", lang), bg=PAL["mint_soft"],
                            fg=PAL["primary"], fs=9.5,
                            size_hint=(None, None), size=(dp(160), dp(30)),
                            radius=15)
        spk.bind(on_release=lambda *_: app.speak(
            build_cabinet_spoken_summary(summary, lang)))
        head.add_widget(spk)
        ti.add_widget(head)
        chips_row = BoxLayout(orientation="horizontal", spacing=dp(6),
                              size_hint_y=None, height=dp(28))
        chips_row.add_widget(chip(f"{t('exp_active', lang)}: {len(summary['valid'])}",
                                  PAL["ok"], PAL["ok_soft"], height=dp(26)))
        chips_row.add_widget(chip(f"{t('exp_soon2', lang)}: {len(summary['soon'])}",
                                  PAL["warn"], PAL["warn_soft"], height=dp(26)))
        chips_row.add_widget(chip(f"{t('exp_expired2', lang)}: {len(summary['expired'])}",
                                  PAL["danger"], PAL["danger_soft"], height=dp(26)))
        ti.add_widget(chips_row)
        more = RoundedButton(t("exp_dash", lang) + " ›", bg=PAL["track"],
                             fg=PAL["ink"], fs=10, size_hint_y=None,
                             height=dp(26), radius=13, bold=False,
                             on_release=lambda *_: setattr(
                                 app.sm, "current", "expiry"))
        ti.add_widget(more)
        strip.add_widget(ti)
        body.add_widget(strip)

        add = RoundedButton("+  " + t("cab_add", lang), fs=13,
                            size_hint_y=None, height=dp(46), radius=23)
        add.bind(on_release=lambda *_: self.open_form())
        body.add_widget(add)

        box = BoxLayout(orientation="vertical", spacing=dp(8),
                        size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(box)
        body.add_widget(scroll)
        self.add_widget(root)

        items = db.fetch_cabinet(app.conn)
        if not items:
            box.add_widget(text_card(t("cabinet_title", lang),
                                     t("cab_empty", lang)))
            return
        for it in items:
            box.add_widget(self._row(it))

    def _row(self, it):
        lang = self.app.language
        card = Card(orientation="vertical", size_hint_y=None,
                    padding=(dp(12), dp(8)), spacing=dp(4))
        top = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(26), spacing=dp(8))
        top.add_widget(txt(it.medicine_name
                           + (f"  •  {it.strength}" if it.strength else ""),
                           14, PAL["ink"], True))
        state = it.expiry_state()
        if state == "valid":
            top.add_widget(chip(t("exp_active", lang), PAL["ok"],
                                PAL["ok_soft"], height=dp(24)))
        elif state == "expiring_soon":
            top.add_widget(chip(t("exp_soon2", lang), PAL["warn"],
                                PAL["warn_soft"], height=dp(24)))
        elif state == "expired":
            top.add_widget(chip(t("exp_expired2", lang), PAL["danger"],
                                PAL["danger_soft"], height=dp(24)))
        else:
            top.add_widget(chip(t("exp_nodate", lang), PAL["muted"],
                                PAL["track"], height=dp(24)))
        card.add_widget(top)

        info_bits = []
        if it.expiry_date:
            info_bits.append(f"EXP {it.expiry_date}")
        if it.dosage:
            info_bits.append(it.dosage)
        if it.storage_place:
            info_bits.append(it.storage_place)
        card.add_widget(txt("  •  ".join(info_bits) if info_bits else "-",
                            10, PAL["muted"], wrap=True, size_hint_y=None,
                            height=dp(30)))

        brow = BoxLayout(orientation="horizontal", spacing=dp(8),
                         size_hint_y=None, height=dp(34))
        qty = it.quantity if it.quantity is not None else 0
        if qty == int(qty):
            qty = int(qty)
        brow.add_widget(txt(t("cab_left", lang, qty=qty,
                              unit=it.quantity_unit or ""), 11, PAL["primary"],
                            True))
        take = RoundedButton(t("cab_took1", lang), bg=PAL["mint_soft"],
                             fg=PAL["primary"], fs=9.5,
                             size_hint=(None, None), size=(dp(110), dp(32)),
                             radius=16)
        take.bind(on_release=lambda *_: self._took_one(it))
        brow.add_widget(take)
        delb = RoundedButton(t("cab_delete2", lang), bg=PAL["danger_soft"],
                             fg=PAL["danger"], fs=9.5,
                             size_hint=(None, None), size=(dp(80), dp(32)),
                             radius=16)
        delb.bind(on_release=lambda *_:
                  (db.delete_cabinet_item(self.app.conn, it.id),
                   self.refresh()))
        brow.add_widget(delb)
        card.add_widget(brow)
        card.height = dp(26 + 30 + 34 + 16 + 4 * 4)
        return card

    def _took_one(self, it):
        if it.quantity is not None and it.quantity > 0:
            db.update_cabinet_quantity(self.app.conn, it.id,
                                       max(0, it.quantity - 1))
        self.refresh()
        self.app.home.refresh()


class CabinetFormSheet(ModalView):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.size_hint = (1, None)
        self.height = dp(560)
        self.background = ""
        self.anchor_y = "bottom"
        self.auto_dismiss = True

    def refresh_ui(self, prefill_name="", prefill_strength=""):
        self.clear_widgets()
        app, lang = self.app, self.app.language
        card = Card(radius=22, orientation="vertical",
                    padding=(dp(16), dp(12)), spacing=dp(7))

        head = BoxLayout(size_hint_y=None, height=dp(26))
        head.add_widget(txt(t("cab_add", lang), 16, PAL["ink"], True))
        x = RoundedButton("X", bg=PAL["track"], fg=PAL["muted"], fs=12,
                          size_hint=(None, None), size=(dp(34), dp(30)),
                          radius=15)
        x.bind(on_release=lambda *_: self.dismiss())
        head.add_widget(x)
        card.add_widget(head)

        def field(label, hint="", prefill=""):
            box = BoxLayout(orientation="vertical", spacing=dp(2),
                            size_hint_y=None, height=dp(58))
            box.add_widget(txt(label, 9.5, PAL["muted"], True,
                               size_hint_y=None, height=dp(14)))
            ti = RoundedInput(hint_text=hint, font_size=dp(13),
                              multiline=False, size_hint_y=None,
                              height=dp(40), text=prefill)
            box.add_widget(ti)
            card.add_widget(box)
            return ti

        self.name_in = field(t("cab_name", lang), prefill=prefill_name)
        self.str_in = field(t("cab_strength2", lang), prefill=prefill_strength or "")
        qty_row = BoxLayout(orientation="horizontal", spacing=dp(8),
                            size_hint_y=None, height=dp(58))
        for lbl, hint, attr in ((t("cab_qty", lang), "10", "qty_in"),
                                (t("cab_unit", lang), "tablets", "unit_in")):
            box = BoxLayout(orientation="vertical", spacing=dp(2))
            box.add_widget(txt(lbl, 9.5, PAL["muted"], True,
                               size_hint_y=None, height=dp(14)))
            ti = RoundedInput(hint_text=hint, font_size=dp(13),
                              multiline=False, size_hint_y=None,
                              height=dp(40))
            box.add_widget(ti)
            qty_row.add_widget(box)
            setattr(self, attr, ti)
        card.add_widget(qty_row)
        self.dose_in = field(t("cab_dosage", lang))
        self.exp_in = field(t("cab_exp", lang))
        self.place_in = field(t("cab_place", lang))

        self.msg = txt("", 10, PAL["warn"], size_hint_y=None, height=dp(14))
        card.add_widget(self.msg)
        save = RoundedButton(t("cab_save", lang), fs=14, size_hint_y=None,
                             height=dp(46), radius=23)
        save.bind(on_release=lambda *_: self._save())
        card.add_widget(save)
        self.add_widget(card)

    def _save(self):
        app, lang = self.app, self.app.language
        name = self.name_in.text.strip()
        if not name:
            self.msg.text = t("cab_need_name", lang)
            return
        try:
            qty = float(self.qty_in.text.strip()) \
                if self.qty_in.text.strip() else None
        except ValueError:
            qty = None
        db.add_cabinet_item(app.conn, {
            "medicine_name": name,
            "strength": self.str_in.text.strip() or None,
            "quantity": qty,
            "quantity_unit": self.unit_in.text.strip() or "tablets",
            "dosage": self.dose_in.text.strip() or None,
            "expiry_date": self.exp_in.text.strip() or None,
            "storage_place": self.place_in.text.strip() or None,
        })
        app.cabinet.refresh()
        app.expiry_scr.refresh()
        app.home.refresh()
        self.dismiss()


# =====================================================================
# EXPIRY dashboard (full screen version of the cabinet strip)
# =====================================================================
class ExpiryScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.refresh()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, t("exp_dash", lang)))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(8)),
                         spacing=dp(10))
        root.add_widget(body)
        root.add_widget(BottomNav(app, active="home"))

        summary = db.cabinet_expiry_summary(app.conn)
        spk = RoundedButton(t("speak_summary", lang), fs=12,
                            size_hint_y=None, height=dp(44), radius=22,
                            bg=PAL["primary"])
        spk.bind(on_release=lambda *_: app.speak(
            build_cabinet_spoken_summary(summary, lang)))
        body.add_widget(spk)

        box = BoxLayout(orientation="vertical", spacing=dp(8),
                        size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(box)
        body.add_widget(scroll)
        self.add_widget(root)

        groups = [
            ("expired", t("exp_expired2", lang), PAL["danger"],
             PAL["danger_soft"]),
            ("soon", t("exp_soon2", lang), PAL["warn"], PAL["warn_soft"]),
            ("valid", t("exp_active", lang), PAL["ok"], PAL["ok_soft"]),
            ("nodate", t("exp_nodate", lang), PAL["muted"], PAL["track"]),
        ]
        for key, label, fg, bg in groups:
            items = summary[key]
            sec = BoxLayout(orientation="vertical", spacing=dp(4),
                            size_hint_y=None)
            sec.bind(minimum_height=sec.setter("height"))
            sec.add_widget(chip(f"{label}  ({len(items)})", fg, bg,
                                height=dp(28)))
            for it in items:
                line = it.medicine_name
                if it.expiry_date:
                    line += f"  •  EXP {it.expiry_date}"
                if it.quantity is not None:
                    q = int(it.quantity) if it.quantity == int(it.quantity) \
                        else it.quantity
                    line += f"  •  {q} {it.quantity_unit or ''}"
                c = Card(size_hint_y=None, height=dp(44),
                         padding=(dp(14), 0))
                c.add_widget(txt(line, 12, PAL["ink"], wrap=False))
                sec.add_widget(c)
            box.add_widget(sec)

        box.add_widget(text_card(t("exp_dash", lang),
                                 t("exp_dispose_note", lang),
                                 title_color=PAL["danger"]))


# =====================================================================
# FAMILY CARE
# =====================================================================
class FamilyScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.form = FamilyFormSheet(app)
        self.refresh()

    def open_form(self):
        self.form.refresh_ui()
        self.form.open()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, t("fam_title", lang)))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(8)),
                         spacing=dp(10))
        root.add_widget(body)
        root.add_widget(BottomNav(app, active="home"))

        add = RoundedButton("+  " + t("fam_add", lang), fs=13,
                            size_hint_y=None, height=dp(46), radius=23)
        add.bind(on_release=lambda *_: self.open_form())
        body.add_widget(add)

        box = BoxLayout(orientation="vertical", spacing=dp(8),
                        size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(box)
        body.add_widget(scroll)
        self.add_widget(root)

        members = db.fetch_family_members(app.conn)
        reminders = db.fetch_reminders(app.conn)
        if not members:
            box.add_widget(text_card(t("fam_title", lang),
                                     t("fam_empty", lang)))
        for m in members:
            n_rem = len([r for r in reminders if r.member_id == m.id])
            card = Card(orientation="horizontal", size_hint_y=None,
                        height=dp(60), padding=(dp(12), 0), spacing=dp(10))
            card.add_widget(Avatar(m.name[:1].upper(), size=dp(38),
                                   pos_hint={"center_y": .5}))
            col = BoxLayout(orientation="vertical")
            col.add_widget(txt(m.name + (f"  ({m.relation})"
                                         if m.relation else ""),
                               13.5, PAL["ink"], True))
            col.add_widget(txt(t("fam_rem_count", lang, n=n_rem), 10,
                               PAL["muted"]))
            card.add_widget(col)
            delb = RoundedButton(t("cab_delete2", lang), bg=PAL["danger_soft"],
                                 fg=PAL["danger"], fs=9.5,
                                 size_hint=(None, None), size=(dp(80), dp(30)),
                                 radius=15, pos_hint={"center_y": .5})
            delb.bind(on_release=lambda *_x, mm=m:
                      (db.delete_family_member(self.app.conn, mm.id),
                       self.refresh(), self.app.reminder_scr.refresh()))
            card.add_widget(delb)
            box.add_widget(card)


class FamilyFormSheet(ModalView):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.size_hint = (1, None)
        self.height = dp(300)
        self.background = ""
        self.anchor_y = "bottom"
        self.auto_dismiss = True

    def refresh_ui(self):
        self.clear_widgets()
        app, lang = self.app, self.app.language
        card = Card(radius=22, orientation="vertical",
                    padding=(dp(16), dp(12)), spacing=dp(8))

        head = BoxLayout(size_hint_y=None, height=dp(26))
        head.add_widget(txt(t("fam_add", lang), 16, PAL["ink"], True))
        x = RoundedButton("X", bg=PAL["track"], fg=PAL["muted"], fs=12,
                          size_hint=(None, None), size=(dp(34), dp(30)),
                          radius=15)
        x.bind(on_release=lambda *_: self.dismiss())
        head.add_widget(x)
        card.add_widget(head)

        self.name_in = RoundedInput(hint_text=t("fam_name", lang),
                                    font_size=dp(14), multiline=False,
                                    size_hint_y=None, height=dp(44))
        card.add_widget(self.name_in)
        self.rel_in = RoundedInput(hint_text=t("fam_relation", lang),
                                   font_size=dp(14), multiline=False,
                                   size_hint_y=None, height=dp(44))
        card.add_widget(self.rel_in)
        self.msg = txt("", 10, PAL["warn"], size_hint_y=None, height=dp(14))
        card.add_widget(self.msg)
        save = RoundedButton(t("save", lang), fs=14, size_hint_y=None,
                             height=dp(46), radius=23)
        save.bind(on_release=lambda *_: self._save())
        card.add_widget(save)
        self.add_widget(card)

    def _save(self):
        app, lang = self.app, self.app.language
        name = self.name_in.text.strip()
        if not name:
            self.msg.text = t("fam_need_name", lang)
            return
        db.add_family_member(app.conn, name,
                             self.rel_in.text.strip() or None)
        app.family.refresh()
        self.dismiss()


# =====================================================================
# AUTHENTICITY CHECKLIST screen
# =====================================================================
class AuthScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.refresh()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, t("auth_title", lang)))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(10)),
                         spacing=dp(10))
        root.add_widget(body)
        root.add_widget(BottomNav(app, active="home"))

        box = BoxLayout(orientation="vertical", spacing=dp(10),
                        size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(box)
        body.add_widget(scroll)
        self.add_widget(root)

        box.add_widget(text_card(t("auth_title", lang),
                                 format_authenticity_checklist(lang),
                                 title_color=PAL["primary"]))


# =====================================================================
# STORAGE GUIDE screen
# =====================================================================
class StorageScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.refresh()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language

        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, t("stor_title", lang)))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(10)),
                         spacing=dp(10))
        root.add_widget(body)
        root.add_widget(BottomNav(app, active="home"))

        box = BoxLayout(orientation="vertical", spacing=dp(10),
                        size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(box)
        body.add_widget(scroll)
        self.add_widget(root)

        box.add_widget(text_card(t("stor_title", lang), t("stor_tips", lang),
                                 title_color=PAL["primary"]))

        # storage notes the user actually recorded in the cabinet
        notes = [it for it in db.fetch_cabinet(app.conn) if it.storage_place]
        if notes:
            lines = [f"• {it.medicine_name} -> {it.storage_place}"
                     for it in notes]
            box.add_widget(text_card(t("stor_from_cabinet", lang),
                                     "\n".join(lines),
                                     title_color=PAL["primary"]))


# =====================================================================
# ABOUT
# =====================================================================
class AboutScreen(ScreenBase):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.refresh()

    def refresh(self):
        self.repaint_bg()
        self.clear_widgets()
        app, lang = self.app, self.app.language
        root = BoxLayout(orientation="vertical")
        root.add_widget(BackBar(app, "About This App" if lang == EN
                                else "ऐप के बारे में"))
        body = BoxLayout(orientation="vertical", padding=(dp(16), dp(10)),
                         spacing=dp(10))
        root.add_widget(body)

        box = BoxLayout(orientation="vertical", spacing=dp(10),
                        size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(box)
        body.add_widget(scroll)
        self.add_widget(root)

        def sec(title, text, color=None):
            box.add_widget(text_card(title, text,
                                     title_color=color or PAL["primary"]))

        if lang == EN:
            sec("WHAT IT DOES",
                "Simple info about common medicines - search, scan pack "
                "photos, check expiry, listen aloud. Plus: medicine cabinet "
                "with quantities, daily voice reminders, family care, expiry "
                "dashboard, authenticity checklist and storage guide.")
            sec("100% PRIVATE & OFFLINE",
                "No internet, no account, no tracking. Photos are scanned "
                "in memory and never saved. Cabinet, reminders, family and "
                "history stay only on this phone.")
            sec("SAFETY FIRST",
                "Never diagnoses, prescribes or guesses. Unclear photo = "
                "honest 'not identified'. Fake/real can not be proven by "
                "any app - we show an honest checklist instead.",
                PAL["warn"])
            sec("DEMO DATA",
                "The 6 bundled medicines are DEMO entries for this SIH "
                "build. A verified database can replace them later.")
            sec("TECHNOLOGY",
                "Python + Kivy • SQLite (local) • on-device ML Kit OCR • "
                "Android TextToSpeech + SpeechRecognizer • Hindi & English • "
                "voice reminders run inside the open app.")
        else:
            sec("YE APP KYA KARTA HAI",
                "आम दवाओं की सरल जानकारी - खोज, packet फोटो स्कैन, समाप्ति "
                "जाँच, बोलकर सुनना। साथ में: दवा कैबिनेट, रोज़ के voice "
                "reminders, परिवार की देखभाल, समाप्ति dashboard, असली दवा "
                "checklist और storage गाइड।")
            sec("100% PRIVATE & OFFLINE",
                "Na internet, na account, na tracking. Photos sirf memory "
                "me. कैबिनेट, reminders, परिवार और history सिर्फ इसी phone "
                "पर रहते हैं।")
            sec("SAFETY SABSE PEHLE",
                "App kabhi diagnose/prescribe/guess nahi karta. धुंधली "
                "photo = ईमानदार 'पहचान नहीं हुई'। असली/नकली कोई app साबित "
                "नहीं कर सकता - हम ईमानदार checklist दिखाते हैं।",
                PAL["warn"])
            sec("DEMO DATA",
                "साथ आई 6 दवाएँ इस SIH build की DEMO entries हैं। बाद में "
                "verified database लगाया जा सकता है।")
            sec("TECHNOLOGY",
                "Python + Kivy • SQLite (local) • on-device ML Kit OCR • "
                "Android TextToSpeech + SpeechRecognizer • Hindi & English • "
                "voice reminders ऐप खुले रहने पर चलते हैं।")
        box.add_widget(txt("Medicine Assistant  •  " + APP_VERSION
                           + "  •  SIH demo build", 10, PAL["muted"],
                           halign="center", size_hint_y=None, height=dp(28)))


if __name__ == "__main__":
    MedicineAssistantApp().run()
