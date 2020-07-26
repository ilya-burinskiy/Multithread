from threading import Semaphore, Thread

class RingBuf:

    def __init__(self, size):
        self.size = size
        self.buf = [0 for _ in range(self.size)]
        self.count = 0              # elements in buf
        self.rear = self.front = 0

        self.e = Semaphore(1)       # enter semaphore
        self.d = Semaphore(0)       # delay semaphore
        self.nd = 0                 # delay count


    def deposit(self, data):
        self.e.acquire()
        while self.count == self.size:
            self.nd += 1
            self.e.release()
            self.d.acquire()
            self.e.acquire()

        self.buf[self.rear] = data
        self.rear = (self.rear + 1) % self.size
        self.count += 1

        while self.nd > 0:
            self.nd -= 1
            self.d.release()
        self.e.release()

    def fetch(self):
        self.e.acquire()
        while self.count == 0:
            self.nd += 1
            self.e.release()
            self.d.acquire()
            self.e.acquire()

        res = self.buf[self.front]
        self.front = (self.front + 1) % self.size
        self.count -= 1

        while self.nd > 0:
            self.nd -= 1
            self.d.release()
        self.e.release()

        return res

def producer(id_):
    i = 0
    while i < N:
        print('%d: producing %d' % (id_, i))
        buf.deposit(i)
        i += 1

def consumer(id_):
    i = 0
    while i < N:
        res = buf.fetch()
        print('%d: consuming %d' % (id_, res))
        i += 1

if __name__ == '__main__':
    N = 10
    M = 10
    buf = RingBuf(5)

    threads = [None for _ in range(2 * M)]
    for i in range(2 * M):
        if i % 2 == 0:
            threads[i] = Thread(target=producer, args=(i, ))
            threads[i].start()
        else:
            threads[i] = Thread(target=consumer, args=(i, ))
            threads[i].start()

    for i in range(2 * M):
        threads[i].join()