"""
re-write a-star solve in python
"""
import copy
import os
from datetime import datetime
from typing import List
from string import ascii_lowercase


BASEDIR = os.path.dirname(os.path.realpath(__file__))
INPUT_DIR = f"{BASEDIR}/../jams"


class Puzzle:
    def __init__(self, initial_grid: List[List[int]], car_names: set, car_orientation: dict,
                 car_size: dict, fixed_position: dict):
        
        self.initial_grid = initial_grid
        self.car_names = car_names
        self.car_orientation = car_orientation
        self.car_size = car_size
        self.fixed_position = fixed_position
        self.initial_node = None

        # for stats purpose
        self.search_count = 1

    def get_car_names(self):
        return self.car_names

    def get_num_cars(self):
        return len(self.car_names)

    def get_car_orientation(self, car_name) -> bool:
        return self.car_orientation[car_name]

    def get_car_size(self, car_name) -> int:
        return self.car_size[car_name]

    def get_fixed_position(self, car_name) -> int:
        return self.fixed_position[car_name]

    def get_initial_node(self):
        return self.initial_node


def read_board(file) -> Puzzle:
    with open(file) as f:
        data = f.read()
    
    grid = [list(line) for line in data.splitlines()]

    car_names = set([it for sl in grid for it in sl if it != '.'])
    car_orientation = {}
    car_size = {}
    fixed_position = {}
    variable_position = {}

    for car_name in car_names:

        squares = [(i, j) for i in range(6) for j in range(6) if grid[i][j] == car_name]
        # True if vertical, False otherwise
        orientation = False if any(s[1] != squares[0][1] for s in squares[1:]) else True
        size = len(squares)
        # col if vertical, row otherwise
        fp = squares[0][1] if orientation else squares[0][0]
        # row if vertical, col otherwise
        vp = squares[0][0] if orientation else squares[0][1]

        car_orientation[car_name] = orientation
        car_size[car_name] = size
        fixed_position[car_name] = fp
        variable_position[car_name] = vp

    puzzle = Puzzle(grid, car_names, car_orientation, car_size, fixed_position)
    state = State(puzzle, variable_position)
    initial_node = Node(state, 0, None)
    puzzle.initial_node = initial_node

    return puzzle


class State:
    def __init__(self, puzzle: Puzzle, var_pos):
        self.puzzle = puzzle
        self.var_pos = var_pos

    def is_goal(self):
        return self.var_pos['x'] == 5

    def get_grid(self):
        grid = [['.' for _ in range(6)] for _ in range(6)]
        for car_name in self.puzzle.get_car_names():
            orientation = self.puzzle.get_car_orientation(car_name)
            size = self.puzzle.get_car_size(car_name)
            fp = self.puzzle.get_fixed_position(car_name)
            if car_name == 'x' and (self.var_pos[car_name] + size) > 6:
                size -= 1
            if orientation:  # vertical
                for d in range(size):
                    grid[self.var_pos[car_name] + d][fp] = car_name
            else:  # horizontal
                for d in range(size):
                    grid[fp][self.var_pos[car_name] + d] = car_name

        return grid

    def expand(self):
        grid = self.get_grid()
        new_states: List[State] = []
        
        for car_name in self.puzzle.get_car_names():
            
            p = self.var_pos[car_name]         
            fp = self.puzzle.get_fixed_position(car_name)
            orientation = self.puzzle.get_car_orientation(car_name)
            
            for np in range(p-1, -1, -1):
                if orientation and grid[np][fp] != '.':  # VERTICAL: col is fixed
                    break
                if not orientation and grid[fp][np] != '.':  # HORIZONTAL: row if fixed
                    break
                new_var_pos = copy.deepcopy(self.var_pos)
                new_var_pos[car_name] = np
                new_states.append(State(self.puzzle, new_var_pos))

            car_size = self.puzzle.get_car_size(car_name)
            
            for np in range(p+car_size, 7):
                if np < 6 and (orientation and grid[np][fp] != '.'):  # VERTICAL: col is fixed
                    break
                if np < 6 and (not orientation and grid[fp][np] != '.'):  # HORIZONTAL: row fixed
                    break
                if np == 6 and car_name != 'x':
                    break
                new_var_pos = copy.deepcopy(self.var_pos)
                new_var_pos[car_name] = np - car_size + 1
                new_states.append(State(self.puzzle, new_var_pos))

        # for stats purpose
        self.puzzle.search_count += len(new_states)

        return new_states


class Node:
    def __init__(self, state: State, depth: int, parent):
        self.state = state
        self.depth = depth
        self.parent = parent

    def expand(self) -> list():
        new_states = self.state.expand()
        new_nodes = []

        for state in new_states:
            new_nodes.append(Node(state, self.depth + 1, self))

        return new_nodes


def find_node(nodelist: List[Node], node: Node):
    node_state = node.state
    for index, nl_node in enumerate(nodelist):
        nl_node_state = nl_node.state        
        if nl_node_state.var_pos == node_state.var_pos:
            return index
    return None


class AStar:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    @staticmethod
    def build_path(current: Node):
        path = [None for _ in range(current.depth + 1)]  # +1 to include root node
        node = current
        while node is not None:
            path[node.depth] = node.state
            node = node.parent
        return path

    def solve(self):
        initial_node = self.puzzle.get_initial_node()
        root = Node(initial_node.state, initial_node.depth, initial_node.parent)
        open = [root]
        closed = []

        while open:
            open = sorted(open, key=lambda it: it.depth)
            current = open.pop(0)

            if current.state.is_goal():
                path = AStar.build_path(current)
                return path

            closed.append(current)

            for successor in current.expand():
                if find_node(open, successor) is not None:
                    self.update_open(open, successor)
                elif find_node(closed, successor) is None:
                    open.append(successor)
    
        return None  # did not find a solution

    def update_open(self, open: List[Node], successor: Node):
        try:
            existing_index = find_node(open, successor)
            existing = open[existing_index]
            if existing.depth > successor.depth:
                del open[existing_index]
                open.append(successor)
        except:  # successor is not part of open
            pass


def pretty_print_path():
    pass


if __name__ == "__main__":

    try:
        for jam in range(1, 41):
            puzzle = read_board(f"{INPUT_DIR}/jam_{jam}.txt")
            solver = AStar(puzzle)
            start_time = datetime.now()
            path = solver.solve()
            end_time = datetime.now()
            elapsed_time = (end_time - start_time)
            sc = solver.puzzle.search_count
            print(f"finished solve for jam {jam} (elapsed = {elapsed_time}, search_count = {sc}")
    except Exception as e:
        print(f"solve failed: {e}")
