#include <iostream>
#include <array>

#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>

using namespace std;
/*                          Invariant
    I: eating[i] == T -> (eating[(i + 1 + N) % N] == F && 
                          eating[(i - 1 + N) % N] == F)
*/

const int N          = 5;  // philosophers count
int didnt_have_diner = 5;  // philosophers who didn't have diner on current 
                           // loop iteration
bool all_had_diner = false;
array<bool, N> eating;
int eating_now = 0;

mutex e, cout_mut;
condition_variable wait_for_forks, wait_for_all;

void give_back_forks(int i)
{
    unique_lock<mutex> lk(e);
    --eating_now;
    cout << i << " finished diner." << "Eating now " << eating_now << endl;
    eating[i] = false;

    for (auto _ = 0; _ < 2; ++_)
        wait_for_forks.notify_one();

    wait_for_all.wait(lk, [] {
            return all_had_diner == true;
        }
    );
    ++didnt_have_diner;
    if (didnt_have_diner == N)
        all_had_diner = false;
}

void take_forks(int i)
{
    unique_lock<mutex> lk(e);
    wait_for_forks.wait(lk, [i] {
        return eating[(i + 1 + N) % N] == false &&
               eating[(i - 1 + N) % N] == false;
        }
    );

    eating[i] = true;
    ++eating_now;
    cout << i << " has diner." << "Eating now " << eating_now << endl;

    --didnt_have_diner;
    if (didnt_have_diner == 0) {
        all_had_diner = true;
        wait_for_all.notify_all();
    }
}

void philosopher(int i)
{
    while (true)
    {
        take_forks(i);
        this_thread::sleep_for(chrono::seconds(2));
        give_back_forks(i);
        this_thread::sleep_for(chrono::seconds(2));
    }
}

int main()
{
    int i;
    array<thread, N> threads;

    for (i = 0; i < N; ++i)
        eating[i] = false;
    for (i = 0; i < N; ++i)
        threads[i] = thread(philosopher, i);
    for (i = 0; i < N; ++i)
        threads[i].join();

    return 0;
}