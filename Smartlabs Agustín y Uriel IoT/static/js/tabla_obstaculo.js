var startTime = Date.now(); // Tiempo de inicio en ms
var isPaused = false;
var frecuencia_actualizacion_datos = 200; // Tiempo para obtener nuevos datos del servidor (en ms)
var intervalId = null;
var controller = null;
var dataPoints = []; // Almacenar los datos para guardar en CSV

function updateTable() {
    if (isPaused) return;

    if (controller) {
        controller.abort(); // Abortar solicitudes anteriores
    }

    controller = new AbortController();
    var signal = controller.signal;

    showLoading();

    fetch('/data_obstaculo', { signal: signal })
        .then(response => {
            if (!response.ok) {
                setTimeout(() => {
                    throw new Error('No se pudo obtener los datos. Estado: ' + response.status);
                }, 4000);
            }
            return response.json();
        })
        .then(data => {
            //hideLoading();

            var currentTime = Date.now() - startTime;

            if (data.obstacle !== undefined) {
                addToTable(currentTime, data.obstacle);

                // Guardar datos para CSV
                dataPoints.push({ time: currentTime, distance: data.obstacle });

                // Limitar a los últimos 100 datos
                if (dataPoints.length > 100) {
                    dataPoints.shift(); // Eliminar el primer elemento
                }

                console.log(`Data point added: ${currentTime} ms, ${data.obstacle} cm`);
            } else {
                console.error('Datos de distancia no disponibles.');
            }
        })
        .catch(error => {
            //hideLoading();
            if (error.name === 'AbortError') {
                console.log('Solicitud abortada debido a la pausa');
            } else {
                console.error('Error al obtener los datos:', error);
                alert('Error al obtener los datos. Estado: ' + error.message);
            }
        });
}

function addToTable(time, distance) {
    var tableBody = document.querySelector('#dataTable tbody');
    var newRow = tableBody.insertRow(0); // Inserta la nueva fila en la parte superior

    // Crear celdas
    var timeCell = newRow.insertCell(0);
    var distanceCell = newRow.insertCell(1);

    // Asignar valores a las celdas
    timeCell.textContent = time;
    distanceCell.textContent = distance;

    // Resaltar fila si el valor es 1
    if (distance === 1) {
        newRow.classList.add('highlight-1');
    }

    // Limitar las filas visibles a las últimas 100
    if (tableBody.rows.length > 100) {
        tableBody.deleteRow(100); // Eliminar la fila más antigua
    }
}

function startUpdating() {
    if (intervalId) {
        clearInterval(intervalId);
    }
    intervalId = setInterval(updateTable, frecuencia_actualizacion_datos);
}

function showLoading() {
    document.getElementById('loading').style.visibility = 'visible';
}

function hideLoading() {
    document.getElementById('loading').style.visibility = 'hidden';
}

// Funcionalidad para guardar como CSV
document.getElementById('saveButton').addEventListener('click', function() {
    var csvContent = 'Tiempo (ms),Valor\n';
    dataPoints.forEach(function(row) {
        csvContent += row.time + ',' + row.distance + '\n';
    });

    var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    var link = document.createElement('a');
    var url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'data_obstaculo.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

document.getElementById('pauseButton').addEventListener('click', function() {
    hideLoading();
    isPaused = true;
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
    document.getElementById('pauseButton').disabled = true;
    document.getElementById('resumeButton').disabled = false;
});

document.getElementById('resumeButton').addEventListener('click', function() {
    if (isPaused) {
        isPaused = false;
        startUpdating();
        document.getElementById('resumeButton').disabled = true;
        document.getElementById('pauseButton').disabled = false;
    }
});

document.getElementById('resetButton').addEventListener('click', function() {
    var tableBody = document.querySelector('#dataTable tbody');
    tableBody.innerHTML = ''; // Limpiar la tabla
    dataPoints = []; // Limpiar los datos almacenados
    startTime = Date.now(); // Reiniciar el tiempo
    if (!isPaused) {
        startUpdating();
    }
});

document.getElementById('menuButton').addEventListener('click', function() {
    window.location.href = '/practicas'; // Redirigir al menú de prácticas
});

// Iniciar la actualización de la tabla cuando se carga la página
startUpdating();
