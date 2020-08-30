#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <list>
#include <iostream>

using namespace std;

char turn;
const int MAX = 2;
const int N   = 8;
const int M   = N / 2 + N % 2;
const int W   = N / 2;

int nm = 0;
int dm = 0;
int dsm = 0;
int nw = 0;
int dw = 0;
int dsw = 0;

mutex e;
condition_variable m, w, sm, sw;

void man_wants_to_enter(int id)
{
    unique_lock<mutex> lk(e);
    if (turn == 'W' || nm == MAX) {
        ++dm;
        // m.wait(lk, []{return turn == 'M' && nm < MAX;});
        m.wait(lk);
    }

    ++nm;
    cout << "nm: " << nm << " nw: " << nw << " id: " << id << endl;
    if (dm > 0 && nm < MAX) {
        --dm;
        m.notify_one();
    } else if (dsm > 0 && nm < MAX) {
        --dsm;
        sm.notify_one();
    }
}

void man_wants_to_exit()
{
    unique_lock<mutex> lk(e);
    --nm;
    ++dsm;

    if (nm == 0) {
        turn = 'W';
        if (dw > 0) {
            --dw;
            w.notify_one();
        } else if (dsw > 0) {
            --dsw;
            sw.notify_one();
        }
    }
}


void man_waits()
{
    unique_lock<mutex> lk(e);
    // sm.wait(lk, []{return turn == 'M' && nm < MAX && dm == 0;});
    sm.wait(lk);
}


void man(int id)
{
    while (true)
    {
        man_wants_to_enter(id);
        this_thread::sleep_for(chrono::seconds(1));
        man_wants_to_exit();
        man_waits();
    }
}


void woman_wants_to_enter(int id)
{
    unique_lock<mutex> lk(e);
    if (turn == 'M' || nw == MAX) {
        ++dw;
        // w.wait(lk, []{return turn == 'W' && nw < MAX;});
        w.wait(lk);
    }

    ++nw;
    cout << "nm: " << nm << " nw: " << nw << " id: " << id << endl;
    if (dw > 0 && nw < MAX) {
        --dw;
        w.notify_one();
    } else if (dsw > 0 && nw < MAX) {
        --dsw;
        sw.notify_one();
    }
}

void woman_wants_to_exit()
{
    unique_lock<mutex> lk(e);
    --nw;
    ++dsw;

    if (nw == 0) {
        turn = 'M';
        if (dm > 0) {
            --dm;
            m.notify_one();
        } else if (dsm > 0) {
            --dsm;
            sm.notify_one();
        }
    }
}


void woman_waits()
{
    unique_lock<mutex> lk(e);
    // sw.wait(lk, []{return turn == 'W' && nw < MAX && dw == 0;});
    sw.wait(lk);
}


void woman(int id)
{
    while (true)
    {
        woman_wants_to_enter(id);
        this_thread::sleep_for(chrono::seconds(1));
        woman_wants_to_exit();
        woman_waits();
    }
}

int main()
{
    turn = ((rand() % 2) % 2 == 0) ? 'M' : 'W';
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