from multiprocessing import Pool, freeze_support
import Native
import PyPP
import time

if __name__ == "__main__":
    freeze_support()
    with Pool() as p:
        beg = time.time()
        p.map(Native.benchmark_no_assert, range(100000))
        fin = time.time()
    print("Native took", fin-beg, "seconds")

    with Pool() as p:
        beg = time.time()
        p.map(PyPP.benchmark_no_assert, range(100000))
        fin = time.time()
    print("PyPP took", fin-beg, "seconds")
