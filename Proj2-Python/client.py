import json
import socket
import threading

# Global variables
server_url = 'localhost'  # Default server address
server_port = 8080        # Default server port
username = ''  # Default empty username

# Function to handle user input
def handle_commands():
    while True:
        command = input("Enter a command: ").strip().lower()

        # %connect command to set server address and port
        if command.startswith("%connect"):
            try:
                _, address, port = command.split()
                global server_url, server_port
                server_url = address
                server_port = int(port)
                print(f"Connected to server at {server_url}:{server_port}")
            except ValueError:
                print("Invalid connect command. Use: %connect <address> <port>")
        
        # %join command to join the message board
        elif command == "%join":
            join_group()
        
        # %post command to post a message
        elif command.startswith("%post"):
            _, subject, *body = command.split()
            body = ' '.join(body)
            post_message(subject, body)
        
        # %users command to get the list of users
        elif command == "%users":
            get_users()
        
        # %leave command to leave the group
        elif command == "%leave":
            leave_group()
        
        # %message command to get a specific message by ID
        elif command.startswith("%message"):
            _, message_id = command.split()
            get_message(int(message_id))
        
        # %exit command to exit the client
        elif command == "%exit":
            print("Exiting the client.")
            break
        
        # Invalid command handling
        else:
            print("Invalid command. Available commands: %connect, %join, %post, %users, %leave, %message, %exit.")

# Command Functions
def send_request(command, data=None):
    # Create socket and send data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_url, server_port))
        
        request_data = {'command': command}
        if data:
            request_data.update(data)
        
        client_socket.send(json.dumps(request_data).encode('utf-8'))
        
        response = client_socket.recv(1024).decode('utf-8')
        print("Response:", response)

def join_group():
    global username
    if not username:
        username = input("Enter your username: ").strip()
    
    # Continuously prompt for a new username if the one entered is taken
    send_request('join', {'username': username})

def post_message(subject, body):
    if not username:
        print("You must join the group first using the %join command.")
        return

    send_request('post', {'sender': username, 'subject': subject, 'body': body})

def get_users():
    send_request('users')

def leave_group():
    global username
    if not username:
        print("You must join the group first using the %join command.")
        return

    send_request('leave', {'username': username})
    username = ''  # Clear username after leaving

def get_message(message_id):
    send_request('message', {'message_id': message_id})

# Function to handle incoming messages
def listen_for_messages():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_url, server_port))

        while True:
            response = client_socket.recv(1024).decode('utf-8')
            if not response:
                break

            response_data = json.loads(response)
            if response_data.get('status') == 'new_message':
                message = response_data.get('message')
                print(f"\nNew Message:\nFrom: {message['sender']}\nSubject: {message['subject']}\nDate: {message['date']}\nBody: {message['body']}\n")
            else:
                print("Response:", response_data)

# Start the client
if __name__ == '__main__':
    # Start a thread to listen for incoming messages
    listen_thread = threading.Thread(target=listen_for_messages)
    listen_thread.daemon = True
    listen_thread.start()

    handle_commands()
