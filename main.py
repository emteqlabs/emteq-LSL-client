from PyQt6 import QtWidgets,QtGui # Should work with PyQt5 / PySide2 / PySide6 as well
import pyqtgraph as pg
from lslbackend import LSL
import numpy as np

class App(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        super(App,self).__init__(parent)

        self.bufferIdx = 0
        self.bufferLength = 1000
        self.plotBuffers = [np.zeros((self.bufferLength))]
        self.backend = LSL()

        ## Define a top-level widget to hold everything

        ## Create some widgets to be placed inside
        self.btn = QtWidgets.QPushButton('scan')
        # text = QtWidgets.QLineEdit('enter text')
        self.scannedOutlets   = QtWidgets.QListWidget()
        self.connectedOutlets = QtWidgets.QListWidget()

        self.plot = pg.PlotWidget()
        self.plot2 = pg.PlotWidget()
        self.plot3 = pg.PlotWidget()
        self.plot4 = pg.PlotWidget()
        self.data_line =  self.plot.plot(self.plotBuffers[0])

        self.btn.clicked.connect(self.buttonCallback)

        ## Create a grid layout to manage the widgets size and position
        self.layout = QtWidgets.QGridLayout()
        # w.setLayout(self.layout)

        ## Add widgets to the layout in their proper positions
        self.layout.addWidget(self.btn, 0, 0)  # button goes in upper-left
        self.layout.addWidget(self.scannedOutlets, 2, 0)  # list widget goes in bottom-left
        self.layout.addWidget(self.connectedOutlets, 3, 0)

        self.scroll = QtWidgets.QScrollArea()

        self.layout.addWidget(self.scroll, 0, 1, 4, 1)
        scrollContent = QtWidgets.QWidget(self.scroll)

        scrollLayout = QtWidgets.QVBoxLayout(scrollContent)
        scrollContent.setLayout(scrollLayout)
        ## Display the widget as a new window

        scrollLayout.addWidget(self.plot)
        scrollLayout.addWidget(self.plot2)
        scrollLayout.addWidget(self.plot3)
        scrollLayout.addWidget(self.plot4)# plot goes on right side, spanning 3 rows
        self.scroll.setWidget(scrollContent)

        # central widget
        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.setLayout(self.layout)

        # set central widget
        self.setCentralWidget(self.centralWidget)

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
    app = QtWidgets.QApplication([])
    mainApp = App()
    mainApp.show()
    app.exec()
