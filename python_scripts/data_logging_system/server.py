#!/usr/bin/env python3
"""esplserver"""

import time
import socket
import threading
from logger import DataLogger
import time


class ESPLServer:
    def __init__(self, IP_ADDR, PORT, SAVE_DIR):
        """
        IP_ADDR -> IP addr of the server
        PORT -> server port number
        SAVE_DIR -> location to store data
        """
        self.IP_ADDR = IP_ADDR
        self.PORT = PORT
        self.LOGGER = DataLogger(SAVE_DIR)  # initialize the logger

        self.HEADER = 4  # size of the header
        self.FORMAT = "utf-8"

        # set the running flag
        self.running = True

        # initialize the server
        self.server = self.initialize_server()
        self.client_threads = []

    def initialize_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.IP_ADDR, self.PORT))
        return server

    def start_logging_thread(self):
        thread = threading.Thread(target=self.LOGGER.write_msg_cache_to_file)
        thread.start()

    def start_server(self, progress_callback):
        """
        start listening to messages
        """

        # start the server
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.IP_ADDR}: {self.PORT}")
        while self.running:
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}", flush=True)
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            self.client_threads.append(thread)

    def handle_client(self, conn, addr):
        """
        funnction to handle each client connection
        """
        print(f"[NEW CONNECTION] {addr} connected.")
        msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(self.FORMAT)
            print(f"[{addr}] {msg}")
            self.LOGGER.log(msg)

        conn.close()
        print(f"[{addr}] Connection Closed")

    def stop(self):
        """
        stops the server, logging threads
        """
        # close all the client threads
        for thread in self.client_threads:
            thread.join()

        # get out of the while loop
        # create a fake connection, to get out of the while loop
        self.running = False
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.IP_ADDR, self.PORT))
        self.server.close()
        self.LOGGER.stop()
        print("SERVER stopped...")
        time.sleep(0.1)  # give the threads some time to close
