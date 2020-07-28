from threading import Barrier, Thread
from os import cpu_count
from random import randint
import matplotlib.pyplot as plt

# An array of integers img[1:n, 1:n] is given. The value of each element is the intensity of the pixel.
# Two neighboring pixels belong to the region if their values ​​are equal. 
# The challenge is to find all areas and assign a unique label to all pixels in the area.


def init_globals():
    global img, n, labels, newlabels, haschanged, parties, barrier, isfinished
    n = 7
    img = [[randint(0, 1) for _ in range(n)] for _ in range(n)]
    labels = [[i * n + j + 1 for j in range(n)] for i in range(n)]
    newlabels = [[None for j in range(n)] for i in range(n)]
    haschanged = [[False for j in range(n)] for i in range(n)]

    parties = cpu_count()
    barrier = Barrier(parties)
    isfinished = [False for _ in range(parties)]

def get_neighbors_labels(i: int, j: int):
    di = [-1, 0, 1, 0]
    dj = [0, -1, 0, 1]
    neighbors_labels = []
    for k in range(4):
        newi = di[k] + i
        newj = dj[k] + j

        if (newi < 0 or newi >= n or
                newj < 0 or newj >= n):
            continue
        if img[i][j] == img[newi][newj]:
            neighbors_labels.append(labels[newi][newj])

    return neighbors_labels

def is_finished(thread_id: int, i0: int, bias: int):
    changes_in_rows = [False for _ in range(bias)]
    for i in range(i0, i0 + bias):
        if any(haschanged[i]):
            changes_in_rows[i - i0] = True
    
    if any(changes_in_rows):
        isfinished[thread_id] = False
    else:
        isfinished[thread_id] = True
    barrier.wait()
    return all(isfinished)

def copy_labels(i0: int, bias: int):
    for i in range(i0, i0 + bias):
        for j in range(n):
            labels[i][j] = newlabels[i][j]

def find_new_labels(thread_id: int, i0: int, bias: int):
    for i in range(i0, i0 + bias):
        for j in range(n):
            neighbors_labels = get_neighbors_labels(i, j)
            if len(neighbors_labels) > 0:
                newlabels[i][j] = max(*neighbors_labels,
                                           labels[i][j])
                if newlabels[i][j] != labels[i][j]:
                    haschanged[i][j] = True
                else:
                    haschanged[i][j] = False
            else:
                newlabels[i][j] = labels[i][j]
                haschanged[i][j] = False


def find_area_labels(thread_id: int, i0: int, bias: int):
    find_new_labels(thread_id, i0, bias)
    barrier.wait()
    copy_labels(i0, bias)
    barrier.wait()
    while not is_finished(thread_id, i0, bias):
        find_new_labels(thread_id, i0, bias)
        barrier.wait()
        copy_labels(i0, bias)
        barrier.wait()


def find_labels():
    i0 = 0
    bias, remainder = n // parties, n % parties

    threads = [None for _ in range(parties)]

    for j in range(parties):
        if j == parties - 1:
            bias += remainder
        threads[j] = Thread(target=find_area_labels,
                            args=(j, i0, bias))
        threads[j].start()
        i0 += bias

    for j in range(parties):
        threads[j].join()

if __name__ == '__main__':
    init_globals()
    find_labels()
    # f, axarr = plt.subplots(nrows=1, ncols=1)
    # axarr.imshow(img)


    # for i in range(n):
    #     for j in range(n):
    #         print(labels[i][j], end=' ')
    #     print()

    # plt.show()
