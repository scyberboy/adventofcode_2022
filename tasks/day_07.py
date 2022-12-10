#!/usr/bin/env python
import os
import re
import sys
import time
from copy import deepcopy
from threading import Thread
from typing import Optional

# GLOBALS
input_data: list[str] = []
prev_time = time.process_time()
input_timeout = 5

# specific to day 7
directory_list = {}

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
def _get_node_by_path(nodes: list[dict], node_path: str) -> Optional[dict]:
    res = None

    # breadth first search
    for node in nodes:
        if node["path"] == node_path:
            return node

    # if no luck - go deep into each current level node's content
    for node in nodes:
        res = _get_node_by_path(node["content"], node_path)
        if res:
            break

    return res


def _construct_path(dir_sequence: list[str]) -> str:
    if len(dir_sequence) == 1:
        return "/"
    else:
        return "/" + "/".join(dir_sequence[1:])


def update_parent_sizes(nodes: list[dict], node):
    # exit condition
    if node["path"] == "/":
        return

    my_path = node["path"]
    my_size = node["size"]
    # print(f"UPS: enter - {my_path}({my_size})")
    parent_path = my_path.rsplit("/", 1)[0]
    if not parent_path:
        parent_path = "/"
    # print(f"UPS: parent_path - {parent_path}")
    parent = _get_node_by_path(nodes, parent_path)
    if parent:
        # print(f'UPS: found parent - {parent["path"]}({parent["size"]})')
        parent["size"] += my_size
        # print(f'UPS: new size set - {parent["path"]}({parent["size"]})')
        update_parent_sizes(nodes, parent)
    else:
        # print(f"UPS: no parent found - returning...")
        return


def _generate_dir_dict_(nodes: list[dict]) -> dict[str:int]:
    result = {}
    for node in nodes:
        if node["type"] == "d":
            result[node["path"]] = node["size"]
        result.update(_generate_dir_dict_(node["content"]))

    return result


def find_solution_a():
    """
    Find all the directories with a total size of at most 100000.
    What is the sum of the total sizes of those directories?
    """
    global input_data
    global directory_list

    type_f = "f"
    type_d = "d"
    pat_dir = r"dir"
    pat_file = r"\d+"

    node = {"path": "/",
            "type": "d",  # "f" or "d"
            "size": 0,
            "content": [],  # list of nodes
            }
    root_fs = [deepcopy(node)]
    root_node = root_fs[0]  # just an alias for quick access
    curr_node = root_node

    curr_dir_sequence = ["/"]
    prop_1 = ""

    # first line of input - skip it. root_fs is already initialized
    for line in input_data[1:]:

        # print(f"---------------------\n line: {pprint.pformat(line)}")

        # if COMMAND
        if line.startswith("$"):
            line = line[2:]

            # CD
            if line.startswith("cd"):
                if line.endswith(".."):
                    cd_up = True
                    cd_down = False
                    curr_label = ""
                else:  # cd <DIR>
                    cd_up = False
                    cd_down = True
                    curr_label = line.split(" ")[1]

            # LS
            elif line.startswith("ls"):
                continue
            else:
                raise BaseException(f"Unexpected command: {line}")

        # if DIR or FILE
        else:
            cd_up = False
            cd_down = False
            prop_1, curr_label = line.split(" ")

        # We've got the current data, let's process it

        prev_node = curr_node

        if cd_up:
            _ = curr_dir_sequence.pop()
        elif cd_down:
            curr_dir_sequence.append(curr_label)

        # print(f"curr_dir_sequence({len(curr_dir_sequence)}): {pprint.pformat(curr_dir_sequence)}")

        curr_node_path = _construct_path(curr_dir_sequence)
        # print(f"curr_node_path({len(curr_node_path)}): {pprint.pformat(curr_node_path)}")

        curr_node = _get_node_by_path(root_fs, curr_node_path)
        # print(f"curr_node(): {pprint.pformat(curr_node)}")

        if cd_up:
            # when we go up - update target(parent) folder's size with the one we're just exiting
            # print("\t going UP, so UPDATING {}'s size({}) with lower one {}({})"
            #       .format(curr_node['path'], curr_node['size'], prev_node['path'], prev_node['size']))
            curr_node["size"] += prev_node["size"]
            # print(f"\t UPDATED {curr_node['path']} size is now = {curr_node['size']}")

        if cd_up or cd_down:
            continue

        new_node = deepcopy(node)
        _path = _construct_path(curr_dir_sequence + [curr_label])
        _type = type_d if re.match(pat_dir, prop_1) else type_f
        _size = int(prop_1) if re.match(pat_file, prop_1) else 0

        new_node["path"] = _path
        new_node["type"] = _type
        new_node["size"] = _size

        curr_node["content"].append(new_node)
        curr_node["size"] += new_node["size"]

        # print(f"new_node: {pprint.pformat(new_node)}")

    # We need to update all parent's sizes up to "/" traversing the current chain
    update_parent_sizes(root_fs, curr_node)

    # print(f"FINAL root_fs:\n {pprint.pformat(root_fs, sort_dicts=False, indent=2, width=120, compact=False)}")

    # Now, generate directory list (indeed dict with name:size)
    candidates = _generate_dir_dict_(root_fs)
    # print(f"candidates: {pprint.pformat(candidates)}")

    # Let's now traverse and found what we need !!!
    dir_size_limit = 100000
    total_sum = 0

    for name, size in candidates.items():
        if size <= dir_size_limit:
            total_sum += size

    directory_list = deepcopy(candidates)
    # print(f"global directory_list: {pprint.pformat(directory_list)}")
    # print(f"total_sum: {pprint.pformat(total_sum)}")

    return total_sum


def find_solution_b():
    """
    Find the smallest directory that, if deleted, would free up enough space on the filesystem to run the update.
    What is the total size of that directory?
    """
    global directory_list

    total_fs_size = 70000000
    free_space_needed = 30000000
    current_root_fs_size = directory_list.get("/", 0)
    current_free_space = total_fs_size - current_root_fs_size
    space_to_free = free_space_needed - current_free_space

    # print(f"current_root_fs_size: {pprint.pformat(current_root_fs_size)}")
    # print(f"current_free_space: {pprint.pformat(current_free_space)}")
    # print(f"space_to_free: {pprint.pformat(space_to_free)}")

    sizes_for_deletion: list[int] = []
    for name, size in directory_list.items():
        if size >= space_to_free:
            sizes_for_deletion.append(size)

    sizes_for_deletion.sort()
    # print(f"sizes_for_deletion: {pprint.pformat(sizes_for_deletion)}")

    result = 0 if len(sizes_for_deletion) == 0 else sizes_for_deletion[0]
    return result


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
