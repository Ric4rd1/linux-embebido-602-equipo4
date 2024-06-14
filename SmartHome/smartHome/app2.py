import threading
import time
import tkinter as tk
from tkinter import BOTH, Button, Checkbutton, Frame, IntVar, Label, messagebox, Tk
from tkinter.ttk import Combobox
import logging
from logging.handlers import RotatingFileHandler
import sys
import subprocess

from utils import find_available_serial_ports, get_current_network_name
from serial_sensor import BAUDRATES, SerialSensor
from home_server import ADDRESSES, PORTS, HomeServer
from home_client import HomeClient

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler and set its level to DEBUG
file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)

# Create a console handler and set its level to DEBUG
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Create a formatter for the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Test logging
#logger.debug('Debug message')
#logger.info('Info message')
#logger.warning('Warning message')
#logger.error('Error message')


class App(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent: Tk = parent
        self.serial_device: SerialSensor | None = None
        self.home_server: HomeServer | None = None
        self.home_client: HomeClient | None = None
        self.init_gui()
        logger.info('Smart Home App running...')
        
    def init_gui(self) -> None:
        self.parent.title('Smart Home')
        self.parent.geometry('550x500')
        self['bg'] = '#40A578'
        self.pack(expand=True, fill=BOTH)

        # Title label
        self.title_label = Label(self, text="Smart Home Setup", font=('Arial', 16), bg='#40A578', fg='#FFFFFF')
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

        # Subtitles lables
        self.serial_setup_label = Label(self, text="Serial Setup", font=('Arial', 12), bg='#40A578', fg='#FFFFFF')
        self.serial_setup_label.grid(row=1, column=0, pady=(5, 5))

        self.server_setup_label = Label(self, text="Server Setup", font=('Arial', 12), bg='#40A578', fg='#FFFFFF')
        self.server_setup_label.grid(row=1, column=1, pady=(5, 5))

        # Wi-Fi network label
        self.network_label = Label(self, text="Wi-Fi: ", font=('Arial', 10), bg='#40A578', fg='#FFFFFF')
        self.network_label.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        self.update_network_label()

        # Log file button
        self.log_file_button = Button(self, text="Open Log", command=self.open_log_file)
        self.log_file_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
        
        # Serial Setup frame
        self.setup_frame = Frame(self, bg='#9DDE8B', padx=10, pady=10)
        self.setup_frame.grid(row=2, column=0, padx=20, pady=0, sticky="nw")

        self.baudrate_combobox = self._create_baudrate_combobox()
        self.baudrate_combobox.grid(row=0, column=0, padx=5, pady=5)
        
        self.serial_devices_combobox = self._init_serial_devices_combobox()
        self.serial_devices_combobox.grid(row=1, column=0, padx=5, pady=5)
        
        self.refresh_serial_devices_button = self._create_refresh_serial_devices_button()
        self.refresh_serial_devices_button.grid(row=2, column=0, padx=5, pady=5)
        
        self.status_label = self._create_status_label()
        self.status_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        # Conect button
        self.connect_button = self.create_connect_button()
        self.connect_button.grid(row=3, column=0, padx=5, pady=50)
        
        # Add setup_frame to the main grid
        self.setup_frame.grid_rowconfigure(0, weight=1)
        self.setup_frame.grid_rowconfigure(1, weight=1)
        self.setup_frame.grid_rowconfigure(2, weight=1)
        self.setup_frame.grid_rowconfigure(3, weight=1)
        self.setup_frame.grid_columnconfigure(0, weight=1)
        
        # Socket setup frame
        self.socket_frame = Frame(self, bg='#9DDE8B', padx=10, pady=10)
        self.socket_frame.grid(row=2, column=1, padx=20, pady=0, sticky="ne")
        
        self.address_combobox = self._create_address_combobox()
        self.address_combobox.grid(row=0, column=0, padx=5, pady=5)

        self.port_combobox = self._create_port_combobox()
        self.port_combobox.grid(row=1, column=0, padx=5, pady=5)

        self.initialize_server_button = self._create_initialize_server_button()
        self.initialize_server_button.grid(row=2, column=0, padx=5, pady=5)

        self.close_server_button = self._create_close_server_button()
        self.close_server_button.grid(row=3, column=0, padx=5, pady=5)

        self.server_status_label = self._create_server_status_label()
        self.server_status_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
    
        
        # Add socket_frame to the main grid
        self.socket_frame.grid_rowconfigure(0, weight=1)
        self.socket_frame.grid_rowconfigure(1, weight=1)
        self.socket_frame.grid_columnconfigure(0, weight=1)
        

        # Other settings
        self.baudrate_combobox.current(0)


    def update_network_label(self):
        network_name = get_current_network_name()
        self.network_label.config(text=f"Wi-Fi: {network_name}")
        self.parent.after(5000, self.update_network_label)  # Update every 5 seconds

    def refresh_serial_devices(self) -> None:
        ports = find_available_serial_ports()
        self.serial_devices_combobox['values'] = ports

    def connect_serial_device(self) -> None:
        try:
            baudrate = int(self.baudrate_combobox.get())
            port = self.serial_devices_combobox.get()
            if port == '':
                messagebox.showerror("Port not selected", f'Select a valid port {port=}')
                self.update_status(False)
                return
            self.serial_device = SerialSensor(port=port, baudrate=baudrate)
            logger.info('Serial device connected successfully')
            self.update_status(True)
        except ValueError:
            messagebox.showerror("Wrong baudrate", 'Baudrate not valid')
            self.update_status(False)
            return
        
    def initialize_server(self) -> None:
        try:
            address = self.address_combobox.get()
            port = int(self.port_combobox.get())
            if address == '':
                messagebox.showerror("Address not selected", "Select a valid address")
                self.update_server_status(False)
                return

            # Start the server in a separate thread
            self.server_thread = threading.Thread(target=self.start_server_thread, args=(address, port))
            self.server_thread.daemon = True  # Set the thread as a daemon so it terminates with the main thread
            self.server_thread.start()
            # Start the Web Server in a separate thread
            '''
            time.sleep(1)
            self.webServer_thread = threading.Thread(target=self.start_webServer_thread, args=(address, port))
            self.webServer_thread.daemon = True  # Set the thread as a daemon so it terminates with the main thread
            self.webServer_thread.start()
            '''
            '''
            try:
                self.home_client = HomeClient(host='0.0.0.0', port=5017, sockHost=address, sockPort=port)
                self.home_client.start()
                logger.info('Web Server initialized')
            except Exception as e:
                print(f"An error occurred when initializing Web server: {e}")
                logger.error(f"An error occurred when initializing Web server: {e}")
                return
            '''
            #time.sleep(1)
            #self.initialize_webServer(address,port)
            self.update_server_status(True)
        except ValueError:
            messagebox.showerror("Wrong port", "Port not valid")
            self.update_server_status(False)
            return
    
    def initialize_webServer(self, address, port):
        #time.sleep(1)
        self.home_client = HomeClient(host='0.0.0.0', port=5017, sockHost=address, sockPort=port)
        self.home_client.start()
        logger.info('Web Server initialized')
        return

    def start_server_thread(self, address: str, port: int) -> None:
        try:
            self.home_server = HomeServer(host=address, port=port, message_callback=self.send_serial)
            logger.info('Server initialized')
            self.home_server.start()
        except Exception as e:
            print(f"An error occurred when initializing server: {e}")
            logger.error(f"An error occurred when initializing server: {e}")
            self.update_server_status(False)
            return
        
    def start_webServer_thread(self, address: str, port: int) -> None:
        try:
            self.home_client = HomeClient(host='0.0.0.0', port=5017, sockHost=address, sockPort=port)
            logger.info('Web server initialized')
            self.home_client.start()
        except Exception as e:
            print(f"An error occurred when initializing  Web server: {e}")
            logger.error(f"An error occurred when initializing Web server: {e}")
            self.update_server_status(False)
            return

    def close_server(self) -> None:
        #self.home_client.close()
        #time.sleep(.2)
        self.home_server.close()
        self.update_server_status(False)
        logger.info('Closing server...')
        return
    
    def send_serial(self, message) -> None:
        if self.serial_device is not None:
            logger.info(f"Sending message via serial: {message}")
            try:
                self.serial_device.send(str(message))
                logger.info("Message sent successfully")
            except Exception as e:
                logger.error(f"Failed to send message via serial: {e}")
            return
        messagebox.showerror("Serial device not connected", 'Setup serial device')

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
        return Button(self.setup_frame, 
                      text="Connect", 
                      command=self.connect_serial_device,
                      width=20,
                      height=5,
                      bg='#E6FF94',
                      font=('Arial', 12),
                      foreground="#006769")
    
    def _create_status_label(self) -> Label:
        return Label(self.setup_frame, text="Status: Not Connected", foreground="#006769", font=('Arial', 12))
    
    def _create_server_status_label(self) -> Label:
        return Label(self.socket_frame, text="Status: Not Initialized", foreground="#006769", font=('Arial', 12))
    
    def update_status(self, connected: bool) -> None:
        status_text = "Connected" if connected else "Not Connected"
        self.status_label['text'] = f"Status: {status_text}"

    def update_server_status(self, connected: bool) -> None:
        status_text = "Initialized" if connected else "Not Initialized"
        self.server_status_label['text'] = f"Status: {status_text}"

    def _create_address_combobox(self) -> Combobox:
        address_values = ADDRESSES
        return Combobox(self.socket_frame, values=address_values)
    
    def _create_port_combobox(self) -> Combobox:
        port_values = PORTS
        return Combobox(self.socket_frame, values=port_values)
    
    def _create_initialize_server_button(self) -> Button:
        return Button(self.socket_frame, 
                      text="Initialize Server", 
                      command=self.initialize_server,
                      width=20,
                      height=5,
                      bg='#E6FF94',
                      font=('Arial', 12),
                      foreground="#006769")
    
    def _create_close_server_button(self) -> Button:
        return Button(self.socket_frame, 
                      text="Close server", 
                      command=self.close_server,
                      foreground="#006769",
                      bg='#E6FF94')
    
    def open_log_file(self) -> None:
        try:
            #subprocess.Popen(['notepad.exe', 'app.log'])  # On Windows
            # subprocess.Popen(['open', 'app.log'])  # On macOS
            subprocess.Popen(['xdg-open', 'app.log'])  # On Linux
        except Exception as e:
            logger.error(f"Failed to open log file: {e}")
            messagebox.showerror("Error", f"Failed to open log file: {e}")

    
    
    
root = Tk()

if __name__ == '__main__':
    ex = App(root)
    root.mainloop()
