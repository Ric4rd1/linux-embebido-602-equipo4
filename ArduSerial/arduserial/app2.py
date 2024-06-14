import tkinter as tk
from tkinter import BOTH, Button, Frame, Label, messagebox, Tk
from tkinter.ttk import Combobox

from utils import find_available_serial_ports
from serial_sensor import BAUDRATES, SerialSensor

class App(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent: Tk = parent
        self.serial_device: SerialSensor | None = None
        self.init_gui()
        
    def init_gui(self) -> None:
        self.parent.title('ArduSerial')
        self.parent.geometry('500x400')
        self['bg'] = '#40A578'
        self.pack(expand=True, fill=BOTH)
        
        # Setup frame
        self.setup_frame = Frame(self, bg='#9DDE8B', padx=10, pady=10)
        self.setup_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        self.baudrate_combobox = self._create_baudrate_combobox()
        self.baudrate_combobox.grid(row=0, column=0, padx=5, pady=5)
        
        self.serial_devices_combobox = self._init_serial_devices_combobox()
        self.serial_devices_combobox.grid(row=2, column=0, padx=5, pady=5)
        
        self.refresh_serial_devices_button = self._create_refresh_serial_devices_button()
        self.refresh_serial_devices_button.grid(row=3, column=0, padx=5, pady=5)
        
        # Conect button
        self.connect_button = self.create_connect_button()
        self.connect_button.grid(row=1, column=0, padx=5, pady=50)
        
        # Add setup_frame to the main grid
        self.setup_frame.grid_rowconfigure(0, weight=1)
        self.setup_frame.grid_rowconfigure(1, weight=1)
        self.setup_frame.grid_rowconfigure(2, weight=1)
        self.setup_frame.grid_rowconfigure(3, weight=1)
        self.setup_frame.grid_columnconfigure(0, weight=1)
        
        # Temperature display frame
        self.temperature_frame = Frame(self, bg='#9DDE8B', padx=10, pady=10)
        self.temperature_frame.grid(row=0, column=1, padx=20, pady=20, sticky="ne")
        
        self.temperature_label = self._create_temperature_label()
        self.temperature_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.read_temperature_button = self._create_read_temperature_button()
        self.read_temperature_button.grid(row=1, column=0, padx=5, pady=5)
        
        # Add temperature_frame to the main grid
        self.temperature_frame.grid_rowconfigure(0, weight=1)
        self.temperature_frame.grid_rowconfigure(1, weight=1)
        self.temperature_frame.grid_columnconfigure(0, weight=1)
        
        # Other settings
        self.baudrate_combobox.current(0)
    
    def refresh_serial_devices(self) -> None:
        ports = find_available_serial_ports()
        self.serial_devices_combobox['values'] = ports

    def connect_serial_device(self) -> None:
        try:
            baudrate = int(self.baudrate_combobox.get())
            port = self.serial_devices_combobox.get()
            if port == '':
                messagebox.showerror("Port not selected", f'Select a valid port {port=}')
                return
            self.serial_device = SerialSensor(port=port, baudrate=baudrate)
        except ValueError:
            messagebox.showerror("Wrong baudrate", 'Baudrate not valid')
            return
        
    def read_temperature(self) -> None:
        if self.serial_device is not None:
            temperature = self.serial_device.send('TC2')
            self.temperature_label['text'] = f"{temperature[1:-4]} °C"
            return
        messagebox.showerror("Device not connected", 'Connect to a device first')
    
    def _init_serial_devices_combobox(self) -> Combobox:
        ports = find_available_serial_ports()
        return Combobox(self.setup_frame, values=ports) 
    
    def _create_refresh_serial_devices_button(self) -> Button:
        return Button(self.setup_frame, 
                      text="Refresh serial devices", 
                      command=self.refresh_serial_devices,
                      foreground="#006769",
                      bg='#E6FF94')
    
    def _create_baudrate_combobox(self) -> Combobox:
        baudrates_values = ['BAUDRATES'] + BAUDRATES
        return Combobox(self.setup_frame, values=baudrates_values)
    
    def create_connect_button(self) -> Button:
        return Button(master = self, 
                      text="Connect", 
                      command=self.connect_serial_device,
                      width=20,
                      height=5,
                      bg='#E6FF94',
                      font=('Arial', 12),
                      foreground="#006769")
    
    def _create_temperature_label(self) -> Label:
        return Label(self.temperature_frame, text="XX.XX °C", foreground="#006769", font=('Arial', 20))
    
    def _create_read_temperature_button(self) -> Button:
        return Button(self.temperature_frame, 
                      text="Read temperature", 
                      command=self.read_temperature,
                      foreground="#006769",
                      bg='#E6FF94')
    
    
    
root = Tk()

if __name__ == '__main__':
    ex = App(root)
    root.mainloop()
