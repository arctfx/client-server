from asyncio import PriorityQueue
import selectors
import threading
import multiprocessing

# manager = multiprocessing.Manager()
# table = manager.list(
#     [manager.list([0] * size) for _ in range(size)])  # Example 5x5 table, shared between processes
# # table = [[0 for _ in range(size)] for _ in range(size)]
# table_lock = threading.Lock()


"""
Because the function is called from a process, it is a good idea to be separated in a different module than main
"""


def fill_table_chunk(start_row, end_row, table_chunk, thread_num):
    for i in range(len(table_chunk)):
        for j in range(len(table_chunk[0])):
            table_chunk[i][j] = thread_num


"""
Deprecated
"""


# Shared table and lock
class TableDB:
    def __init__(self, num_rows, num_cols):
        self.manager = multiprocessing.Manager()
        self.table = self.manager.list([self.manager.list([0] * num_cols) for _ in range(num_rows)])
        self.table_lock = threading.Lock()
        self.num_rows = num_rows
        self.num_cols = num_cols


def fill_table_thread(table, thread_id, num_rows, num_cols, n):
    """Fill rows in the table where row % thread_num == 0 with thread_num."""
    # with table_lock:
    for i in range(0, num_rows//n+1):
        row = i*n+thread_id-1
        #   if row % thread_id == 0:
        for col in range(num_cols):
            if row < num_rows:
                table[row][col] = thread_id
    # conn.sendall(json.dumps({"thread": thread_num, "status": "finished"}).encode())


# table = list()
queue = PriorityQueue()


# 2D table with history
class Table:
    def __init__(self, x=10, y=10):
        self.x = x
        self.y = y
        self.table = []
        self.queue = PriorityQueue()

    def add(self, x, y, what):
        self.table.append(((x, y), what))
        self.queue.put(((x, y), what))

