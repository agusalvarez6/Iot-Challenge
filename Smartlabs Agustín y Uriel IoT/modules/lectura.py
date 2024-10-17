import serial
import serial.tools.list_ports
import time

def find_serial_port(baud_rate=115200):
    """Encuentra el puerto serial conectado con el ESP32.
    
    Args:
        baud_rate (int): La velocidad de baudios para intentar conectar.
    
    Returns:
        str: El puerto serial encontrado o None si no se encuentra ninguno.
    """
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            ser = serial.Serial(port.device, baud_rate, timeout=1)
            ser.close()  # Cierra inmediatamente después de la conexión para probar
            return port.device
        except (OSError, serial.SerialException):
            continue
    return None

# Encuentra el puerto serial
serial_port = find_serial_port()
if serial_port is None:
    print("No se pudo encontrar un puerto serial compatible.")
else:
    print(f"Puerto serial encontrado: {serial_port}")

    try:
        # Abre la conexión serial
        ser = serial.Serial(serial_port, 115200, timeout=1)
        print(f"Conectado al puerto {serial_port} a 115200 baudios.")
        print("Leyendo datos desde el puerto serial. Presiona Ctrl+C para salir.")
        
        while True:
            if ser.in_waiting > 0:  # Verifica si hay datos disponibles para leer
                line = ser.readline().decode('latin-1').strip()  # Lee y decodifica la línea de datos
                print(f"Datos recibidos: {line}")
    except serial.SerialException as e:
        print(f"Error al abrir el puerto serial: {e}")
    except KeyboardInterrupt:
        print("Interrupción por el usuario. Cerrando...")
    finally:
        ser.close()
