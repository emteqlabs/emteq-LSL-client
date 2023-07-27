from PyQt6 import QtCore,QtWidgets,QtGui # Should work with PyQt5 / PySide2 / PySide6 as well
import pyqtgraph as pg
from lslbackend import LSL
import numpy as np
import csvSaver as csv

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

        # set the title
        self.setWindowTitle("Emteq LSL Client")

        self.recording = False

        self.bufferLength = 100
        self.streamIsSet = dict()
        self.plotsStream = dict()
        self.plotBuffers = dict()
        self.dataLines   = dict()
        self.buffersIdx = dict()
        self.plotList = []
        self.backend = LSL(self.signalCallback)

        ## Define a top-level widget to hold everything

        ## Create some widgets to be placed inside
        self.btnScan = QtWidgets.QPushButton('scan')
        self.btnRecord = QtWidgets.QPushButton('record')
        # text = QtWidgets.QLineEdit('enter text')
        self.scannedOutlets   = QtWidgets.QListWidget()
        self.connectedOutlets = QtWidgets.QListWidget()

        self.btnScan.clicked.connect(self.buttonScan)
        self.btnRecord.clicked.connect(self.buttonRecord)
        self.btnRecord.setStyleSheet("color : green")

        ## Create a grid layout to manage the widgets size and position
        self.layout = QtWidgets.QGridLayout()
        self.menuLayout = QtWidgets.QVBoxLayout()
        self.v_widget = QtWidgets.QWidget()
        self.v_widget.setLayout(self.menuLayout)
        # w.setLayout(self.layout)

        ## Add widgets to the layout in their proper positions
        self.menuLayout.addWidget(self.btnScan)  # button goes in upper-left
        self.menuLayout.addWidget(self.btnRecord)  # button goes in upper-left
        self.menuLayout.addWidget(self.scannedOutlets)  # list widget goes in bottom-left
        self.menuLayout.addWidget(self.connectedOutlets)
        self.v_widget.setFixedWidth(200)

        self.connectedOutlets.itemClicked.connect(self.connectedItemCallback)
        self.scannedOutlets.itemClicked.connect(self.itemCallback)

        self.layout.addWidget(self.v_widget)
        # self.layout.addLayout(self.menuLayout, 0, 0)

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
 
        self.newDataSignal.connect(self.someSlot)

    def addStreamPlots(self,streamName,channels):
        self.plotBuffers[streamName] = []
        self.buffersIdx[streamName] = [0]*len(channels)

        self.plotsStream[streamName] = []
        self.dataLines[streamName] = []
        for n in range(len(channels)):
            self.plotsStream[streamName].append(pg.PlotWidget())
            self.plotsStream[streamName][n].setTitle(f'{channels[n]}')
            self.plotBuffers[streamName].append(np.zeros(self.bufferLength))
            self.scrollLayout.addRow(self.plotsStream[streamName][n])# plot goes on right side, spanning 3 rows
            self.dataLines[streamName].append(self.plotsStream[streamName][n].plot(self.plotBuffers[streamName][n]))

        self.streamIsSet[streamName] = True
        pass

    def removeStreamPlots(self,streamName):
        self.streamIsSet[streamName] = False
        for n in range(len(self.plotsStream[streamName])):
            self.scrollLayout.removeRow(self.plotsStream[streamName][n])
            csv.close(streamName)

    def onName(self,name,source_id):
        if not self.scannedOutlets.findItems(f"{name+source_id}",QtCore.Qt.MatchFlag.MatchExactly) and not self.connectedOutlets.findItems(f"{name+source_id}",QtCore.Qt.MatchFlag.MatchExactly):
            self.scannedOutlets.addItem(name+source_id)

    def buttonScan(self):
        self.backend.scan(onName=self.onName)

    def buttonRecord(self):
        if self.recording:
            self.recording = False
            self.btnRecord.setText("record")
            self.btnRecord.setStyleSheet("color : green")
        else:
            self.recording = True
            self.btnRecord.setText("stop recording")
            self.btnRecord.setStyleSheet("color : red")

    def itemCallback(self,item):

        self.scannedOutlets.takeItem(self.scannedOutlets.row(item))

        if not self.connectedOutlets.findItems(item.text(),QtCore.Qt.MatchFlag.MatchExactly):
            self.connectedOutlets.addItem(item.text())

        nChannelsToAdd = self.backend.open(item.text())
        self.addStreamPlots(item.text(),nChannelsToAdd)

    def connectedItemCallback(self,item):
        self.connectedOutlets.takeItem(self.connectedOutlets.row(item))

        self.backend.close(item.text())
        self.removeStreamPlots(item.text())

        if not self.scannedOutlets.findItems(item.text(),QtCore.Qt.MatchFlag.MatchExactly):
            self.scannedOutlets.addItem(item.text())

    def signalCallback(self,streamsData):
        # print(f"sample: {sample}, timestamp: {timestamp}")
        for streamName in streamsData.keys():
            if not (streamName in self.streamIsSet.keys()):
                return

            if not self.streamIsSet[streamName]:
                return

            samples   = streamsData[streamName][0]
            timestamp = streamsData[streamName][1]
            nChannels = samples.keys()
            for n,channel in enumerate(nChannels):
                self.plotBuffers[streamName][n][self.buffersIdx[streamName]] = samples[channel]

                self.buffersIdx[streamName][n] += 1
                if self.buffersIdx[streamName][n] >= self.bufferLength:
                    self.buffersIdx[streamName][n] = 0

            self.newDataSignal.emit(streamName,len(nChannels))

            if self.recording:
                csv.save(streamName,np.array(list(samples.values())),timestamp,list(nChannels))

    def closeEvent(self, event):
        self.backend.closeAll()


if __name__ == "__main__":
    ## Always start by initializing Qt (only once per application)
    app = QtWidgets.QApplication([])
    mainApp = App()
    mainApp.show()
    app.exec()
