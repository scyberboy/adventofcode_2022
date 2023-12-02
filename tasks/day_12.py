#!/usr/bin/env python
import os
import re
import sys
import time
from threading import Thread

import numpy as np

# GLOBALS
input_data: list[list[str]] = []
prev_time = time.process_time()
input_timeout = 5

# day 12 specifics
alpha_lower = "abcdefghijklmnopqrstuvwxyz"
heat_map: np.array = np.empty_like
nr_rows = -1
nr_cols = -1
start_point_name = "S"
start_point_coors: (int, int) = (-1, -1)
target_point_name = "E"
target_point_coors: (int, int) = (-1, -1)
curr_shortest_path_len = 100000
visited_nodes = set()

# Generic (sub-main)
filename = os.path.basename(__file__)
day_token = re.search(r"\d+", filename)
day_nr = day_token.group() if day_token else "unknown"
print(f"day_nr: {day_nr}")


def show_elapsed_time():
    global prev_time
    cur_time = time.process_time()
    diff = cur_time - prev_time
    prev_time = cur_time
    print(f"[{cur_time}] took: {diff} sec.")


# MISC
def read_input():
    global input_data
    # print("reading input... START")

    for line in sys.stdin:
        input_data.append([x for x in line.strip()])

    # print("reading input... END")


# READ INPUT
def controlled_input_read():
    read_input_thread = Thread(target=read_input, daemon=True, )
    read_input_thread.start()
    read_input_thread.join(timeout=input_timeout)
    if read_input_thread.is_alive():
        print(f"Timeout limit ({input_timeout} sec.) reached - exiting")
        sys.exit(1)


# SOLUTIONS


def get_neighs(curr_node: (int, int)) -> list[(int, int)]:
    neigh_offsets = [(0, 1), (1, 0), (-1, 0), (0, -1)]
    neighs = []
    for x_off, y_off in neigh_offsets:
        new_x, new_y = curr_node
        new_x += x_off
        new_y += y_off
        if 0 <= new_x < nr_rows and \
                0 <= new_y < nr_cols and \
                is_reachable(curr_node, (new_x, new_y)):
            neighs.append((new_x, new_y))

    return neighs


def is_reachable(from_node: (int, int), to_node: (int, int)) -> bool:
    from_name = heat_map[from_node]
    to_name = heat_map[to_node]

    # print(f"from_name: {from_name}")
    # print(f"to_name: {to_name}")
    if from_name != start_point_name:
        from_value = alpha_lower.index(from_name)
    else:
        from_value = -1

    if to_name == target_point_name:
        to_value = 26
    elif to_name == start_point_name:
        to_value = -1
    else:
        to_value = alpha_lower.index(to_name)

    # I'll rather need suitable candidates, then the reachable ones.
    # I don't need to go lower ever - so consider same or one level higher only !!!

    is_candidate = False
    if from_value == to_value or \
            from_value + 1 == to_value:
        is_candidate = True

    return is_candidate


def find_path_to_end(curr_path: list[(int, int)], curr_node: (int, int)) -> list[(int, int)]:
    global curr_shortest_path_len

    # print(f"find_path_to_end(), curr_shortest_path_len: {curr_shortest_path_len}")
    # print(f"find_path_to_end(), curr_path len: {len(curr_path)}")
    # print(f"find_path_to_end(), curr_path: {curr_path}")
    # print(f"find_path_to_end(), curr_node: {curr_node}")

    if len(curr_path) >= curr_shortest_path_len:
        return []

    # print(f"find_path_to_end(), curr_path len: {len(curr_path)}")
    # if len(curr_path) % 100 == 0:
    #     print(f"find_path_to_end(), curr_node: {curr_node}")
    #     print(f"find_path_to_end(), curr_path len: {len(curr_path)}")
    #     print(f"find_path_to_end(), curr_path: {curr_path}")

    # stop condition - we've reached the end (E)
    if curr_node == target_point_coors:
        print(f"find_path_to_end(), curr_node is END node !!!")
        return curr_path.copy()

    if curr_node in visited_nodes:
        return []

    visited_nodes.add(curr_node)

    paths_to_end = []
    next_path = []
    neighs = get_neighs(curr_node)
    # print(f"find_path_to_end(), neighs: {neighs}")
    for neigh in neighs:
        if neigh not in curr_path and \
                is_reachable(curr_node, neigh):
            # print(f"find_path_to_end(), next node: {neigh}")
            curr_path.append(neigh)
            if neigh == target_point_coors:
                print(f"find_path_to_end(), neigh is END node !!!")
                if len(curr_path) < curr_shortest_path_len:
                    print(f"find_path_to_end(), save it because it's shorter")
                    curr_shortest_path_len = len(curr_path)
                    return curr_path.copy()
                else:
                    print(f"find_path_to_end(), skip it because it's same or longer")
                    return []
            next_path = find_path_to_end(curr_path, neigh)
            if target_point_coors in next_path:
                # return next_path
                paths_to_end.append(next_path)
            else:
                curr_path.pop()

    # print(f"find_path_to_end(), paths_to_end: {paths_to_end}")
    # in paths_to_end we possibly have different paths to end - we want the shortest one
    sorted_stuff = sorted(paths_to_end, key=len)
    if len(sorted_stuff) > 0:
        # print(f"find_path_to_end(), sorted_stuff: {sorted_stuff}")
        return sorted_stuff[0]

    return next_path


def find_solution_a():
    """
    What is the fewest steps required to move from your current position
    to the location that should get the best signal?
    """
    all_paths_to_end: list[list[(int, int)]] = []

    neighs = get_neighs(start_point_coors)
    for neigh in neighs:
        curr_path: list[(int, int)] = [start_point_coors]
        if is_reachable(start_point_coors, neigh):
            curr_path.append(neigh)
            path_to_end = find_path_to_end(curr_path, neigh)
            if len(path_to_end) > 0:
                print(f"\tFOUND ({len(path_to_end)} nodes long) path_to_end:\n {path_to_end}")
                all_paths_to_end.append(path_to_end)

    print(f"nr of paths to end: {len(all_paths_to_end)}")
    print(f"all_paths_to_end: {all_paths_to_end}")

    # subtract one, because we need nr. of steps, not nr. of nodes (incl. S & E)
    return min([len(x) for x in all_paths_to_end]) - 1


def find_solution_b():
    """

    """

    return False


def set_map_poi_coors():
    global heat_map
    global start_point_coors
    global target_point_coors
    global nr_rows
    global nr_cols

    is_start_set = False
    is_target_set = False

    heat_map = np.array(input_data)
    nr_rows, nr_cols = heat_map.shape
    for x_coor in range(nr_rows):
        for y_coor in range(nr_cols):
            if heat_map[x_coor, y_coor] == start_point_name:
                start_point_coors = (x_coor, y_coor)
                is_start_set = True
            if heat_map[x_coor, y_coor] == target_point_name:
                target_point_coors = (x_coor, y_coor)
                is_target_set = True
            if is_start_set and is_target_set:
                break


def do_main():
    show_elapsed_time()

    print("read input")
    controlled_input_read()
    show_elapsed_time()

    # print(f"input_data({len(input_data)}):\n",
    #       pprint.pformat(input_data, sort_dicts=False, indent=3, width=100, compact=False))
    set_map_poi_coors()
    print(f"heat_map:\n {heat_map}")
    print(f"heat_map.shape: {heat_map.shape}")
    print(f"start_point_coors: {start_point_coors}")
    print(f"target_point_coors: {target_point_coors}")

    rec_limit = sys.getrecursionlimit()
    print(f"sys.getrecursionlimit(): {rec_limit}")

    new_rec_limit = 10000
    if rec_limit < new_rec_limit:
        print(f"Setting it to {new_rec_limit}")
        sys.setrecursionlimit(new_rec_limit)

    print("\n==================================================================================\n")

    result_a = find_solution_a()
    print(f"result_a: {result_a}")
    show_elapsed_time()

    print("\n==================================================================================\n")

    result_b = find_solution_b()
    print(f"result_b: {result_b}")
    show_elapsed_time()


# MAIN
if __name__ == "__main__":
    # execute only if run as a script
    do_main()
