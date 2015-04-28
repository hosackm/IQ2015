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


class Loudness(object):
    def __init__(self, windowlength=50, numBuffers=4):
        self.numBuffers = numBuffers
        self.bufcount = 0
        self.buf = np.array([], dtype=np.float32)
        self.rms_queue = []
        self.windowlength = windowlength

    def addSamples(self, samples):
        """samples is a string of bytes"""
        self.buf = np.append(
            self.buf,
            np.fromstring(
                samples,
                dtype=np.float32))
        self.bufcount += 1
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
        # self.lqueue = ""
        self.lqueue = Loudness()
        self.fqueue = ""
        self.fcount = 0
        self.lcount = 0
        self.sock = zmqSocket
        self._loudDelay = loudDelay
        next = lambda x: int(pow(2, ceil(log(x)/log(2))))
        self._fftlength = next(fftlength * RATE)  # seconds

    def addSamples(self, samples):
        # maybe add samples recursively to the loudness buf
        lready = self.lqueue.addSamples(samples)
        self.fqueue = ''.join([self.fqueue, samples])
        self.fcount += CHUNK
        if self.fcount >= self._fftlength:
            self.calcFFT()
        if lready:
            _, lval = lready
            #print "fire loudness!"
            self.sock.send('l' + json.dumps({'value': 10.*log(lval)}))

    def calcFFT(self):
        """Convert to numpy array.
        Calculate the fft on the samples in the fft queue.
        Send ZMQ message.
        Clear fqueue."""
        arr = np.fromstring(self.fqueue, dtype=np.float32)
        fft = np.fft.fft(arr)[:len(arr)/2:50]
        mag = map(abs, fft)
        # don't send all values we don't need that pinpoint accuracy
        # maybe every 10 values
        #print "fire fft"

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


def main(ip='tcp://127.0.0.1:7777'):
    ctx = zmq.Context()
    s = ctx.socket(zmq.PUSH)
    s.connect(ip)
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
