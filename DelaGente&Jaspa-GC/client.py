import socket
import tkinter as tk
from tkinter import scrolledtext
import threading
import random  # For simulating packet loss

soc = socket.socket()

root = tk.Tk()
root.title("Client Chat")

name = input("Enter your name: ")
server_host = input("Enter server's IP address: ")
port = 1423

def connect_to_server():
    global connected
    try:
        print(f"Connecting to {server_host}:{port}...")
        soc.connect((server_host, port))
        soc.send(name.encode())
        print("***Connected to the server***")
        connected = True
    except Exception as e:
        print(f"Connection failed: {e}")
        connected = False

connected = False
connect_to_server()

client_label = tk.Label(root, text=f"Client: {name}", font=("Helvetica", 12, "bold"))
client_label.grid(row=0, column=0, padx=10, pady=(10, 0))

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
chat_area.grid(row=1, column=0, padx=10, pady=(5, 10))

def update_chat(message):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, message + '\n')
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

def send_message():
    global connected
    if connected:
        message = input_field.get()
        if message.strip():  # Only send non-empty messages
            # Convert text to binary
            binary_message = text_to_binary(message)
            crc_checksum = calculate_crc(binary_message)
            
            # Introduce 5% probability of message corruption
            if random.random() < 0.05:
                # Corrupt the binary message by flipping the last bit
                corrupted_binary_message = binary_message[:-1] + ('1' if binary_message[-1] == '0' else '0')
                message_with_crc = f"{corrupted_binary_message}|{crc_checksum}"
                update_chat(f"{name} > {message}\n\tSent (Corrupted): {corrupted_binary_message}")
            else:
                message_with_crc = f"{binary_message}|{crc_checksum}"
                update_chat(f"{name} > {message}\n\tSent (Valid): {binary_message}")
            
            try:
                soc.send(message_with_crc.encode())
                if message == "[bye]":
                    update_chat("You left the chat room.")
                    root.after(2000, root.quit)
            except Exception as e:
                update_chat(f"Error: {e}")
                connected = False
            finally:
                input_field.delete(0, tk.END)

def receive_messages():
    global connected
    while connected:
        try:
            message_with_crc = soc.recv(1024).decode()
            if "|" in message_with_crc:
                message, crc_checksum_or_error = message_with_crc.rsplit("|", 1)
                
                is_valid = verify_crc(message, crc_checksum_or_error)
                sender = "Server" if name not in message else name
                translated_message = translate_binary_to_text(message)
                
                if is_valid:
                    update_chat(f"{sender} > {message}\n\tValid: Yes\n\tTranslated: {translated_message}")
                else:
                    update_chat(f"{sender} > {message}\n\tValid: No")
        except:
            update_chat("Disconnected from server.")
            connected = False
            break

def text_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def calculate_crc(data, polynomial="10101"):
    # Add zeros to the data equal to the degree of the polynomial (4 for x^4 + x + 1)
    data = data + "0" * (len(polynomial) - 1)
    
    # Convert data to a list for easier manipulation
    data = list(data)
    poly = list(polynomial)
    
    # Perform the division (XOR operation) bit by bit
    for i in range(len(data) - len(poly) + 1):
        if data[i] == '1':  # Only perform division if the bit is '1'
            for j in range(len(poly)):
                data[i + j] = str(int(data[i + j]) ^ int(poly[j]))  # XOR operation
    
    # Return the remainder after division, which is the CRC checksum
    return "".join(data[-(len(polynomial) - 1):])  # Return the remainder part

def verify_crc(data, checksum, polynomial="10101"):
    # Append the checksum to the original data
    data_with_checksum = data + checksum
    
    # Calculate the CRC over the data with the checksum
    remainder = calculate_crc(data_with_checksum, polynomial)
    
    # If the remainder is all zeros, the data is valid
    return remainder == "0" * (len(polynomial) - 1)

def translate_binary_to_text(binary_str):
    # Convert binary to text message
    return ''.join(chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8))

input_field = tk.Entry(root, width=50)
input_field.grid(row=2, column=0, padx=10, pady=10)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.grid(row=3, column=0, pady=10)

receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

root.mainloop()
