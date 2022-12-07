#!/usr/bin/env python
import os
import pprint
import re
import sys
import time
from threading import Thread

# GLOBALS
input_data: list[str] = []
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
    Find all the directories with a total size of at most 100000.
    What is the sum of the total sizes of those directories?
    """
    global input_data

    type_f = "f"
    type_d = "d"
    pat_dir = r"dir"
    pat_file = r"\d+"

    root_node = {"type": type_d,  # or "d"
                 "size": 0,
                 "content": {},  # of nodes...?
                 }
    root_fs = {"/": root_node}

    # fill in the root_fs
    curr_lvl = 0
    curr_cd_label = "/"
    curr_dir_sequence = []
    prop_1 = ""
    prop_2 = ""
    adding = True
    cd_up = False
    tmp = 0

    for line in input_data:

        print(f"line: {pprint.pformat(line)}")
        cd_up = False

        # if is command
        if line.startswith("$"):
            line = line[2:]
            # CD
            if line.startswith("cd"):
                if line.endswith("/"):
                    curr_lvl = 0
                    curr_cd_label = "/"
                    curr_dir_sequence = [curr_cd_label]
                    continue
                elif line.endswith(".."):
                    curr_lvl -= 1
                    curr_cd_label = curr_dir_sequence.pop()
                    cd_up = True
                    adding = False
                else:
                    curr_lvl += 1
                    curr_cd_label = line.split(" ")[-1]
                    curr_dir_sequence.append(curr_cd_label)
                    continue
            # LS
            elif line.startswith("ls"):
                adding = True
                continue
            else:
                raise BaseException(f"Unexpected command: {line}")

        # if is dir or file
        else:
            prop_1, prop_2 = line.split(" ")

        # We've got the current data, let's process it
        curr_node = root_fs

        print(f"curr_dir_sequence({len(curr_dir_sequence)}): {pprint.pformat(curr_dir_sequence)}")

        elem = None
        for elem in curr_dir_sequence:
            if "content" in curr_node:
                curr_node = curr_node["content"][elem]
            else:
                curr_node = curr_node[elem]

        print(f"curr_node({elem}): {pprint.pformat(curr_node)}")

        if cd_up:
            # update size
            last_node_size = curr_node["content"][curr_cd_label]["size"]
            print(f"last_node_size({curr_cd_label}) : {pprint.pformat(last_node_size)}")
            print(f"updating curr_node['size']({curr_node['size']})")
            curr_node["size"] += last_node_size
            print(f"new curr_node['size']({elem}): {curr_node['size']}")

        if not adding:
            continue

        new_node_name = ""
        new_node_type = ""
        new_node_size = 0
        new_node_content = {}

        # DIR
        if re.match(pat_dir, prop_1):
            new_node_name = prop_2
            new_node_type = type_d
            # FILE
        elif re.match(pat_file, prop_1):
            new_node_name = prop_2
            new_node_type = type_f
            new_node_size = int(prop_1)

        new_node = {"type": new_node_type,
                    "size": new_node_size,
                    "content": new_node_content,
                    }

        curr_node["content"][new_node_name] = new_node
        curr_node["size"] += new_node_size
        tmp = curr_node["size"]

        print(f"new_node({new_node_name}): {pprint.pformat(new_node)}")

        print(f"root_fs: {pprint.pformat(root_fs)}")

    # let's update the root_fs["/"] size with the last dir we were in
    root_fs["/"]["size"] = tmp

    print(f"FINAL root_fs: {pprint.pformat(root_fs)}")

    # Let's now traverse and found what we need !!!
    dir_size_limit = 100000
    total_sum = 0
    candidates = []
    curr_node = root_fs["/"]
    while True:

    return False


def find_solution_b():
    """
    How many characters need to be processed before the first start-of-message marker is detected?
    """

    return False


# MAIN
def do_main():
    show_elapsed_time()

    print("read input")
    controlled_input_read()
    show_elapsed_time()

    print(f"input_data({len(input_data)}):", input_data)

    result_a = find_solution_a()
    print(f"result_a: {result_a}")
    show_elapsed_time()

    result_b = find_solution_b()
    print(f"result_b: {result_b}")
    show_elapsed_time()


if __name__ == "__main__":
    # execute only if run as a script
    do_main()
