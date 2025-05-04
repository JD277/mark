import requests

# Configura la IP y puerto del servidor (ajusta según tu caso)
BASE_URL = "http://192.168.0.136"  # Cambia por la IP real
PORT = 8000  # Puerto del servidor (si aplica)

# Función para enviar comandos al servidor
def send_command(endpoint):
    url = f"{BASE_URL}:{PORT}{endpoint}"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            print(f"[+] Comando {endpoint} enviado. Respuesta: {response.text}")
        else:
            print(f"[-] Error al enviar comando {endpoint}. Código: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[!] No se pudo conectar al servidor: {e}")

# Menú interactivo
def menu():
    print("\n=== Control Remoto ===")
    print("1. Avanzar     (forward)")
    print("2. Girar Izquierda (left)")
    print("3. Retroceder  (backward)")
    print("4. Girar Derecha   (right)")
    print("5. Salir")
    choice = input("Elige una opción: ")
    return choice

# Bucle principal
if __name__ == "__main__":
    while True:
        option = menu()
        if option == "1":
            send_command("/forward")
        elif option == "2":
            send_command("/left")
        elif option == "3":
            send_command("/backward")
        elif option == "4":
            send_command("/right")
        elif option == "5":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")