#!/usr/bin/env python3

# Filename: pycalc.py

"""PyCalc is a simple calculator built using Python and PyQt5."""

import sys

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtWidgets import QApplication, QToolBar, QAction
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from functools import partial


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

        self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.p.start("python3", ["../server_excel.py"])
        self.p.readyReadStandardOutput.connect(self.handle_server_logs)

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

    def setBoxText(self, box_id, text):
        """Set display's text."""
        self.boxes[box_id].display.setText(text)

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

    def handle_server_logs(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf-8")
        print(stdout)

        for line in stdout.splitlines():
            if line.startswith("LOGGER::"):
                msgs = line.split(",")
                box_id = msgs[1]
                text = msgs[2]
                self.setBoxText(box_id, text)

    def closeEvent(self, event):
        self.p.terminate()


# Client code
def main():
    """Main function."""
    # Create an instance of QApplication
    pycalc = QApplication(sys.argv)
    # Show the calculator's GUI
    view = TemperatureUI()
    view.show()

    # Create instances of the model and the controller
    # model = evaluateExpression
    # PyCalcCtrl(model=model, view=view)
    # Execute the calculator's main loop
    sys.exit(pycalc.exec())


if __name__ == "__main__":
    main()
