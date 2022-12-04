#!/usr/bin/env python
import os
import re
import sys
import time
from threading import Thread

# GLOBALS
input_data = []
prev_time = time.process_time()
input_timeout = 5

filename = os.path.basename(__file__)
day_token = re.search(r"\d+", filename)
day_nr = day_token.group() if day_token else "unknown"
print(f"day_nr: {day_nr}")


# MISC
def show_elapsed_time():
    global prev_time
    cur_time = time.process_time()
    diff = cur_time - prev_time
    prev_time = cur_time
    print(f"[{cur_time}] took: {diff} sec.")


# READ INPUT
def read_input():
    global input_data

    # print("reading input... START")

    cnt = 0
    for line in sys.stdin:
        cnt += 1
        # print(f"[{cnt}] {line}")

        # if len(val) > 0:
        str_pat = r"\d+"
        res = re.findall(str_pat, line.strip())
        # print(res)
        input_data.append([int(elem) for elem in res])

    # print("reading input... END")


def controlled_input_read():
    read_input_thread = Thread(target=read_input, daemon=True, )
    read_input_thread.start()
    read_input_thread.join(timeout=input_timeout)
    if read_input_thread.is_alive():
        print(f"Timeout limit ({input_timeout} sec.) reached - exiting")
        sys.exit(1)


# SOLUTIONS
def find_solution_a():
    """
    In how many assignment pairs does one range fully contain the other?
    """

    total_contained = 0
    for b1, e1, b2, e2 in input_data:
        set1 = set([elem for elem in range(b1, e1 + 1)])
        set2 = set([elem for elem in range(b2, e2 + 1)])
        union_set = set1 | set2
        if union_set == max(set1, set2):
            # print(f"True -> union:{union_set}, set1:{set1}, set2:{set2}")
            total_contained += 1

    return total_contained


def find_solution_b():
    """
    In how many assignment pairs do the ranges overlap?
    """
    total_overlapping = 0
    for b1, e1, b2, e2 in input_data:
        set1 = set([elem for elem in range(b1, e1 + 1)])
        set2 = set([elem for elem in range(b2, e2 + 1)])
        intersection_set = set1 & set2
        if len(intersection_set) > 0:
            # print(f"True -> intersection_set:{intersection_set}, set1:{set1}, set2:{set2}")
            total_overlapping += 1

    return total_overlapping


# MAIN
def do_main():
    show_elapsed_time()

    print("read input")
    controlled_input_read()
    show_elapsed_time()

    # print(f"input_data({len(input_data)}):", input_data)

    result_a = find_solution_a()
    print(f"result_a: {result_a}")
    show_elapsed_time()

    result_b = find_solution_b()
    print(f"result_b: {result_b}")
    show_elapsed_time()


if __name__ == "__main__":
    # execute only if run as a script
    do_main()
