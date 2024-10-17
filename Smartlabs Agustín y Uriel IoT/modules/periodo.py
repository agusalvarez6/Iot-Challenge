import serial
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Button, Label, StringVar, Frame
from tkinter.filedialog import asksaveasfilename
import serial.tools.list_ports
import tkinter.messagebox as messagebox

def find_serial_port(baud_rate=115200):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            ser = serial.Serial(port.device, baud_rate, timeout=1)
            ser.close()
            return port.device
        except (OSError, serial.SerialException):
            messagebox.showerror("Error", "Error de comunicación.")
            finalizar_programa()  # Llama a la función para cerrar el programa
    return None

serial_port = find_serial_port()
baud_rate = 115200

try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Puerto serial abierto: {serial_port}")
except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
    exit()

pico_times = []
data = []
update_task = None  # Variable para guardar el identificador del `after`

def calcular_periodo_y_error(tiempos):
    if len(tiempos) < 2:
        return None, None

    diferencias = np.diff(tiempos)
    periodo_estimado = np.mean(diferencias) * 2
    error_margen = (np.std(diferencias) / np.sqrt(len(diferencias))) * 2
    
    return periodo_estimado, error_margen

root = Tk()
root.title("Monitor de Péndulo")

periodo_var = StringVar()
error_var = StringVar()

Label(root, text="Período estimado:").pack()
periodo_label = Label(root, textvariable=periodo_var)
periodo_label.pack()

Label(root, text="Margen de error:").pack()
error_label = Label(root, textvariable=error_var)
error_label.pack()

fig, ax = plt.subplots()
xdata, ydata = [], []
line, = ax.plot([], [], 'r-')

def init():
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 2)
    ax.set_xlabel('Número de muestras')
    ax.set_ylabel('Margen de error (segundos)')
    return line,

def update_graph():
    global xdata, ydata

    if len(pico_times) > 1:
        periodo, error = calcular_periodo_y_error(pico_times)
        if periodo is not None:
            error_var.set(f"{error:.4f} segundos")
            xdata.append(len(pico_times))
            ydata.append(error)
            data.append({"Muestra": len(pico_times), "Período (s)": periodo})

            line.set_data(xdata, ydata)
            ax.set_xlim(max(0, len(pico_times) - 50), len(pico_times))
            ax.set_ylim(0, max(ydata) + 0.1 if ydata else 2)
    
    canvas.draw()

def update_data():
    global pico_times

    if ser.is_open:
        ser.write(b'P') 
        try:
            line = ser.readline().decode('latin-1').strip()
            
            if line == '1':
                current_time = time.time()
                pico_times.append(current_time)
                
                if len(pico_times) > 500:
                    pico_times = pico_times[-500:]
                
                periodo, error = calcular_periodo_y_error(pico_times)
                
                if periodo is not None:
                    periodo_var.set(f"{periodo:.4f} segundos")
                    
        except (UnicodeDecodeError, ValueError) as e:
            print(f"Error de lectura: {e}")
    else:
        messagebox.showerror("Error", "Error de comunicación.")
        finalizar_programa()  # Llama a la función para cerrar el programa

    update_graph()
    root.after(100, update_data)

def reset_data():
    global pico_times, data
    pico_times = []
    data = []
    periodo_var.set("N/A")
    error_var.set("N/A")
    xdata.clear()
    ydata.clear()
    line.set_data(xdata, ydata)
    update_graph()

def export_data():
    global data
    file_path = asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*")])
    
    if file_path:
        try:
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            print(f"Datos exportados a {file_path}")
        except PermissionError:
            print("No se puede guardar el archivo. Asegúrate de que el archivo no esté abierto.")

def finalizar_programa():
    global update_task
    if update_task is not None:
        root.after_cancel(update_task)  # Cancelar la llamada a `update_data` si está pendiente
    if ser.is_open:
        ser.close()
    root.destroy()

button_frame = Frame(root)
button_frame.pack()

reset_button = Button(button_frame, text="Resetear", command=reset_data)
reset_button.pack(side="left")

export_button = Button(button_frame, text="Exportar", command=export_data)
export_button.pack(side="left")

finalizar_button = Button(button_frame, text="Finalizar", command=finalizar_programa)
finalizar_button.pack(side="left")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side="top", fill="both", expand=True)

init()
update_data()

root.mainloop()