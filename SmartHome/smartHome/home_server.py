import socket
import threading
import logging
from logging.handlers import RotatingFileHandler
import sys

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

ADDRESSES = [
    'localhost',
    '127.0.0.1'
]

PORTS = [
    1234,
    3333,
    2222
]

class HomeServer:
    def __init__(self, host='localhost', port=1234, message_callback=None):
        self.host = host
        self.port = port
        self.message_callback = message_callback
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

    def start(self):
        self.server_socket.listen(5)
        logger.info(f"Server started on {self.host}:{self.port}")
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                logger.info(f"New connection from {client_address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
        except Exception as e:
            logger.exception(f"Server error: {e}")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        self.clients.append(client_socket)
        try:
            while True:
                message = client_socket.recv(1024)
                if not message:
                    break
                decoded_message = message.decode('utf-8')
                logger.info(f"Received message from {client_address}: {decoded_message}")
                if self.message_callback:
                    self.message_callback(decoded_message)
                # Broadcast the message to all clients
                self.broadcast_message(message, client_socket)
        except Exception as e:
            logger.exception(f"Error with client {client_address}: {e}")
        finally:
            logger.info(f"Closing connection with {client_address}")
            self.clients.remove(client_socket)
            client_socket.close()

    def broadcast_message(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:  # Avoid sending the message back to the sender
                try:
                    client.sendall(message)
                except Exception as e:
                    logger.exception(f"Failed to send message to a client: {e}")

    def close(self) -> None:
        logger.info(f"Closing server on {self.host}:{self.port}")
        self.server_socket.close()

if __name__ == '__main__':
    server = HomeServer(host='0.0.0.0', port=3333)
    server.start()
