from tkinter import BOTH
from tkinter import Button
from tkinter import Frame
from tkinter import Label
from tkinter import messagebox
from tkinter import Tk
from tkinter.ttk import Combobox

from utils import find_available_serial_ports
from serial_sensor import BAUDRATES
from serial_sensor import SerialSensor

class App(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent:Tk = parent
        self.serial_device:SerialSensor| None = None
        # Aqui vamos a crear todos los componentes graficos
        self.serial_devices_combobox:Combobox = self._init_serial_devices_combobox()
        self.refresh_serial_devices_button:Button = self._create_refresh_serial_devices_button()
        self.baudrate_combobox:Combobox = self._create_baudrate_combobox()
        self.connect_button: Button = self.create_connect_button()
        self.temperature_label: Label = self._ceate_temperature_label()
        self.read_temperature_button: Button = self._create_read_temperature_button()
        self.init_gui()
        

    def init_gui(self,) -> None:
        self.parent.title = 'ArduSerial'
        self.parent.geometry('700x400')
        self['bg'] = 'white'
        self.pack(expand=True, fill=BOTH)

        # Row 0
        self.serial_devices_combobox.grid(row=0, column=0)
        self.refresh_serial_devices_button.grid(row=0, column=1)
        self.baudrate_combobox.grid(row=0, column=2)
        self.connect_button.grid(row=0, column=3)

        # Row 1
        self.temperature_label.grid(row=1, column=0)
        self.read_temperature_button.grid(row=1, column=1)

        # Other settings
        self.baudrate_combobox.current(0)
    
    def refresh_serial_devices(self,) -> None:
        ports = find_available_serial_ports()
        self.serial_devices_combobox['values'] = ports

    def conncect_serial_device(self,) -> None:
        try:
            baudrate = int(self.baudrate_combobox.get())
            port =  self.serial_devices_combobox.get()
            if port == '':
                messagebox.showerror("Port not selected", f'Select a Valid port {port=}')
                return
            self.serial_device = SerialSensor(
                port=port,
                baudrate=baudrate
            )
        except ValueError:
            messagebox.showerror("Wrong baudrate", 'Budrate not valid')
            return
        
    def read_temperature(self,) -> None:
        if self.serial_device is not None:
            temperature = self.serial_device.send('TC2')
            self.temperature_label['text'] = f"{temperature[1:-4]} °C"
            return
        messagebox.showerror("Device not connected", 'Connect to a device first')
    
    def _init_serial_devices_combobox(self, )  -> Combobox:
        ports = find_available_serial_ports()
        return Combobox(self, values=ports)
    
    def _create_refresh_serial_devices_button(self, ) -> Button:
        return Button(master=self, 
                      text="Refresh serial devices", 
                      command=self.refresh_serial_devices)
    
    def _create_baudrate_combobox(self, ) -> Combobox:
        baudrates_values = ['BAUDRATES'] + BAUDRATES
        return Combobox(
            master=self,
            values=baudrates_values,
        )
    
    def create_connect_button(self, ) -> Button:
        return Button(
            master=self,
            text="Connect",
            command=self.conncect_serial_device
        )
    
    def _ceate_temperature_label(self, ) -> Label:
        return Label(
            master=self,
            text="XX.XX °C",
            foreground="red",
            font=('Arial', 20)
        )
    
    def _create_read_temperature_button(self, ) -> Button:
        return Button(
            master=self,
            text="Read temperature",
            command=self.read_temperature
        )
    
root = Tk()

if __name__ == '__main__':
    ex = App(root)

    root.mainloop()