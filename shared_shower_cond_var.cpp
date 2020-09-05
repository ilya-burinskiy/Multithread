#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <list>
#include <iostream>

using namespace std;

/**
 * nm = number of men in shower
 * nw = number of women in shower
 *                  
 *                          Invariant
 * I: (nm == 0 || turn == 'M') && (nw == 0 || turn == 'W') :=
 *    (nm == 0 && nw == 0) || (nm == 0 && turn == 'W') ||
 *    (nw == 0 && turn == 'M')
 */

const int N = 7;
const int MAX = 3;
const int M = N / 2 + N % 2;
const int W = N / 2;
char turn = 'W';

mutex mut;
condition_variable mqueue;      // men's shower queue
condition_variable wqueue;      // women's shower queue 
condition_variable smqueue;     // men's after shower queue
condition_variable swqueue;     // women's after shower queue

bool can_leave_mqueue = true;
bool can_leave_wqueue = true;
bool can_leave_smqueue = false;
bool can_leave_swqueue = false;
int m_didnt_have_shower = M;
int w_didnt_have_shower = W;
int m_in_shower = 0;
int w_in_shower = 0;

void man(int i);
void m_enteres_shower(int i);
void m_leaves_shower(int i);

void woman(int i);
void w_enteres_shower(int i);
void w_leaves_shower(int i);

int main()
{
    list<thread> threads;
    int i;
    for (i = 0; i < N; i++) {
        if (i % 2 == 0)
            threads.push_back(thread(man, i));
        else
            threads.push_back(thread(woman, i));
    }

    for (auto& t: threads)
        t.join();
}


void man(int i)
{
    while (true)
    {
        m_enteres_shower(i);
        this_thread::sleep_for(chrono::seconds(1));
        m_leaves_shower(i);
    }
}

void m_enteres_shower(int i)
{
    unique_lock<mutex> lk(mut);
    mqueue.wait(lk, [] {
            return turn == 'M' && can_leave_mqueue;
        }
    );

    ++m_in_shower;
    --m_didnt_have_shower;

    cout << "nm: " << m_in_shower << " nw: " << w_in_shower << " id: " << i << endl;

    if (m_in_shower == MAX) {
        can_leave_mqueue = false;
    } else if (m_didnt_have_shower > 0) {
        mqueue.notify_all();
    } else {
        can_leave_smqueue = true;
        smqueue.notify_all();
    }
}

void m_leaves_shower(int i)
{
    unique_lock<mutex> lk(mut);
    --m_in_shower;

    if (m_in_shower == 0) {
        turn = 'W';
        can_leave_wqueue = true;
        if (w_didnt_have_shower > 0) {
            wqueue.notify_all();
        } else {
            can_leave_swqueue = true;
            swqueue.notify_all();
        }
    }

    smqueue.wait(lk, [] {
            return turn == 'M' && can_leave_smqueue;
        }
    );

    ++m_didnt_have_shower;
}


void woman(int i)
{
    while (true)
    {
        w_enteres_shower(i);
        this_thread::sleep_for(chrono::seconds(1));
        w_leaves_shower(i);
    }
}

void w_enteres_shower(int i)
{
    unique_lock<mutex> lk(mut);
    wqueue.wait(lk, [] {
            return turn == 'W' && can_leave_wqueue;
        }
    );

    ++w_in_shower;
    --w_didnt_have_shower;

    cout << "nm: " << m_in_shower << " nw: " << w_in_shower << " id: " << i << endl;

    if (w_in_shower == MAX) {
        can_leave_wqueue = false;
    } else if (w_didnt_have_shower > 0) {
        wqueue.notify_all();
    } else {
        can_leave_swqueue = true;
        swqueue.notify_all();
    }
}

void w_leaves_shower(int i) 
{
    unique_lock<mutex> lk(mut);
    --w_in_shower;

    if (w_in_shower == 0) {
        turn = 'M';
        can_leave_mqueue = true;
        if (m_didnt_have_shower > 0) {
            mqueue.notify_all();
        } else {
            can_leave_smqueue = true;
            smqueue.notify_all();
        }
    }

    swqueue.wait(lk, [] {
            return turn == 'W' && can_leave_swqueue;
        }
    );

    ++w_didnt_have_shower;
}