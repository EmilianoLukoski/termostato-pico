import uasyncio as asyncio
from wlan import connect_wifi
#from mqtt import connect_mqtt, publish_data, subscribe_topics
#from storage import load_params

async def main():
    # Conectar WiFi
    connect_wifi()
    

# Iniciar el bucle de asyncio
asyncio.run(main())
