import network, time
from machine import Pin
try:
    import urequests as requests
except ImportError:
    import requests
from lcd import LCD
from config import SSID, PASSWORD, GLANCES, TEMP_ON, TEMP_BLINK, DISKS

lcd = LCD(rs=16, e=17, d4=18, d5=19, d6=20, d7=21)
led = Pin(15, Pin.OUT)
btn = Pin(14, Pin.IN, Pin.PULL_UP)

N_PAGES = 3
REFRESH_MS = 3000
page = 0
pressed = False
last_press = 0


def on_button(p):
    global pressed, last_press
    now = time.ticks_ms()
    if time.ticks_diff(now, last_press) > 250:
        last_press = now
        pressed = True

btn.irq(trigger=Pin.IRQ_FALLING, handler=on_button)


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        for _ in range(20):
            if wlan.isconnected():
                break
            lcd.write(0, "Connessione WiFi")
            time.sleep(1)
    return wlan


def get(path):
    r = requests.get(GLANCES + "/api/4/" + path)
    try:
        return r.json()
    finally:
        r.close()


def read_temp():
    best = None
    for s in get("sensors"):
        if "temperature" in str(s.get("type", "")):
            v = s.get("value")
            if v is not None and (best is None or v > best):
                best = v
    return best


def update_led(temp):
    if temp is None or temp < TEMP_ON:
        led.value(0)
    elif temp >= TEMP_BLINK:
        led.value((time.ticks_ms() // 300) % 2)
    else:
        led.value(1)


def disk_line(fs, label, mnt):
    for f in fs:
        if f.get("mnt_point") == mnt:
            free_gb = f["free"] / 1024**3
            return "%-3s %2d%% lib %3dG" % (label, f["percent"], free_gb)
    return "%-3s n/d" % label


def show_page(p, temp):
    if p == 0:
        cpu = get("cpu")["total"]
        mem = get("mem")
        t = -1 if temp is None else temp
        lcd.write(0, "CPU %3d%%  T %3dC" % (cpu, t))
        lcd.write(1, "Lib %.1fG Us %2d%%" % (mem["available"] / 1024**3, mem["percent"]))
    elif p == 1:
        fs = get("fs")
        for i in range(2):
            if i < len(DISKS):
                lcd.write(i, disk_line(fs, DISKS[i][0], DISKS[i][1]))
            else:
                lcd.write(i, "")
    else:
        up = get("uptime")
        if isinstance(up, dict):
            up = list(up.values())[0]
        ld = get("load")
        lcd.write(0, "Up " + str(up)[:13])
        lcd.write(1, "L %.1f %.1f %.1f" % (ld["min1"], ld["min5"], ld["min15"]))


wlan = connect()
temp = None
last = time.ticks_add(time.ticks_ms(), -REFRESH_MS)

while True:
    now = time.ticks_ms()
    if pressed or time.ticks_diff(now, last) >= REFRESH_MS:
        if pressed:
            page = (page + 1) % N_PAGES
            pressed = False
        last = now
        try:
            if not wlan.isconnected():
                wlan = connect()
            temp = read_temp()
            show_page(page, temp)
        except Exception as e:
            print(e)
            temp = None
            lcd.write(0, "Glances offline")
            lcd.write(1, "Riprovo...")
    update_led(temp)
    time.sleep_ms(50)
