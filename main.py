from wlan import connect_wifi
import uasyncio as asyncio
from mqtt import connect_mqtt, publish_status, mqtt_loop

async def main():
    connect_wifi()  # Conectar a la red WiFi
    await connect_mqtt()  # Conectar al broker MQTT

    # Iniciar la publicación periódica de parámetros
    asyncio.create_task(publish_status())

    # Mantener la conexión activa
    await mqtt_loop()

# Ejecutar el programa
asyncio.run(main())
