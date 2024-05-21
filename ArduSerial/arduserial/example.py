#librerías estandares de python(A-Z)
import time

#librerías de terceros(A-Z)
import serial

#librerías locales o módulos 
from locate_ports import findPorts

#inicializar serial
ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200)

time.sleep(2)

#mandar bytes para escribir, b cambia la string a cadena de bytes
ser.write(b'Hola')

time.sleep(1)

for i in range(1, 4):
    to_send = f'prueba {i}'
    #mandar to_send codificado en utf-8, manda bytes
    ser.write(to_send.encode('utf-8'))
    time.sleep(.5)
    received = ser.readline()
    print("Received: ", received)

ser.close()

portsList = findPorts()
print(portsList)
