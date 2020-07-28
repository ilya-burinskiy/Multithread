from threading import Semaphore, Thread
from time import sleep
from random import randint

N = 5               # threads num
M = N // 2 + N % 2  # number of men
W = N // 2          # number of women

nm = 0              # number of men in shower
nw = 0              # number of women in shower
turn = None         # whose turn to use the shower
is_set = False      # is turn is set

e = Semaphore(1)    # for entring in critical area
m = Semaphore(0)    # for pause man
w = Semaphore(0)    # for pause woman

dm = 0              # number of suspended men
dw = 0              # number of suspended women

def set_turn(s):
    global e, is_set, turn
    e.acquire()
    if not is_set:
        turn = s
    e.release()

def man():
    global nm, nw, turn, e, m, w, dm, dw
    set_turn('M')
    while True:
        e.acquire()
        if nw > 0 or turn == 'W':
            dm += 1
            e.release()
            m.acquire()
        nm += 1
        if nm == M:
            turn = 'W'
        print('nw = %d, nm = %d' % (nw, nm))
        if dm > 0:
            dm -= 1
            m.release()
        else:
            e.release()
        sleep(1)

        e.acquire()
        nm -= 1
        print('nw = %d, nm = %d' % (nw, nm))

        if nm == 0 and dw > 0:
            dw -= 1
            w.release()
        elif dm > 0 and turn == 'M':
            dm -= 1
            m.release()
        else:
            e.release()

def woman():
    global nm, nw, turn, e, m, w, dm, dw
    set_turn('W')
    while True:
        e.acquire()
        if nm > 0 or turn == 'M':
            dw += 1
            e.release()
            w.acquire()
        nw += 1
        if nw == W:
            turn = 'M'
        print('nw = %d, nm = %d' % (nw, nm))
        if dw > 0:
            dw -= 1
            w.release()
        else:
            e.release()

        sleep(1)

        e.acquire()
        nw -= 1
        print('nw = %d, nm = %d' % (nw, nm))

        if nw == 0 and dm > 0:
            dm -= 1
            m.release()
        elif dw > 0 and turn == 'W':
            dw -= 1
            w.release()
        else:
            e.release()

def main():
    threads = [None for _ in range(N)]
    for i in range(N):
        if i % 2 == 0:
            threads[i] = Thread(target=man)
        else:
            threads[i] = Thread(target=woman)
        threads[i].start()

    for i in range(N):
        threads[i].join()

if __name__ == '__main__':
    main()
