import socket
import threading
import json
from datetime import datetime

# In-memory storage for users, messages, and client connections
users = []  # List of currently connected users
messages = []  # List of posted messages
clients = []  # List of active client connections
user_groups = {}  # Dictionary to map users to groups
client_user_mapping = {}  # Map client sockets to usernames


groups = [
    {'group_id': 1, 'group_name': 'Group1'},
    {'group_id': 2, 'group_name': 'Group2'},
    {'group_id': 3, 'group_name': 'Group3'},
    {'group_id': 4, 'group_name': 'Group4'},
    {'group_id': 5, 'group_name': 'Group5'}
]


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
            'body': self.body,
        }
    

users = ['Alice', 'Bob', 'Charlie']
messages = [
    #Message('Alice', 'Hello', 'Hello everyone!'),
    #Message('Bob', 'Hi', 'Hi Alice!'),
    #Message('Charlie', 'Greetings', 'Greetings to all!')
]
clients = []
user_groups = {
    'Alice': [groups[0], groups[1]],
    'Bob': [groups[1], groups[2]],
    'Charlie': [groups[2], groups[3]]
}

running = True

client_user_mapping_lock = threading.Lock()
# Function to handle client requests
def handle_client(client_socket, client_address):

    # Add client socket to the list of active clients
    clients.append(client_socket)
    global running
    while running:
        try:
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
                if username in users:
                    client_socket.send(json.dumps({'status': 'failure', 'message': f'Username "{username}" is already taken.'}).encode('utf-8'))
                else:
                    users.append(username)
                    with client_user_mapping_lock:
                        client_user_mapping[client_socket] = username
                    user_groups[username] = [] 
                    print(f"Updated client_user_mapping: {client_user_mapping}")  # Debugging statement
                    broadcast_message(f'{username} has joined the chat room!\n'.encode('utf-8'))
                
                
                print(f"User '{username}' has joined the the general chat.")

                
                #last_messages = get_last_messages()
                #print("Test:", last_messages)
                #for msg in last_messages:
                #    broadcast_message(msg)

                # Broadcast the user joining message to all connected clients
                #join_message = Message('System', 'User Joined', f'User "{username}" has joined the group.')
                #broadcast_message(join_message)

                # Send success response
                client_socket.send(json.dumps({'status': 'success', 'message': f'Welcome, {username}!' }).encode('utf-8'))

            elif command == '%connect':
                address_port = message[1:]
                if len(address_port) == 2:
                    try:
                        new_host = address_port[0]
                        new_port = int(address_port[1])
                        client_socket.close()
                        new_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        new_client.connect((new_host, new_port))
                        client_socket.send(f'Connected to specified address {new_host} and port {new_port}.\n'.encode('utf-8'))
                    except Exception as e:
                        client_socket.send(f'Error connecting: {str(e)}'.encode('utf-8'))
                else:
                    client_socket.send('Invalid command format. Use "%connect [address] [port]\n".'.encode('utf-8'))
            


            elif command == 'grouppost':
                print(f"Updated client_user_mapping: {client_user_mapping}")  # Debugging statement
                group_id = request_data.get('group_id')
                sender = request_data.get('sender')
                subject = request_data.get('subject')
                body = request_data.get('body')
                print(f"Received group_id: {group_id}")  # Debug: print received group_id

                # Validate that the group_id is an integer
                try:
                    group_id = int(group_id)
                except ValueError:
                    client_socket.send(json.dumps({'status': 'failure', 'message': 'Invalid group_id format.'}).encode('utf-8'))
                    return
                if not sender or not subject or not body:
                    client_socket.send(json.dumps({'status': 'failure', 'message': 'Sender, subject, and body are required.'}).encode('utf-8'))
                else:
                    # Validate that the sender is in the specified group
                    group = next((g for g in groups if g['group_id'] == group_id), None)
                    print(group)
                    print(user_groups.get(sender, []))
                    if not group or group not in user_groups.get(sender, []):
                        client_socket.send(json.dumps({'status': 'failure', 'message': 'You are not a member of the specified group.'}).encode('utf-8'))
                    else:
                        # Get current timestamp
                        now = datetime.now()
                        post_date = now.strftime('%Y-%m-%d %H:%M:%S')
                        full_message = f"Date: {post_date}\nSender: {sender}\nSubject: {subject}\nContent: {body}\n"
                        messages.append(full_message)
                        print(f"Message posted by {sender} in group '{group['group_name']}': '{subject}'")
                        # Broadcast the message to the group
                        broadcast_message_group(full_message.encode('utf-8'), group_id)

                        client_socket.send(json.dumps({'status': 'success', 'message': f'group message posted successfully!'}).encode('utf-8'))
                        client_socket.send(json.dumps({'status': 'success', 'message': f'group message posted successfully!'}).encode('utf-8'))
                print("Server ran group post")

            elif command == 'post':
                # Extract the subject and body from the message
                subject = request_data.get('subject')
                body = request_data.get('body')
                sender = request_data.get('sender')

                # Check if the subject and body are not empty
                if not subject or not body:
                    client_socket.send(json.dumps({'status': 'failure', 'message': 'Subject and body are required.'}).encode('utf-8'))
                else:
                    # Get current timestamp
                    now = datetime.now()
                    post_date = now.strftime('%Y-%m-%d %H:%M:%S')

                    # Format the message as per the new requirement
                    full_message = f"Date: {post_date}\nSender: {sender}\nSubject: {subject}\nContent: {body}\n"

                    
                    # Append the formatted message to the messages list
                    messages.append(full_message)

                    print(f"Message posted by {sender}: '{subject}'")

                    # Broadcast the formatted message to all clients
                    broadcast_message(full_message.encode('utf-8'))

                    # Send a success response to the client
                    client_socket.send(json.dumps({'status': 'success', 'message': f'Message titled "{subject}" posted successfully!'}).encode('utf-8'))

            elif command == 'leave':
                username = request_data.get('username')
                if not username or username not in users:
                    client_socket.send(json.dumps({'status': 'failure', 'message': f'User "{username}" not found.'}).encode('utf-8'))
                else:
                    users.remove(username)

                    print(f"User '{username}' has left the chat.")
                    
                    # Broadcast that the user has left
                    broadcast_message(f'{username} has left the chat room!\n'.encode('utf-8'))
                    
                    client_socket.send(f'User "{username}" has left the chat.'.encode('utf-8'))
                    client_socket.send(json.dumps({'status': 'success', 'message': 'User has left group successfully!'}).encode('utf-8'))

            elif command == 'groupleave':
                group_id = request_data.get('group_name')
                username = request_data.get('username')
                print(group_id)
                if username not in users:
                    client_socket.send(json.dumps({'status': 'failure', 'message': f'User "{username}" not found in the system.'}).encode('utf-8'))
                else:
                    group = next((g for g in groups if g['group_name'] == group_id), None)
                    print(group)
                    if group:
                        user_groups_list = user_groups.get(username, [])
                        group_in_user_groups = next((ug for ug in user_groups_list if ug['group_name'] == group_id), None)
                        
                        if group_in_user_groups:
                            user_groups[username].remove(group_in_user_groups)
                            print(f"User '{username}' has left group '{group['group_name']}'.")
                            
                            # Broadcast that the user has left the group
                            leave_message = Message('System', 'User Left Group', f'User "{username}" has left group "{group["group_name"]}".')
                            numbers_only = ''.join([char for char in group_id if char.isdigit()])
                            broadcast_message_group(leave_message, numbers_only)
                            
                            client_socket.send(f'User "{username}" has left group "{group["group_name"]}".'.encode('utf-8'))
                            client_socket.send(json.dumps({'status': 'success', 'message': f'user has left group successfully!'}).encode('utf-8'))
                        else:
                            client_socket.send(json.dumps({'status': 'failure', 'message': f'User "{username}" is not in the specified group.'}).encode('utf-8'))
                    else:
                        client_socket.send(json.dumps({'status': 'failure', 'message': f'Group with ID "{group_id}" not found.'}).encode('utf-8'))

            elif command == 'users':
                client_socket.send(f'Connect User:\n{users}'.encode('utf-8'))
                # Send a success response to the client
                client_socket.send(json.dumps({'status': 'success', 'message': f'user list posted successfully!'}).encode('utf-8'))

            elif command == 'groupusers':
                group_id = request_data.get('group_id')
                group = next((g for g in groups if g['group_name'] == group_id), None)
                print(group_id)
                print(groups)
                if group:
                    group_users = [user for user, user_groups_list in user_groups.items() if group in user_groups_list]
                    client_socket.send(f'Connect Users In Group:\n {group_users}'.encode('utf-8'))
                    
                else:
                    client_socket.send(json.dumps({'status': 'failure', 'message': 'Group not found.'}).encode('utf-8'))
                client_socket.send(json.dumps({'status': 'success', 'message': f'user list posted successfully!'}).encode('utf-8'))
            elif command == 'groups':
                if groups:
                    # Send a list of all available groups
                    group_names = [group['group_name'] for group in groups]
                    group_names_string = '\n'.join(group_names)
                                   
                    client_socket.send(f'Joinable Groups:\n{group_names_string}'.encode('utf-8'))

                    client_socket.send(json.dumps({'status': 'success', 'message': f'group list posted successfully!'}).encode('utf-8'))
                            
            elif command == 'join_group':
                print(f"Updated client_user_mapping: {client_user_mapping}")  # Debugging statement
                username = request_data.get('username')
                group_id = request_data.get('group_id')
                print(group_id)
                group = next((g for g in groups if g['group_name'] == group_id), None)
                print(group)
                if not username:
                    client_socket.send(json.dumps({'status': 'failure', 'message': 'You must join first before joining a group.'}).encode('utf-8'))
                elif not group:
                    client_socket.send(json.dumps({'status': 'failure', 'message': 'Group not found.'}).encode('utf-8'))
                else:
                    if username not in user_groups:
                        user_groups[username] = []
                    if group in user_groups[username]:
                        client_socket.send(json.dumps({'status': 'failure', 'message': f'User "{username}" is already in group "{group["group_name"]}".'}).encode('utf-8'))
                    else:
                        user_groups[username].append(group)
                        print(f"User '{username}' joined group '{group['group_name']}'.")
                        client_socket.send(f'Status: success\nMessage: You have successfully joined the group "{group["group_name"]}".'.encode('utf-8'))
                        client_socket.send(json.dumps({'status': 'success', 'message': f'group joined successfully!'}).encode('utf-8'))
                print(user_groups)

            elif command == 'message':
                group_id = request_data.get('group_id')
                message_id = request_data.get('message_id')
                group = next((g for g in groups if g['group_id'] == group_id or g['group_name'] == group_id), None)
                group_messages = [msg for msg in messages if msg.sender == group['group_name']]
                if 0 < message_id <= len(group_messages):
                    message = group_messages[message_id - 1].to_dict()
                    client_socket.send(json.dumps({'status': 'success', 'message': message}).encode('utf-8'))
                    print("Message Attempted")
                else:
                    client_socket.send(json.dumps({'status': 'failure', 'message': f'Message with ID {message_id} not found in group "{group["group_name"]}".'}).encode('utf-8'))
                print(f"Error handling client request: {e}")
        except Exception as e:
            print(f"Error handling client request: {e}")
        finally:
            # Remove client from the active list and username mapping when disconnecting
            print("attempted final")
                ##print(f"User '{disconnected_user}' has disconnected.")
    
    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()
        


# Function to broadcast a message to all connected clients
def broadcast_message(message):
    for client in clients:
        client.send(message)

def broadcast_message_group(message, group_id):
    for client_socket in clients:
        with client_user_mapping_lock:
            username = client_user_mapping.get(client_socket)
            print(username)
        if username:
            user_groups_for_user = user_groups.get(username, [])
            if any(group['group_id'] == group_id for group in user_groups_for_user):
                try:
                    client_socket.send(message)
                except:
                    clients.remove(client_socket)

def get_client_username(client):
    print(client_user_mapping)
    return client_user_mapping.get(client)


# Function to handle server console commands
def handle_server_console():
    while True:
        try:
            command = input("Enter server command: ").strip().lower()
        except EOFError:
            print("EOFError: Exiting the server.")
            break

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
    print("Server started on port 5050...")

    #welcome_message = Message('System', 'Welcome to General Chat', f'Welcome Users, to the general chat!')
    #broadcast_message(welcome_message)

    #nice_message = Message('System', 'Please Be Nice', 'Please be respectful and kind to everyone in the chat.')
    #broadcast_message(nice_message)

    while True:
        # Accept incoming client connections
        client_socket, addr = server.accept()
        print(f"Connection established with {addr}")
        
        # Handle each client in a new thread
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

def get_last_messages():
    # Return the last two messages from the global messages list
    print("attempting to send user 1")
    return [msg.to_dict() for msg in messages[-2:]]

def get_messages_from_group(group_id, limit=2):
    # Here you would query your database or data structure to get the last `limit` messages for the given group.
    # Example:
    messages = [
        {'sender': 'User1', 'subject': 'Hello World', 'date': '2024-12-03', 'body': 'This is the first message.'},
        {'sender': 'User2', 'subject': 'Greetings', 'date': '2024-12-02', 'body': 'This is the second message.'},
    ]
    return messages[-limit:]  # Return the last `limit` messages
start_server()