import socket
import threading
import multiprocessing
import time
from multiprocessing import freeze_support
import selectors
import asyncio

import table_db

size = 1000

# ---------------------------------------------------------------------------------
# Variables for holding information about connections
connections = []
total_connections = 0
N = 2

sel = selectors.DefaultSelector()


# Client class, new instance created for each connected client
# Each instance has the socket and address that is associated with items
# Along with an assigned ID and a name chosen by the client
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

    # Attempt to get data from client
    # If unable to, assume client has disconnected and remove him from server data
    # If able to, and we get data back, print it in the server and send it back to every
    # client aside from the client that has sent it
    # .decode is used to convert the byte data into a printable string
    def run(self):
        while self.signal:
            try:
                data = self.socket.recv(32)
            except:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                connections.remove(self)
                break
            if data != "":
                print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))
                for client in connections:
                    if client.id != self.id:
                        client.socket.sendall(data)


# Wait for new connections
def newConnections(socket_):
    while True:
        sock, address = socket_.accept()

        # print("Accepted connection from " + address)
        global total_connections, N
        connections.append(Client(sock, address, total_connections, "Name", True))
        connections[len(connections) - 1].start()
        print("New connection at ID " + str(connections[len(connections) - 1]))
        total_connections += 1

        # Handle Client - should be in a separate thread

        start_time = time.time()

        # Initialize table
        # table = table_db.TableDB(size, size)
        #
        # manager = multiprocessing.Manager()
        # table_proxy = manager.list([manager.list([0] * size) for _ in range(size)])

        # processes = []
        # for thread_num in range(N):
        #     process = multiprocessing.Process(
        #         target=table_db.fill_table_thread, args=(table, thread_num, size, size, N))
        #     processes.append(process)
        #     process.start()
        #     # print("new process has started")
        #     # for row_ in table_proxy:
        #     #     print(row_)
        #
        # # Wait for all processes to complete
        # for process in processes:
        #     process.join()
        #
        # # Calculate elapsed time
        # elapsed_time = time.time() - start_time

        table = fill_table(size, size, N)

        # Print the table to the server's console
        print("Final table state:")
        # for row_ in table:
        #     print(row_)

        # print(f"All threads finished in {elapsed_time:.2f} seconds.")


def fill_table(num_rows, num_cols, num_processes):
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
        process = multiprocessing.Process(target=table_db.fill_table_chunk, args=(start_row, end_row, table_chunk, i + 1))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    elapsed_time = time.time() - start_time
    print(f"Table filled with {num_processes} processes in {elapsed_time:.2f} seconds.")
    return table


def main():
    # Get host and port
    host = input("Host: ")
    port = int(input("Port: "))

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    # Create new thread to wait for connections
    newConnectionsThread = threading.Thread(target=newConnections, args=(sock,))
    newConnectionsThread.start()


if __name__ == "__main__":
    freeze_support()
    # multiprocessing.set_start_method("spawn")

    # t = table_db.TableDB(10, 10)
    # for i in range(3+1):
    #     table_db.fill_table_thread(t, i, 3)
    #
    # for row in t.table:
    #     print(row)

    main()
