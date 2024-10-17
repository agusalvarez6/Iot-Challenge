import serial
import serial.tools.list_ports
import time
import threading
import json

class SensorObstaculo:
    def __init__(self, baud_rate=115200):
        self.baud_rate = baud_rate
        self.serial_port = self.find_serial_port()
        if self.serial_port is None:
            raise Exception("Error: No se pudo encontrar el puerto serial del Arduino")
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            time.sleep(2)  # Esperar a que la conexión serial se estabilice
            print(f"Puerto serial {self.serial_port} abierto: {self.ser.is_open}")
        except serial.SerialException as e:
            raise Exception(f"No se pudo abrir el puerto serial {self.serial_port}: {e}")
        self.latest_obstacle = None
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self.read_data, name="SensorObstaculoThread")
        self.thread.daemon = True
        self.thread.start()

    def find_serial_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                ser = serial.Serial(port.device, self.baud_rate, timeout=1)
                ser.close()
                return port.device
            except (OSError, serial.SerialException):
                continue
        return None

    def read_data(self):
        failed_attempts = 0  # Contador de intentos fallidos
        while self.running:
            try:
                if self.ser is not None and self.ser.is_open:
                    self.ser.flushInput()
                    self.ser.write(b'P')  # Enviar comando para solicitar datos A distancia P contacto
                    line = self.ser.readline().decode('latin-1').strip()

                    if line:
                        try:
                            print(f"Linea: {line}")
                            obstacle = int(line)
                            with self.lock:
                                self.latest_obstacle = {'obstacle': obstacle}
                                with open("obstacle_val", 'w') as archivo:
                                    json.dump(self.latest_obstacle, archivo)  # Convertir el diccionario a JSON
                                    archivo.write("\n")
                                failed_attempts = 0
                        except ValueError:
                            print(f"Error en la conversión a entero: {line}")
                    else:
                        failed_attempts += 1
                        if failed_attempts >= 50:  # Mostrar mensaje después de 50 fallos consecutivos
                            print("Datos vacíos recibidos repetidamente.")
                            failed_attempts = 0
                else:
                    print("Puerto serial no disponible.")
                    self.running = False
            except serial.SerialException as e:
                print(f"Error de comunicación: {e}")
                self.running = False
            except Exception as e:
                print(f"Error inesperado en el hilo del sensor: {e}")
                self.running = False
            time.sleep(0.2)  # Esperar 200 ms antes de la siguiente lectura

    def get_latest_obstacle(self):
        with self.lock:
            return self.latest_obstacle

    def stop(self):
        print("Deteniendo el hilo del sensor de obstáculos...")
        self.running = False
        try:
            # Asegurarse de que el hilo haya terminado
            if self.thread.is_alive():
                self.thread.join(timeout=1)
                print("Hilo del sensor de obstáculos detenido.")
            else:
                print("El hilo ya estaba detenido.")
        except Exception as e:
            print(f"Error al detener el hilo del sensor: {e}")
        finally:
            # Cerrar el puerto serial solo después de detener el hilo
            if self.ser and self.ser.is_open:
                try:
                    self.ser.close()
                    print("Puerto serial cerrado.")
                except Exception as e:
                    print(f"Error al cerrar el puerto serial: {e}")


