"""Example program to show how to read a multi-channel time series from LSL."""

import pylsl
from threading import Thread

class Stream():

    def __init__(self, name, source_id, lslType, callback):
        self.name = name
        self.source_id = source_id
        self.lslType = lslType
        self.callback = callback

        self.streams = resolve_stream(lslType, name)
        # create a new inlet to read from the stream

        self.inlet = pylsl.StreamInlet(streams[0])

        self.streamWorker = Thread(target=self.__worker)
        self.streamWorker.start()


    def __worker(self):

        while True:
            # get a new sample (you can also omit the timestamp part if you're not
            # interested in it)
            sample, timestamp = self.inlet.pull_sample()

            self.callback(sample, timestamp)

class LSL:

    def __init__(self):
        self.discoveredOutlets = dict()
        self.openStreams       = dict()
        pass

    def scan(self,onName):
        self.streams = pylsl.resolve_streams()
        for stream in self.streams:
            print(dir(stream),stream.name(),stream.hostname(),stream.session_id(),stream.source_id())
            self.discoveredOutlets[stream.name()+stream.source_id()] = stream
            onName(stream.name(),stream.source_id())

    def open(self,name,source_id,callback):
        stream = self.discoveredOutlets[name+source_id]
        self.openStreams[name+source_id] = Stream(stream.name(),stream.source_id(),stream.type(),callback)
        pass
