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
        time.sleep(0.3)

if __name__ == '__main__':
    main()
