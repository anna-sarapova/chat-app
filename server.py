import threading
import socket
import argparse
import os


class Server(threading.Thread):

    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        socket_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        socket_s.bind((self.host, self.port))
        socket_s.listen(1)
        print("Listening at", socket_s.getsockname())

        while True:
            # Accepting new connection
            sock, socket_name = socket_s.accept()
            print(f"Accepting a new connection from {sock.getpeername()} to {sock.getsockname()}")

            # Create a new thread
            server_socket = ServerSocket(sock, socket_name, self)

            # Start a new thread
            server_socket.start()

            # Add thread to active connection
            self.connections.append(server_socket)
            print("Ready to receive messages from", sock.getpeername())

    def broadcast(self, message, source):
        for connection in self.connections:
            # Send to all connected clients except the source client
            if connection.socket_name != source:
                connection.send(message)

    def remove_connection(self, connection):
        self.connections.remove(connection)


class ServerSocket(threading.Thread):

    def __init__(self, sock, socket_name, server):
        super().__init__()
        self.sock = sock
        self.socket_name = socket_name
        self.server = server             # the parent thread

    def run(self):
        while True:
            message = self.sock.recv(1024).decode('ascii')

            if message:
                print(f"{self.socket_name} says {message}")
                self.server.broadcast(message, self.socket_name)

            else:
                print(f"{self.socket_name} has closed the connection")
                self.sock.close()
                server.remove_connection(self)
                return

    def send(self, message):
        self.sock.sendall(message.encode('ascii'))


def exit_server(server):
    while True:
        input_text = input("")
        if input_text == "QUIT":
            print("Closing all connections...")
            for connection in server.connections:
                connection.sock.close()

            print("Shouting down the server...")
            os._exit(os.EX_OK)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chat Room Server")
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port(default 1060)')

    args = parser.parse_args()

    server = Server(args.host, args.p)
    server.start()

    exit_server = threading.Thread(target=exit, args=(server,))
    exit_server.start()


