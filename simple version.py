import tkinter as tk
from tkinter import messagebox, StringVar, END, N, E, S, W
import serial
import serial.tools.list_ports
import threading
import queue
from datetime import datetime

# Serial port object
ser = serial.Serial()
receive_queue = queue.Queue()

# Thread to receive data from the serial port
def receive_data():
    while ser.is_open:
        try:
            data = ser.readline().decode().strip()
            receive_queue.put(data)
        except serial.SerialException:
            break

# GUI Functions
def connect():
    selected_port = port_var.get()
    selected_baud = baud_var.get()
    try:
        ser.port = selected_port
        ser.baudrate = int(selected_baud)
        ser.open()
        if ser.is_open:
            ser.dtr = dtr_var.get()
            update_rts_control()  # Update RTS control state
            messagebox.showinfo("Success", "Serial port connected!")
            threading.Thread(target=receive_data, daemon=True).start()  # Start receive thread
        else:
            messagebox.showerror("Error", "Failed to connect to the serial port.")
    except serial.SerialException:
        messagebox.showerror("Error", "Failed to connect to the serial port.")

def disconnect():
    if ser.is_open:
        ser.close()
        messagebox.showinfo("Success", "Serial port disconnected.")
    else:
        messagebox.showinfo("Info", "Serial port is already disconnected.")

def send_data():
    data = entry.get()
    if ser.is_open:
        ser.write(data.encode())
    else:
        messagebox.showinfo("Info", "Serial port is not connected.")

def process_received_data():
    while not receive_queue.empty():
        data = receive_queue.get()
        if timestamp_var.get():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = f"{timestamp} - {data}"
        text_area.insert(tk.END, data + "\n")
        text_area.see(tk.END)  # Auto-scroll to the end
        receive_queue.task_done()
    window.after(100, process_received_data)  # Schedule next processing after 100ms

def update_rts_control():
    if ser.is_open:
        ser.rts = rts_var.get()

def clear_text_area():
    text_area.delete("1.0", tk.END)

# Create GUI
window = tk.Tk()
window.title("Serial Port Program")

# Serial Port Selection
ports = [port.device for port in serial.tools.list_ports.comports()]
port_label = tk.Label(window, text="Serial Port:")
port_label.grid(row=0, column=0)
port_var = StringVar()
port_combobox = tk.OptionMenu(window, port_var, *ports)
port_combobox.grid(row=0, column=1, padx=10, pady=5, sticky=W)

# Baud Rate Selection
baud_label = tk.Label(window, text="Baud Rate:")
baud_label.grid(row=1, column=0)
baud_var = StringVar()
baud_combobox = tk.OptionMenu(window, baud_var, "9600", "115200")
baud_combobox.grid(row=1, column=1, padx=10, pady=5, sticky=W)

# DTR Control
dtr_label = tk.Label(window, text="DTR Control:")
dtr_label.grid(row=2, column=0)
dtr_var = tk.BooleanVar()
dtr_checkbutton = tk.Checkbutton(window, text="Enable", variable=dtr_var)
dtr_checkbutton.grid(row=2, column=1, padx=10, pady=5, sticky=W)

# RTS Control
rts_label = tk.Label(window, text="RTS Control:")
rts_label.grid(row=3, column=0)
rts_var = tk.BooleanVar()
rts_checkbutton = tk.Checkbutton(window, text="Enable", variable=rts_var, command=update_rts_control)
rts_checkbutton.grid(row=3, column=1, padx=10, pady=5, sticky=W)

# Timestamp Option
timestamp_var = tk.BooleanVar()
timestamp_checkbox = tk.Checkbutton(window, text="Timestamp", variable=timestamp_var)
timestamp_checkbox.grid(row=6, column=1, padx=10, pady=5, sticky=W)

# Connect Button
connect_button = tk.Button(window, text="Connect", command=connect)
connect_button.grid(row=0, column=2, padx=10, pady=5)

# Disconnect Button
disconnect_button = tk.Button(window, text="Disconnect", command=disconnect)
disconnect_button.grid(row=1, column=2, padx=10, pady=5)

# Data Entry
entry = tk.Entry(window)
entry.grid(row=4, column=0, padx=10, pady=5)

# Send Button
send_button = tk.Button(window, text="Send", command=send_data)
send_button.grid(row=4, column=1, padx=0, pady=0, sticky=E)

# Text Area
text_area = tk.Text(window)
text_area.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky=N+S+E+W)

# Configure grid weights to expand the text area vertically
window.grid_rowconfigure(3, weight=1)
window.grid_columnconfigure(0, weight=1)

# Clear Button
clear_button = tk.Button(window, text="Clear", command=clear_text_area)
clear_button.grid(row=6, column=2, padx=0, pady=0, sticky=W)

# Process received data
process_received_data()

window.mainloop()
