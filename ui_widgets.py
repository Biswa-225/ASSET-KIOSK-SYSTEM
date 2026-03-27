# ui_widgets.py
from rounded_button import RoundedButton
from config import FONT_FAMILY
from sound_gpio import buzzer


def rbtn(parent, text, command=None,
         width=220, height=70, radius=30,
         bg="#444444", hover=None, fg="white",
         font_size=16, bold=True,
         click_sound=True, press_anim=True):
    """
    Rounded button helper used across all pages.

    - Plays a buzzer click (GPIO) on every press if click_sound=True
    - Keeps consistent style defaults (width/height/radius/fonts/colors)
    - Passes click_sound + press_anim to RoundedButton for UI animation control
    """
    def _wrapped_cmd():
        if click_sound:
            try:
                buzzer.click()
            except Exception:
                pass
        if callable(command):
            command()

    return RoundedButton(
        parent,
        text=text,
        command=_wrapped_cmd,
        width=width,
        height=height,
        radius=radius,
        bg=bg,
        hover_bg=(hover or bg),
        fg=fg,
        font=(FONT_FAMILY, font_size, "bold" if bold else "normal"),
        click_sound=click_sound,
        press_anim=press_anim,
    )
