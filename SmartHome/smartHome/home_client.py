'''
import socket
import time

ADDRESS = 'localhost'
PORT = 1234

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.connect((ADDRESS, PORT))

try:
    while True:
        to_send = input("Enter message to send: ")
        sock.send(to_send.encode('utf-8'))
        time.sleep(1)
except KeyboardInterrupt:
    print("Closing connection")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    sock.close()
    print("Connection closed")
'''
import socket
from flask import Flask, render_template,request,jsonify 
import logging
from logging.handlers import RotatingFileHandler
import sys
from werkzeug.serving import run_simple

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

class HomeClient:
    def __init__(self, host, port, sockHost, sockPort):
        self.host=host
        self.port=port
        self.sockHost=sockHost
        self.sockPort=sockPort

        # Web app
        self.app=Flask(__name__)

        # Socket configuration
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.sock.connect((sockHost, sockPort))

        # Route handlers
        self.app.add_url_rule('/', 'principal', self.principal)
        self.app.add_url_rule('/actualizar_estado', 'actualizar_estado', self.actualizar_estado, methods=['POST'])
        self.app.add_url_rule('/get_temperature', 'get_temperature', self.get_temperature, methods=['GET'])
    
    def principal(self):
        return render_template('index.html')
    
    def actualizar_estado(self):
        data = request.json
        dispositivo = data.get('dispositivo')
        estado = data.get('estado')
        logger.info(f'Dispositivo: {dispositivo}, Estado: {estado}')
        command = str(dispositivo) + str(estado)
        logger.info(f"Sending through sock: {command}")
        self.sock.send(command.encode('utf-8'))
        return jsonify({'message': 'Estado actualizado'}), 200

    def get_temperature(self):
        data = request.json
        parametro = data.get()
        command = str(parametro)
        #temperature = self.sock.send(command.encode('utf-8'))
        temperature = 10
        response = {'temperatura': temperature,}
        return jsonify(response)

    def start(self):
        try:
            logger.info(f"Web Server started on {self.host}:{self.port}")
            #run_simple(self.host, self.port, self.app, use_reloader=False)
            self.app.run(host=self.host,debug=True,port=self.port)#se reinicia el servidor automaticamente
        except Exception as e:
            logger.info(f"Web Server could not start on {self.host}:{self.port}, Error: {e}")
            self.sock.close()
        except KeyboardInterrupt:
            self.sock.close()

    def close(self):
        self.sock.close()

if __name__ == '__main__':
    webServer = HomeClient(host='0.0.0.0', port=5017, sockHost='localhost', sockPort=1234)
    webServer.start()
    