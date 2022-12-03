#!/usr/bin/env python
import operator
import os
import re
import sys
import time
from collections import Counter
from threading import Thread

# GLOBALS
input_data = []
prev_time = time.process_time()
input_timeout = 5

# day 03 part a
priority_map = dict()
alpha_lower = 'abcdefghijklmnopqrstuvwxyz'
alpha_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

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


def fill_in_priority_map() -> None:
    all_alpha = alpha_lower + alpha_upper
    for idx in range(52):
        priority_map[all_alpha[idx]] = idx + 1


# READ INPUT
def read_input():
    global input_data

    # print("reading input... START")

    cnt = 0
    for line in sys.stdin:
        cnt += 1
        # print(f"[{cnt}] {line}")

        # if len(val) > 0:
        input_data.append(line.strip())

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
    Find the item type that appears in both compartments of each rucksack.
    What is the sum of the priorities of those item types?
    """
    common_items = []
    for line in input_data:
        comp_1 = Counter(line[:len(line) // 2])
        comp_2 = Counter(line[len(line) // 2:])
        common = comp_1 & comp_2  # intersection ;)
        # getting the first (and only) element of list created by counter's keys
        # Counter({'b': 1})
        # dict_keys(['b'])
        # ['b']
        item_value = list(common.keys())[0]
        common_items.append(item_value)

    result = 0
    for item in common_items:
        result += priority_map[item]

    return result


def find_solution_b():
    """
    Find the item type that corresponds to the badges of each three-Elf group.
    What is the sum of the priorities of those item types?
    """
    three_elves_group = []
    group_size = 3
    curr_list = []
    for idx, elem in enumerate(input_data):
        if idx % group_size == 0 and idx > 0:
            three_elves_group.append(curr_list)
            curr_list = [elem]
        else:
            curr_list.append(elem)

    # add the last one
    three_elves_group.append(curr_list)

    # print(f"three_elves_group: {three_elves_group}\n")

    common_items = []

    for group in three_elves_group:
        # print(f"group:{group}")
        cnt_list = list(map(Counter, group))
        # print(f"cnt_list:{cnt_list}")
        comm_tmp = list(map(operator.and_, cnt_list, cnt_list[1:]))
        # print(f"comm_tmp:{comm_tmp}\n")
        comm = list(map(operator.and_, comm_tmp, comm_tmp[1:]))
        # print(f"comm:{comm}\n")

        item_value = list(comm[0].keys())[0]
        common_items.append(item_value)

    result = 0
    for item in common_items:
        result += priority_map[item]

    return result


# MAIN
def do_main():
    show_elapsed_time()

    print("read input")
    controlled_input_read()
    show_elapsed_time()

    # print("input_data", input_data)

    fill_in_priority_map()
    # print("priority_map", priority_map)

    result_a = find_solution_a()
    print(f"result_a: {result_a}")
    show_elapsed_time()

    result_b = find_solution_b()
    print(f"result_b: {result_b}")
    show_elapsed_time()


if __name__ == "__main__":
    # execute only if run as a script
    do_main()
