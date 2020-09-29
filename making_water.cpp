#include <thread>
#include <mutex>
#include <condition_variable>
#include <iostream>
#include <vector>
#include <chrono>

using namespace std;

int hready = 0;
int oready = 0;
int atoms_in_h2o = 0;

mutex mut;
condition_variable can_leave_molecule, h_pool, o_pool;

void H()
{
    while (true)
    {
        {

            unique_lock<mutex> lk(mut);
            if (hready >= 2)
                h_pool.wait(lk, []{return hready < 2;});

            ++hready;
            ++atoms_in_h2o;
            cout << 'H' << endl;
            if (atoms_in_h2o < 3)
                can_leave_molecule.wait(lk);
            else
            {
                atoms_in_h2o = 0;
                can_leave_molecule.notify_all();
            }

            --hready;
            h_pool.notify_one();
        }
    }
}


void O()
{
    while (true)
    {
        {

            unique_lock<mutex> lk(mut);
            if (oready >= 1)
                o_pool.wait(lk, []{return oready < 1;});
            
            ++oready;
            ++atoms_in_h2o;
            cout << 'O' << endl;
            if (atoms_in_h2o < 3)
                can_leave_molecule.wait(lk);
            else
            {
                atoms_in_h2o = 0;
                can_leave_molecule.notify_all();
            }

            --oready;
            o_pool.notify_one();
        }
    }
}

int main()
{
    const int h_count = 6;
    const int o_count = 3;
    vector<thread> threads;

    int i;
    for (i = 0; i < h_count; ++i)
        threads.push_back(thread(H));
    for (i = 0; i < o_count; ++i)
        threads.push_back(thread(O));

    for (auto& t: threads)
        t.join();
}