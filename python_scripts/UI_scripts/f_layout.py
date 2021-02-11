# Filename: f_layout.py

"""Form layout example."""

import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit, QPushButton
from PyQt5.QtWidgets import QWidget

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("QFormLayout")
layout = QFormLayout()
layout.addRow("Name:", QLineEdit())
layout.addRow("Age:", QLineEdit())
layout.addRow("Job:", QPushButton("Employed"))
layout.addRow("Hobbies:", QLineEdit())
window.setLayout(layout)
window.show()
sys.exit(app.exec_())
