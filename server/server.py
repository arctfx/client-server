import socket
import sys
import threading
import multiprocessing
import time
from multiprocessing import freeze_support
import selectors
import asyncio

import table_db

size = 10

# ---------------------------------------------------------------------------------
# Variables for holding information about connections
connections = []
total_connections = 0
N = 1

sel = selectors.DefaultSelector()


"""
New instance created for each client
Some functionalities are deprecated in Client
"""


class Client(threading.Thread):
    def __init__(self, socket_, address, id_, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket_
        self.address = address
        self.id = id_
        self.name = name
        self.signal = signal

    def __str__(self):
        return str(self.id) + " " + str(self.address)

    # Deprecated?
    def run(self):
        while self.signal:
            try:
                data = self.socket.recv(32)
            except:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                connections.remove(self)
                break
            # if data != "":
            #     print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))
            #     for client in connections:
            #         if client.id != self.id:
            #             client.socket.sendall(data)


# async def newConnections_async(host, port):
#     server = await asyncio.start_server(newConnections, socket)
#     addr = server.sockets[0].getsockname()
#     print(f"Serving on {addr}")
#
#     async with server:
#         await server.serve_forever()
#
#
# def newConnections_wrapper(host, port):
#     # Start the asyncio event loop in the current thread
#     asyncio.run(newConnections_async(host, port))


def newConnections(socket_):  # Wait for new connections
    # print("Debug: newConnections call!")
    while True:
        sock, address = socket_.accept()  # sock is the client socket, while socket_ is the server socket!

        """ Here we use a little trick to enable multiple clients to connect to the server at the same time:
               socket_.accept() acts like a semaphore
            Alternatively, we could use selectors for I/O multiplexing """
        newConnectionsThread = threading.Thread(target=newConnections, args=(socket_,))
        newConnectionsThread.start()

        """ Receive input from the client """
        # data = sock.recv(32)
        size_ = size
        try:
            while True:
                data = sock.recv(32)
                if data:
                    size_ = int(data.decode("utf-8"))
                    print(f"Received integer: {size_}")
                    break
        except ValueError:
            print(f"Invalid data received from {address}. Expected an integer.")
        except Exception as e:
            print(f"Error handling client {address}: {e}")

        # print("Accepted connection from " + address)
        global total_connections, N
        connections.append(Client(sock, address, total_connections, "Name", True))
        connections[len(connections) - 1].start()
        print("New connection at ID " + str(connections[len(connections) - 1]))
        total_connections += 1

        """ Handle Client """
        start_time = time.time()

        elapsed_time: float = fill_table(size_, size_, N)

        sock.sendall(str(elapsed_time).encode("utf-8"))  # Send back the output

        # Debug: table
        # print("Final table state:")
        # for row_ in table:
        #    print(row_)


def fill_table(num_rows, num_cols, num_processes) -> float:
    """Optimized parallel table fill."""
    table = [[0] * num_cols for _ in range(num_rows)]

    # Calculate row chunks for each process
    chunk_size = num_rows // num_processes
    processes = []
    start_time = time.time()

    for i in range(num_processes):
        start_row = i * chunk_size
        end_row = (i + 1) * chunk_size if i < num_processes - 1 else num_rows

        table_chunk = table[start_row:end_row]  # Local copy for the process
        process = multiprocessing.Process(target=table_db.fill_table_chunk,
                                          args=(start_row, end_row, table_chunk, i + 1))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    elapsed_time = time.time() - start_time
    print(f"Table filled with {num_processes} processes in {elapsed_time:.2f} seconds.")
    # return table
    return elapsed_time


def main():
    # Get host and port
    try:
        host, port = sys.argv[1], int(sys.argv[2])
        print(f"Host: {host}, port: {port}")
    except IndexError:
        host = input("Host: ")
        port = int(input("Port: "))

    # Create new server socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()
        # sock.setblocking(False)
        # sel.register(sock, selectors.EVENT_READ, data=None)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

    # Create new thread to wait for connections
    newConnectionsThread = threading.Thread(target=newConnections, args=(sock,))
    newConnectionsThread.start()


if __name__ == "__main__":
    freeze_support()
    # multiprocessing.set_start_method("spawn")
    main()
