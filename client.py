import flet as ft
import requests
from PIL import Image
from io import BytesIO
import threading
import time

# Dirección del servidor
SERVER_URL = "http://192.168.139.217:8000"  # Cambia por tu IP

# Variables globales
propano_value = 0

def update_propano(page):
    """Actualiza el valor del sensor de propano."""
    global propano_value
    try:
        response = requests.get(f"{SERVER_URL}/propano")
        data = response.json()
        propano_value = data["propano"]
    except Exception as e:
        print(f"[!] Error al obtener propano: {e}")

def send_command(command):
    """Envía un comando al servidor."""
    try:
        requests.get(f"{SERVER_URL}/command/{command}")
    except Exception as e:
        print(f"[!] Error al enviar comando: {e}")

def update_camera(camera_image):
    """Actualiza la imagen de la cámara."""
    try:
        response = requests.get(f"{SERVER_URL}/camara", stream=True)
        bytes_data = b""
        for chunk in response.iter_content(chunk_size=1024):
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8')  # Inicio de imagen JPEG
            b = bytes_data.find(b'\xff\xd9')  # Fin de imagen JPEG
            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                image = Image.open(BytesIO(jpg))
                buffer = BytesIO()
                image.save(buffer, format="JPEG")
                img_str = buffer.getvalue().decode('iso-8859-1')
                camera_image.src_base64 = img_str
                break
    except Exception as e:
        print(f"[!] Error al actualizar cámara: {e}")

def periodic_update(page, camera_image):
    """Función que se ejecuta en segundo plano para actualizar imágenes y sensores."""
    while True:
        update_propano(page)
        update_camera(camera_image)
        page.update()
        time.sleep(0.5)  # Actualización cada 0.5 segundos

def main(page: ft.Page):
    # Estilo de la página
    page.title = "Control Remoto con Cámara y Sensor de Propano"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Sección de la cámara
    camera_image = ft.Image(
        src_base64="",
        width=320,
        height=240,
        fit=ft.ImageFit.CONTAIN,
    )

    # Sección del sensor de propano
    propano_label = ft.Text(
        value=f"Propano: {propano_value}%",
        size=20,
        color=ft.Colors.WHITE,
    )

    # Cruceta de control
    def on_arrow_click(e):
        if e.control.data == "up":
            send_command("forward")
        elif e.control.data == "down":
            send_command("backward")
        elif e.control.data == "left":
            send_command("left")
        elif e.control.data == "right":
            send_command("right")

    arrow_buttons = [
        ft.ElevatedButton(
            on_click=on_arrow_click,
            data="up",
            text='up',
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        ),
        ft.Row(
            [
                ft.ElevatedButton(
                    on_click=on_arrow_click,
                    data="left",
                    text='left',
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                ),
                ft.ElevatedButton(
                    on_click=on_arrow_click,
                    data="down",
                    text='down',
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                ),
                ft.ElevatedButton(
                    on_click=on_arrow_click,
                    data="right",
                    text='right',
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    ]

    # Diseño de la interfaz
    content = ft.Column(
        [
            ft.Container(
                content=camera_image,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Text(
                    value="Control Remoto",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=propano_label,
                            alignment=ft.alignment.center,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Column(
                    arrow_buttons,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
    )

    page.add(content)

    # Iniciar actualizaciones periódicas en un hilo
    def start_periodic_update():
        thread = threading.Thread(target=periodic_update, args=(page, camera_image), daemon=True)
        thread.start()

    start_periodic_update()

# Iniciar la aplicación Flet
ft.app(target=main)