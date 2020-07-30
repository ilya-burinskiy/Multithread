#include <atomic>
#include <iostream>
#include <thread>

using namespace std;

class sem {

private:
    atomic<int> _s;

public:
    sem(int val): _s{val}
    {
    }

    ~sem()
    {
    }

    void acquire()
    {
        int prev, tmp;
        while (true)
        {
            await_loop:
                tmp = _s.load();
                if (tmp == 0)
                    goto await_loop;
            prev = atomic_fetch_add(&_s, -1);
            if (prev < 0) 
            {
                atomic_fetch_add(&_s, 1);
                continue;
            } 
            else
                break;
        }
    }

    void release()
    {
        atomic_fetch_add(&_s, 1);
    }
};

static int buff;
static sem empty(1);
static sem full(0);
static sem mutex(0);

void producer()
{
    for (int i = 0; i < 10; i++)
    {
        empty.acquire();
        buff = i;
        cout << "Produced: " << i << endl;
        full.release();
    }
}

void consumer()
{
    int data;
    for (int i = 0; i < 10; i++)
    {
        full.acquire();
        data = buff;
        cout << "Consumed: " << data << endl;
        empty.release();
    }
}


int main()
{
    thread prod = thread(producer);
    thread cons = thread(consumer);
    prod.join();
    cons.join();
}