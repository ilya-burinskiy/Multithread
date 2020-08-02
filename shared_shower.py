from threading import Semaphore, Thread
from time import sleep
from random import randint

# Suppose the dorm has a shower room that can be used by men and women, 
# but not at the same time: define a global invariant, 
# then design a solution using semaphores to synchronize.
# BAD: (nm > 0 && turn == 'W') || (nw > 0 && turn == 'M')
# GOOD: (nm == 0 || turn == 'M') && (nw == 0 || turn == 'W') =
#       (nm == 0 && nw == 0) || (nm == 0 && turn == 'W') ||
#       (nw == 0 && turn == 'M')

MAX_COUNT = 2       # maximum number of people in the shower

N = 6               # threads num
M = N // 2 + N % 2  # number of men
W = N // 2          # number of women

nm = 0              # number of men in shower
nw = 0              # number of women in shower
turn = None         # whose turn to use the shower

e = Semaphore(1)    # for entring in critical area
m = Semaphore(0)    # for pause man
w = Semaphore(0)    # for pause woman
sm = Semaphore(0)   # for pause man who took a shower
sw = Semaphore(0)   # for woman who took a shower

dm = 0              # number of suspended men
dw = 0              # number of suspended women
dsm = 0             # number of man who took a shower
dsw = 0             # nubmer of woman who took a shower

def man(id_):
    global nm, nw, turn, e, m, w, sm, sw, dm, dw, dsm, dsw

    while True:

        # Enter protocol
        e.acquire()
        if nw > 0 or turn == 'W' or nm == MAX_COUNT:
            dm += 1
            e.release()
            m.acquire()
        nm += 1
        if nm == min(MAX_COUNT, M):
            turn = 'W'
        print('nw: %d nm: %d id: %d' % (nw, nm, id_))

        # SIGNAL
        if dm > 0 and nm < MAX_COUNT:
            dm -= 1
            m.release()
        elif dsm > 0 and nm < MAX_COUNT:
            dsm -= 1
            sm.release()
            e.release()
        else:
            e.release()

        # Showering
        sleep(1)

        # Exit protocol
        e.acquire()
        nm -= 1
        dsm += 1
        # print('nw: %d nm: %d id: %d' % (nw, nm, id_))
        if nm == 0:
            if dw > 0:
                dw -= 1
                w.release()
            elif dsw > 0:
                dsw -= 1
                sw.release()
                e.release()
        elif turn == 'M':
            if dm > 0 and nm < MAX_COUNT:
                dm -= 1
                m.release()
            elif dsm > 0 and nm < MAX_COUNT:
                dsm -= 1
                sm.release()
                e.release()
        else:
            e.release()
        
        sm.acquire()

def woman(id_):
    global nm, nw, turn, e, m, w, sm, sw, dm, dw, dsm, dsw

    while True:

        # Enter protocol
        e.acquire()
        if nm > 0 or turn == 'M' or nw == MAX_COUNT:
            dw += 1
            e.release()
            w.acquire()
        nw += 1
        if nw == min(MAX_COUNT, W):
            turn = 'M'
        print('nw: %d nm: %d id: %d' % (nw, nm, id_))

        # SIGNAL
        if dw > 0 and nw < MAX_COUNT:
            dw -= 1
            w.release()
        elif dsw > 0 and nw < MAX_COUNT:
            dsw -= 1
            sw.release()
            e.release()
        else:
            e.release()

        # Showering
        sleep(1)

        # Exit protocol
        e.acquire()
        nw -= 1
        dsw += 1
        # print('nw: %d nm: %d id: %d' % (nw, nm, id_))

        if nw == 0:
            if dm > 0:
                dm -= 1
                m.release()
            elif dsm > 0:
                dsm -= 1
                sm.release()
                e.release()
        elif turn == 'W':
            if dw > 0 and nw < MAX_COUNT:
                dw -= 1
                w.release()
            elif dsw > 0 and nw < MAX_COUNT:
                dsw -= 1
                sw.release()
                e.release()
        else:
            e.release()
        
        sw.acquire()

def main():
    global turn
    turn = ['M', 'W'][randint(0, 1)]

    threads = [None for _ in range(N)]
    for i in range(N):
        if i % 2 == 0:
            threads[i] = Thread(target=man, args=(i, ))
        else:
            threads[i] = Thread(target=woman, args=(i, ))
        threads[i].start()

    for i in range(N):
        threads[i].join()

if __name__ == '__main__':
    main()
