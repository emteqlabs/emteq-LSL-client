"""Example program to show how to read a multi-channel time series from LSL."""

import pylsl
from threading import Thread, Lock


class Stream:

    def __init__(self,stream) -> None:
        self.stream = stream
        self.name = stream.name()
        self.source_id = stream.source_id()
        self.lslType = stream.type()
        # self.channels = stream.channels()
        self.inlet = pylsl.StreamInlet(self.stream)
        self.info  = self.inlet.info()

        #collect channels names
        self.channels = []
        ch = self.info.desc().child("channels").child("channel")
        for k in range(self.info.channel_count()):
            chnName = ch.child_value("label")

            backupNameIterator = 1
            while(chnName in self.channels or len(chnName) == 0):
                if(not f"{chnName}{backupNameIterator}" in self.channels):
                    chnName = f"{chnName}{backupNameIterator}"
                else:
                    backupNameIterator+=1

            self.channels.append(chnName)
            ch = ch.next_sibling()


class StreamManager:

    def __init__(self, callback):

        self.dictLock = Lock()

        self.streams = dict()

        self.callback = callback

        self.workerRun = True
        self.workersPool = dict()
        # self.streamWorker = Thread(target=self.__worker)
        # self.streamWorker.start()


    def openStream(self,name,stream):
        with self.dictLock:
            stream__ = Stream(stream)
            if stream__:
                self.streams[name] = stream__

        self.workersPool[f"worker_{name}"] = {"worker" : Thread(target=self.__worker,args=(f"worker_{name}",stream__,)),"run":True}
        self.workersPool[f"worker_{name}"]["worker"].start()
        pass

    def __worker(self,wName,stream__):

        while self.workersPool[wName]["run"]:
            streamData = dict()
                # get a new sample (you can also omit the timestamp part if you're not
                # interested in it)

            sample, timestamp = stream__.inlet.pull_sample()
            metaSample = dict()
            for n,s in enumerate(sample):
                metaSample[stream__.channels[n]] = s

            streamData[stream__.name+stream__.source_id] = (metaSample, timestamp)

            self.callback(streamData)

    def getChannels(self,name):
        if not name in self.streams.keys():
            return []

        return self.streams[name].channels

    def closeStream(self,name):
        with self.dictLock:
            self.streams.pop(name)
        self.workersPool[f"worker_{name}"]["run"] = False

    def close(self):
        self.workerRun = False

    def __del__(self):
        self.workerRun = False


class LSL:

    def __init__(self,callback):
        self.discoveredOutlets = dict()
        self.openStreams       = dict()
        self.streamManager     = StreamManager(callback)
        pass

    def scan(self,onName):
        self.streams = pylsl.resolve_streams()
        for stream in self.streams:
            self.discoveredOutlets[stream.name()+stream.source_id()] = stream
            onName(stream.name(),stream.source_id())

    def open(self,name):
        if name in self.discoveredOutlets.keys():
            stream = self.discoveredOutlets[name]
            self.streamManager.openStream(name,stream)
            return self.streamManager.getChannels(name)
        else:
            return 0

    def close(self,name):
        pass
        self.streamManager.closeStream(name)
        # self.openStreams[name].close()

    def closeAll(self):
        pass
        self.streamManager.close()