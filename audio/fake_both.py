import zmq
import time
import json
from random import randint


def main():
    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUSH)
    socket.bind("tcp://127.0.0.1:7777")
    while True:
        i = randint(0, 30)
        print 'sending {}'.format(i)
        socket.send('l' + json.dumps(
            {'value': i})
        )
        time.sleep(0.5)

        arr = [randint(0, 100) for ix in xrange(1025)]
        l = len(arr)
        print 'sending {}'.format(arr)
        socket.send('f' + json.dumps({
            'nsamp': l,
            'samples': arr})
        )
        time.sleep(3.0)

if __name__ == '__main__':
    main()
