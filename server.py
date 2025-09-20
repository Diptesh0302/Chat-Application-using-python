# server.py
import socket
import threading

# --- Connection Data ---
# Use '0.0.0.0' to allow connections from any IP address on your network
HOST = '0.0.0.0'
PORT = 8500

# --- Server Setup ---
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# --- Lists For Clients and Their Nicknames ---
clients = []
nicknames = []

# --- Functions ---

def broadcast(message, _client=None):
    """Sends a message to all clients, with an option to exclude one."""
    for client in clients:
        if client != _client:
            try:
                client.send(message)
            except:
                # If sending fails, assume the client is disconnected
                remove_client(client)

def remove_client(client):
    """Removes a client and their nickname from the lists."""
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        nickname = nicknames[index]
        broadcast(f'{nickname} left the chat!'.encode('utf-8'))
        print(f"Removed {nickname}")
        nicknames.remove(nickname)
        client.close()

def handle_client(client):
    """Handles messages from a single client."""
    while True:
        try:
            # Receive message from a client
            message = client.recv(1024)
            if message:
                 # Broadcast the received message to all other clients
                broadcast(message, client)
            else:
                # If no message is received, the client has disconnected
                remove_client(client)
                break
        except:
            # Handle error and remove the client
            remove_client(client)
            break

def receive_connections():
    """Accepts new client connections and starts a thread for each."""
    print('Server is running and listening ...')
    while True:
        # Accept a new connection
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # Request and store the nickname
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        # Print and broadcast the new connection
        print(f"Nickname of the client is {nickname}!")
        broadcast(f"{nickname} joined the chat!".encode('utf-8'), client)
        client.send('Connected to the server!'.encode('utf-8'))

        # Start a new thread to handle this client
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

# --- Main Execution ---
if __name__ == "__main__":
    receive_connections()