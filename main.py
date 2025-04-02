from mqtt_as import MQTTClient, config
import asyncio
import ujson as json
import machine, dht, network, time
from settings import SSID, password, BROKER  

# Asignación de pines
rele = machine.Pin(6, machine.Pin.OUT)
led = machine.Pin(2, machine.Pin.OUT)

# Inicializar sensor DHT22 con manejo de error
dht_available = True
try:
    sensor = dht.DHT22(machine.Pin(15))
except Exception as e:
    print(f"Error al inicializar DHT22: {e}")
    dht_available = False

# Variables globales
global setpoint, periodo, modo, estado_rele, temperatura
CONFIG_FILE = "config.json"

async def guardar_config():
    try:
        data = {
            "setpoint": setpoint,
            "periodo": periodo,
            "modo": modo,
            "estado_rele": estado_rele
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
        print("Configuración guardada correctamente.")
    except Exception as e:
        print(f"Error al guardar configuración: {e}")

async def cargar_config():
    global setpoint, periodo, modo, estado_rele
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            setpoint = data.get("setpoint", 25)
            periodo = data.get("periodo", 10)
            modo = data.get("modo", 1)
            estado_rele = data.get("estado_rele", 0)
        print("Configuración cargada correctamente.")
    except (OSError, ValueError) as e:
        print(f"Error al cargar configuración: {e}")
        setpoint, periodo, modo, estado_rele = 25, 10, 1, 0
        asyncio.create_task(guardar_config())

# Obtener ID único
id = "".join("{:02X}".format(b) for b in machine.unique_id())

asyncio.create_task(cargar_config())

# Conexión WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, password)

print("Conectando a WiFi...")
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print("Esperando conexión...")
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError("Error en la conexión de red")
else:
    print("Conectado a WiFi")
    print("Dirección IP:", wlan.ifconfig()[0])

# Configuración MQTT
config['server'] = BROKER
config['ssid'] = SSID
config['wifi_pw'] = password

async def conexion(client):
    while True:
        await client.up.wait()
        client.up.clear()
        for sub in ["setpoint", "periodo", "destello", "modo", "rele"]:
            await client.subscribe(f"{id}/{sub}", 1)

async def mensajes(client):
    async for topic, msg, retained in client.queue:
        global setpoint, periodo, modo, estado_rele
        mensaje = msg.decode()
        subtopic = topic.decode().split("/")[-1]
        print(f"Mensaje recibido: {subtopic} = {mensaje}")
        
        if subtopic == "setpoint" and modo == 1:  # Modo automático
            try:
                setpoint = float(mensaje)
            except:
                print("Error en el tipo de la variable. Espera un flotante.")
            asyncio.create_task(control_rele())
            asyncio.create_task(guardar_config()) 
        
        elif subtopic == "periodo":
            try:
                periodo = int(mensaje)
            except:
                print("Error en el tipo de la variable. Espera un entero.")
            asyncio.create_task(guardar_config())
        
        elif subtopic == "modo":
            try:
                modo = int(mensaje)
            except:
                print("Error en el tipo de la variable. Espera un entero.")
            asyncio.create_task(control_rele()) 
            asyncio.create_task(guardar_config())
        
        elif subtopic == "rele" and modo == 0:  # Modo manual
            try:
                estado_rele = int(mensaje)
            except:
                print("Error en el tipo de la variable. Espera un entero.") 
            asyncio.create_task(control_rele())
            asyncio.create_task(guardar_config())
        
        elif subtopic == "destello":
            asyncio.create_task(destellar_led())

async def control_rele():
    if modo == 1:  # Automático
        rele.value(temperatura > setpoint)
    else:  # Manual
        rele.value(estado_rele)

async def destellar_led():
    for _ in range(10):
        led.on()
        await asyncio.sleep(0.2)
        led.off()
        await asyncio.sleep(0.2)
        
async def limpiar_mensajes_retained(client):
    temas = ["setpoint", "periodo", "destello", "modo", "rele"]
    for tema in temas:
        await client.publish(f"{id}/{tema}", "", qos=1, retain=True)

async def main(client):
    await client.connect()
    await limpiar_mensajes_retained(client)
    asyncio.create_task(conexion(client))   
    asyncio.create_task(mensajes(client))
    asyncio.create_task(control_rele())
    
    global temperatura
    while True:
        try:
            if dht_available:
                sensor.measure()
                temperatura = sensor.temperature()
                humedad = sensor.humidity()
            else:
                raise Exception("Sensor no disponible")
        except Exception as e:
            print(f"Error al leer DHT22: {e}")
            temperatura, humedad = 25.0, 60.0  # Valores por defecto
        
        data = {
            "temperatura": temperatura,
            "humedad": humedad,
            "setpoint": setpoint,
            "periodo": periodo,
            "modo": modo
        }
        
        await client.publish(id, json.dumps(data), qos=1)
        await asyncio.sleep(periodo)

# Configuración MQTT
config["queue_len"] = 1
MQTTClient.DEBUG = True
client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:
    client.close()