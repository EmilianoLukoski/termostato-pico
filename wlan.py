import network
import time
from settings import SSID, password

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=0xa11140)  # Desactivar modo ahorro de energía
    wlan.connect(SSID, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Esperando conexión WiFi...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('¡Error en la conexion WiFi!')
    else:
        print('Conectado a WiFi')
        print('IP:', wlan.ifconfig()[0])
