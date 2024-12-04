# Project 2: Simple Client-Server Interaction
`By: Andrew P & Dylan B`

Project 2 for Computer Networks at University of Cincinnati Fall 2024 Semester.

### Files Included:
- `client.py`: The Python script that acts as the client. It sends requests to the server and processes the responses.
- `server.py`: The Python script that acts as the server. It handles requests from the client and sends responses back.
---
## Setting Up and Running the Project
### Step 1: Running the Server
- Open a terminal (or command prompt).
- Navigate to the directory containing the project files (client.py, server.py, and index.html).
- Start the server by running the following command:
```
python server.py
```
The server will start and listen for incoming requests on a specified port (typically http://localhost:5050).
### Step 2: Running the Client
- The client (client.py) is typically invoked from within the HTML page (via JavaScript) or can be manually run from the terminal.
- To run the client, use the following command in a new terminal:
```
python client.py
```
The client will connect to the server at http://localhost:5050, send requests, and handle the server's responses.
---
## How To Utilize the GUI
- To operate the GUI in place of the CLI, run the client.py script and enter in "GUI" when prompted to.
- The GUI will then appear and allow you to interact with the server.

- To Connect: Enter the server's IP address and port number in the input fields and click the "Connect" button.
- To Join A Group:
    - Enter the username in the input field and click the "Join Any Group" button.
    OR
    - Click "Join Group By ID" and enter the name of the group and username when prompted

- To Leave A Group:
    - Enter the username in the input field and click the "Leave Group" button.
    OR
    - Click "Leave Group By ID" and enter the name of the group and username when prompted

- To Send a Message: Enter the subject of the message alongside the message in the input fields and click the "Post" Button
- To Obtain Users:
    - Click "Get Users"
    OR
    - Click "Get Users by Group" and enter the name of the group

- To View Available Groups" Click on "Get Groups"

- To Obtain Messages: Click on "Get Message" and enter the ID of the message you want to find
---

## How To Use The Client Code 
### Step 1: Connect to The Server
```
%connect localhost 5050 
```
### Step 2: Join The Bored
```
%join
```
You will be prompted to enter a user name.
```
Enter your username: YourName
```
### Step 3: Post To The Bored
```
%post (Post Title) (Post Content)
```
### Full Example:
```
%connect localhost 5050 

%join
Enter your username: Dylan

%post Hello Hello I'm new here!
```
### Results: 
```
New Message:
From: Dylan
Subject: hello
Date: 2024-11-25 13:21:20
Body: hello i'm new here
```
All Users will be able to see your messages.
Multiple Terminal Instances can be run to simulate users joining.

# Issues:
### Getting Started
Originally, we planned to use Svelte as the basis for the visual elements of the GUI. However, after extensive testing and due to the lack of documentation on using Svelte with sockets and threading in Python, we decided to switch to a Python GUI library.

We breifly attempted to create a single-page HTML application. However, this proved to be quite challenging and time-consuming. After much frustration and numerous headaches, we decided as a group to revert to using Python libraries for gui of this project.

### Issues With Server Side Code
Early on, we encountered an issue where the server-side code wouldn't return the last two messages whenever a user joined the chat.

Another issue we encountered was that the code couldn't detect when a user disconnected abruptly (such as through a crash) and failed to remove them from the user list

User authentication has been a constant issue. In the early version of the code, the %users function worked as intended. However, between merging and updating to accommodate part two, it seemingly broke. This created issues where the server would allow any username to pass, even when it clearly shouldn't. We tried addressing this issue by reverting to older versions and directly integrating that code among other troubleshooting ideas, but we were unable to fix it.

The message ID system is also non-functional due to a similar issue. Although the system properly logs and documents all incoming and outgoing messages and saves them into a list, attempting to display messages only to recently joined users causes a bug. This was one of the most annoying issues we encountered. We tried isolating messages to send them to the user prior to their join group message being sent by the server, but this didn't fix the issue. Some of the code used for debugging and attempting to solve this problem can still be found in server.py. Given more time, we believe we could solve this bug.

### Issues With Client Side Code
Issues that we encountered included ensuring that user errors were handled properly as certain actions (i.e. typing in the wrong command, not providing enough info) could have easily cause the program to crash or freeze.

Also, we had encountered issues with the client code not being able to read the data from the server side code properly.