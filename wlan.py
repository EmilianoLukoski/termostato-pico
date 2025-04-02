import network
import time
from settings import SSID, password

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, password)
    print("Conectando a WiFi...")
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("Esperando conexion...")
        time.sleep(1)
    if wlan.status() != 3:
        raise RuntimeError("Error en la conexion de red")
    print("Conectado a WiFi")
    print("Direccion IP:", wlan.ifconfig()[0])
    return wlan


### mqtt.py
from mqtt_as import MQTTClient, config
from settings import BROKER, SSID, password

config["server"] = BROKER
config["ssid"] = SSID
config["wifi_pw"] = password

client = MQTTClient(config)

def iniciar_mqtt():
    return client