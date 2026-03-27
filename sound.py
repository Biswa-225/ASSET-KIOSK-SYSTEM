# sound_gpio.py
import time
import threading

try:
    from gpiozero import PWMOutputDevice
except Exception:
    PWMOutputDevice = None


class ClickBuzzer:
    """
    3-pin buzzer/speaker click via GPIO PWM.
    - Works with active buzzer modules (most 3-pin Gravity sounders).
    - If your module is passive (speaker), this still works (tone output).
    """
    def __init__(self, gpio_pin=18, enabled=True):
        self.enabled = enabled
        self.gpio_pin = gpio_pin
        self._lock = threading.Lock()
        self._last = 0.0

        self._pwm = None
        if PWMOutputDevice is not None and enabled:
            # frequency not set here; we set per click
            self._pwm = PWMOutputDevice(gpio_pin, initial_value=0.0, frequency=2000)

    def click(self, freq=2200, dur=0.02, gap=0.01, volume=0.6):
        """
        freq: Hz
        dur : seconds for the tone
        volume: 0..1 PWM duty
        """
        if not self.enabled or self._pwm is None:
            return

        now = time.time()
        with self._lock:
            # debounce: prevent double-touch events creating two clicks
            if now - self._last < 0.05:
                return
            self._last = now

            try:
                self._pwm.frequency = int(freq)
                self._pwm.value = float(volume)
                time.sleep(float(dur))
                self._pwm.value = 0.0
                time.sleep(float(gap))
            except Exception:
                # never break UI due to sound errors
                try:
                    self._pwm.value = 0.0
                except Exception:
                    pass

    def close(self):
        try:
            if self._pwm:
                self._pwm.value = 0.0
                self._pwm.close()
        except Exception:
            pass


# Global instance used by UI
buzzer = ClickBuzzer(gpio_pin=18, enabled=True)
