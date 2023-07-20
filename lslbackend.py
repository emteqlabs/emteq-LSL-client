"""Example program to show how to read a multi-channel time series from LSL."""

import pylsl
from threading import Thread


class Stream:

    def __init__(self,stream) -> None:
        self.stream = stream
        self.name = stream.name()
        self.source_id = stream.source_id()
        self.lslType = stream.type()
        self.inlet = pylsl.StreamInlet(self.stream)

class StreamManager:

    def __init__(self, callback):

        self.streams = dict()

        self.callback = callback

        self.workerRun = True
        self.streamWorker = Thread(target=self.__worker)
        self.streamWorker.start()

        print("started thread")

    def openStream(self,name,stream):
        self.streams[name] = Stream(stream)
        pass

    def __worker(self):

        while self.workerRun:
            if self.streams:
                streamData = dict()
                for stream in self.streams.values():
                    # get a new sample (you can also omit the timestamp part if you're not
                    # interested in it)
                    sample, timestamp = stream.inlet.pull_sample()
                    streamData[self.stream.name()+self.stream.source_id()] = (sample, timestamp)

                self.callback(streamData)

    def close(self):
        self.workerRun = False

    def __del__(self):
        self.workerRun = False


class LSL:

    def __init__(self):
        self.discoveredOutlets = dict()
        self.openStreams       = dict()
        self.streamManager     = StreamManager()
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
            print(dir(stream))

            print("adding stream to open streams")
            self.openStreams[name] = Stream(stream,callback)
            return stream.channel_count()
        else:
            print(f"stream not found")
            return 0
        pass

    def close(self,name):
        self.openStreams[name].close()