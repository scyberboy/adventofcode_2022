#!/usr/bin/env python
import os
import pprint
import re
import sys
import time
from copy import deepcopy
from threading import Thread

# GLOBALS
input_data: list[str] = []
prev_time = time.process_time()
input_timeout = 5

# day 11 specific

MONKEY_INIT: list['Monkey'] = []
tmp_monkeys: list['Monkey'] = []

# This is the LCD (най-малко общо кратно) of all test divisors of monkeys in input
# I've stolen it directly from my friend Lyubo [https://github.com/lyubolp]
# Although I was figuring it out on intuitive level :)
MAGIC_CONSTANT = 9699690


# In our case product of the prime numbers up to 23 (incl.)
# From other publications, if you apply modulo of M to a number N and then apply K, the result doesn't change
# if M is multiple of K
# Thus we have set/list of Ks - our monkeys divisors
# Taking the product of the whole list guarantees that it will be a multiple to any of them ;)

# NB - Dunno if it's only for me, but interim results with the sample input didn't match the ones given :(


class Monkey:
    def __init__(self, new_items_list=[], new_inspection_rule="", new_throw_test="",
                 new_throw_test_divisor=1, new_throw_rule={}):
        self.__items: list[int] = new_items_list
        self.__inspection_rule: str = new_inspection_rule
        self.__throw_test: str = new_throw_test
        self.__throw_test_divisor: int = new_throw_test_divisor
        self.__throw_rule: dict[bool, int] = new_throw_rule
        self.__relief_action = "int(value / 3)"
        self.__nr_inspected = 0

    def __repr__(self):
        return "Monkey(" + self.__str__() + ")"

    def __str__(self):
        return ", ".join([str(elem) for elem in self.__dict__.values()])

    def do_turn(self):
        self.inspect_items()
        while len(self.__items) > 0:
            value = self.__items.pop(0)
            self.evaluate(value)

    def inspect_items(self):
        for idx, old in enumerate(self.__items):
            new = eval(self.__inspection_rule)
            self.__items[idx] = new
            # increase counter with every performed inspection
            self.__nr_inspected += 1

    def evaluate(self, value):
        # decrease worrying level
        new_value = self.perform_relief(value)
        # perform test
        result = self.perform_test(new_value)

        # throw based on result and new value
        self.throw_at(result, new_value)

    def perform_test(self, value) -> bool:
        # this works because the variable in the throw test is named 'value' ;)
        # thus it gets resolved by current locals()
        return eval(self.__throw_test)

    def throw_at(self, test_result: bool, value: int):
        target_monkey_idx = self.__throw_rule[test_result]
        tmp_monkeys[target_monkey_idx].add_item(value)

    def add_item(self, value: int):
        self.__items.append(value)

    def get_inspection_score(self):
        return self.__nr_inspected

    def perform_relief(self, value):
        return eval(self.__relief_action)

    def set_relief_action(self, new_action):
        self.__relief_action = new_action

    def set_inspection_score(self, param):
        self.__nr_inspected = param


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
        if line.startswith("Monkey"):

            # print(f"creating {line.strip()}")

            items_line = sys.stdin.readline().strip()
            tmp = items_line.split(": ")
            items = [int(elem) for elem in tmp[-1].split(", ")]

            inspection_rule_line = sys.stdin.readline().strip()
            inspection_rule = inspection_rule_line.split("= ")[-1]

            throw_test_line = sys.stdin.readline().strip()
            division_value = throw_test_line.split()[-1]
            throw_test = "value % {} == 0".format(division_value)

            throw_rule_dict = {True: -1, False: -1}
            throw_rule_line = sys.stdin.readline().strip()
            throw_target_true = int(throw_rule_line.split()[-1])
            throw_rule_line = sys.stdin.readline().strip()
            throw_target_false = int(throw_rule_line.split()[-1])
            throw_rule_dict[True] = throw_target_true
            throw_rule_dict[False] = throw_target_false

            # now construct the monkey
            new_monkey = Monkey(items, inspection_rule, throw_test, int(division_value), throw_rule_dict)

            # add it to global list of monkeys
            MONKEY_INIT.append(new_monkey)

        else:
            # the empty line between monkeys
            continue

        # print(f"Monkeys so far: {MONKEY}")

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
    Count the total number of times each monkey inspects items over 20 rounds.
    The level of monkey business in this situation can be found by multiplying inspection score of the two most active.
    What is the level of monkey business after 20 rounds of stuff-slinging simian shenanigans?
    """
    global tmp_monkeys

    nr_rounds = 20
    monkeys = deepcopy(MONKEY_INIT)
    tmp_monkeys = monkeys

    for _ in range(nr_rounds):
        for monkey in monkeys:
            monkey.do_turn()

    print(f"Monkeys after {nr_rounds} rounds:\n {pprint.pformat(monkeys)}")

    inspection_scores = [elem.get_inspection_score() for elem in monkeys]
    inspection_scores.sort()

    print(f"inspection_scores: {inspection_scores}")

    if len(inspection_scores) > 1:
        result = inspection_scores[-2] * inspection_scores[-1]
    else:
        result = -1

    return result


def find_solution_b():
    """
    Worry levels are no longer divided by three after each item is inspected;
    You'll need to find another way to keep your worry levels manageable.
    Starting again from the initial state in your puzzle input, what is the level of monkey business after 10000 rounds?
    """
    global tmp_monkeys

    nr_rounds = 10000
    monkeys = deepcopy(MONKEY_INIT)
    tmp_monkeys = monkeys

    # set new relief rule
    for monkey in monkeys:
        # monkey.set_relief_action("value")  # stays the same, so no relief
        monkey.set_relief_action("value % MAGIC_CONSTANT")

    for _ in range(0, nr_rounds):

        # print(f"================== round {_} ==================")
        for idx, monkey in enumerate(monkeys):
            monkey.do_turn()

    print(f"Monkeys after {nr_rounds} rounds:\n {pprint.pformat(monkeys)}")

    inspection_scores = [elem.get_inspection_score() for elem in monkeys]
    inspection_scores.sort()

    print(f"inspection_scores: {inspection_scores}")

    if len(inspection_scores) > 1:
        result = inspection_scores[-2] * inspection_scores[-1]
    else:
        result = -1

    return result


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
