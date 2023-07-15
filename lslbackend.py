"""Example program to show how to read a multi-channel time series from LSL."""

import pylsl
from threading import Thread

class Stream():

    def __init__(self, stream, callback):
        print("opening streams")
        self.stream = stream
        self.name = stream.name()
        self.source_id = stream.source_id()
        self.lslType = stream.type()
        self.callback = callback
        print(f"params set name: {self.name} type: {self.lslType}")

        # create a new inlet to read from the stream
        print(f"stream resolved {self.stream}")

        self.inlet = pylsl.StreamInlet(self.stream)

        print("starting thread")

        self.workerRun = True
        self.streamWorker = Thread(target=self.__worker)
        self.streamWorker.start()

        print("started thread")


    def __worker(self):

        while self.workerRun:
            # get a new sample (you can also omit the timestamp part if you're not
            # interested in it)
            sample, timestamp = self.inlet.pull_sample()

            self.callback(sample, timestamp)

    def close(self):
        self.workerRun = False

    def __del__(self):
        self.workerRun = False


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

    def open(self,name,callback):
        print(f"opening stream {name}")
        if name in self.discoveredOutlets.keys():
            print("stream found")
            stream = self.discoveredOutlets[name]
            
            print("adding stream to open streams")
            self.openStreams[name] = Stream(stream,callback)
        else:
            print(f"stream not found")
        pass

    def close(self,name):
        self.openStreams[name].close()