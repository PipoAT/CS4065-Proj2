import json
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

# Global variables
server_url = 'localhost'  # Default server address
server_port = 5050       # Default server port
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
            global username
            if not username:
                username = input("Enter your username: ").strip()
            
            # Continuously prompt for a new username if the one entered is taken
            send_request('join', {'username': username})
        
        # %post command to post a message
        elif command.startswith("%post"):
            _, subject, *body = command.split()
            body = ' '.join(body)
            post_message(subject, body)
        
        # %users command to get the list of users
        elif command == "%users":
            send_request('users')
        
        # %leave command to leave the group
        elif command == "%leave":
            if not username:
                print("You must join the group first using the %join command.")
                return

            send_request('leave', {'username': username})
            username = ''  # Clear username after leaving
        
        # %message command to get a specific message by ID
        elif command.startswith("%message"):
            try:
                _, message_id = command.split()
                message_id = int(message_id)  # Ensure it's an integer
                get_message(message_id)
            except ValueError:
                print("Invalid message ID. Please provide a valid numeric ID.")
        # %exit command to exit the client
        elif command == "%exit":
            print("Exiting the client.")
            break

        elif command == "%groups":
            groups = send_request('groups')
            groups_list = json.loads(groups).get('groups', [])
            for group in groups_list:
                print(f"Group ID: {group['group_id']}, Group Name: {group['group_name']}")

        elif command == "%groupjoin":
            join_group_by_id()

        elif command.startswith("%grouppost"):
            parts = command.split(' ', 3)  # Split into 3 parts: group_id, subject, body
            if len(parts) < 4:
                print("Missing Parts -> Make While Later")
            else:
                group_id = parts[1]  # Assuming the first part is the group ID
                subject = parts[2]  # The second part is the subject
                body = parts[3]  # The third part is the body

                # Assuming 'post_to_group_by_id' is a function to handle posting a message to a group
                post_to_group_by_id(group_id, subject, body)
            print("Grouppost ran.")

        elif command == "%groupusers":
            get_users_by_id()

        elif command == "%groupleave":
            leave_group_by_id()
        
        elif command == "%groupmessage":
            get_message_by_id()
        
        # Invalid command handling
        else:
            print("Invalid command. Available commands: %connect, %join, %post, %users, %leave, %message, %exit, %groups, %groupjoin, %grouppost, %groupusers, %groupleave, %groupmessage.")

def join_group_by_id():
    global username
    
    # Ensure that the username is set before proceeding
    if not username:
        print("Username is required to join a group. Please set your username first.")
        username = input("Enter your username: ").strip()

    groups = send_request('groups')
    groups_list = json.loads(groups).get('groups', [])
    print("Available groups:")
    for group in groups_list:
        print(f"Group ID: {group['group_id']}, Group Name: {group['group_name']}    ")

    group_id = input("Enter the group name: ")
    group = next((g for g in groups_list if g['group_id'] == group_id or g['group_name'] == group_id), None)
    
    if not group:
        print(f"Group {group_id} not found.")
        return

    # Use the global username for joining the group
    response = send_request('join_group', {'group_id': group['group_id'], 'username': username})
    response_data = json.loads(response)
    if response_data.get('status') == 'success':
        print(f"Successfully joined group {group_id}")
    else:
        print(f"Failed to join group {group_id}: {response_data.get('error', response_data.get('message'))}")


def post_to_group_by_id(group, subject, body):
    while not subject.strip() or not body.strip():
        if not subject.strip():
            subject = input("Please enter a title (subject) for your post: ").strip()
        
        if not body.strip():
            body = input("Please enter the body (content) of your post: ").strip()

        # Provide feedback on the correct format if both are missing
        if not subject.strip() or not body.strip():
            print("Both title and body are required. Please follow this format:")
            print("Title (subject): A brief title for the post.")
            print("Body: The content of your post.\n")
    
    # Once both are provided, send the post request
    send_request('grouppost', {'group': group, 'sender': username, 'subject': subject, 'body': body})

def get_users_by_id():
    response = send_request('groups')
    groups_list = json.loads(response).get('groups', [])
    group_id = input("Enter the group ID: ")
    group = next((g for g in groups_list if g['group_id'] == group_id or g['group_name'] == group_id), None)
    response = send_request('groupusers', {'group_id': group['group_id']})
    users = json.loads(response).get('users', [])
    if not users:
        print(f"No users found in group {group_id}.")
    else:
        print(f"Users in group {group_id}:")
        for user in users:
            print(user)

def leave_group_by_id():
    response = send_request('groups')
    group_id = input("Enter the group ID: ")
    username = input("Enter your username: ")
    groups_list = json.loads(response).get('groups', [])
    group = next((g for g in groups_list if g['group_id'] == group_id or g['group_name'] == group_id), None)
    if not group:
        print(f"Group {group_id} not found.")
        return

    response = send_request('groupleave', {'group_id': group['group_id'], 'username': username})
    print( f"Successfully left group {group_id}")
        

def get_message_by_id():
    send_request('groupmessage', {'message_id': message_id})

def send_request(command, data=None, data2=None):
    # Create socket and send data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.settimeout(5)  # Set a timeout of 5 seconds
        try:
            client_socket.connect((server_url, server_port))
            
            request_data = {'command': command}
            if data:
                request_data.update(data)

            if data2:
                request_data.update(data2)
            
            client_socket.send(json.dumps(request_data).encode('utf-8'))
            
            response = client_socket.recv(1024).decode('utf-8')
            return response
        except socket.timeout:
            print("Request timed out. Please try again.")
            return json.dumps({'status': 'error', 'error': 'Request timed out'})
        except Exception as e:
            print(f"An error occurred: {e}")
            return json.dumps({'status': 'error', 'error': str(e)})

def post_message(subject, body):
    if not username:
        print("You must join the group first using the %join command.")
        return

    send_request('post', {'sender': username, 'subject': subject, 'body': body})
    print(subject, body)    

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

    class ChatClientGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("Chat Client")

            self.server_url = tk.StringVar(value='localhost')
            self.server_port = tk.IntVar(value=5050)
            self.username = tk.StringVar()

            self.create_widgets()

        def create_widgets(self):
            # Server connection frame
            connection_frame = tk.Frame(self.root)
            connection_frame.pack(pady=10)

            tk.Label(connection_frame, text="Server Address:").grid(row=0, column=0, padx=5)
            tk.Entry(connection_frame, textvariable=self.server_url).grid(row=0, column=1, padx=5)
            tk.Label(connection_frame, text="Port:").grid(row=0, column=2, padx=5)
            tk.Entry(connection_frame, textvariable=self.server_port).grid(row=0, column=3, padx=5)
            tk.Button(connection_frame, text="Connect", command=self.connect_to_server).grid(row=0, column=4, padx=5)

            # Username frame
            username_frame = tk.Frame(self.root)
            username_frame.pack(pady=10)

            tk.Label(username_frame, text="Username:").grid(row=0, column=0, padx=5)
            tk.Entry(username_frame, textvariable=self.username).grid(row=0, column=1, padx=5)
            tk.Button(username_frame, text="Join Any Group", command=self.join_group).grid(row=0, column=2, padx=5)
            tk.Button(username_frame, text="Join Group By ID", command=self.join_group_by_id).grid(row=0, column=3, padx=5)

            # Message display area
            self.message_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', width=50, height=15)
            self.message_area.pack(pady=10)

            # Message posting frame
            post_frame = tk.Frame(self.root)
            post_frame.pack(pady=10)

            tk.Label(post_frame, text="Subject:").grid(row=0, column=0, padx=5)
            self.subject_entry = tk.Entry(post_frame)
            self.subject_entry.grid(row=0, column=1, padx=5)
            tk.Label(post_frame, text="Message:").grid(row=1, column=0, padx=5)
            self.message_entry = tk.Entry(post_frame)
            self.message_entry.grid(row=1, column=1, padx=5)
            tk.Button(post_frame, text="Post", command=self.post_message).grid(row=1, column=2, padx=5)

            # Users and exit buttons
            button_frame = tk.Frame(self.root)
            button_frame.pack(pady=10)

            tk.Button(button_frame, text="Get Users", command=self.get_users).grid(row=0, column=0, padx=5)
            tk.Button(button_frame, text="Get Users by Group", command=self.get_users_by_id).grid(row=0, column=1, padx=5)
            tk.Button(button_frame, text="Get Groups", command=self.get_groups).grid(row=0, column=2, padx=5)
            tk.Button(button_frame, text="Get Message", command=self.get_message_by_id).grid(row=0, column=3, padx=5)
            tk.Button(button_frame, text="Leave Group", command=self.leave_group).grid(row=0, column=4, padx=5)
            tk.Button(button_frame, text="Leave Group By ID", command=self.leave_group_by_id).grid(row=0, column=5, padx=5)
            tk.Button(button_frame, text="Exit", command=self.exit_client).grid(row=0, column=6, padx=5)

        def get_groups(self):
            # Send a request to the server to get the list of groups
            response = send_request('groups')
            groups = json.loads(response).get('groups', [])
            if not groups:
                messagebox.showerror("Error", "No groups available.")
            else:
                messagebox.showinfo("Groups", "\n".join([f"Group ID: {group['group_id']}, Group Name: {group['group_name']}" for group in groups]))

        def get_message_by_id(self):
            # Send a request to the server to get a message by its ID
            message_id = tk.simpledialog.askstring("Message ID", "Enter the message ID:")
            response = send_request('message', {'message_id': message_id})
            print(response)

        def connect_to_server(self):
            global server_url, server_port
            server_url = self.server_url.get()
            server_port = self.server_port.get()
            self.append_message(f"Connected to server at {server_url}:{server_port}")

        def join_group(self):
            global username
            username = self.username.get()
            if not username:
                messagebox.showerror("Error", "Username cannot be empty.")
                return
            send_request('join', {'username': username})
            

        def join_group_by_id(self):
            # Fetch the list of groups first
            response = send_request('groups')
            groups_list = json.loads(response).get('groups', [])
            if not groups_list:
                messagebox.showerror("Error", "No groups available.")
                return

            group_id = tk.simpledialog.askstring("Group ID", "Enter the group ID or Name to leave:")
            if not group_id:
                return
            username = tk.simpledialog.askstring("Username", "Enter your username:")
            if not username:
                return

            group = next((g for g in groups_list if g['group_id'] == group_id or g['group_name'] == group_id), None)
            if not group:
                messagebox.showerror("Error", f"Group {group_id} not found.")
                return

            response = send_request('join_group', {'group_id': group['group_id'], 'username': username})
            response_data = json.loads(response)
            if response_data.get('status') == 'success':
                messagebox.showinfo("Success", f"Successfully joined group {group_id}")
                gui.append_message(f"{username} successfully joined group {group_id}")
            else:
                messagebox.showerror("Error", f"Failed to join group {group_id}: {response_data.get('error', response_data.get('message'))}")

        def leave_group_by_id(self):
            # Fetch the list of groups first
            response = send_request('groups')
            groups_list = json.loads(response).get('groups', [])
            if not groups_list:
                messagebox.showerror("Error", "No groups available.")
                return

            group_id = tk.simpledialog.askstring("Group ID", "Enter the group ID or Name:")
            if not group_id:
                return
            username = tk.simpledialog.askstring("Username", "Enter your username:")
            if not username:
                return

            group = next((g for g in groups_list if g['group_id'] == group_id or g['group_name'] == group_id), None)
            if not group:
                messagebox.showerror("Error", f"Group {group_id} not found.")
                return

            response = send_request('groupleave', {'group_id': group['group_id'], 'username': username})
            response_data = json.loads(response)
            if response_data.get('status') == 'success':
                messagebox.showinfo("Success", f"Successfully left group {group_id}")
                gui.append_message(f"{username} successfully left group {group_id}")
                username = ''
            else:
                messagebox.showerror("Error", f"Failed to leave group {group_id}: {response_data.get('error', response_data.get('message'))}")

        def post_message(self):
            subject = self.subject_entry.get()
            body = self.message_entry.get()
            if not username:
                messagebox.showerror("Error", "You must join the group first.")
                return
            send_request('post', {'sender': username, 'subject': subject, 'body': body})

        def get_users(self):
            send_request('users')
            response = send_request('users')
            users = json.loads(response).get('users', [])
            if not users:
                messagebox.showerror("Error", "No users in the group.")
            else:
                messagebox.showinfo("Users", "\n".join(users))

        def get_users_by_id(self):
            response = send_request('groups')
            groups_list = json.loads(response).get('groups', [])
            group_id = tk.simpledialog.askstring("Group ID", "Enter the group ID or Name:")
            if not group_id:
                return
            group = next((g for g in groups_list if g['group_id'] == group_id or g['group_name'] == group_id), None)
            if not group:
                messagebox.showerror("Error", f"Group {group_id} not found.")
                return

            response = send_request('groupusers', {'group_id': group['group_id']})
            users = json.loads(response).get('users', [])
            if not users:
                messagebox.showinfo("Users", "No users found in the group.")
            else:
                messagebox.showinfo("Users", "\n".join(users))
            

        def leave_group(self):
            global username
            if not username:
                messagebox.showerror("Error", "You must join the group first.")
                return
            send_request('leave', {'username': username})
            username = ''
            self.append_message("You have left the group.")

        def exit_client(self):
            self.root.quit()

        def append_message(self, message):
            self.message_area.config(state='normal')
            self.message_area.insert(tk.END, message + '\n')
            self.message_area.config(state='disabled')

        def post_group_message(self):
            group = self.group_entry.get()
            subject = self.subject_entry.get()
            body = self.message_entry.get()
            
            if not username:
                messagebox.showerror("Error", "You must join the group first.")
                return
            message = send_request('grouppost', {'group': group, 'sender': username, 'subject': subject, 'body': body})
            gui.append_message(f"{message}.")

        def gui_listen_for_messages(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((server_url, server_port))

                while True:
                    response = client_socket.recv(1024).decode('utf-8')
                    if not response:
                        break

                    response_data = json.loads(response)
                    if response_data.get('status') == 'new_message':
                        message = response_data.get('message')
                        gui.append_message(f"\nNew Message:\nFrom: {message['sender']}\nSubject: {message['subject']}\nDate: {message['date']}\nBody: {message['body']}\n")
                    else:
                        gui.append_message("Response: " + str(response_data))

    if __name__ == '__main__':
        print("Select preferred client interface: GUI/CLI")
        command = input().strip().lower()
        if command == "cli":
            handle_commands()
        elif command == "gui": 
            root = tk.Tk()
            gui = ChatClientGUI(root)

            listen_thread = threading.Thread(target=gui.gui_listen_for_messages)
            listen_thread.daemon = True
            listen_thread.start()

            root.mainloop()
        else:
            print("Please use a valid command: cli | gui")