import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Configuración
HOST = "0.0.0.0"
PORT = 8000

# Abrir la cámara (0 es la cámara predeterminada)
cap = cv2.VideoCapture(0)

# Ajustar resolución si quieres mejorar velocidad
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 25]

# Variable global para almacenar el último frame
last_frame = None

def capture_frames():
    global last_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Guardamos el último frame para enviarlo cuando se solicite
        last_frame = frame

class CamaraHandler(BaseHTTPRequestHandler):
    def _send_response(self, message):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def do_GET(self):
        if self.path == "/camara":
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()

            try:
                while True:
                    if last_frame is not None:
                        # Codificar frame como JPEG
                        ret, jpeg = cv2.imencode(".jpg", last_frame,encode_param)
                        if ret:
                            # Escribir frame al cliente
                            self.wfile.write(b"--frame\r\n")
                            self.send_header("Content-type", "image/jpeg")
                            self.send_header("Content-length", str(len(jpeg.tobytes())))
                            self.end_headers()
                            self.wfile.write(jpeg.tobytes())
                            self.wfile.write(b"\r\n")
            except Exception as e:
                print(f"[!] Cliente desconectado: {e}")
        elif self.path == "/forward":
            print("Ejecutando: Avanzar")
            self._send_response("Moviendo hacia adelante")

        elif self.path == "/left":
            print("Ejecutando: Girar izquierda")
            self._send_response("Girando a la izquierda")

        elif self.path == "/backward":
            print("Ejecutando: Retroceder")
            self._send_response("Moviendo hacia atrás")

        elif self.path == "/right":
            print("Ejecutando: Girar derecha")
            self._send_response("Girando a la derecha")

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