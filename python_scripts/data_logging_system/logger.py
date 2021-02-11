#!/usr/bin/env python3
"""logger class"""

import os
import datetime
import csv


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

    def __init__(self, BASE_DIR):
        """
        initialization
        """
        self.BASE_DIR = BASE_DIR
        self.CSV_HEADER = "TIME,ID,TEMP"

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
        message written to the csv log file, and send msg to
        """
        while self.running:
            if len(self.MSG_CACHE) > 0:
                data_str = self.MSG_CACHE.pop()
                box_id, temperature = self.parse_msg(data_str)
                progress_callback.emit((box_id, temperature))
                self.write_msg(data_str)

        print("LOGGER stopped...")

    def write_msg_cache(self):
        """
        message written to the csv log file
        """
        while self.running:
            if len(self.MSG_CACHE) > 0:
                data_str = self.MSG_CACHE.pop()
                self.write_msg(data_str)

        print("LOGGER stopped...")

    def stop(self):
        self.running = False
