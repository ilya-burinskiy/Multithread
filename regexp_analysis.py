from threading import Thread, Barrier
from os import cpu_count

# Consider a simple language for calculating expressions with the following syntax:
#       expression :: = operand | expression operator operand 
#       operand ::= identifier | number 
#       operator: = + |
# An identifier is a sequence of letters or numbers starting with a letter,
# a number is a sequence of numbers, and the operator is a + or * sign.
# Given an array of characters [0: n - 1]. Each character is a letter, number, +, or *.
# The sequence of characters from ch[0] to ch[n - 1] represents a sentence in the represented language.
# Write a data-parallel algorithm that defines the token (nonterminal) that the symbol belongs to for each character. 
# We can assume that there are several processes, one per character. 
# The result for each character must be an answer: ID, NUM, OP.

s = 'c45+b91+4566+895+1000'
n = len(s)
k = cpu_count()
b = Barrier(k)
state = [0 for _ in range(n)]
old_state = [0 for _ in range(n)]

def move(state, char):
    transit_table = [
        [1, 2, 3],
        [1, 1, 3],
        [1, 2, 3],
        [1, 2, None]
    ]

    new_state = None

    if char.isalpha():
        new_state = transit_table[state][0]
    elif char.isnumeric():
        new_state = transit_table[state][1]
    elif char in ('*', '+'):
        new_state = transit_table[state][2]
    return new_state

def identify_terminal(start, end):
    global state, old_state
    step = 1
    for i in range(start, end):
        state[i] = move(state[i], s[i])
    b.wait()

    while step < n:
        for i in range(start, end):
            old_state[i] = state[i]
        b.wait()
        for i in range(start, end):
            if (i - step >= 0):
                state[i] = move(old_state[i - 1], s[i])
        b.wait()
        step += 1

def print_terminals():
    global state
    for s in state:
        if s == 1:
            print('ID ', end='')
        elif s == 2:
            print('NUM ', end='')
        else:
            print('OP ', end='')

def main():
    threads = []

    start = 0
    end = n // k 
    for i in range(k):
        if i == k - 1:
            end += n % k
        threads.append(Thread(target=identify_terminal, args=(start, end)))
        start = end
        end += n // k

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print_terminals()
    print()

if __name__ == '__main__':
    main()