#!/usr/bin/env python3
"""UI components"""

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QToolBar,
    QAction,
    QMainWindow,
    QWidget,
    QLabel,
    QGridLayout,
    QLineEdit,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QRunnable, pyqtSlot, QThreadPool
import sys
from server import ESPLServer
import socket


class WorkerSignals(QObject):
    """
    signal to notify the progress of a thread
    """

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


class DisplayGrid:
    def __init__(self):
        self.widget = QWidget()

        """Create the boxes"""
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

        # Add boxesLayout to the the widget
        self.widget.setLayout(boxesLayout)

    def setBoxText(self, msg):
        """Set display's text."""
        box_id, text = msg
        self.boxes[box_id].display.setText(text)
        # self.display.setFocus()  # ?

    def clearBoxText(self):
        """Clear the display."""
        self.setBoxText(box_id, "")


# Create a subclass of QMainWindow to setup the calculator's GUI
class TemperatureUI(QMainWindow):
    """PyCalc's View (GUI)."""

    def __init__(self, IP_ADDR, PORT, BASE_DIR):
        """View initializer."""
        super().__init__()
        # Set some main window's properties
        self.setWindowTitle("DataLogger")
        self.setFixedSize(800, 400)

        # Set the central widget and the general layout
        main_layout = QVBoxLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # add the display widget
        self.display_grid = DisplayGrid()
        main_layout.addWidget(self.display_grid.widget)
        self._createToolBars()

        # define logger, server
        self.server = ESPLServer(IP_ADDR, PORT, BASE_DIR)
        self.startServerThread()

    def startServerThread(self):
        self.threadpool = QThreadPool()
        # Pass the function to execute
        server_thread = Worker(self.server.start_server)
        self.threadpool.start(server_thread)

        # logger
        logger_thread = Worker(self.server.LOGGER.write_msg_cache_to_file)
        logger_thread.signals.progress.connect(self.display_grid.setBoxText)
        self.threadpool.start(logger_thread)

    def _createToolBars(self):
        # create actions
        self.settingsAction = QAction("Settings", self)
        self.exitAction = QAction("Exit", self)

        # File toolbar
        fileToolBar = self.addToolBar("File")
        fileToolBar.addAction(self.settingsAction)
        fileToolBar.addAction(self.exitAction)
        fileToolBar.setMovable(False)

    def shutdown(self):
        self.server.stop()


def main():
    """Main function."""

    # Server settings
    PORT = 5050
    IP_ADDR = socket.gethostbyname(socket.gethostname())
    BASE_DIR = "/Users/kedar/code/data/"

    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Show the calculator's GUI
    view = TemperatureUI(IP_ADDR, PORT, BASE_DIR)
    view.show()
    app.aboutToQuit.connect(view.shutdown)

    # execute the app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
