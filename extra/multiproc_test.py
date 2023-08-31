#!python3
"""
this test will define a dummy function that sleeps and prints, then returns an object
the main process will poll the stdout of the dummy function and print it then recieve the object
"""
import time
from multiprocessing import Pipe, Process


def dummy_function(child_conn, n=10):
    for i in range(n):
        print("dummy_function", i)
        time.sleep(1)
    child_conn.send("dummy_function done")


if __name__ == "__main__":
    parent_conn, child_conn = Pipe()
    p = Process(
        target=dummy_function,
        args=(
            child_conn,
            10,
        ),
    )
    p.start()
    while p.is_alive():
        print("main process")
        if parent_conn.poll():
            print(parent_conn.recv())
        time.sleep(0.5)
    p.join()
    print("end while loop")
    print(parent_conn.recv())
    print("main process done")
