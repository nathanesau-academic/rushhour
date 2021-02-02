"""
re-write a-star solve in python
"""
import copy
import os
from typing import List
from string import ascii_lowercase


BASEDIR = os.path.dirname(os.path.realpath(__file__))
INPUT_DIR = f"{BASEDIR}/../jams"


class Puzzle:
    """
    variables: grid, car_names, car_orientation, car_size, fixed_position
    functions: get_num_cars, get_car_orientation, get_car_size,
               get_fixed_position, get_initial_node
    """

    def __init__(self, initial_grid: List[List[int]], num_cars: int, car_orientation: list,
                 car_size: list, fixed_position: list):
        
        self.initial_grid = initial_grid
        self.num_cars = num_cars        
        self.car_orientation = car_orientation
        self.car_size = car_size
        self.fixed_position = fixed_position
        self.initial_node = None

        # for stats purpose
        self.search_count = 1

    def get_num_cars(self):
        """
        number of unique types of cars
        """
        return self.num_cars

    def get_car_orientation(self, v) -> bool:
        """
        return True if vertical, False otherwise
        """
        return self.car_orientation[v]

    def get_car_size(self, v) -> int:
        """
        return size of car
        """
        return self.car_size[v]

    def get_fixed_position(self, v) -> int:
        """
        return col if vertical, row otherwise
        """
        return self.fixed_position[v]

    def get_initial_node(self):
        return self.initial_node


def read_board(file) -> Puzzle:
    """
    for example, following are expected:
    
        num_cars = 8
        car_orientation = [False, True, False, True, False, True, False, True]
        car_size = [2, 3, 2, 3, 3, 2, 2, 3]
        fixed_position = [2, 0, 0, 3, 5, 0, 4, 5]

        variable_position = [1, 1, 0, 1, 2, 4, 4, 0]
    """

    with open(file) as f:
        data = f.read()
    
    grid = [list(line) for line in data.splitlines()]

    car_names = set([it for sl in grid for it in sl if it != '.'])
    car_numbers = dict((k, ascii_lowercase.index(k) + 1 if k != 'x' else 0) for k in car_names)
    num_cars = len(car_numbers)
    car_orientation = [0 for _ in range(num_cars)]
    car_size = [0 for _ in range(num_cars)]
    fixed_position = [0 for _ in range(num_cars)]
    variable_position = [0 for _ in range(num_cars)]

    # replace car_names with car_numbers
    for i in range(6):
        for j in range(6):
            if grid[i][j] == '.':
                grid[i][j] = -1
            else:
                grid[i][j] = car_numbers[grid[i][j]]

    for v in range(num_cars):

        squares = [(i, j) for i in range(6) for j in range(6) if grid[i][j] == v]
        # True if vertical, False otherwise
        orientation = False if any(s[1] != squares[0][1] for s in squares[1:]) else True
        size = len(squares)
        # col if vertical, row otherwise
        fp = squares[0][1] if orientation else squares[0][0]
        # row if vertical, col otherwise
        vp = squares[0][0] if orientation else squares[0][1]

        car_orientation[v] = orientation
        car_size[v] = size
        fixed_position[v] = fp
        variable_position[v] = vp

    # transpose grid
    grid = [*zip(*grid)]

    puzzle = Puzzle(grid, num_cars, car_orientation, car_size, fixed_position)

    state = State(puzzle, variable_position)
    initial_node = Node(state, 0, None)
    puzzle.initial_node = initial_node

    return puzzle


class State:
    """
    variables: puzzle, var_pos
    methods: is_goal, get_grid, expand
    """

    def __init__(self, puzzle: Puzzle, var_pos):
        self.puzzle = puzzle
        self.var_pos = var_pos

    def is_goal(self):
        """
        return True if puzzle solved, False otherwise
        """
        return self.var_pos[0] == 5

    def get_grid(self):
        """
        return grid with var_pos applied
        """
        grid = [[-1 for _ in range(6)] for _ in range(6)]
        for v in range(self.puzzle.get_num_cars()):
            orientation = self.puzzle.get_car_orientation(v)
            size = self.puzzle.get_car_size(v)
            fp = self.puzzle.get_fixed_position(v)
            if v == 0 and (self.var_pos[v] + size) > 6:
                size -= 1
            if orientation:  # vertical
                for d in range(size):
                    grid[fp][self.var_pos[v] + d] = v
            else:  # horizontal
                for d in range(size):
                    grid[self.var_pos[v] + d][fp] = v

        return grid

    def expand(self):
        """
        NOTE: in the java code grid is transposed
        """

        # reference to grid
        grid = self.get_grid()
        num_cars = self.puzzle.get_num_cars()
        new_states: List[State] = []
        
        for v in range(num_cars):
            
            p = self.var_pos[v]         
            fp = self.puzzle.get_fixed_position(v)
            orientation = self.puzzle.get_car_orientation(v)
            
            for np in range(p-1, -1, -1):
                if orientation and grid[fp][np] >= 0:  # VERTICAL: col is fixed
                    break
                if not orientation and grid[np][fp] >= 0:  # HORIZONTAL: row if fixed
                    break
                new_var_pos = copy.deepcopy(self.var_pos)
                new_var_pos[v] = np
                new_states.append(State(self.puzzle, new_var_pos))

            car_size = self.puzzle.get_car_size(v)
            
            for np in range(p+car_size, 7):
                if np < 6 and (orientation and grid[fp][np] >= 0):  # VERTICAL: col is fixed
                    break
                if np < 6 and (not orientation and grid[np][fp] >= 0):  # HORIZONTAL: row fixed
                    break
                if np == 6 and v != 0:
                    break
                new_var_pos = copy.deepcopy(self.var_pos)
                new_var_pos[v] = np - car_size + 1
                new_states.append(State(self.puzzle, new_var_pos))

        # for stats purpose
        self.puzzle.search_count += len(new_states)

        return new_states


class Node:
    """
    variables: state, depth, parent
    methods: expand
    """

    def __init__(self, state: State, depth: int, parent):
        self.state = state
        self.depth = depth
        self.parent = parent

    def expand(self) -> list():
        """
        expand this node, in other words, computes all nodes
        immediately reachable from this node and returns them
        as an array of nodes
        """
        new_states = self.state.expand()
        new_nodes = []

        for state in new_states:
            new_nodes.append(Node(state, self.depth + 1, self))

        return new_nodes


def find_node_in_nodelist(nodelist: List[Node], node: Node):
    """
    return index if node in nodelist, None otherwise
    """
    node_state = node.state
    for index, nl_node in enumerate(nodelist):
        nl_node_state = nl_node.state        
        if nl_node_state.var_pos == node_state.var_pos:
            return index
    return None


class AStar:
    """
    variables: puzzle
    methods: solve, keep_better_node_on_open_list
    """

    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    def build_path(self, current: Node):
        # +1 to include root node
        path = [None for _ in range(current.depth + 1)]
        node = current
        while node is not None:
            path[node.depth] = node.state
            node = node.parent
        return path

    def solve(self):

        initial_node = self.puzzle.get_initial_node()
        root = Node(initial_node.state, initial_node.depth, initial_node.parent)
        open: List[Node] = [root]
        closed: List[Node] = []

        while open:

            # sort nodes
            open = sorted(open, key=lambda it: it.depth)

            # pop from front
            current: Node = open.pop(0)

            if current.state.is_goal():
                path = self.build_path(current)
                return path

            closed.append(current)

            for successor in current.expand():
                if find_node_in_nodelist(open, successor) is not None:
                    self.update_open(open, successor)
                elif find_node_in_nodelist(closed, successor) is None:
                    open.append(successor)
    
        # did not find a solution
        return None

    def update_open(self, open: List[Node], successor: Node):
        try:
            existing_index = find_node_in_nodelist(open, successor)
            existing = open[existing_index]
            if existing.depth > successor.depth:
                del open[existing_index]
                open.append(successor)
        except:  # successor is not part of open
            pass


def pretty_print_path():
    """
    print path using "car_name" -> left 2, etc.
    """
    pass


if __name__ == "__main__":

    puzzle = read_board(f"{INPUT_DIR}/jam_1.txt")
    solver = AStar(puzzle)

    path = solver.solve()
    print(f"final search_count: {solver.puzzle.search_count}")
    print(path)