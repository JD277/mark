from http.server import BaseHTTPRequestHandler, HTTPServer

# Dirección IP y puerto del servidor
HOST = "0.0.0.0"  # Escucha en todas las interfaces
PORT = 8000

class RequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, message):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def do_GET(self):
        print(f"[Solicitud recibida] Ruta: {self.path}")
        if self.path == "/forward":
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
            print("Ruta no reconocida")
            self.send_error(404, "No encontrado")

def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"[Servidor iniciado] Escuchando en http://{HOST}:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()