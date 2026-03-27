# rounded_button.py
import tkinter as tk

def _round_rect(canvas, x1, y1, x2, y2, r=25, **kwargs):
    r = max(0, min(r, int((x2 - x1) / 2), int((y2 - y1) / 2)))
    pts = [
        x1 + r, y1,
        x2 - r, y1,
        x2,     y1,
        x2,     y1 + r,
        x2,     y2 - r,
        x2,     y2,
        x2 - r, y2,
        x1 + r, y2,
        x1,     y2,
        x1,     y2 - r,
        x1,     y1 + r,
        x1,     y1
    ]
    return canvas.create_polygon(*pts, smooth=True, splinesteps=36, **kwargs)

def _darken_hex(hex_color: str, factor: float = 0.85) -> str:
    """
    Darken a #RRGGBB color by factor (0..1). If parsing fails, return original.
    """
    try:
        s = hex_color.strip()
        if not s.startswith("#") or len(s) != 7:
            return hex_color
        r = int(s[1:3], 16)
        g = int(s[3:5], 16)
        b = int(s[5:7], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color

class RoundedButton(tk.Canvas):
    """
    Stable rounded button for kiosk use.

    Features:
    - Rounded corners via smoothed polygon
    - Canvas-only bindings (prevents label flicker/disappear)
    - Optional click_sound callback
    - Optional press_anim (darken on press)
    - Ignores unknown kwargs so UI helper changes don't crash the app
    """
    def __init__(self, parent, text, command,
                 width=260, height=90, radius=35,
                 bg="#444444", fg="#000000",
                 font=("Arial", 22, "bold"),
                 outline="", outline_width=0,
                 hover_bg=None,
                 click_sound=None,
                 press_anim=False,
                 **_ignored_kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent["bg"],
            highlightthickness=0,
            bd=0
        )

        self._cmd = command
        self._bg = bg
        self._hover_bg = hover_bg or bg
        self._click_sound = click_sound
        self._press_anim = bool(press_anim)

        self._pressed_bg = _darken_hex(bg, 0.82) if self._press_anim else bg
        self._pressed_hover_bg = _darken_hex(self._hover_bg, 0.82) if self._press_anim else self._hover_bg

        self._shape = _round_rect(
            self, 2, 2, width - 2, height - 2,
            r=radius,
            fill=bg,
            outline=outline,
            width=outline_width
        )

        self._label = self.create_text(
            width // 2,
            height // 2,
            text=text,
            fill=fg,
            font=font
        )

        # Prevent enter/leave bounce: label should not receive events
        self.itemconfigure(self._label, state="disabled")
        self.tag_raise(self._label, self._shape)

        # Bind only on canvas
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self._inside = False

    def set_text(self, text: str):
        self.itemconfigure(self._label, text=text)
        self.tag_raise(self._label, self._shape)

    def _on_enter(self, _evt=None):
        self._inside = True
        self.itemconfigure(self._shape, fill=self._hover_bg)
        self.tag_raise(self._label, self._shape)

    def _on_leave(self, _evt=None):
        self._inside = False
        self.itemconfigure(self._shape, fill=self._bg)
        self.tag_raise(self._label, self._shape)

    def _on_press(self, _evt=None):
        if not self._press_anim:
            return
        # pressed color depending on hover state
        self.itemconfigure(self._shape, fill=self._pressed_hover_bg if self._inside else self._pressed_bg)
        self.tag_raise(self._label, self._shape)

    def _on_release(self, _evt=None):
        # restore hover/non-hover color
        self.itemconfigure(self._shape, fill=self._hover_bg if self._inside else self._bg)
        self.tag_raise(self._label, self._shape)

        # click action
        if callable(self._click_sound):
            try:
                self._click_sound()
            except Exception:
                pass
        if callable(self._cmd):
            self._cmd()
