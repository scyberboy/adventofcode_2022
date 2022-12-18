#!/usr/bin/env python
import os
import re
import sys
import time
from threading import Thread

# GLOBALS
input_data: list[str] = []
prev_time = time.process_time()
input_timeout = 5

# day 10 specific
cycle_map: dict[int, int] = dict()
register_x = 1

# Generic (sub-main)
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

    for line in sys.stdin:
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

def get_previous(cycle_nr) -> int:
    for idx in range(cycle_nr - 1, -1):
        if idx in cycle_map:
            return cycle_map.get(idx)

    return register_x


def build_cycle_map():
    global register_x
    global cycle_map

    curr_cycle = 0
    curr_register_x = register_x
    cycle_map[curr_cycle] = curr_register_x

    for line in input_data:
        curr_cycle += 1

        # if curr_cycle > 20:
        #     break

        # print(f"-----------------{curr_cycle}---------------------")
        #
        # print(f"line: {line}")
        # print(f"register_x: {register_x}")
        # print(f"curr_register_x: {curr_register_x}")
        # print("cycle_map:", curr_cycle, " -> ", cycle_map.get(curr_cycle, curr_register_x))

        if line.startswith("noop"):
            if curr_cycle not in cycle_map:
                # print("is NOT in")
                cycle_map[curr_cycle] = curr_register_x
                register_x = curr_register_x
            else:
                # print("is in")
                curr_register_x = cycle_map[curr_cycle]
                register_x = curr_register_x

            continue

        curr_register_x = cycle_map.get(curr_cycle)
        if not curr_register_x:
            curr_register_x = cycle_map.get(curr_cycle - 1)

        # print(f"curr_register_x: {curr_register_x}")
        cycle_map[curr_cycle] = curr_register_x

        value = int(line.split()[1])

        target_cycle = curr_cycle + 2
        # previous_cycle_val = get_previous(curr_cycle)
        cycle_map[target_cycle] = curr_register_x + value
        # print(f"cycle_map[{target_cycle}] = {curr_register_x} + {value}")

        # advance the current cycle as well
        curr_cycle += 1

        # set register X value to the current calculated one
        register_x = curr_register_x

        # print(f"curr_register_x: {curr_register_x}")

        # print(f"-----------------{curr_cycle}---------------------")

    # now normalize the map - if any missing fill it with value from previous
    max_key = max([elem for elem in cycle_map.keys()])
    # print(f"max_key: {max_key}")
    for idx in range(max_key + 1):
        if idx not in cycle_map:
            cycle_map[idx] = cycle_map[idx - 1]


def find_solution_a():
    """
    For now, consider the signal strength (the cycle number multiplied by the value of the X register)
    Find the signal strength during the 20th, 60th, 100th, 140th, 180th, and 220th cycles.
    What is the sum of these six signal strengths?
    """
    build_cycle_map()

    # print("\nfinal cycle_map:\n{}"
    #       .format(pprint.pformat(cycle_map, sort_dicts=True, indent=4, width=10, compact=False)))

    interesting_cycle_nr = [20, 60, 100, 140, 180, 220]
    interesting_cycle_strength = []
    for idx in interesting_cycle_nr:
        val_x = cycle_map.get(idx, 0)
        val_strength = idx * val_x
        interesting_cycle_strength.append(val_strength)

    for idx in range(len(interesting_cycle_nr)):
        print(f"{idx}: {interesting_cycle_nr[idx]} * {cycle_map.get(interesting_cycle_nr[idx], 0)}"
              f" => {interesting_cycle_strength[idx]}")

    result = sum(interesting_cycle_strength)

    return result


def find_solution_b():
    """

    """
    pix_lit = "#"
    pix_dark = "."
    row_len = 40
    row = ""

    for idx in range(240):
        if idx % row_len == 0:
            print(row)
            row = ""

        cycle_nr = idx + 1
        register_val = cycle_map.get(cycle_nr, -10)
        sprite = [register_val - 1, register_val, register_val + 1]

        pix_nr = idx % row_len
        if pix_nr in sprite:
            row += pix_lit
        else:
            row += pix_dark

    print(row)

    return False


# MAIN
def do_main():
    show_elapsed_time()

    print("read input")
    controlled_input_read()
    show_elapsed_time()

    # print(f"input_data({len(input_data)}):\n",
    #       pprint.pformat(input_data, sort_dicts=False, indent=3, width=100, compact=False))

    print("\n==================================================================================\n")

    result_a = find_solution_a()
    print(f"result_a: {result_a}")
    show_elapsed_time()

    print("\n==================================================================================\n")

    result_b = find_solution_b()
    print(f"result_b: {result_b}")
    show_elapsed_time()


if __name__ == "__main__":
    # execute only if run as a script
    do_main()
