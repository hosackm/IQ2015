import zmq
import time
import json
from random import randint


def main():
    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUSH)
    socket.connect("tcp://169.254.229.123:7777")
    while True:
        arr = [randint(0, 100) for i in xrange(1024)]
        l = len(arr)
        print 'sending {}'.format(arr)
        socket.send('f' + json.dumps({
            'nsamp': l,
            'samples': arr})
        )
        time.sleep(0.3)

if __name__ == '__main__':
    main()
