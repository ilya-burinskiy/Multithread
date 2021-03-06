from threading import Semaphore, Thread
from random import randint
import time

class Barrier:

    def __init__(self, parties):
        self.n = parties
        self.count = 0
        self.arrive = Semaphore(1)
        self.go = Semaphore(0)

    def wait(self):

        self.arrive.acquire()
        self.count += 1

        if self.count != self.n:
            self.arrive.release()
            self.go.acquire()

        
        if self.count == 1:
            self.count -= 1
            self.arrive.release()
        else:
            self.count -= 1
            self.go.release()


def calc_sum1():
    global a, s1, old
    t = time.time()
    s1[0] = a[0]
    for i in range(1, N):
        s1[i] = s1[i - 1] + a[i]
    t = time.time() - t
    print("Time: %.3f" % (100 * t))
    return

def subarray_sum(start, end):
    global a, s2, old, barrier
    d = 1
    for i in range(start, end):
        s2[i] = a[i]
    barrier.wait()
    
    while d < N:
        for i in range(start, end):
            old[i] = s2[i]
        barrier.wait()

        for i in range(start, end):
            if i - d >= 0:
                s2[i] = old[i - d] + s2[i]
        barrier.wait()
        d = d + d
    
def calc_sum2():
    t = time.time()
    threads = [None for _ in range(K)]
    start = 0
    end = N // K
    for i in range(K):
        threads[i] = Thread(target=subarray_sum, args=(start, end)) 
        start = end
        end = end + N // K
    
    for i in range(K):
        threads[i].start()
    for i in range(K):
        threads[i].join()
    t = time.time() - t
    print("Time: %.3f" % (t))

if __name__ == "__main__":

    N = 60_000               # array size
    K = 60                   # num of threads
    barrier = Barrier(parties=K)

    a = [randint(0, 100) for _ in range(N)]
    s1 = [None for _ in range(N)]
    s2 = [None for _ in range(N)]
    old = [None for _ in range(N)]

    calc_sum1()
    calc_sum2()

    assert s1 == s2