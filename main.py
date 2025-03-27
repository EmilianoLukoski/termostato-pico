import wlan

try:
    ip_info = wlan.conectar_wifi()
    print("Conexión exitosa:", ip_info)
except RuntimeError as e:
    print("Error:", e)
