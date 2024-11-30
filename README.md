# Project 2: Simple Client-Server Interaction

Project 2 for Computer Networks at University of Cincinnati Fall 2024 Semester.

### Files Included:
- `client.py`: The Python script that acts as the client. It sends requests to the server and processes the responses.
- `server.py`: The Python script that acts as the server. It handles requests from the client and sends responses back.
- `index.html`: Not currently Working - A simple HTML page that the client interacts with.
- `login.html`: Not currently Working - Leagacy Idea
---
## Setting Up and Running the Project
### Step 1: Running the Server
- Open a terminal (or command prompt).
- Navigate to the directory containing the project files (client.py, server.py, and index.html).
- Start the server by running the following command:
```
python server.py
```
The server will start and listen for incoming requests on a specified port (typically http://localhost:8080).
### Step 2: Running the Client
- The client (client.py) is typically invoked from within the HTML page (via JavaScript) or can be manually run from the terminal.
- To run the client, use the following command in a new terminal:
```
python client.py
```
The client will connect to the server at http://localhost:8080, send requests, and handle the server's responses.
---
## How To Utilize the GUI
### Step 1: Enter the Server Address and Port, and click "Connect"
### Step 2: Enter the Username, and click "Join"
### Step 3: You can perform any of the actions below:
#### - To Send a Message, Enter the Subject and Message, and click "Post"
#### - To View All Users, click "Get Users"
#### - To Leave the Chat, click "Leave"
#### - To Exit the GUI, click "Exit"
---


## How To Use The Client Code 
### Step 1: Connect to The Server
```
%connect localhost 8080 
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
%connect localhost 8080 

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