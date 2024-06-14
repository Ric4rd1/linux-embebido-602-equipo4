import serial.tools.list_ports
#encontrar los puertos y listarlos 

def findPorts()->list[str]:
    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append(port.device)
    return ports

 