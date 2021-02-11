#!/usr/bin/env python3

# Filename: pycalc.py

"""PyCalc is a simple calculator built using Python and PyQt5."""

import sys
import threading

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtWidgets import QApplication, QToolBar, QAction
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from functools import partial

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import traceback, sys
import socket
import threading
import os
import datetime
import csv

# Server settings
HEADER = 4
PORT = 5050
IP_ADDR = socket.gethostbyname(socket.gethostname())

# logging settings
BASE_DIR = "/Users/kedar/code/data/"
CSV_HEADER = "TIME,ID,TEMP"


def str_format(num):
    """
    correctly formats the data to be at least length 2
    """
    return "{:02}".format(num)


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
    month = str_format(dt.month)
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

        self.running = True

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
                f.write(self.CSV_HEADER + "\n")
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
            f.write(msg + "\n")
        print(f"logged msg:: {msg} to file {file_path}")

    @staticmethod
    def parse_msg(data_str):
        """
        parses the msg from client and returns the id, temp
        # format: TIME,ID,MSG
        """
        _id = data_str.split(",")[1]
        _temperature = data_str.split(",")[2]
        return _id, _temperature

    def write_msg_cache_to_file(self, progress_callback):
        """
        message written to the csv log file
        """
        while self.running:
            if len(self.MSG_CACHE) > 0:
                data_str = self.MSG_CACHE.pop()
                box_id, temperature = self.parse_msg(data_str)
                progress_callback.emit((box_id, temperature))
                self.write_msg(data_str)

        print("LOGGER stopped...")

    def stop(self):
        self.running = False


class ESPLServer:
    def __init__(self, IP_ADDR, PORT, HEADER, logger):
        self.IP_ADDR = IP_ADDR
        self.PORT = PORT
        self.HEADER = HEADER
        self.LOGGER = logger
        self.FORMAT = "utf-8"

        self.running = True

    def initialize_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.IP_ADDR, self.PORT))
        return server

    def start_logging_thread(self):
        thread = threading.Thread(target=self.LOGGER.write_msg_cache_to_file)
        thread.start()

    def start_server(self, progress_callback):
        # initialize the server
        self.server = self.initialize_server()

        # start the server

        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.IP_ADDR}: {self.PORT}")
        while self.running:
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

    def stop(self):
        self.running = False
        # create a fake connection, to get out of the while loop
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.IP_ADDR, self.PORT))
        self.server.close()
        self.LOGGER.close()
        print("SERVER stopped...")


class WorkerSignals(QObject):
    progress = pyqtSignal(tuple)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        result = self.fn(*self.args, **self.kwargs)


class BoxWidget:
    def __init__(self, id_text, width=90, height=70):
        self.widget = QWidget()
        self.layout = QVBoxLayout()

        # Set some display's properties
        self.display = QLineEdit()
        self.display.setFixedHeight(height)

        self.display.setAlignment(Qt.AlignCenter)
        self.display.setReadOnly(True)

        # create label
        self.label = QLabel(f"ID: {id_text}")
        self.label.setAlignment(Qt.AlignCenter)

        # add label and display
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.label)

        self.widget.setLayout(self.layout)
        self.widget.setFixedHeight(150)

    def setDisplayText(self, text):
        """Set display's text."""
        self.display.setText(text)
        self.display.setFocus()  # ?

    def displayText(self):
        """Get display's text."""
        return self.display.text()

    def clearDisplay(self):
        """Clear the display."""
        self.setDisplayText("")


# Create a subclass of QMainWindow to setup the calculator's GUI
class TemperatureUI(QMainWindow):
    """PyCalc's View (GUI)."""

    def __init__(self):
        """View initializer."""
        super().__init__()
        # Set some main window's properties
        self.setWindowTitle("DataLogger")
        self.setFixedSize(800, 400)
        # Set the central widget and the general layout
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        # Create the display and the buttons
        boxes_layout = self._createBoxes()

        self._createActions()
        self._createToolBars()

        self.threadpool = QThreadPool()

        # define logger, server
        logger = DataLogger(BASE_DIR, CSV_HEADER)
        self.server = ESPLServer(IP_ADDR, PORT, HEADER, logger)

        # Pass the function to execute
        self.server_thread = Worker(self.server.start_server)
        self.threadpool.start(self.server_thread)

        # logger
        self.logger_thread = Worker(self.server.LOGGER.write_msg_cache_to_file)
        self.logger_thread.signals.progress.connect(self.setBoxText)
        self.threadpool.start(self.logger_thread)

        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def _createBoxes(self):
        """Create the buttons."""
        self.boxes = {}
        boxesLayout = QGridLayout()
        # Button text | position on the QGridLayout
        _boxes = {
            "001": (0, 0),
            "002": (0, 1),
            "003": (0, 2),
            "004": (0, 3),
            "005": (1, 0),
            "006": (1, 1),
            "007": (1, 2),
            "008": (1, 3),
        }
        # Create the buttons and add them to the grid layout
        for _id, pos in _boxes.items():
            self.boxes[_id] = BoxWidget(_id)
            boxesLayout.addWidget(self.boxes[_id].widget, pos[0], pos[1])

        # Add buttonsLayout to the general layout
        self.generalLayout.addLayout(boxesLayout)

    def setBoxText(self, msg):
        """Set display's text."""
        box_id, text = msg
        self.boxes[box_id].display.setText(text)
        # self.display.setFocus()  # ?

    def clearBoxText(self):
        """Clear the display."""
        self.setBoxText(box_id, "")

    def _createActions(self):
        # File actions
        self.settingsAction = QAction("Settings", self)
        self.exitAction = QAction("Exit", self)

    def _createToolBars(self):
        # File toolbar
        fileToolBar = self.addToolBar("File")
        fileToolBar.addAction(self.settingsAction)
        fileToolBar.addAction(self.exitAction)
        fileToolBar.setMovable(False)

    def shutdown(self):
        self.server.stop()
        time.sleep(0.1)


# # Client code
def main():
    """Main function."""

    # Create an instance of QApplication
    app = QApplication(sys.argv)
    # Show the calculator's GUI
    view = TemperatureUI()
    view.show()

    app.aboutToQuit.connect(view.shutdown)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
