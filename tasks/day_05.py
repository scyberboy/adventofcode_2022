#!/usr/bin/env python
import os
import re
import sys
import time
from copy import deepcopy
from threading import Thread

# GLOBALS
input_data = []
prev_time = time.process_time()
input_timeout = 5

# day 5 specific
stacks: list[list[str]] = []

move_commands: list[(int, int, int)] = []

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
    global stacks
    global move_commands

    # print("reading input... START")

    cnt = 0

    # first read stacks content (w/o numbering) in List[List[str]]
    for line in sys.stdin:
        if len(line) < 2:
            stacks.pop()
            break

        cnt += 1
        # print(f"[{cnt}] '{line}'")

        # if len(val) > 0:
        str_pat = r"(.{3})\s?"
        res = re.findall(str_pat, line)
        # print(f"1 res: {res}")
        stacks.append([elem.strip("[] ") for elem in res])

    # then read the moves in List[List(quant, from, to)] or something
    for line in sys.stdin:
        cnt += 1
        # print(f"[{cnt}] {line}")

        # if len(val) > 0:
        str_pat = r"(\d+)"
        res = re.findall(str_pat, line.strip())
        # print(f"2 res: {res}")
        move_commands.append([int(elem) for elem in res])

    # print(f"stacks: {stacks}")
    # print(f"move_commands: {move_commands}")

    # Now normalize stacks to represent reals stacks indexes as humanly readable shown by columns
    stacks_reversed = [elem for elem in reversed(stacks)]
    # print(f"stacks_reversed: {stacks_reversed}")

    # We may need to re-shape stacks so empty it first
    del stacks[:]

    for idx_inner in range(len(stacks_reversed[0])):
        stacks.append([])
        for idx_outer in range(len(stacks_reversed)):
            elem = stacks_reversed[idx_outer].pop(0)
            stacks[idx_inner].append(elem)

    # print(f"(re-shaped) stacks: {stacks}")

    # get rid of empty crates in each stack
    for idx in range(len(stacks)):
        while "" in stacks[idx]:
            stacks[idx].remove("")

    # print(f"stripped stacks: {stacks}")

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
    The crane moves one crate at a time.
    After the rearrangement procedure completes, what crate ends up on top of each stack?
    """
    global move_commands
    global stacks

    result_stacks = deepcopy(stacks)

    for qty, src, dst in move_commands:
        # transform stack numbers to indexes to match our internal representation
        src -= 1
        dst -= 1
        for _ in range(qty):
            elem = result_stacks[src].pop()
            result_stacks[dst].append(elem)

    # print(f"A final stacks: {result_stacks}")
    result = [elem[-1] if elem[-1] else "" for elem in result_stacks]
    # print(f"result: {result}")

    return "".join(result)


def find_solution_b():
    """
    The crane moves as many crates as specified at a time, thus preserving their order ;)
    After the rearrangement procedure completes, what crate ends up on top of each stack?
    """
    global move_commands
    global stacks

    result_stacks = deepcopy(stacks)
    # my_l1
    # [1, 3, 4]
    # my_l1[len(my_l1)-2:]
    # [3, 4]
    for qty, src, dst in move_commands:
        # transform stack numbers to indexes to match our internal representation
        src -= 1
        dst -= 1
        elems = result_stacks[src][len(result_stacks[src]) - qty:]
        # now remove them from src
        del result_stacks[src][len(result_stacks[src]) - qty:]
        result_stacks[dst].extend(elems)

    # print(f"B final stacks: {result_stacks}")
    result = [elem[-1] if elem[-1] else "" for elem in result_stacks]
    # print(f"result: {result}")

    return "".join(result)


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
