from flask import Flask, render_template, request, jsonify
import subprocess
from modules.sensor_distancia import Sensor
from modules.sensor_obstaculo import SensorObstaculo
from modules.sensor_hall import SensorHall
import atexit
import json
import signal
import sys
import threading

app = Flask(__name__)

# Variables para las instancias de los sensores
sensor_distancia = None
sensor_obstaculo = None
sensor_hall = None

# Inicializar el sensor
def initialize_sensor_distancia():
    global sensor_distancia
    if not sensor_distancia:
        try:
            sensor_distancia = Sensor()
            print("Sensor de distancia activado")
        except Exception as e:
            print(f"Error al activar el sensor de distancia: {e}")
    else:
        if sensor_distancia.running == False:
            try:
                sensor_distancia = Sensor()
                print("Sensor de distancia activado")
            except Exception as e:
                print(f"Error al activar el sensor de distancia: {e}")

def initialize_sensor_obstaculo():
    global sensor_obstaculo
    if not sensor_obstaculo:
        try:
            sensor_obstaculo = SensorObstaculo()
            print("Sensor de obstaculo activado")
        except Exception as e:
            print(f"Error al activar el sensor de obstaculo: {e}")
    else:
        if sensor_obstaculo.running == False:
            try:
                sensor_obstaculo = SensorObstaculo()
                print("Sensor de obstaculo activado")
            except Exception as e:
                print(f"Error al activar el sensor de obstaculo: {e}")

# Inicializar el sensor
def initialize_sensor_hall():
    global sensor_hall
    if not sensor_hall:
        try:
            sensor_hall = SensorHall()
            print("Sensor hall activado")
        except Exception as e:
            print(f"Error al activar el sensor hall: {e}")
    else:
        if sensor_hall.running == False:
            try:
                sensor_hall = SensorHall()
                print("Sensor hall activado")
            except Exception as e:
                print(f"Error al activar el sensor hall: {e}")

# Registrar una función para cerrar ambos sensores al terminar la aplicación
def cleanup():
    global sensor_distancia, sensor_obstaculo
    
    if sensor_distancia:
        try:
            print("Deteniendo el sensor de distancia...")
            sensor_distancia.stop()
        except Exception as e:
            print(f"Error al detener el sensor de distancia: {e}")
    
    if sensor_obstaculo:
        try:
            print("Deteniendo el sensor de obstáculos...")
            sensor_obstaculo.stop()
        except Exception as e:
            print(f"Error al detener el sensor de obstáculos: {e}")

    if sensor_hall:
        try:
            print("Deteniendo el sensor de hall...")
            sensor_hall.stop()
        except Exception as e:
            print(f"Error al detener el sensor de hall: {e}")
atexit.register(cleanup)  # Registrar la función de limpieza para ser llamada al salir de la aplicación

# Función para listar los hilos en ejecución
def list_threads():
    threads = threading.enumerate()
    thread_info = [{"name": thread.name, "is_alive": thread.is_alive()} for thread in threads]
    return thread_info

# Ruta principal que muestra la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/practicas')
def practicas():
    cleanup()
    return render_template('practicas.html')

# Ruta para ejecutar armonico.py
@app.route('/run_armonico', methods=['POST'])
def run_armonico():
    try:
        result = subprocess.run(['python', 'modules/armonico.py'], capture_output=True, text=True)
        return jsonify({"output": result.stdout, "error": result.stderr})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para ejecutar otros módulos, por ejemplo pendulo.py
@app.route('/run_pendulo', methods=['POST'])
def run_pendulo():
    try:
        result = subprocess.run(['python', 'modules/pendulo.py'], capture_output=True, text=True)
        return jsonify({"output": result.stdout, "error": result.stderr})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para mostrar graph_distancia.html
@app.route('/graph_distancia')
def graph_distancia():
    initialize_sensor_distancia()
    return render_template('graph_distancia.html')

# Ruta para mostrar graph_obstaculo.html
@app.route('/graph_obstaculo')
def graph_obstaculo():
    initialize_sensor_obstaculo()
    return render_template('graph_obstaculo.html')

# Ruta para mostrar table_obstaculo.html
@app.route('/table_obstaculo')
def table_obstaculo():
    initialize_sensor_obstaculo()
    return render_template('table_obstaculo.html')

# Ruta para mostrar graph_hall.html
@app.route('/graph_hall')
def graph_hall():
    initialize_sensor_hall()
    return render_template('graph_hall.html')

# Ruta para obtener datos del sensor de distancia
@app.route('/data_distancia')
def data_distancia():
    
    if sensor_distancia:
        try:
            # Leer el contenido del archivo del sensor de distancia
            with open("val", 'r') as archivo:
                content = archivo.read().strip()
                if content:
                    # Convertir el contenido JSON a un diccionario
                    latest_data = json.loads(content)
                    return jsonify(latest_data)
                else:
                    return jsonify({"error": "No data available"}), 204
        except Exception as e:
            print(f"Error al obtener los datos del sensor de distancia: {e}")
            return jsonify({"error": "Error processing data"}), 500
    else:
        return jsonify({"error": "Sensor de distancia no inicializado"}), 500

# Ruta para obtener datos del sensor de obstáculos
@app.route('/data_obstaculo')
def data_obstaculo():
    
    if sensor_obstaculo:
        try:
            # Leer el contenido del archivo del sensor de obstáculos
            with open("obstacle_val", 'r') as archivo:
                content = archivo.read().strip()
                if content:
                    # Convertir el contenido JSON a un diccionario
                    latest_data = json.loads(content)
                    #setea obstacle_val a 0
                    with open("obstacle_val", 'w') as archivo:
                        json.dump({"obstacle": 0}, archivo)
                        archivo.write("\n")
                    return jsonify(latest_data)
                else:
                    return jsonify({"error": "No data available"}), 204
        except Exception as e:
            print(f"Error al obtener los datos del sensor de obstáculos: {e}")
            return jsonify({"error": "Error processing data"}), 500
    else:
        print("Sensor de obstáculos no inicializado")
        return jsonify({"error": "Sensor de obstáculos no inicializado"}), 500
    
# Ruta para obtener datos del sensor de distancia
@app.route('/data_hall')
def data_hall():
    
    if sensor_hall:
        try:
            # Leer el contenido del archivo del sensor de distancia
            with open("hall_val", 'r') as archivo:
                content = archivo.read().strip()
                if content:
                    # Convertir el contenido JSON a un diccionario
                    latest_data = json.loads(content)
                    return jsonify(latest_data)
                else:
                    return jsonify({"error": "No data available"}), 204
        except Exception as e:
            print(f"Error al obtener los datos del sensor de hall: {e}")
            return jsonify({"error": "Error processing data"}), 500
    else:
        return jsonify({"error": "Sensor de hall no inicializado"}), 500

# Ruta para listar los hilos en ejecución
@app.route('/list_threads')
def list_threads_route():
    threads_info = list_threads()
    return jsonify(threads_info)

# Ruta para listar los hilos en ejecución
@app.route('/kill_threads')
def kill_threads():
    cleanup()
    threads_info = list_threads()
    # elimina los hilos con un nombre específico
    for thread in threads_info:
        if thread["name"] == "SensorThread" or thread["name"] == "SensorDistanciaThread":
            threads_info.remove(thread)
    return jsonify(threads_info)

# Manejar la señal de interrupción (Ctrl+C)
def signal_handler(sig, frame):
    print("Interrupción detectada. Deteniendo el servidor y los sensores...")
    cleanup()  # Llamar a la función de limpieza para detener los sensores
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    try:
        app.run(debug=True, threaded=True)  # Iniciar Flask con soporte para múltiples hilos
    except Exception as e:
        print(f"Excepción en la ejecución del servidor: {e}")
    finally:
        print("Servidor Flask detenido.")
        cleanup()
