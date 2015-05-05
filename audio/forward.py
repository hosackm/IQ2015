import sys
import zmq
import pyaudio
import json
import numpy as np
from math import log

CHUNK = 1024
OUTPORT = 7777
INPORT = 7776
CHANNELS = 1
RATE = 48000
FORMAT = pyaudio.paFloat32


class Loudness(object):
    def __init__(self, windowlength=10, numBuffers=4):
        self.numBuffers = numBuffers
        self.bufcount = 0
        self.buf = np.array([], dtype=np.float32)
        self.rms_queue = []
        self.windowlength = windowlength

    def addSamples(self, samples):
        """samples is a string of bytes"""
        try:
            self.buf = np.append(
                self.buf,
                np.fromstring(
                    samples,
                    dtype=np.float32))
            self.bufcount += 1
        except:
            pass
        if self.bufcount >= self.numBuffers:
            self.bufcount = 0
            rms = np.sqrt(np.mean(np.square(self.buf)))
            self.buf = np.array([], dtype=np.float32)
            return self.addRMS(rms)
        return False

    def addRMS(self, val):
        self.rms_queue.append(val)
        if len(self.rms_queue) >= self.windowlength:
            return True, self.rms_queue.pop(0)
        return False


class AudioBuffer(object):
    """Class for buffering port audio samples and
    performing Loudness and FFT measurements"""
    def __init__(self, zmqSocket, loudDelay=1024, fftlength=5):
        self.lqueue = Loudness()
        self.fqueue = ""
        self.fcount = 0
        self.lcount = 0
        self.sock = zmqSocket
        self._loudDelay = loudDelay
        self._fftlength = 65536*2

    def addSamples(self, samples):
        lready = self.lqueue.addSamples(samples)
        self.fqueue = ''.join([self.fqueue, samples])
        self.fcount += CHUNK
        if self.fcount >= self._fftlength:
            self.calcFFT()
        if lready:
            _, lval = lready
            self.sock.send('l' + json.dumps({'value': 10.*log(lval)}))

    def calcFFT(self):
        """Convert to numpy array.
        Calculate the fft on the samples in the fft queue.
        Send ZMQ message.
        Clear fqueue."""
        try:
            arr = np.fromstring(self.fqueue, dtype=np.float32)
            # Slice for improved performance [200:len(arr)/2:50]#[len(arr)/2:]
            fft = np.fft.fft(arr)[len(arr)/2:]
            f = lambda x: 100 + 20. * log(abs(x))
            mag = map(f, fft)

            self.sock.send('f' + json.dumps({
                'nsamp': len(mag),
                'samples': mag}))
            self.fqueue = ""
            self.fcount = 0
        except:
            pass

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
    insock = zmq.Context().socket(zmq.PULL)
    outsock = zmq.Context().socket(zmq.PUSH)

    insock.bind('tcp://en2:7776')
    outsock.connect('tcp://127.0.0.1:7777')
    buffer = AudioBuffer(outsock)

    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK)

    while True:
        buffer.addSamples(insock.recv())

    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
