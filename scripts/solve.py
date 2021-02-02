"""
re-write a-star solve in python
"""
import copy
import os
from typing import List


BASEDIR = os.path.dirname(os.path.realpath(__file__))
INPUT_DIR = f"{BASEDIR}/../jams"


class Puzzle:
    """
    variables: grid, car_names, car_orientation, car_size, fixed_position
    functions: get_grid, get_num_cars, get_fixed_position,
               get_car_orientation, get_car_size
    """

    def __init__(self, grid: List[List[str]], car_names: set, car_orientation: dict,
                 car_size: dict, fixed_position: dict):
        
        self.grid = grid
        self.car_names = car_names
        self.car_orientation = car_orientation
        self.car_size = car_size
        self.fixed_position = fixed_position
        self.initial_node = None

        # for stats purpose
        self.search_count = 1

    def get_grid(self) -> List[List[str]]:
        """
        return puzzle grid
        """
        return self.grid

    def get_car_names(self) -> set:
        return self.car_names

    def get_car_orientation(self, car_name) -> bool:
        """
        return True if vertical, False otherwise
        """
        return self.car_orientation[car_name]

    def get_car_size(self, car_name) -> int:
        """
        return size of car
        """
        return self.car_size[car_name]

    def get_fixed_position(self, car_name) -> int:
        """
        return col if vertical, row otherwise
        """
        return self.fixed_position[car_name]

    def get_initial_node(self):
        return self.initial_node


def read_board(file) -> Puzzle:
    """
    for example, following are expected:
    
        num_cars = 8
        car_orientation = {'x': False, 'a': True, 'b': False, 'c': True,
                           'd': False, 'e': True, 'f': False, 'g': True}
        car_size = {'x': 2, 'a': 3, 'b': 2, 'c': 3, 'd': 3, 'e': 2, 'f': 2, 'g': 3}
        fixed_position = {'x': 2, 'a': 0, 'b': 0, 'c': 3, 'd': 5, 'e': 0, 'f': 4, 'g': 5}

        variable_position = {'x': 1, 'a': 1, 'b': 0, 'c': 1, 'd': 2, 'e': 4, 'f': 4, 'g': 0}
    """

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
    """
    variables: puzzle, var_pos
    methods: is_goal, expand
    """

    def __init__(self, puzzle: Puzzle, var_pos):
        self.puzzle = puzzle
        self.var_pos = var_pos

    def is_goal(self):
        """
        return True if puzzle solved, False otherwise
        """
        return self.var_pos['x'] == 5

    def expand(self):
        """
        NOTE: in the java code grid is transposed
        """

        # reference to grid
        grid = self.puzzle.get_grid()
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
            for np in range(p+car_size, 6):
                if orientation and grid[np][fp] != '.':  # VERTICAL: col is fixed
                    break
                if not orientation and grid[fp][np] != '.':  # HORIZONTAL: row fixed
                    break
                new_var_pos = copy.deepcopy(self.var_pos)
                new_var_pos[car_name] = np - car_size + 1
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

            # check for solution
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


if __name__ == "__main__":

    puzzle = read_board(f"{INPUT_DIR}/jam_1.txt")
    solver = AStar(puzzle)

    # jam_1.txt should be solvable with search count ~ 11587
    path = solver.solve()
    print(path)