#include <thread>
#include <cstdlib>
#include <experimental/random>
#include <vector>
#include <utility>
#include <atomic>
#include <iostream>
#include <algorithm>
#include <cassert>

using namespace std;

template<typename T>
void qsort_thread(vector<T>& A, size_t l, size_t r);

template<typename T>
void qsort_single(vector<T>& A, size_t l, size_t r);

template<typename T>
void qsort_(vector<T>& A, size_t l, size_t r);

template<typename T>
pair<size_t, size_t> partition(vector<T>& A, size_t l, size_t r);

int main()
{
    vector<int> v;
    for (auto _ = 0; _ < 40; ++_)
        v.push_back(experimental::randint(-10, 10));
    auto vcopy = v;

    qsort_<int>(v, 0, v.size());
    sort(vcopy.begin(), vcopy.end());

    assert(v == vcopy); 
    return 0;
}


template<typename T>
void qsort_(vector<T>& A, size_t l, size_t r)
{
    if (r <= l) {
        return;
    }

    auto [j, k] = partition(A, l, r);
    qsort_thread(A, l, j);
    qsort_thread(A, k + 1, r);
}

template<typename T>
void qsort_single(vector<T>& A, size_t l, size_t r)
{
    if (r <= l)
        return;

    auto [j, k] = partition(A, l, r);
    qsort_single(A, l, j);
    qsort_single(A, k + 1, r);
}


template<typename T>
void qsort_thread(vector<T>& A, size_t l, size_t r)
{
    static uint num_threads = thread::hardware_concurrency();
    static atomic<int> helpers_working(1);

    static int ratio = 4;
    static int threshold = A.size() / ratio;

    int n = r - l + 1;
    if (helpers_working.load() == num_threads || n >= threshold) {
        qsort_(A, l, r);
    } else {
        ++helpers_working;
        thread(qsort_single<T>, ref(A), l, r).detach();
        --helpers_working;
    }
}

template<typename T>
pair<size_t, size_t> partition(vector<T>& A, size_t l, size_t r)
{
    auto rnd = experimental::randint(l, r - 1);
    swap(A[l], A[rnd]);

    auto pivot = A[l];
    size_t j, k;
    j = k = l;
    for (auto i = l + 1; i < r; ++i) {
        if (A[i] < pivot) {
            ++j;
            ++k;
            swap(A[j], A[i]);
            if (j < k)
                swap(A[k], A[i]);
        } else if (A[i] == pivot) {
            ++k;
            swap(A[k], A[i]);
        }
    }

    swap(A[l], A[j]);
    return pair<size_t, size_t>(j, k);
}