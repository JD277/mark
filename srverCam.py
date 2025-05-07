import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import random  # Simulación del sensor de propano

# Configuración
HOST = "0.0.0.0"
PORT = 8000

# Abrir la cámara (0 es la predeterminada)
cap = cv2.VideoCapture(0)

# Ajustar resolución baja para reducir latencia
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Variable global para almacenar el último frame
last_frame = None

# Simulación del sensor de propano
propano_value = 0

def capture_frames():
    global last_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        last_frame = frame

class CamaraHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/camara":
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()

            try:
                while True:
                    if last_frame is not None:
                        ret, jpeg = cv2.imencode(".jpg", last_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                        if ret:
                            self.wfile.write(b"--frame\r\n")
                            self.send_header("Content-type", "image/jpeg")
                            self.send_header("Content-length", str(len(jpeg.tobytes())))
                            self.end_headers()
                            self.wfile.write(jpeg.tobytes())
                            self.wfile.write(b"\r\n")
            except Exception as e:
                print(f"[!] Cliente desconectado: {e}")

        elif self.path.startswith("/command"):
            command = self.path.split("/")[-1]
            print(f"[+] Comando recibido: {command}")
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes(f"Comando ejecutado: {command}", "utf-8"))

        elif self.path == "/propano":
            global propano_value
            propano_value = random.randint(0, 100)  # Simulación
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(f'{{"propano": {propano_value}}}', "utf-8"))

        else:
            self.send_error(404, "No encontrado")

def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, CamaraHandler)
    print(f"[Servidor iniciado] Escuchando en http://{HOST}:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Iniciar captura de frames en un hilo separado
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()

    # Iniciar servidor HTTP
    run_server()