import network
import time
from settings import SSID, password

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=0xa11140)  # Desactivar el modo de ahorro de energía
    wlan.connect(SSID, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Esperando conexión...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('Error de conexión a la red')
    else:
        print('Conectado')
        print('Datos de la red:', wlan.ifconfig())
        return wlan.ifconfig()

if __name__ == "__main__":
    conectar_wifi()
