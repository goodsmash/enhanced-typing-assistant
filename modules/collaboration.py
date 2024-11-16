import socket
import threading
import logging

class RealTimeCollaborator:
    """
    Enables real-time collaboration using socket connections.
    """
    
    def __init__(self, host='localhost', port=5000):
        """
        Initialize the RealTimeCollaborator server.
        
        :param host: str - Host address.
        :param port: int - Port number.
        """
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.lock = threading.Lock()
        logging.info(f"RealTimeCollaborator initialized on {host}:{port}.")
    
    def start_server(self):
        """
        Start the collaboration server.
        """
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            logging.info(f"Collaboration server started on {self.host}:{self.port}.")
            while True:
                client, addr = self.server.accept()
                with self.lock:
                    self.clients.append(client)
                logging.info(f"Connection established with {addr}.")
                threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()
        except Exception as e:
            logging.error(f"Collaboration server failed: {e}")
    
    def handle_client(self, client_socket: socket.socket, addr):
        """
        Handle communication with a connected client.
        
        :param client_socket: socket.socket - The client socket.
        :param addr: tuple - Client address.
        """
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                logging.debug(f"Received data from {addr}: {data}")
                self.broadcast(data, client_socket)
        except Exception as e:
            logging.error(f"Error handling client {addr}: {e}")
        finally:
            with self.lock:
                self.clients.remove(client_socket)
            client_socket.close()
            logging.info(f"Connection closed with {addr}.")
    
    def broadcast(self, message: str, sender_socket: socket.socket):
        """
        Broadcast a message to all connected clients except the sender.
        
        :param message: str - Message to broadcast.
        :param sender_socket: socket.socket - The sender's socket.
        """
        with self.lock:
            for client in self.clients:
                if client != sender_socket:
                    try:
                        client.send(message.encode())
                        logging.debug("Broadcasted message to a client.")
                    except Exception as e:
                        logging.error(f"Failed to send message to a client: {e}")
                        client.close()
                        self.clients.remove(client)
