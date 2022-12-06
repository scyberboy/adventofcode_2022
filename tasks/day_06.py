#!/usr/bin/env python
import os
import re
import sys
import time
from collections import Counter
from threading import Thread

# GLOBALS
input_data = ""
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
        # print(f"[{cnt}] '{line}'")

        # if len(val) > 0:
        input_data = line.strip()

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
    How many characters need to be processed before the first start-of-packet marker is detected?
    """
    global input_data

    marker_len = 4
    end_idx = -1  # this will be the result as well
    for idx in range(len(input_data)):
        end_idx = idx + marker_len
        candidate = input_data[idx:end_idx]
        cntr = Counter(candidate)
        # my_cnt.most_common(1)
        # [(4, 2)]
        most_common_value = cntr.most_common(1)[0][1]
        if most_common_value == 1:
            break

    return end_idx


def find_solution_b():
    """
    How many characters need to be processed before the first start-of-message marker is detected?
    """
    global input_data

    message_len = 14
    end_idx = -1  # this will be the result as well
    for idx in range(len(input_data)):
        end_idx = idx + message_len
        candidate = input_data[idx:end_idx]
        cntr = Counter(candidate)
        # my_cnt.most_common(1)
        # [(4, 2)]
        most_common_value = cntr.most_common(1)[0][1]
        if most_common_value == 1:
            break

    return end_idx


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
