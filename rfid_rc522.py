# rfid_rc522.py
# SINGLETON + STABLE RC522 READER FOR RASPBERRY PI

import time
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

_rc522_singleton = None


class RC522Reader:
    """
    Singleton RC522 reader.
    Ensures SPI + GPIO are initialized ONLY ONCE.
    """

    def __new__(cls, *args, **kwargs):
        global _rc522_singleton
        if _rc522_singleton is None:
            _rc522_singleton = super().__new__(cls)
        return _rc522_singleton

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        self.reader = MFRC522()
        time.sleep(0.2)  # allow RC522 to settle

    # --------------------------------------------------
    # READ UID (HEX STRING)
    # --------------------------------------------------
    def read_uid_hex(self, timeout_s=8.0):
        print("[RC522] Waiting for card...")
        start = time.time()

        while time.time() - start < timeout_s:
            (status, _) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            if status != self.reader.MI_OK:
                time.sleep(0.05)
                continue

            (status, uid) = self.reader.MFRC522_Anticoll()
            if status == self.reader.MI_OK:
                uid_hex = "".join(f"{x:02X}" for x in uid)
                print(f"[RC522] UID detected: {uid_hex}")
                time.sleep(0.3)  # IMPORTANT: avoid re-trigger
                return uid_hex

            time.sleep(0.05)

        return None

    # --------------------------------------------------
    # WRITE TEXT (OPTIONAL)
    # --------------------------------------------------
    def write_text(self, text, block=8, timeout_s=8.0):
        data = list(text.ljust(16)[:16].encode("ascii"))

        start = time.time()
        while time.time() - start < timeout_s:
            (status, _) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            if status != self.reader.MI_OK:
                time.sleep(0.05)
                continue

            (status, uid) = self.reader.MFRC522_Anticoll()
            if status != self.reader.MI_OK:
                time.sleep(0.05)
                continue

            key = [0xFF] * 6
            self.reader.MFRC522_SelectTag(uid)
            status = self.reader.MFRC522_Auth(
                self.reader.PICC_AUTHENT1A, block, key, uid
            )
            if status != self.reader.MI_OK:
                return False

            self.reader.MFRC522_Write(block, data)
            self.reader.MFRC522_StopCrypto1()
            time.sleep(0.3)
            return True

        return False
