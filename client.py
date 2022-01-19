import argparse
import os
import socket
import sys
import threading
import tkinter as tk


class Send(threading.Thread):

    # Listens to the input from command line
    # sock the connected sock object
    # name(str): the username provided by user

    def __init__(self, sock, name):

        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        # Listen for the user input from the command line and send it to the server
        # Exit the chatroom typing the "QUIT" message
        while True:
            print('{}: '.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            if message == "QUIT":
                self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('ascii'))
                break
            # send message to server for broadcast
            else:
                self.sock.sendall('{}: {} '.format(self.name, message).encode('ascii'))

        print('\nQuitting...')
        self.sock.close()
        os._exit(0)


class Receive(threading.Thread):
    # Listens for incoming messages from the server
    def __init__(self, sock, name):

        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self):
        # Receives data from the server and displays it in the gui
        while True:
            message = self.sock.recv(1024).decode('ascii')

            if message:
                if self.messages:
                    self.messages.insert(tk.END, message)
                    print('\r{}\n{}: '.format(message, self.name), end='')

                else:
                    print('\r{}\n{}: '.format(message, self.name), end='')
            else:
                print('\n No. You have lost connection to the server!')
                print('\nQuitting...')
                self.sock.close()
                os._exit(0)


class Client:
    # Client will manage the client - server connection and the GUI

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None

    def start(self):
        print('Trying to connect to {}:{}...'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))

        print('Successfully connected to {}:{}...'.format(self.host, self.port))

        self.name = input('\nYour name: ')
        print('\nWelcome. {}! Getting ready to send and receive messages...'.format(self.name))

        # Create, send and receive threads
        send = Send(self.sock, self.name)
        receive = Receive(self.sock, self.name)

        send.start()
        receive.start()

        self.sock.sendall('Server: {} has joined the chat. Say something'.format(self.name).encode('ascii'))
        print("\rReady! Leave the chatroom anytime by typing 'QUIT'\n")
        print('{}: '.format(self.name), end='')

        return receive

    def send(self, text_input):
        message = text_input.get()
        text_input.delete(0, tk.END)
        self.messages.insert(tk.END, '{}: {}'.format(self.name, message))

        # Type "QUIT"
        if message == "QUIT":
            self.sock.sendall('Server: {} has left the chat'.format(self.name).encode('ascii'))
            print('\nQuitting...')
            self.sock.close()
            os._exit(0)

        # Send message to the server for broadcast
        else:
            self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))


def main(host, port):
    # Initialise and run the GUI
    client = Client(host, port)
    receive = client.start()

    window = tk.Tk()
    window.title("Chatroom")

    from_message = tk.Frame(master=window)
    scroll_bar = tk.Scrollbar(master=from_message)
    messages = tk.Listbox(master=from_message, yscrollcommand=scroll_bar.set)
    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    receive.messages = messages

    from_message.grid(row=0, column=0, columnspan=2, sticky="nsew")
    from_entry = tk.Frame(master=window)
    text_input = tk.Entry(master=from_entry)

    text_input.pack(fill=tk.BOTH, expand=True)
    text_input.bind("<Return>", lambda x: client.send(text_input))
    text_input.insert(0, "Write your message here")

    button_send = tk.Button(master=window, text='Send', command=lambda: client.send(text_input))

    from_entry.grid(row=1, column=0, padx=10, sticky="ew")
    button_send.grid(row=1, column=1, padx=10, sticky="ew")

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chat Room Server")
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port(default 1060)')

    args = parser.parse_args()

    main(args.host, args.p)
