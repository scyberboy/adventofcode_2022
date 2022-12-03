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

# [AX] -> rock
# [BY] -> paper
# [CZ] -> scissors
# (1 for Rock, 2 for Paper, and 3 for Scissors)
# (0 if you lost, 3 if the round was a draw, and 6 if you won)
my_score_map = {("A", "X"): 3,
                ("A", "Y"): 6,
                ("A", "Z"): 0,
                ("B", "X"): 0,
                ("B", "Y"): 3,
                ("B", "Z"): 6,
                ("C", "X"): 6,
                ("C", "Y"): 0,
                ("C", "Z"): 3,
                }
my_play_score_map = {"X": 1, "Y": 2, "Z": 3}
# part b - my play in each round is the outcome:
# X - should lose (0 points)
# Y - should draw (3 points)
# Z - should win (6 points)
my_play_map = {("A", "X"): "Z",
               ("A", "Y"): "X",
               ("A", "Z"): "Y",
               ("B", "X"): "X",
               ("B", "Y"): "Y",
               ("B", "Z"): "Z",
               ("C", "X"): "Y",
               ("C", "Y"): "Z",
               ("C", "Z"): "X",
               }


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

        opp_play, my_play = line.strip().split(" ")
        # if len(val) > 0:
        input_data.append((opp_play, my_play))

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
    What would your total score be if everything goes exactly according to your strategy guide (the input)?
    """
    total_score = 0
    for play in input_data:
        round_outcome_score = my_score_map.get(play)
        my_play_score = my_play_score_map.get(play[1])
        total_score += (round_outcome_score + my_play_score)

    return total_score


def find_solution_b():
    """
    Following the Elf's instructions for the second column,
    what would your total score be if everything goes exactly according to your strategy guide?
    """
    total_score = 0
    for opp_play, outcome in input_data:
        my_play = my_play_map.get((opp_play, outcome))
        round_outcome_score = my_score_map.get((opp_play, my_play))
        my_play_score = my_play_score_map.get(my_play)
        total_score += (round_outcome_score + my_play_score)

    return total_score


# MAIN
def do_main():
    show_elapsed_time()

    print("read input")
    controlled_input_read()
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
