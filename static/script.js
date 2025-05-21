// Función para mostrar mensajes en la interfaz
function showStatus(message) {
    document.getElementById("statusMessage").textContent = message;
}

// Enviar comando al servidor de comandos (puerto 8001)
function sendCommand(command) {
    showStatus(`Enviando: ${command}`);
    fetch(`${window.location.origin}/command/${command}`)
        .then(response => response.text())
        .then(data => {
            showStatus(`Ejecutado: ${command}`);
        })
        .catch(error => {
            console.error("Error al enviar comando:", error);
            showStatus("Error: No se pudo enviar el comando");
        });
}

document.addEventListener('DOMContentLoaded', () => {
    const buttons = {
        'avanza': 'Avanza',
        'giroIzquierda': 'GiraIzquierda',
        'retrocede': 'Retrocede',
        'giroDerecha': 'GiraDerecha',
        'giroBrazoIzquierda': 'GiraBrazoIzquierda',
        'bajarBrazo': 'BajarBrazo',
        'subirBrazo': 'SubirBrazo',
        'giroBrazoDerecha': 'GiraBrazoDerecha',
        'bajarCamara': 'BajarCamara',
        'subirCamara': 'SubirCamara'
    };

    for (const [id, command] of Object.entries(buttons)) {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', () => {
                sendCommand(command);
            });
        } else {
            console.warn(`Botón no encontrado: ${id}`);
        }
    }

    // Actualizar valor del sensor cada segundo
    /*setInterval(() => {
        fetch(`${window.location.origin}/gas`)
            .then(response => response.json())
            .then(data => {
                document.getElementById("gasValue").textContent = data.gas.toFixed(2);
            })
            .catch(error => {
                console.error("Error al obtener datos del gas:", error);
                document.getElementById("gasValue").textContent = "N/A";
            });
    }, 1000);*/

    // Refrescar imagen de la cámara para evitar caché
    function refreshCameraFeed() {
        const img = document.getElementById("cameraFeed");
        img.src = `${window.location.origin.replace("8001","8000")}/camara`;
    }

    setInterval(refreshCameraFeed, 500);
});