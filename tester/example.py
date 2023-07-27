"""Example program to demonstrate how to send a multi-channel time series to
LSL."""
import sys
import getopt

import time
import numpy as np
from random import random as rand

from pylsl import StreamInfo, StreamOutlet, local_clock


def main():
    srate = 100
    name = 'Tester'
    type = 'TestSig'

    n_channels = 5
    srate = 50.0

    info = StreamInfo(name, type, n_channels, srate, 'float32', 'myuid34234')
    chns = info.desc().append_child("channels")
    # for label in ["C3", "C4", "Cz", "FPz", "POz"]:
    #     ch = chns.append_child("channel")
    #     ch.append_child_value("label", label)

    # first create a new stream info (here we set the name to BioSemi,
    # the content-type to EEG, 8 channels, 100 Hz, and float-valued data) The
    # last value would be the serial number of the device or some other more or
    # less locally unique identifier for the stream as far as available (you
    # could also omit it but interrupted connections wouldn't auto-recover)

    # next make an outlet
    outlet = StreamOutlet(info)

    print("now sending data...")
    start_time = local_clock()
    mysample = [0.0]*n_channels
    timestamp = time.time()
    period = 5.0

    while True:

        if(time.time() - timestamp > period):
            timestamp = time.time()

            print(mysample[0] > 1.0)
            if(mysample[0] > 1.0):
                print(f"LOW {n_channels}")
                for n in range(n_channels):
                    mysample[n] = 0.0

            elif(mysample[0] < 1000.0):
                print("HIGH")
                for n in range(n_channels):
                    mysample[n] = np.random.rand()*1000.0

        # print("sending: ", mysample)
        outlet.push_sample(mysample)
        # now send it and wait for a bit before trying again.
        time.sleep(0.02)


if __name__ == '__main__':
    main()