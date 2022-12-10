#!/usr/bin/env python
import itertools
import operator
import os
import re
import sys
import time
from threading import Thread

# GLOBALS
input_data: dict[int, dict[int, int]] = {}
prev_time = time.process_time()
input_timeout = 5

# day 8 specific
nr_elems_on_map = -1
limit_x = -1
limit_y = -1

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
    global nr_elems_on_map
    global limit_x
    global limit_y
    # print("reading input... START")

    row = 0
    column = 0
    for line in sys.stdin:
        column = 0
        input_data[row] = {}
        for char in line.strip():
            value = int(char)
            elem = {column: value}
            input_data[row].update(elem)
            column += 1
        row += 1

    limit_x = row
    limit_y = column
    nr_elems_on_map = row * column

    # print("reading input... END")


def controlled_input_read():
    read_input_thread = Thread(target=read_input, daemon=True, )
    read_input_thread.start()
    read_input_thread.join(timeout=input_timeout)
    if read_input_thread.is_alive():
        print(f"Timeout limit ({input_timeout} sec.) reached - exiting")
        sys.exit(1)


# SOLUTIONS

def are_all_smaller(value, candidates):
    result = all(map(operator.gt, itertools.repeat(value, len(candidates)), candidates))
    # print(f"value: {value}")
    # print(f"candidates: {candidates}")
    # print(f"result: {result}")

    return result


def is_visible(curr_x: int, curr_y: int) -> bool:
    # check all neighbours till the edge (UP, DOWN, LEFT, RIGHT)
    # if in any direction all are smaller than us - return True(visible)
    my_height = input_data[curr_x][curr_y]

    heights_up = [input_data[x][curr_y] for x in range(curr_x)]
    if are_all_smaller(my_height, heights_up):
        return True

    heights_down = [input_data[x][curr_y] for x in range(curr_x + 1, limit_x)]
    if are_all_smaller(my_height, heights_down):
        return True

    heights_left = [input_data[curr_x][y] for y in range(curr_y)]
    if are_all_smaller(my_height, heights_left):
        return True

    heights_right = [input_data[curr_x][y] for y in range(curr_y + 1, limit_y)]
    if are_all_smaller(my_height, heights_right):
        return True

    return False


def find_solution_a():
    """
    A tree is visible if all the other trees between it and an edge of the grid are shorter than it.
    How many trees are visible from outside the grid?
    """

    inner_nr_visible = 0
    total_checked = 0
    for row in range(1, limit_x - 1):
        for column in range(1, limit_y - 1):
            if is_visible(row, column):
                inner_nr_visible += 1
            total_checked += 1

    inner_nr_non_visible = total_checked - inner_nr_visible
    total_visible = nr_elems_on_map - inner_nr_non_visible

    return total_visible


def calculate_viewing_distance(height, heights) -> int:
    # starting with viewing distance 1
    # if in any direction there are bigger or same than us - stop increasing the distance
    distance = 0
    for neigh_height in heights:
        distance += 1
        if neigh_height >= height:
            break

    return distance


def calculate_scenic_score(curr_x: int, curr_y: int) -> int:
    # check all neighbours from me, outwards, till the edge (UP, DOWN, LEFT, RIGHT)
    # get all four viewing distances and multiply them to get the total scenic score

    my_height = input_data[curr_x][curr_y]

    heights_up = [input_data[x][curr_y] for x in reversed(range(curr_x))]
    distance_up = calculate_viewing_distance(my_height, heights_up)

    heights_down = [input_data[x][curr_y] for x in range(curr_x + 1, limit_x)]
    distance_down = calculate_viewing_distance(my_height, heights_down)

    heights_left = [input_data[curr_x][y] for y in reversed(range(curr_y))]
    distance_left = calculate_viewing_distance(my_height, heights_left)

    heights_right = [input_data[curr_x][y] for y in range(curr_y + 1, limit_y)]
    distance_right = calculate_viewing_distance(my_height, heights_right)

    # print(f"distances for [{curr_x}][{curr_y}]: {distance_up}, {distance_down}, {distance_left}, {distance_right}")

    score = distance_up * distance_down * distance_left * distance_right
    # print(f"score for [{curr_x}][{curr_y}]: {score}")

    return score


def find_solution_b():
    """
    A tree's scenic score is found by multiplying together its viewing distance in each of the four directions
    What is the highest scenic score possible for any tree?
    """
    max_scenic_score = -1

    for row in range(1, limit_x - 1):
        for column in range(1, limit_y - 1):
            curr_score = calculate_scenic_score(row, column)
            if curr_score > max_scenic_score:
                max_scenic_score = curr_score
                # print(f"we've got max - {max_scenic_score}, for [{row}][{column}] = {input_data[row][column]}")

    return max_scenic_score


# MAIN
def do_main():
    show_elapsed_time()

    print("read input")
    controlled_input_read()
    show_elapsed_time()

    # print(f"input_data({len(input_data)}):\n",
    #       pprint.pformat(input_data, sort_dicts=False, indent=3, width=100, compact=False))
    # print(f"nr_elems_on_map: {nr_elems_on_map}")

    result_a = find_solution_a()
    print(f"result_a: {result_a}")
    show_elapsed_time()

    result_b = find_solution_b()
    print(f"result_b: {result_b}")
    show_elapsed_time()


if __name__ == "__main__":
    # execute only if run as a script
    do_main()
