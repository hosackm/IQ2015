import sys
import zmq
import pyaudio
import json
import numpy as np
from math import ceil, log

CHUNK = 1024
PORT = 7777
CHANNELS = 1
RATE = 48000
FORMAT = pyaudio.paFloat32


class AudioBuffer(object):
    """Class for buffering port audio samples and
    performing Loudness and FFT measurements"""
    def __init__(self, zmqSocket, loudDelay=1024, fftlength=5):
        self.lqueue = ""
        self.fqueue = ""
        self.fcount = 0
        self.lcount = 0
        self.sock = zmqSocket
        self._loudDelay = loudDelay
        next = lambda x: int(pow(2, ceil(log(x)/log(2))))
        self._fftlength = next(fftlength * RATE)  # seconds

    def addSamples(self, samples):
        # maybe add samples recursively to the loudness buf
        self.lqueue = ''.join([self.lqueue, samples])
        self.fqueue = ''.join([self.fqueue, samples])
        self.lcount += CHUNK
        self.fcount += CHUNK
        if self.lcount >= self.loudDelay:
            self.calcLoudness()
        if self.fcount >= self._fftlength:
            self.calcFFT()

    def calcLoudness(self):
        """Convert to numpy array.
        Calculate the loudness on the samples in the loudness queue.
        Send ZMQ message.
        Clear fqueue."""
        print "fire loudness!"

        # calc loudness
        arr = np.fromstring(self.lqueue, dtype=np.float32)

        # send ZMQ message

        self.lqueue = ""

    def calcFFT(self):
        """Convert to numpy array.
        Calculate the fft on the samples in the fft queue.
        Send ZMQ message.
        Clear fqueue."""
        arr = np.fromstring(self.fqueue, dtype=np.float32)
        fft = np.fft.fft(arr)[:len(arr)/2:10]
        mag = map(abs, fft)
        # don't send all values we don't need that pinpoint accuracy
        # maybe every 10 values
        print "fire fft"

        self.sock.send('f' + json.dumps({
            'nsamp': len(mag),
            'samples': mag}))
        self.fqueue = ""
        self.fcount = 0

    @property
    def loudDelay(self):
        return self._loudDelay

    @loudDelay.setter
    def loudDelay(self, val):
        self._loudDelay = val

    @property
    def fftlength(self):
        return self._fftlength

    @fftlength.setter
    def fftlength(self, val):
        self._fftlength = val


def main(ip="127.0.0.1"):
    ctx = zmq.Context()
    s = ctx.socket(zmq.PUSH)
    s.connect('tcp://127.0.0.1:7777')
    buffer = AudioBuffer(s)

    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK)

    while True:
        buffer.addSamples(stream.read(CHUNK))

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
