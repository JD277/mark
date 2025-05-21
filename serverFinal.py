import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os
import random
from board import ArduinoController  # 🔁 Importamos desde otro archivo

# Configuración
VIDEO_PORT = 8000
COMMAND_PORT = 8001
HOST = "0.0.0.0"

# Abrir la cámara
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

last_frame = None
propano_value = 0

# Inicializar el controlador de Arduino
arduino = ArduinoController("COM4")  # Cambia por tu puerto real

# Configurar componentes del Arduino
arduino.setup_motor(2, 3, "motor_izquierda", 5)
arduino.setup_motor(7, 8, "motor_derecha", 6)
arduino.setup_gas_sensor(0, "mq2")  # Sensor MQ2 en A0

def capture_frames():
    global last_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (160, 120))
        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        if ret:
            last_frame = jpeg.tobytes()

# ----------------------------
# Servidor de Video (Puerto 8000)
# ----------------------------

class VideoRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/camara":
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()

            try:
                while True:
                    if last_frame is not None:
                        self.wfile.write(b"--frame\r\n")
                        self.send_header("Content-type", "image/jpeg")
                        self.send_header("Content-length", str(len(last_frame)))
                        self.end_headers()
                        self.wfile.write(last_frame)
                        self.wfile.write(b"\r\n")
            except Exception as e:
                print(f"[!] Cliente desconectado: {e}")

        else:
            self.send_error(404, "No encontrado")

def run_video_server():
    server_address = (HOST, VIDEO_PORT)
    httpd = HTTPServer(server_address, VideoRequestHandler)
    print(f"[Servidor de Video] Escuchando en http://{HOST}:{VIDEO_PORT}")
    httpd.serve_forever()

# ----------------------------
# Servidor de Comandos (Puerto 8001)
# ----------------------------

class CommandRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Ruta principal
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())

        # Servir archivos estáticos
        elif self.path.startswith("/static/"):
            file_path = self.path[1:]  # Quitar el '/'
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    self.send_response(200)
                    if file_path.endswith(".css"):
                        self.send_header("Content-type", "text/css")
                    elif file_path.endswith(".js"):
                        self.send_header("Content-type", "application/javascript")
                    self.end_headers()
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Archivo no encontrado")

        # Comandos
        elif self.path.startswith("/command"):
            command = self.path.split("/")[-1]
            print(f"[+] Comando recibido: {command}")

            if command == "Avanza":
                arduino.set_motor_speed("motor_izquierda", 255)
                arduino.set_motor_speed("motor_derecha", 255)
            elif command == "Retrocede":
                arduino.set_motor_speed("motor_izquierda", -255)
                arduino.set_motor_speed("motor_derecha", -255)
            elif command == "GiraIzquierda":
                arduino.set_motor_speed("motor_izquierda", -255)
                arduino.set_motor_speed("motor_derecha", 255)
            elif command == "GiraDerecha":
                arduino.set_motor_speed("motor_izquierda", 255)
                arduino.set_motor_speed("motor_derecha", -255)
            elif command == "Detener":
                arduino.set_motor_speed("motor_izquierda", 0)
                arduino.set_motor_speed("motor_derecha", 0)

            # Agregar más comandos para brazo y camara si es necesario

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes(f"Comando ejecutado: {command}", "utf-8"))

        # Sensor de gas
        elif self.path == "/gas":
            gas_level = arduino.read_gas_sensor("mq2")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(f'{{"gas": {gas_level}}}', "utf-8"))

        else:
            self.send_error(404, "No encontrado")

def run_command_server():
    server_address = (HOST, COMMAND_PORT)
    httpd = HTTPServer(server_address, CommandRequestHandler)
    print(f"[Servidor de Comandos] Escuchando en http://{HOST}:{COMMAND_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Iniciar captura de frames en un hilo
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()

    # Iniciar servidor de video
    video_thread = threading.Thread(target=run_video_server, daemon=True)
    video_thread.start()

    # Iniciar servidor de comandos
    run_command_server()