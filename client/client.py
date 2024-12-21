import socket
import threading
import sys
import json


# Wait for incoming data from server
# .decode is used to turn the message in bytes to a string
def receive(socket_, signal):
    while signal:
        try:
            data = socket_.recv(32)
            print(str(data.decode("utf-8")))
        except Exception as exception:
            print(f"You have been disconnected from the server: {exception}")
            signal = False
            break
        finally:
            socket_.close()
            input("Press enter to quit")
            sys.exit(0)


""" Main """
# Get host and port
host = input("Host: ")
port = int(input("Port: "))

# Attempt connection to server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print("Connected to the server.")
except Exception as e:
    print(f"Could not make a connection to the server: {e}")
    input("Press enter to quit")
    sys.exit(0)

try:
    while True:  # Prompt user for an integer
        try:
            size = int(input("Input [Table size]: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    # Send input to the server
    sock.sendall(str(size).encode("utf-8"))
except Exception as e:
    print(f"Error sending data to the server: {e}")

# finally:
#     # Close the connection
#     print("Closing connection.")
#     sock.close()

# Create new thread to wait for data
receiveThread = threading.Thread(target=receive, args=(sock, True))
receiveThread.start()


# if __name__ == 'main':
#     # Send data to server
#     # str.encode is used to turn the string message into bytes, so it can be sent across the network
#     # while True:
#     #     message = input()
#     #     sock.sendall(str.encode(message))
