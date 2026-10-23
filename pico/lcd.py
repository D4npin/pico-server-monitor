from machine import Pin
import time

class LCD:
    def __init__(self, rs, e, d4, d5, d6, d7):
        self.rs = Pin(rs, Pin.OUT)
        self.e = Pin(e, Pin.OUT)
        self.d = [Pin(p, Pin.OUT) for p in (d4, d5, d6, d7)]
        time.sleep_ms(50)
        self._nibble(0x3, 0); time.sleep_ms(5)
        self._nibble(0x3, 0); time.sleep_us(150)
        self._nibble(0x3, 0)
        self._nibble(0x2, 0)
        self.cmd(0x28)  # 4 bit, 2 righe
        self.cmd(0x0C)  # display on, cursore off
        self.cmd(0x06)
        self.clear()

    def _nibble(self, n, rs):
        self.rs.value(rs)
        for i, p in enumerate(self.d):
            p.value((n >> i) & 1)
        self.e.value(1); time.sleep_us(2)
        self.e.value(0); time.sleep_us(50)

    def _byte(self, b, rs):
        self._nibble(b >> 4, rs)
        self._nibble(b & 0xF, rs)

    def cmd(self, c):
        self._byte(c, 0)
        if c in (1, 2):
            time.sleep_ms(2)

    def clear(self):
        self.cmd(1)

    def write(self, line, text):
        self.cmd(0x80 | (0x40 * line))
        for ch in text[:16] + " " * (16 - len(text[:16])):
            self._byte(ord(ch), 1)
