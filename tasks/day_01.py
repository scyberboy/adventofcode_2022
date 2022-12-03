#!/usr/bin/env python
import os
import re
import sys
import time

# GLOBALS
input_data = []
elves = dict()

filename = os.path.basename(__file__)
day_nr = re.search(r"\d+", filename).group()
print(f"day_nr: {day_nr}")

prev_time = time.process_time()


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
    cnt = 0
    for line in sys.stdin:
        cnt += 1
        # print(f"[{cnt}] {line}")

        # val = line.strip()
        # if len(val) > 0:
        input_data.append(line.strip())


# SOLUTIONS
def find_solution_a():
    global elves
    # idx: {    "items" : [int, ...]
    #           "sum": int
    #       }
    idx_elves = 0
    curr_elf = {"items": [], "sum": 0}

    for inp_elem in input_data:

        if inp_elem == "":
            elves[idx_elves] = curr_elf.copy()

            idx_elves += 1
            curr_elf["items"] = []
            curr_elf["sum"] = 0
            continue

        curr_elf["items"].append(int(inp_elem))
        curr_elf["sum"] = sum(curr_elf["items"])

        # print(f"[{idx_elves}] {curr_elf}")

    # add the last one which have been prepared
    elves[idx_elves] = curr_elf

    # print(f"elves: {elves}")

    calories_list = sorted([val.get("sum") for val in elves.values()])
    result = calories_list[-1]

    return result


def find_solution_b():
    global elves

    calories_list = sorted([val.get("sum") for val in elves.values()])
    result = sum(calories_list[-3:])

    return result


# MAIN
def do_main():
    show_elapsed_time()

    print("read input")
    read_input()
    show_elapsed_time()
    # print("input_data", input_data)

    result_a = find_solution_a()
    print(f"result_a: {result_a}")
    show_elapsed_time()

    result_b = find_solution_b()
    print(f"result_b: {result_b}")
    show_elapsed_time()


if __name__ == "__main__":
    # execute only if run as a script
    do_main()
