var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Etiquetas del eje X
        datasets: [
            {
                label: 'Puntos de Distancia (cm)',
                data: [], // Datos de los puntos
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                pointRadius: 6, // Tamaño de los puntos
                pointBorderColor: 'rgba(75, 192, 192, 1)',
                pointBackgroundColor: 'rgba(255, 255, 255, 0.8)', // Fondo blanco para los puntos
                pointBorderWidth: 2, // Grosor del borde del punto
                fill: false,
                showLine: false // Desactivar la línea
            },
            {
                label: 'Línea de Distancia (cm)',
                data: [], // Datos de la línea
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2,
                fill: false,
                tension: 0.4, // Suavizar la línea del gráfico
                showLine: true, // Asegurar que la línea esté visible
                pointRadius: 0 // No mostrar puntos en la línea
            }
        ]
    },
    options: {
        animation: {
            duration: 1000 // Añadir animación suave
        },
        scales: {
            x: {
                type: 'linear',
                position: 'bottom',
                title: {
                    display: true,
                    text: 'Tiempo (s)',
                    color: '#ffffff'
                },
                ticks: {
                    callback: function(value) {
                        return (value / 1000).toFixed(2); // Convertir a segundos
                    },
                    color: '#ffffff'
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.2)'
                },
                min: 0, // El tiempo arranca en 0
                max: 20000 // Establecer el rango de 20 segundos por defecto
            },
            y: {
                title: {
                    display: true,
                    text: 'Distancia (cm)',
                    color: '#ffffff'
                },
                ticks: {
                    min: 0,
                    max: 300,
                    stepSize: 10,
                    color: '#ffffff'
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.2)'
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: '#ffffff'
                }
            },
            tooltip: {
                backgroundColor: '#333333',
                titleColor: '#ffffff',
                bodyColor: '#ffffff'
            }
        }
    }
});

var startTime = Date.now(); // Tiempo de inicio en ms
var isPaused = false;
var frecuencia_actualizacion_datos = 200; // Tiempo para obtener nuevos datos del servidor (en ms)
var intervalId = null; // Identificador del intervalo
var controller = null; // Controlador global para abortar solicitudes

function updateChart() {
    if (isPaused) return; // Evitar actualizaciones si está pausado

    if (controller) {
        controller.abort(); // Abortar cualquier solicitud anterior
    }

    controller = new AbortController();
    var signal = controller.signal;

    showLoading(); // Mostrar el indicador de carga

    fetch('/data_hall', { signal: signal })
    .then(response => {
        if (!response.ok) {
            //espera 4 segundos
            setTimeout(() => {
                throw new Error('No se pudo obtener los datos. Estado: ' + response.status);
            }, 4000);
            
        }
        
        return response.json();
    })
    .then(data => {
        //hideLoading(); // Ocultar el indicador de carga

        console.log('Datos recibidos:', data); // Mensaje de depuración

        var requestTime = Date.now(); // Tiempo de solicitud completada

        if (data.mgfield !== undefined) {
            var currentTime = Date.now() - startTime; // Tiempo transcurrido desde el inicio

            // Agregar los datos al gráfico
            myChart.data.labels.push(currentTime);
            myChart.data.datasets[0].data.push({ x: currentTime, y: data.mgfield }); // Agregar punto
            myChart.data.datasets[1].data.push({ x: currentTime, y: data.mgfield }); // Agregar punto a la línea

            // Mantener solo los últimos 10 segundos de datos
            var tenSeconds = 10000; // 10 segundos en ms
            var cutoffTime = currentTime - tenSeconds;

            // Eliminar los datos antiguos
            while (myChart.data.labels.length > 0 && myChart.data.labels[0] < cutoffTime) {
                myChart.data.labels.shift();
                myChart.data.datasets.forEach(dataset => dataset.data.shift());
            }

            // Ajustar el rango del eje X de manera gradual
            var minX = myChart.data.labels[0] || 0;
            var maxX = minX + tenSeconds;

            // Ajustar el rango del eje X de manera gradual para suavizar el desplazamiento
            if (Math.abs(myChart.options.scales.x.min - minX) > frecuencia_actualizacion_datos / 2 ||
                Math.abs(myChart.options.scales.x.max - maxX) > frecuencia_actualizacion_datos / 2) {
                myChart.options.scales.x.min = minX;
                myChart.options.scales.x.max = maxX;
                myChart.update('none'); // Actualización sin animación
            }

            // Actualizar el gráfico sin animación
            myChart.update('none'); // Actualización sin animación

            console.log(`Data point added: ${currentTime} ms, ${data.hall} cm`);
        } else {
            console.error('Datos hall no disponibles.');
        }
    })
    .catch(error => {
        //hideLoading(); // Ocultar el indicador de carga
        if (error.name === 'AbortError') {
            console.log('Solicitud abortada debido a la pausa');
        } else {
            console.error('Error al obtener los datos:', error);
            alert('Error al obtener los datos. Estado: ' + error.message); // Mostrar mensaje de error
        }
    });
}


function startUpdating() {
    if (intervalId) {
        clearInterval(intervalId); // Asegúrate de que no haya intervalos previos
    }
    intervalId = setInterval(updateChart, frecuencia_actualizacion_datos); // Actualizar cada 200 ms
}

function showLoading() {
    document.getElementById('loading').style.visibility = 'visible';
}

function hideLoading() {
    document.getElementById('loading').style.visibility = 'hidden';
}

document.getElementById('pauseButton').addEventListener('click', function() {
    hideLoading(); // Ocultar el indicador de carga
    isPaused = true;
    if (intervalId) {
        clearInterval(intervalId); // Detener las solicitudes futuras
        intervalId = null; // Asegurarse de que el identificador del intervalo sea nulo
    }
    document.getElementById('pauseButton').disabled = true;
    document.getElementById('resumeButton').disabled = false;
});

document.getElementById('resumeButton').addEventListener('click', function() {
    if (isPaused) {
        isPaused = false;
        startUpdating(); // Reanudar las actualizaciones
        document.getElementById('resumeButton').disabled = true;
        document.getElementById('pauseButton').disabled = false;
    }
});

document.getElementById('resetButton').addEventListener('click', function() {
    myChart.data.labels = [];
    myChart.data.datasets.forEach(dataset => dataset.data = []);
    myChart.update('none'); // Actualización sin animación
    startTime = Date.now(); // Reiniciar el tiempo de inicio
    if (!isPaused) {
        startUpdating(); // Reiniciar la actualización si no está pausado
    }
});

document.getElementById('menuButton').addEventListener('click', function() {
    window.location.href = '/practicas'; // Redirigir al menú de prácticas
});

startUpdating();
