// Función para enviar comandos al servidor
function sendCommand(command) {
    console.log("Enviando comando:", command);

    fetch(`/command/${encodeURIComponent(command)}`)
        .then(response => response.text())
        .then(data => {
            console.log("Servidor respondió:", data);
        })
        .catch(error => {
            console.error("Error al enviar comando:", error);
        });
}

// Asignar eventos a cada botón
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
    setInterval(() => {
        fetch("/gas")
            .then(response => response.json())
            .then(data => {
                document.getElementById("gasValue").textContent = data.gas.toFixed(2);
            })
            .catch(error => console.error("Error al obtener datos del gas:", error));
    }, 1000);

    // Refrescar imagen de la cámara para evitar caché
    function refreshCameraFeed() {
        const img = document.getElementById("cameraFeed");
        img.src = `/camara`;
    }

    setInterval(refreshCameraFeed, 1000);
});