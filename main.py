from PyQt6 import QtCore,QtWidgets,QtGui # Should work with PyQt5 / PySide2 / PySide6 as well
import pyqtgraph as pg
from lslbackend import LSL
import numpy as np

class App(QtWidgets.QMainWindow):


    # create a signal equivalent to "void someSignal(int, QWidget)"
    newDataSignal = QtCore.pyqtSignal(str,int)

    # define a slot with the same signature
    @QtCore.pyqtSlot(str,int)
    def someSlot(self,streamName,nChannels):
        for n in range(nChannels):
            self.dataLines[streamName][n].setData(self.plotBuffers[streamName][n])

    def __init__(self, parent = None):
        super(App,self).__init__(parent)

        self.bufferLength = 1000
        self.streamIsSet = dict()
        self.plotsStream = dict()
        self.plotBuffers = dict()
        self.dataLines   = dict()
        self.buffersIdx = dict()
        self.plotList = []
        self.backend = LSL()

        ## Define a top-level widget to hold everything

        ## Create some widgets to be placed inside
        self.btn = QtWidgets.QPushButton('scan')
        # text = QtWidgets.QLineEdit('enter text')
        self.scannedOutlets   = QtWidgets.QListWidget()
        self.connectedOutlets = QtWidgets.QListWidget()

        self.btn.clicked.connect(self.buttonCallback)

        ## Create a grid layout to manage the widgets size and position
        self.layout = QtWidgets.QGridLayout()
        # w.setLayout(self.layout)

        ## Add widgets to the layout in their proper positions
        self.layout.addWidget(self.btn, 0, 0)  # button goes in upper-left
        self.layout.addWidget(self.scannedOutlets, 2, 0)  # list widget goes in bottom-left
        self.layout.addWidget(self.connectedOutlets, 3, 0)

        # scroll area widget contents - layout
        self.scrollLayout = QtWidgets.QFormLayout()

        # scroll area widget contents
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        # scroll area
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.layout.addWidget(self.scrollArea, 0, 1, 4, 1)

        # central widget
        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.setLayout(self.layout)

        # set central widget
        self.setCentralWidget(self.centralWidget)

        # connect the signal to the slot
        print(dir(self.newDataSignal))
        self.newDataSignal.connect(self.someSlot)

    def addStreamPlots(self,streamName,numberOfPlots):
        self.plotBuffers[streamName] = [np.zeros(self.bufferLength)]*numberOfPlots
        self.buffersIdx[streamName] = 0

        self.plotsStream[streamName] = []
        self.dataLines[streamName] = []
        for n in range(numberOfPlots):
            self.plotsStream[streamName].append(pg.PlotWidget())
            self.scrollLayout.addRow(self.plotsStream[streamName][n])# plot goes on right side, spanning 3 rows
            self.dataLines[streamName].append(self.plotsStream[streamName][n].plot(self.plotBuffers[streamName][n]))

        self.streamIsSet[streamName] = True
        pass

    def removeStreamPlots(self,streamName):
        self.streamIsSet[streamName] = False
        for n in range(len(self.plotsStream[streamName])):
            self.scrollLayout.removeRow(self.plotsStream[streamName][n])

    def onName(self,name,source_id):
        self.scannedOutlets.addItem(name+source_id)
        self.scannedOutlets.itemClicked.connect(self.itemCallback)

    def buttonCallback(self):
        self.backend.scan(onName=self.onName)

    def itemCallback(self,item):

        self.scannedOutlets.takeItem(self.scannedOutlets.row(item))
        self.scannedOutlets.itemClicked.disconnect()

        self.connectedOutlets.addItem(item.text())
        self.connectedOutlets.itemClicked.connect(self.connectedItemCallback)

        nChannelsToAdd = self.backend.open(item.text(),self.signalCallback)
        self.addStreamPlots(item.text(),nChannelsToAdd)

    def connectedItemCallback(self,item):
        print(f"connectedItemCallback {item.text()}")
        self.connectedOutlets.takeItem(self.connectedOutlets.row(item))
        self.connectedOutlets.itemClicked.disconnect()

        self.backend.close(item.text())
        self.removeStreamPlots(item.text())

        self.scannedOutlets.addItem(item.text())
        self.scannedOutlets.itemClicked.connect(self.itemCallback)

    def signalCallback(self,streamName, samples, timestamp):
        # print(f"sample: {sample}, timestamp: {timestamp}")
        if not (streamName in self.streamIsSet.keys()):
            return

        if not self.streamIsSet[streamName]:
            return

        nChannels = len(samples)
        for n in range(nChannels):
            self.plotBuffers[streamName][n][self.buffersIdx[streamName]] = samples[n]

            self.buffersIdx[streamName] += 1
            if self.buffersIdx[streamName] >= self.bufferLength:
                self.buffersIdx[streamName] = 0

        self.newDataSignal.emit(streamName,nChannels)


if __name__ == "__main__":
    ## Always start by initializing Qt (only once per application)
    app = QtWidgets.QApplication([])
    mainApp = App()
    mainApp.show()
    app.exec()
