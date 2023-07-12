from PyQt6 import QtWidgets  # Should work with PyQt5 / PySide2 / PySide6 as well
import pyqtgraph as pg
from lslbackend import LSL

class App:

    def __init__(self):

        self.backend = LSL()

        self.app = QtWidgets.QApplication([])
        ## Define a top-level widget to hold everything
        w = QtWidgets.QWidget()
        w.setWindowTitle('PyQtGraph example')

        ## Create some widgets to be placed inside
        self.btn = QtWidgets.QPushButton('scan')
        # text = QtWidgets.QLineEdit('enter text')
        self.listw = QtWidgets.QListWidget()
        plot = pg.PlotWidget()

        self.btn.clicked.connect(self.buttonCallback)

        ## Create a grid layout to manage the widgets size and position
        layout = QtWidgets.QGridLayout()
        w.setLayout(layout)

        ## Add widgets to the layout in their proper positions
        layout.addWidget(self.btn, 0, 0)  # button goes in upper-left
        layout.addWidget(self.listw, 2, 0)  # list widget goes in bottom-left
        layout.addWidget(plot, 0, 1, 3, 1)  # plot goes on right side, spanning 3 rows
        ## Display the widget as a new window
        w.show()

        # ## Start the Qt event loop
        self.app.exec()  # or app.exec_() for PyQt5 / PySide2

    def onName(self,name,source_id):
        self.listw.addItem(name+source_id)

    def buttonCallback(self):
        self.backend.scan(onName=self.onName)

        print("clicked")


if __name__ == "__main__":
    ## Always start by initializing Qt (only once per application)
    app = App()
