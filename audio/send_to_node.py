import sys
import zmq
import pyaudio
import json
import numpy as np
<<<<<<< HEAD
from math import ceil, log
=======
>>>>>>> 8ac4b79855fcc50934a343e6c42bd7928a5c2afa

CHUNK = 1024
PORT = 7777
CHANNELS = 1
RATE = 48000
FORMAT = pyaudio.paFloat32


class AudioBuffer(object):
    """Class for buffering port audio samples and
    performing Loudness and FFT measurements"""
<<<<<<< HEAD
    def __init__(self, zmqSocket, loudDelay=1024, fftlength=5):
        self.lqueue = ""
        self.fqueue = ""
        self.fcount = 0
        self.lcount = 0
        self.sock = zmqSocket
        self._loudDelay = loudDelay
        next = lambda x: int(pow(2, ceil(log(x)/log(2))))
        self._fftlength = next(fftlength * RATE)  # seconds
=======
    def __init__(self, zmqSocket, loudDelay=1024, fftsize=8192):
        self.lqueue = ""
        self.fqueue = ""
        self.sock = zmqSocket
        self._loudDelay = loudDelay
        self._fftsize = fftsize
>>>>>>> 8ac4b79855fcc50934a343e6c42bd7928a5c2afa

    def addSamples(self, samples):
        # maybe add samples recursively to the loudness buf
        self.lqueue = ''.join([self.lqueue, samples])
        self.fqueue = ''.join([self.fqueue, samples])
<<<<<<< HEAD
        self.lcount += CHUNK
        self.fcount += CHUNK
        if len(self.lqueue) >= self.loudDelay:
            self.calcLoudness()
        if self.fcount >= self._fftlength:
=======
        if len(self.lqueue) >= self.loudDelay:
            self.calcLoudness()
        if len(self.fqueue) >= self.fftsize:
>>>>>>> 8ac4b79855fcc50934a343e6c42bd7928a5c2afa
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
<<<<<<< HEAD
        print 'fired fft'
        arr = np.fromstring(self.fqueue, dtype=np.float32)
        fft = np.fft.fft(arr)[:len(arr)/2:10]
        mag = map(abs, fft)
        # don't send all values we don't need that pinpoint accuracy
        # maybe every 10 values
=======
        print "fire fft"

        arr = np.fromstring(self.fqueue, dtype=np.float32)
        fft = np.fft.fft(arr)[:len(arr)/2]
        mag = map(abs, fft)
>>>>>>> 8ac4b79855fcc50934a343e6c42bd7928a5c2afa

        self.sock.send('f' + json.dumps({
            'nsamp': len(mag),
            'samples': mag}))
        self.fqueue = ""
<<<<<<< HEAD
        self.fcount = 0
=======
>>>>>>> 8ac4b79855fcc50934a343e6c42bd7928a5c2afa

    @property
    def loudDelay(self):
        return self._loudDelay

    @loudDelay.setter
    def loudDelay(self, val):
        self._loudDelay = val

    @property
<<<<<<< HEAD
    def fftlength(self):
        return self._fftlength

    @fftlength.setter
    def fftlength(self, val):
        self._fftlength = val
=======
    def fftsize(self):
        return self._fftsize

    @fftsize.setter
    def fftsize(self, val):
        self._fftsize = val
>>>>>>> 8ac4b79855fcc50934a343e6c42bd7928a5c2afa


def main(ip="127.0.0.1"):
    ctx = zmq.Context()
    s = ctx.socket(zmq.PUSH)
<<<<<<< HEAD
    s.connect('tcp://127.0.0.1:7777')
=======
    s.bind('tcp://127.0.0.1:{}'.format(PORT))
>>>>>>> 8ac4b79855fcc50934a343e6c42bd7928a5c2afa
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
