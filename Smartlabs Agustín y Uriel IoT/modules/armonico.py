import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from scipy.signal import find_peaks
from matplotlib.widgets import Button
import tkinter.messagebox as messagebox
import serial.tools.list_ports
import time

def find_serial_port(baud_rate=115200):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            ser = serial.Serial(port.device, baud_rate, timeout=1)
            ser.close()
            return port.device
        except (OSError, serial.SerialException):
            continue
    return None

serial_port = find_serial_port()
if serial_port is None:
    messagebox.showerror("Error", "Error de comunicación.")
    exit(1)
else:
    print(f"Conectado al puerto: {serial_port}")

baud_rate = 115200
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=0.1)
    print(f"Puerto serial {serial_port} abierto: {ser.is_open}")
    time.sleep(2)
except serial.SerialException as e:
    print(f"No se pudo abrir el puerto serial {serial_port}: {e}")
    exit(1)

# Configuración de la gráfica
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
xdata, ydata = [], []
ln, = plt.plot([], [], 'r-', label="Movimiento armónico")
env_ln, = plt.plot([], [], 'b--', label="Envolvente")

window_size = 10
ani_running = True

def init():
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 400)
    ax.legend()
    return ln, env_ln

def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def calculate_envelope(x, y):
    peaks, _ = find_peaks(y)
    if len(peaks) > 1:  # Necesitamos al menos dos picos para interpolar
        envelope_x = np.array(x)[peaks]
        envelope_y = np.array(y)[peaks]
        envelope = np.interp(x, envelope_x, envelope_y)
    else:
        envelope = y  # Si no hay suficientes picos, devolvemos la señal original
    return envelope

def update(frame):
    if not ani_running:
        return ln, env_ln
    if not ser.is_open:
        print("Puerto serial está cerrado.")
        messagebox.showerror("Error", "Error de comunicación.")
        exit(1)
        return ln, env_ln
    ser.flushInput()

    ser.write(b'A') 

    line = ser.readline().decode('latin-1').strip()
    print(f"Datos recibidos: {line}")
    if line:
        try:
            y = float(line)
            xdata.append(frame)
            ydata.append(y)
            if len(xdata) > 1000:
                xdata.pop(0)
                ydata.pop(0)

            if len(ydata) >= window_size:
                y_smooth = smooth(ydata, window_size)
                envelope = calculate_envelope(xdata, y_smooth)
            else:
                y_smooth = ydata
                envelope = ydata  # Envolvente de los datos sin suavizar

            ln.set_data(xdata, y_smooth)
            env_ln.set_data(xdata, envelope)
            ax.set_xlim(max(0, frame - 500), frame)
            ax.set_ylim(min(y_smooth) - 5, max(y_smooth) + 5)

            return ln, env_ln
        except ValueError:
            print("Error en la conversión a flotante")
            pass
    return ln, env_ln

def toggle_pause(event):
    global ani_running
    if ani_running:
        ani.event_source.stop()
    else:
        ani.event_source.start()
    ani_running = not ani_running

def reset(event):
    global xdata, ydata
    xdata.clear()
    ydata.clear()
    ln.set_data([], [])
    env_ln.set_data([], [])
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 400)
    plt.draw()

# Botones de pausa y reset
pause_ax = plt.axes([0.65, 0.05, 0.15, 0.075])
pause_button = Button(pause_ax, 'Inicio/Pausa')
pause_button.on_clicked(toggle_pause)

reset_ax = plt.axes([0.81, 0.05, 0.1, 0.075])
reset_button = Button(reset_ax, 'Reset')
reset_button.on_clicked(reset)

ani = animation.FuncAnimation(fig, update, init_func=init, interval=5, blit=True)
plt.show()