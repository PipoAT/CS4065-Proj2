import socket
import threading
import json
from datetime import datetime

# In-memory storage for users, messages, and client connections
users = []  # List of currently connected users
messages = []  # List of posted messages
clients = []  # List of active client connections

# Message class to structure messages
class Message:
    def __init__(self, sender, subject, body):
        self.message_id = len(messages) + 1
        self.sender = sender
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.subject = subject
        self.body = body

    def to_dict(self):
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'date': self.date,
            'subject': self.subject,
            'body': self.body
        }

# Function to handle client requests
def handle_client(client_socket, client_address):
    global users, messages, clients

    # Add client socket to the list of active clients
    clients.append(client_socket)

    # Read the client message
    request = client_socket.recv(1024).decode('utf-8')
    if not request:
        return

    # Parse the request
    request_data = json.loads(request)
    command = request_data.get('command')

    if command == 'join':
        username = request_data.get('username')

        # Ensure username is not empty and not already taken
        while not username or username in users:
            if username in users:
                client_socket.send(json.dumps({'status': 'failure', 'message': f'Username "{username}" is already taken.'}).encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8')  # Prompt for a new username
        
        users.append(username)
        print(f"User '{username}' has joined the group.")
        
        # Broadcast the user joining message to all connected clients
        join_message = Message('System', 'User Joined', f'User "{username}" has joined the group.')
        broadcast_message(join_message)

        # Send success response
        client_socket.send(json.dumps({'status': 'success', 'message': f'Welcome, {username}!' }).encode('utf-8'))

    elif command == 'post':
        sender = request_data.get('sender')
        subject = request_data.get('subject')
        body = request_data.get('body')
        if not sender or not subject or not body:
            client_socket.send(json.dumps({'status': 'failure', 'message': 'Sender, subject, and body are required.'}).encode('utf-8'))
        else:
            new_message = Message(sender, subject, body)
            messages.append(new_message)
            print(f"Message posted by {sender}: '{subject}'")

            # Broadcast the message to all connected clients
            broadcast_message(new_message)

            client_socket.send(json.dumps({'status': 'success', 'message': f'Message titled "{subject}" posted successfully!'}).encode('utf-8'))

    elif command == 'leave':
        username = request_data.get('username')
        if username not in users:
            client_socket.send(json.dumps({'status': 'failure', 'message': f'User "{username}" not found in the group.'}).encode('utf-8'))
        else:
            users.remove(username)
            print(f"User '{username}' has left the group.")
            # Broadcast that the user has left
            leave_message = Message('System', 'User Left', f'User "{username}" has left the group.')
            broadcast_message(leave_message)
            client_socket.send(json.dumps({'status': 'success', 'message': f'{username} has left the group.'}).encode('utf-8'))

    elif command == 'users':
        client_socket.send(json.dumps({'status': 'success', 'users': users}).encode('utf-8'))

    elif command == 'message':
        message_id = request_data.get('message_id')
        if 0 < message_id <= len(messages):
            message = messages[message_id - 1].to_dict()
            client_socket.send(json.dumps({'status': 'success', 'message': message}).encode('utf-8'))
        else:
            client_socket.send(json.dumps({'status': 'failure', 'message': f'Message with ID {message_id} not found.'}).encode('utf-8'))

    client_socket.close()
    # Remove the client from the active clients list when they disconnect
    clients.remove(client_socket)

# Function to broadcast a message to all connected clients
def broadcast_message(message):
    global clients
    for client in clients:
        try:
            client.send(json.dumps({'status': 'new_message', 'message': message.to_dict()}).encode('utf-8'))
        except:
            # If sending the message fails (e.g., client disconnected), remove the client
            clients.remove(client)

# Function to handle server console commands
def handle_server_console():
    while True:
        command = input("Enter server command: ").strip().lower()

        if command == "list_users":
            if users:
                print("Currently connected users:")
                for user in users:
                    print(f"- {user}")
            else:
                print("No users are currently connected.")

        elif command == "exit":
            print("Exiting the server.")
            break

        else:
            print("Unknown command. Available commands: list_users, exit.")

# Main server function
def start_server():
    # Start the server to listen for incoming connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5050))
    server.listen(5)
    print("Server started on port 8080...")

    # Start a thread to handle server console commands
    console_thread = threading.Thread(target=handle_server_console)
    console_thread.daemon = True  # Daemonize so it exits when the main program exits
    console_thread.start()

    while True:
        # Accept incoming client connections
        client_socket, addr = server.accept()
        print(f"Connection established with {addr}")
        
        # Handle each client in a new thread
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()
