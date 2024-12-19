import socket
import tkinter as tk
from tkinter import scrolledtext
import threading
import random  # For introducing a 5% probability of message corruption for testing

# Set up server information
server_socket = socket.socket()
host = socket.gethostname()
ip = socket.gethostbyname(host)
port = 1423
server_socket.bind((host, port))
server_socket.listen()

print(f"Server is running on {host} with IP {ip} and port {port}")

# GUI setup
root = tk.Tk()
root.title("Server Chat")

server_label = tk.Label(root, text="SERVER", font=("Helvetica", 12, "bold"))
server_label.grid(row=0, column=0, padx=10, pady=(10, 0))

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
chat_area.grid(row=1, column=0, padx=10, pady=(5, 10))

def update_chat(message):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, message + '\n')
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

update_chat("Waiting for clients to connect...")

clients = []
client_names = {}

# Function to calculate CRC checksum for data using polynomial "10101"
def calculate_crc(data, polynomial="10101"):
    data = data + "0" * (len(polynomial) - 1)
    data = list(data)
    poly = list(polynomial)

    for i in range(len(data) - len(poly) + 1):
        if data[i] == '1':
            for j in range(len(poly)):
                data[i + j] = str(int(data[i + j]) ^ int(poly[j]))

    return "".join(data[-(len(polynomial) - 1):])  # Return the remainder part

# Function to verify the CRC checksum of received data
def verify_crc(data, checksum, polynomial="10101"):
    data_with_checksum = data + checksum
    remainder = calculate_crc(data_with_checksum, polynomial)
    return remainder == "0" * (len(polynomial) - 1)

# Track the last broadcasted message to avoid repetition
last_broadcasted_message = None

def broadcast(message, sender_socket=None):
    global last_broadcasted_message

    # Convert the message to binary
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    # Calculate the CRC checksum
    crc_checksum = calculate_crc(binary_message)

    # Introduce a 5% probability of message corruption
    if random.random() < 0.05:
        corrupted_binary_message = binary_message[:-1] + ('1' if binary_message[-1] == '0' else '0')
        message_with_crc = f"{corrupted_binary_message}|{crc_checksum}"
        update_chat(f"Server > {message}\n\tSent (Corrupted): {corrupted_binary_message}")
    else:
        message_with_crc = f"{binary_message}|{crc_checksum}"
        update_chat(f"Server > {message}\n\tSent (Valid): {binary_message}")

    # Send the message with CRC to all clients, excluding the sender
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message_with_crc.encode())
            except Exception as e:
                update_chat(f"Error sending to client: {e}")
                clients.remove(client)

    last_broadcasted_message = message

# Function to send a message from the server
def send_message():
    message = input_field.get().strip()
    if message:  # Only send non-empty messages
        broadcast(message)  # Broadcast only the core message (without "Server >")
        input_field.delete(0, tk.END)

# Function to accept incoming client connections
def accept_clients():
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        send_button.config(state=tk.NORMAL)  # Enable the send button after a client connects
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    try:
        client_name = client_socket.recv(1024).decode()  # Assume the client sends its name first
        client_names[client_socket] = client_name

        # Notify all clients about the new connection
        broadcast(f"{client_name} has joined the chat room.", client_socket)
        update_chat(f"{client_name} has joined the chat room.")

        while True:
            message_with_crc = client_socket.recv(1024).decode()
            if "|" in message_with_crc:
                message_binary, crc_checksum = message_with_crc.rsplit("|", 1)

                if verify_crc(message_binary, crc_checksum):
                    # Message is valid
                    message = ''.join(chr(int(message_binary[i:i+8], 2)) for i in range(0, len(message_binary), 8))
                    if message == "[bye]":
                        broadcast(f"{client_name} has left the chat room.", client_socket)
                        update_chat(f"{client_name} has left the chat room.")
                        client_socket.close()
                        clients.remove(client_socket)
                        break
                    else:
                        # Broadcast the valid message to other clients
                        broadcast(message, client_socket)
                        update_chat(f"{client_name} > {message_binary}\n\tValid: Yes\n\tTranslated: {message}")
                else:
                    # Message is corrupted
                    update_chat(f"{client_name} > {message_binary}\n\tValid: No")
                    broadcast(f"{message_binary}", client_socket)
    except Exception as e:
        update_chat(f"Error handling client {client_names.get(client_socket, 'Unknown')}: {e}")
        client_socket.close()
        clients.remove(client_socket)

# GUI input and send message
input_field = tk.Entry(root, width=50, fg="grey")
input_field.grid(row=2, column=0, padx=10, pady=10)
input_field.insert(0, "Write your message here")
input_field.bind("<FocusIn>", lambda event: input_field.delete(0, tk.END) or input_field.config(fg="black"))
input_field.bind("<FocusOut>", lambda event: input_field.insert(0, "Write your message here") or input_field.config(fg="grey"))

send_button = tk.Button(root, text="Send", command=send_message, state=tk.DISABLED)
send_button.grid(row=3, column=0, pady=10)

# Start accepting clients in a separate thread
accept_thread = threading.Thread(target=accept_clients, daemon=True)
accept_thread.start()

# Run the Tkinter main loop
root.mainloop()
