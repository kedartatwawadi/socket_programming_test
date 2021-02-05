import socket
import threading
import os
import datetime
import csv


def str_format(num):
    """
    correctly formats the data to be at least length 2
    """
    return '{:02}'.format(num)

def get_current_time_str():
    dt = datetime.datetime.now()
    HH = str_format(dt.hour)
    MM = str_format(dt.minute)
    SS = str_format(dt.second)
    current_time = f"{HH}:{MM}:{SS}"
    return current_time

def get_DD_filepath(base_dir, ext=".csv"):
    """
    returns file path corresponding to the date
    """
    # get 
    dir_path = get_MMYY_directory_path(base_dir)

    # get the file_name
    dt = datetime.datetime.today()
    day = str_format(dt.day) + ext
    path = os.path.join(dir_path, day)

    return path

def get_MMYY_directory_path(base_dir):
    """
    returns the current Month, year directory
    """
    dt = datetime.datetime.today()
    year = str_format(dt.year)
    month= str_format(dt.month)
    path = os.path.join(base_dir, year)
    path = os.path.join(path, month)
    return path

class DataLogger:
    """
    class which handles the logging to the csv file
    """
    def __init__(self, BASE_DIR, CSV_HEADER):
        """
        initialization
        """
        self.BASE_DIR = BASE_DIR
        self.CSV_HEADER = CSV_HEADER

        # cache where threads write their messages
        self.MSG_CACHE = []

    def initialize_DDMMYY_logfile(self):
        """
        creates the log dir and initializes the logfile
        """
        
        # create MMYY directory if needed
        dir_path = get_MMYY_directory_path(self.BASE_DIR)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=False)
        
        # initialize the CSV file if needed
        file_path = get_DD_filepath(self.BASE_DIR)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(self.CSV_HEADER+"\n")
        return file_path

    def log(self, msg):
        """
        add message to the msg cache
        """
        current_time = get_current_time_str()
        msg = f"{current_time},{msg}"

        self.MSG_CACHE.append(msg)

    def write_msg(self, msg):
        """
        write data to log file
        """

        # initialize file path if needed
        file_path = self.initialize_DDMMYY_logfile()
        with open(file_path, "a") as f:
            f.write(msg+"\n")
        print(f"logged msg:: {msg} to file {file_path}")


    def write_msg_cache_to_file(self):
        """
        message written to the csv log file
        """
        while True:
            if len(self.MSG_CACHE) > 0:
                data_str = self.MSG_CACHE.pop()
                self.write_msg(data_str)


class ESPLServer:
    def __init__(self, IP_ADDR, PORT, HEADER, logger):
        self.IP_ADDR = IP_ADDR
        self.PORT = PORT
        self.HEADER = HEADER
        self.LOGGER = logger
        self.FORMAT = "utf-8"

    def initialize_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.IP_ADDR, self.PORT))
        return server

    def start_logging_thread(self):
        thread = threading.Thread(target=self.LOGGER.write_msg_cache_to_file)
        thread.start()

    def start_server(self):
        # initialize the server
        self.server = self.initialize_server()

        # initialize the logging thread
        self.start_logging_thread()

        # start the server
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.IP_ADDR}: {self.PORT}")
        while True:
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}", flush=True)
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(self.FORMAT)
            print(f"[{addr}] {msg}")
            self.LOGGER.log(msg)

        conn.close()
        print(f"[{addr}] Connection Closed")


# Server settings 
HEADER = 4 
PORT = 5050
IP_ADDR = socket.gethostbyname(socket.gethostname())

# logging settings
BASE_DIR = "/Users/kedar/code/data/"
CSV_HEADER = "TIME,ID,TEMP"

# define logger, server
logger = DataLogger(BASE_DIR, CSV_HEADER)
server = ESPLServer(IP_ADDR, PORT, HEADER, logger)

# start server
print("[STARTING] server is starting...")
server.start_server()




