#!/usr/bin/env python
import math
import os
import re
import sys
import time
from enum import Enum
from threading import Thread
from typing import Optional

# GLOBALS
input_data: list[list[str, int]] = []
prev_time = time.process_time()
input_timeout = 5


# day 9 specific
class Positions(Enum):
    OVERLAPPING = 0
    # means touching
    ADJACENT_STRAIGHT = 1  # means exactly above/below or next to (equal x or y)
    ADJACENT_DIAGONAL = 2
    # means not touching
    APART_STRAIGHT = 3
    APART_DIAGONAL = 4

    # generic for internal use
    ADJACENT = 5
    APART = 6
    STRAIGHT = 7
    DIAGONAL = 8


class Point:
    def __init__(self, coor_x: int = 0, coor_y: int = 0, direction: Optional[str] = None):
        self.x = coor_x
        self.y = coor_y
        self.from_direction = direction

    def __hash__(self):
        return hash(f"{self.x}, {self.y}")

    def __eq__(self, other) -> bool:
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def __lt__(self, other):
        if self.x > other.x:
            return True
        elif self.x == other.x:
            if self.y < other.y:
                return True
            else:
                return False
        else:
            return False

    def __str__(self):
        return f"[{self.__from_direction} => {self.x},{self.y}]"

    def __repr__(self):
        return f"Point{self.__str__()}"

    def distance_to(self, other):
        comp_1 = other.x - self.x
        comp_2 = other.y - self.y
        return math.sqrt(comp_1 * comp_1 + comp_2 * comp_2)

    def get_relative_position(self, other):
        # overlapping
        if self == other:
            return Positions.OVERLAPPING
        # adjacent/apart (straight/diagonal)
        else:
            diagonal = self._is_diagonal(other)
            adjacent = self._is_adjacent(other)
            # print(f"p1{self}, p2{other} - diagonal: {diagonal}, adjacent: {adjacent}")
            if adjacent and diagonal:
                return Positions.ADJACENT_DIAGONAL
            elif adjacent and not diagonal:
                return Positions.ADJACENT_STRAIGHT
            elif not adjacent and diagonal:
                return Positions.APART_DIAGONAL
            elif not adjacent and not diagonal:
                return Positions.APART_STRAIGHT
            else:
                raise BaseException(f"Can't determine relativity of p1({self}) and p2({other})")

    def _is_diagonal(self, other):
        if self == other:
            return False
        if self.x == other.x or self.y == other.y:
            return False
        else:
            return True

    def _is_straight(self, other):
        raise NotImplementedError()

    def _is_adjacent(self, other):
        distance = self.distance_to(other)
        return True if 0 < distance <= 1.42 else False

    @property
    def from_direction(self) -> Optional[str]:
        return self.__from_direction

    @from_direction.setter
    def from_direction(self, direction: Optional[str]):
        self.__from_direction = direction

    def going_to(self, position: 'Point') -> Optional[str]:
        if self == position:
            return None

        # DIAG
        if self._is_diagonal(position):
            ver_diff = max(position.x, self.x) - min(position.x, self.x)
            hor_diff = max(position.y, self.y) - min(position.y, self.y)

            more_hor = True if hor_diff > ver_diff else False

            if more_hor:
                if position.y < self.y:
                    return "L"
                elif position.y > self.y:
                    return "R"
            else:
                if position.x < self.x:
                    return "D"
                elif position.x > self.x:
                    return "U"

        # STRAIGHT
        else:
            if position.x < self.x:
                return "D"
            elif position.x > self.x:
                return "U"

            if position.y < self.y:
                return "L"
            elif position.y > self.y:
                return "R"


visited_by_tail: list[Point] = []

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
        direction, steps = line.strip().split()
        elem = [direction, int(steps)]
        input_data.append(elem)

    # print("reading input... END")


def controlled_input_read():
    read_input_thread = Thread(target=read_input, daemon=True, )
    read_input_thread.start()
    read_input_thread.join(timeout=input_timeout)
    if read_input_thread.is_alive():
        print(f"Timeout limit ({input_timeout} sec.) reached - exiting")
        sys.exit(1)


def add_unique(bucket: list, elem: object):
    if elem not in bucket:
        bucket.append(elem)


# SOLUTIONS
def calculate_new_position(position: Point, direction: str, steps: int) -> Point:
    new_x = position.x
    new_y = position.y
    if direction == "U":
        new_x += steps
    elif direction == "D":
        new_x -= steps
    elif direction == "L":
        new_y -= steps
    elif direction == "R":
        new_y += steps
    else:
        raise BaseException(f"Bad direction/steps given: {direction} -> {steps}")

    return Point(new_x, new_y, direction)


def generate_tail_positions(tail_position: Point, head_position: Point) -> list[Point]:
    positions: list[Point] = [tail_position]

    relativity = tail_position.get_relative_position(head_position)
    # print(f"GTP tail_position: {tail_position}")
    # print(f"GTP head_position: {head_position}")
    # print(f"GTP relativity: {relativity}")

    # if overlapping or adjacent already - no moves to keep-up
    if relativity in [Positions.OVERLAPPING, Positions.ADJACENT_STRAIGHT, Positions.ADJACENT_DIAGONAL]:
        return positions

    going_towards = tail_position.going_to(head_position)
    # directions = [head_position.from_direction, tail_position.from_direction]
    # directions = [going_towards, head_position.from_direction, tail_position.from_direction]
    directions = [going_towards]
    # directions = [going_towards, head_position.from_direction]

    from_x = tail_position.x
    from_y = tail_position.y
    to_x = head_position.x
    to_y = head_position.y
    target_x = head_position.x
    target_y = head_position.y

    if relativity in [Positions.APART_DIAGONAL]:
        abs_diff_x = abs(from_x - target_x)
        if abs_diff_x > 1:
            target_x = target_x - 1 if target_x > from_x else target_x + 1

        abs_diff_y = abs(from_y - target_y)
        if abs_diff_y > 1:
            target_y = target_y - 1 if target_y > from_y else target_y + 1

    # BUG 01
    # head_position: [U => 1,4]
    # tail_position: [R => 0,2]
    # GTP tail_position: [R => 0,2]
    # GTP head_position: [U => 1,4]
    # GTP relativity: Positions.APART_DIAGONAL
    # POSSIBLE tail_positions: []

    # BUG 02
    # head_position: [R => 2,2]
    # tail_position: [None => 0,0]
    # GTP tail_position: [None => 0,0]
    # GTP head_position: [R => 2,2]
    # GTP relativity: Positions.APART_DIAGONAL
    # POSSIBLE tail_positions: [Point[None => 0,0], Point[R => 2,1]]

    # BUG 03
    # GTP tail_position: [D => 9,0]
    # GTP head_position: [D => 7,-23]
    # GTP relativity: Positions.APART_DIAGONAL
    # target_x -> 8
    # target_y -> -22
    # GTP positions: [Point[D => 9,0], Point[D => 8,-22]]

    # BUG 04
    # tail_position: [D => 2,0]
    # head_position: [D => -1,-20]
    # POSSIBLE tail_positions: [Point[D => 2,0], Point[L => 0,-1], Point[L => 0,-2], Point[L => 0,-3], Point[L => 0,-4],
    # Point[L => 0,-5], Point[L => 0,-6], Point[L => 0,-7], Point[L => 0,-8], Point[L => 0,-9], Point[L => 0,-10],
    # Point[L => 0,-11], Point[L => 0,-12], Point[L => 0,-13], Point[L => 0,-14], Point[L => 0,-15], Point[L => 0,-16],
    # Point[L => 0,-17], Point[L => 0,-18], Point[L => 0,-19]]

    # print(f"GTP directions: {directions}")
    for direction in directions:
        if not direction:
            continue

        # head_position: [R => 0,4]
        # tail_position: [None => 0,0]
        # GTP tail_position: [None => 0,0]
        # GTP head_position: [R => 0,4]
        # GTP relativity: Positions.APART_STRAIGHT
        # POSSIBLE tail_positions: [Point[None => 0,0], Point[R => -1,1], Point[R => -1,2], Point[R => -1,3]]
        if direction == "U":
            from_x += 1
            # coor_y = min(to_y, from_y + 1) if to_y >= from_y else min(to_y, from_y - 1)
            for coor_x in range(from_x, to_x):
                elem = (Point(coor_x, target_y, direction))
                add_unique(positions, elem)
        elif direction == "D":
            from_x -= 1
            # coor_y = min(to_y, from_y + 1) if to_y >= from_y else min(to_y, from_y - 1)
            for coor_x in range(from_x, to_x, -1):
                elem = (Point(coor_x, target_y, direction))
                add_unique(positions, elem)
        elif direction == "L":
            from_y -= 1
            # coor_x = min(to_x, from_x + 1) if to_x >= from_x else min(to_x, from_x - 1)
            for coor_y in range(from_y, to_y, -1):
                elem = (Point(target_x, coor_y, direction))
                add_unique(positions, elem)
        elif direction == "R":
            from_y += 1
            # coor_x = min(to_x, from_x + 1) if to_x >= from_x else min(to_x, from_x - 1)
            for coor_y in range(from_y, to_y):
                elem = (Point(target_x, coor_y, direction))
                add_unique(positions, elem)
        else:
            raise BaseException(f"Bad direction given: {direction}")

    # print(f"GTP positions: {positions}")

    return positions


def simulate_rope(head_positions_w_direction: list[Point], tail_position: Point, nr_knots: int) -> list[list[Point]]:
    rope: list[list[Point]] = []
    # always start with (add) the initial tail position
    knot_tail_positions: list[Point] = []

    visualize_steps(head_positions_w_direction)

    # print(f"START - sim rope")

    for _ in range(nr_knots - 1):

        # DEBUG
        # if _ > 6:
        #     break

        print(f"sim rope, knot nr: {_}")
        # print(f"head_positions_w_direction: {head_positions_w_direction}")

        for head_position in head_positions_w_direction:
            # print(f"tail_position: {tail_position}")
            # print(f"head_position: {head_position}")

            tail_positions = generate_tail_positions(tail_position, head_position)
            # print(f"POSSIBLE tail_positions: {tail_positions}")
            for position in tail_positions:
                # BUG 04 - try having all steps, even duplicated
                # add_unique(knot_tail_positions, position)
                knot_tail_positions.append(position)
                # YEP, this helped !!! :)

            # set tail's new position - the last in list if there was any
            if len(tail_positions) > 0:
                tail_position = tail_positions[-1]

        if len(knot_tail_positions) > 0:
            add_unique(rope, knot_tail_positions.copy())

            # new head is first element
            head_positions_w_direction = rope[-1]

            # new tail - same as new head ( try 01 ) - NOK
            # (try 02) it's the previous head's first position - NOK
            # (try 03) - same as first new head
            tail_position = head_positions_w_direction[0]

            # if new tail is not adjacent anymore to the second new head - take the next one from previous iteration
            # new_relativity = tail_position.get_relative_position(head_positions_w_direction[1])
            # if new_relativity not in [Positions.ADJACENT_STRAIGHT, Positions.ADJACENT_DIAGONAL]:
            #     tail_position = rope[-1][1]

            del knot_tail_positions[:]

            visualize_steps(rope[-1])

        # width = max([len(elem) for elem in rope]) * 20 + 3
        # print("rope after knot nr.{} :\n{}"
        #       .format(_, pprint.pformat(rope, sort_dicts=False, indent=2, width=width, compact=False)))

    return rope


def init_head_positions_w_direction(position: Point) -> list[Point]:
    result: list[Point] = [position]

    for idx, (direction, steps) in enumerate(input_data):
        # DEBUG
        if idx > 2500:
            break

        new_position = calculate_new_position(position, direction, steps)
        result.append(new_position)
        position = new_position

    return result


def visualize_steps(steps: list[Point]):
    if len(steps) < 2:
        return

    sorted_steps = sorted(steps)
    # print(f"sorted_steps: {sorted_steps}")

    min_y = 1000000
    max_y = -1000000
    for elem in sorted_steps:
        y = elem.y
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y

    # print(f"min_y: {min_y}")
    # print(f"max_y: {max_y}")

    elem = sorted_steps[0]
    prev_x = elem.x
    prev_y = elem.y

    # print(f"x: {prev_x}, y: {prev_y}")

    line_str = f"{prev_x}\t: "
    empty_dots = "." * abs(prev_y - min_y)
    line_str += empty_dots
    line_str += "#"
    for elem in sorted_steps[1:]:
        x = elem.x
        y = elem.y

        # print(f"x: {x}, y: {y}")

        if x != prev_x:
            prev_x = x
            # fill it to the end
            empty_dots = "." * abs(max_y - prev_y)
            line_str += empty_dots
            print(line_str)

            prev_y = y

            line_str = f"{x}\t: "
            empty_dots = "." * abs(y - min_y)
            line_str += empty_dots
            line_str += "#"

        if y != prev_y:
            empty_dots = "." * abs(y - prev_y - 1)
            line_str += empty_dots
            line_str += "#"

            prev_y = y

    empty_dots = "." * abs(prev_y - max_y)
    line_str += empty_dots
    print(line_str)


def find_solution_a():
    """
    Simulate your complete hypothetical series of motions for two knots (H+T).
    How many positions does the tail of the rope visit at least once?
    """

    start_x = 0
    start_y = 0
    head_position = Point(start_x, start_y)
    tail_position = Point(start_x, start_y)

    head_positions_w_direction = init_head_positions_w_direction(head_position)
    # print(f"INIT head_positions_w_direction: {head_positions_w_direction}")

    nr_of_knots = 2

    result = simulate_rope(head_positions_w_direction, tail_position, nr_of_knots)

    tail_steps = []

    if len(result) > 0:
        # width = max([len(elem) for elem in result]) * 19 + 3
        # print(f"\t\t ====> \t\t {nr_of_knots} knots rope simulated:\n"
        #       f"{pprint.pformat(result, sort_dicts=False, indent=2, width=width, compact=False)}")
        tail_steps = set(result[-1])
        print(f"tail steps: {tail_steps}")

    visualize_steps(tail_steps)

    return len(tail_steps)


def find_solution_b():
    """
    Simulate your complete hypothetical series of motions for ten knots (H+T1+T2+...+T9).
    How many positions does the tail of the rope visit at least once?
    """

    start_x = 0
    start_y = 0
    head_position = Point(start_x, start_y)
    tail_position = Point(start_x, start_y)

    head_positions_w_direction = init_head_positions_w_direction(head_position)
    # print(f"INIT head_positions_w_direction: {head_positions_w_direction}")

    nr_of_knots = 10

    result = simulate_rope(head_positions_w_direction, tail_position, nr_of_knots)
    tail_steps = []

    if len(result) > 0:
        # width = max([len(elem) for elem in result]) * 19 + 3
        # print(f"\t\t ====> \t\t {nr_of_knots} knots rope simulated:\n"
        #       f"{pprint.pformat(result, sort_dicts=False, indent=2, width=width, compact=False)}")
        tail_steps = set(result[-1])
        print(f"\ntail steps: {tail_steps}")

    visualize_steps(tail_steps)

    return len(tail_steps)


# MAIN
def do_main():
    show_elapsed_time()

    print("read input")
    controlled_input_read()
    show_elapsed_time()

    # print(f"input_data({len(input_data)}):\n",
    #       pprint.pformat(input_data, sort_dicts=False, indent=3, width=100, compact=False))

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
