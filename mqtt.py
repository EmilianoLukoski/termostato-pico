from mqtt_as import MQTTClient, config
from settings import BROKER, SSID, password

config["server"] = BROKER
config["ssid"] = SSID
config["wifi_pw"] = password

client = MQTTClient(config)

def iniciar_mqtt():
    return client