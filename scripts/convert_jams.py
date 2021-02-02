"""
convert jams format

original format:
1 2 h 2
0 1 v 3
0 0 h 2
3 1 v 3
2 5 h 3
0 4 v 2
4 4 h 2
5 0 v 3

new format:
bb...g
a..c.g
axxc.g
a..c..
e...ff
e.ddd.

explanation of original format:
x = col 1, row 2, horizontal 2
a = col 0, row 1, vertical 3
b = col 0, row 0, horizontal 2
c = col 3, row 1, vertical 3
d = col 2, row 5, horizontal 3
e = col 0, row 4, vertical 2
f = col 4, row 4, horizontal 2
g = col 5, row 0, vertical 3

note: script only works for 6x6 grid
"""
import os
from string import ascii_lowercase


BASEDIR = os.path.dirname(os.path.realpath(__file__))
INPUT_DIR = f"{BASEDIR}/.."
OUTPUT_DIR = f"{BASEDIR}/../jams"


if __name__ == "__main__":

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(f"{INPUT_DIR}/jams.txt") as f:
        data = f.read()

    print("starting converting jams")

    # jam variables
    board = []
    title = ""
    index = None

    for line in data.splitlines():
        if line.startswith("Jam"):
            # start of jam entry
            # read from file
            board = [['.' for _ in range(6)] for _ in range(6)]
            title = line.replace("-", "_").lower().strip()
            index = None

        elif line.startswith("."):
            # end of jam entry
            # write to file
            with open(f"{OUTPUT_DIR}/{title}.txt", 'w') as f:
                f.write('\n'.join(''.join(line) for line in board))

        elif line.startswith("6"):
            # grid size (must be size)
            continue
        
        else:
            car_name = 'x' if index is None else ascii_lowercase[index]
            index = index + 1 if index is not None else 0
            col, row, orient, size = line.split(' ')
            if orient == 'h': # horizontal
                for j in range(int(col), int(col)+int(size)):
                    board[int(row)][j] = car_name
            else: # vertical
                for i in range(int(row), int(row)+int(size)):
                    board[i][int(col)] = car_name
    
    print("finishing converting jams")
    print(f"see {os.path.dirname(os.path.realpath(OUTPUT_DIR))}")