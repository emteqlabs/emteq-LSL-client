from PyQt6 import QtWidgets  # Should work with PyQt5 / PySide2 / PySide6 as well
import pyqtgraph as pg
from lslbackend import LSL
import numpy as np

class App:

    def __init__(self):

        self.bufferIdx = 0
        self.bufferLength = 1000
        self.plotBuffer = np.zeros((self.bufferLength))
        self.backend = LSL()

        self.app = QtWidgets.QApplication([])
        ## Define a top-level widget to hold everything
        w = QtWidgets.QWidget()
        w.setWindowTitle('PyQtGraph example')

        ## Create some widgets to be placed inside
        self.btn = QtWidgets.QPushButton('scan')
        # text = QtWidgets.QLineEdit('enter text')
        self.scannedOutlets   = QtWidgets.QListWidget()
        self.connectedOutlets = QtWidgets.QListWidget()

        self.plot = pg.PlotWidget()
        self.data_line =  self.plot.plot(self.plotBuffer)

        self.btn.clicked.connect(self.buttonCallback)

        ## Create a grid layout to manage the widgets size and position
        layout = QtWidgets.QGridLayout()
        w.setLayout(layout)

        ## Add widgets to the layout in their proper positions
        layout.addWidget(self.btn, 0, 0)  # button goes in upper-left
        layout.addWidget(self.scannedOutlets, 2, 0)  # list widget goes in bottom-left
        layout.addWidget(self.connectedOutlets, 3, 0)
        layout.addWidget(self.plot, 0, 1, 3, 1)  # plot goes on right side, spanning 3 rows
        ## Display the widget as a new window
        w.show()

        # ## Start the Qt event loop
        self.app.exec()  # or app.exec_() for PyQt5 / PySide2

    def onName(self,name,source_id):
        self.scannedOutlets.addItem(name+source_id)
        self.scannedOutlets.itemClicked.connect(self.itemCallback)

    def buttonCallback(self):
        self.backend.scan(onName=self.onName)

        print("clicked")

    def itemCallback(self,item):
        print(f"itemCallback {item.text()}")

        self.scannedOutlets.takeItem(self.scannedOutlets.row(item))
        self.scannedOutlets.itemClicked.disconnect()

        self.connectedOutlets.addItem(item.text())
        self.connectedOutlets.itemClicked.connect(self.connectedItemCallback)

        self.backend.open(item.text(),self.signalCallback)

    def connectedItemCallback(self,item):
        print(f"connectedItemCallback {item.text()}")
        self.connectedOutlets.takeItem(self.connectedOutlets.row(item))
        self.connectedOutlets.itemClicked.disconnect()

        self.backend.close(item.text())

        self.scannedOutlets.addItem(item.text())
        self.scannedOutlets.itemClicked.connect(self.itemCallback)

    def signalCallback(self,sample, timestamp):
        # print(f"sample: {sample}, timestamp: {timestamp}")
        self.plotBuffer[self.bufferIdx] = sample[0]
        self.bufferIdx += 1
        if self.bufferIdx >= self.bufferLength:
            self.bufferIdx = 0

        self.data_line.setData(self.plotBuffer)
        pass

if __name__ == "__main__":
    ## Always start by initializing Qt (only once per application)
    app = App()
