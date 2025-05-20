import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import cv2
import random

# Configuración
HOST = "0.0.0.0"
PORT = 8000

# Abrir la cámara
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

last_frame = None
propano_value = 0

def capture_frames():
    global last_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (320, 240))
        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        if ret:
            last_frame = jpeg.tobytes()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Servir archivos estáticos
        if self.path.startswith("/static/"):
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

        # Ruta principal
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())

        # Transmisión MJPEG
        elif self.path == "/camara":
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

        # Comandos
        elif self.path.startswith("/command"):
            command = self.path.split("/")[-1]
            print(f"[+] Comando recibido: {command}")
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes(f"Comando ejecutado: {command}", "utf-8"))

        # Sensor de gas
        elif self.path == "/gas":
            propano_value = random.uniform(0, 1.0)  # Simulación
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(f'{{"gas": {propano_value}}}', "utf-8"))

        else:
            self.send_error(404, "No encontrado")

def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"[Servidor iniciado] Escuchando en http://{HOST}:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Iniciar captura de frames en un hilo separado
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()

    # Iniciar servidor HTTP
    run_server()