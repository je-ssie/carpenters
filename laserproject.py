#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 15:42:30 2026.

@author: jessie and sabrina
"""


from itertools import permutations
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class Block:
    def __init__(self, position, fixed = False):
        self.position = position
        self.fixed = fixed

    def get_all_faces(self):
        by, bx = self.position
        x = bx * 2
        y = by * 2
        return [(x, y + 1), (x + 2, y + 1), (x + 1, y), (x + 1, y + 2)]

    def get_face(self, x, y):

        # block coordinates
        by, bx = self.position
        bx *= 2
        by *= 2

        # translate to grid coordinates to check face
        if (bx, by + 1) == (x, y):
            face = "left"
        elif (bx + 2, by + 1) == (x, y):
            face = "right"
        elif (bx + 1, by) == (x, y):
            face = "top"
        elif (bx + 1, by + 2) == (x, y):
            face = "bottom"
        else:
            face = None

        return face

    def set_position(self, new_pos):

        assert self.fixed != True, "Trying to move a fixed block."

        self.position = new_pos

    def __repr__(self):
        return f"{self.type}"


"""
(0,0) block -> left(0, 1) right(2, 1) top(1, 0) bottom(1, 2)
[0][1], (1, 0) block -> left(2, 1) right(4, 1) top(3, 0) bottom(3, 2)
[1][2], (2, 1) block -> left(4, 3) right(6, 3) top(5, 2) bottom(5, 4)
"""


class Reflect(Block):

    def __init__(self, position, fixed = False):
        super().__init__(position, fixed)
        self.type = "A"

    def laser_directions(self, vx, vy, face):
        # may need to change arguments based on how we code main part

        # to store new direction of laser after collision
        new_dir = []

        if (face == "top") or (face == "bottom"):
            new_dir.append((vx, -vy))
        elif (face == "left") or (face == "right"):
            new_dir.append((-vx, vy))

        return new_dir


class Refract(Block):

    def __init__(self, position, fixed = False):
        super().__init__(position, fixed)
        self.type = "C"

    def laser_directions(self, vx, vy, face):
        # may need to change arguments based on how we code main part

        # to store new direction of laser after collision
        # for refract block, one laser path stays in the same direction
        new_dir = [(vx, vy)]

        if (face == "top") or (face == "bottom"):
            new_dir.append((vx, -vy))
        elif (face == "left") or (face == "right"):
            new_dir.append((-vx, vy))

        return new_dir


class Opaque(Block):

    def __init__(self, position, fixed = False):
        super().__init__(position, fixed)
        self.type = "B"

    def laser_directions(self, vx, vy, face):

        # no laser path after collision with opaque block
        new_dir = None

        return new_dir


class Transparent(Block):

    def __init__(self, position, fixed = True):
        super().__init__(position, fixed)
        self.type = "x"

    def laser_directions(self, vx, vy, face):

        # to store new direction of laser after collision
        # laser passes through block
        new_dir = [(vx, vy)]

        return new_dir


class Puzzle:
    def __init__(self, file = None):
        self.file = file

        # may need to change certain attributes as we go along

        # 2D list representing block configuration
        # ex. [[Block obj, None, None],
        #      [None, None, Block obj]]
        self.block_grid = None

        # list of all blocks present in grid (including fixed, unfixed)
        self.blocks = []

        # a nested list  tracking path of laser(s) positions
        # ex. if there are two laser paths due to refract block:
        #     [[(1,0), (1,1), (1,2)],    laser path 1
        #      [(1,0), (1,1), (1,0)]]    laser path 2
        self.laser_pos = []

        # list of current laser directions (index aligned with laser_pos)
        self.laser_dir = []

        # target positions for solution (list of tuples)
        self.goal_coords = []

        # read in the file
        if file is not None:
            self.read_bff(file)

    def read_bff(self, file):
        # read in .bff and assign attributes
        # initialize attributes
        block_grid = []
        blocks = []
        laser_pos = []
        laser_dir = []
        goal_coords = []

        # for block_grid, if it is an empty cell leave it as None type

        with open(file, "r") as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
            # removing new lines
            lines = [line for line in lines if line != ""]

            # find the indices for the beginning and end of the grid
            grid_start = lines.index("GRID START")
            grid_stop = lines.index("GRID STOP")

            # split each row to get the 2D rep of the grid from the bff file
            block_grid = [line.split()
                          for line in lines[grid_start+1:grid_stop]]

            # loop through the block_grid and replace the string rep with objects
            # add all the blocks (reflect, refract, opaque) to the blocks list
            for i in range(len(block_grid)):   # row
                for j in range(len(block_grid[0])):   # column

                    block = block_grid[i][j]

                    if block == 'x':
                        b = Transparent([i, j], True)
                        block_grid[i][j] = b
                    elif block == 'o':
                        block_grid[i][j] = None
                    elif block == 'A':
                        b = Reflect([i, j], True)
                        block_grid[i][j] = b
                        blocks.append(b)
                    elif block == 'B':
                        b = Opaque([i, j], True)
                        block_grid[i][j] = b
                        blocks.append(b)
                    elif block == 'C':
                        b = Refract([i, j], True)
                        block_grid[i][j] = b
                        blocks.append(b)

            # loop through the rest of the file
            for line in lines[grid_stop+1:]:
                # split the line by space
                split_line = line.split()
                # if new line
                if split_line == []:
                    continue
                # add the specified amount of the block to the blocks list
                elif split_line[0] == 'A':
                    num_A = int(split_line[1])
                    blocks.append([Reflect(None, False) for i in range(num_A)])
                elif split_line[0] == 'B':
                    num_B = int(split_line[1])
                    blocks.append([Opaque(None, False) for i in range(num_B)])
                elif split_line[0] == 'C':
                    num_C = int(split_line[1])
                    blocks.append([Refract(None, False) for i in range(num_C)])

                # add the specified lasers to their respective laser lists
                # order of the list is ["L", x, y, vx, vy]
                elif split_line[0] == 'L':
                    laser_pos.append(
                        [(int(split_line[1]), int(split_line[2]))])
                    laser_dir.append(
                        (int(split_line[3]), int(split_line[4])))

                # add the specified points lasers need to intersect
                elif split_line[0] == 'P':
                    goal_coords.append(
                        (int(split_line[1]), int(split_line[2])))

            # update attributes
            self.block_grid = [row[:] for row in block_grid]
            self.blocks = blocks[:]
            self.laser_pos = [laser[:] for laser in laser_pos]
            self.laser_dir = laser_dir[:]
            self.goal_coords = goal_coords[:]

    def get_configurations(self):
        # available cells in the block grid to place a block
        avail_pos = []

        for i in range(len(self.block_grid[0])):
            for j in range(len(self.block_grid)):
                if self.block_grid[j][i] is None:
                    avail_pos.append((i, j))

        # get all possible permutation of movable blocks
        movable = 0
        for block in self.blocks:
            if block.fixed == False:
                movable += 1
        return list(permutations(avail_pos, movable))

    def check_collision(self, pos):
        # check if current position collides with a block in game
        # TODO: what if it collides with 2 adjacent blocks ?
        
        x, y = pos
        
        for block in self.blocks:
            if block.type == "x":
                continue
            face = block.get_face(x, y)
            if face is not None:
                return block, face
        return None, None

    def check_boundary(self, position):
        # True if it is on edge, False if not
        
        x, y = position
        
        if x == 0 or y == 0:
            return True
        
        max_x = len(self.block_grid[0]) * 2
        max_y = len(self.block_grid) * 2
        
        if x == max_x or y == max_y:
            return True

        return False

    def check_solved(self, laser_pos):
        all_laser_pos = set()

        # add all the coordinates from all laser paths into one set
        for path in laser_pos:
            for coord in path:
                all_laser_pos.add(coord)

        # check if all goal coordinates are present in laser_pos
        for coord in self.goal_coords:
            if coord not in all_laser_pos:
                return False
        return True

    def solve_puzzle(self):
        # all permutations of block placements
        # TODO: deal with duplicate configs
        configs = self.get_configurations()

        # list of movable blocks
        movable = [block for block in self.blocks if block.fixed == False]

        for config in configs:

            
            # update block positions
            for i in range(len(config)):
                self.movable[i].set_position(config[i])

            # do laser tracing
            laser_pos, laser_dir = self.laser_trace()

            # if this configuration solves the puzzle
            if self.check_solved(laser_pos):
                # update self.laser_pos, self.laser_dir
                self.laser_pos = laser_pos
                self.laser_dir = laser_dir
                return True
        
        print("No solution found.")
        return False
    
    def laser_trace(self):
        # make copy of position and direction
        laser_pos = [pos[:] for pos in self.laser_pos]
        laser_dir = self.laser_dir[:]
        
        complete = False
        
        count = 0 # delete later for debugging
        
        while not complete:
            if count > 10: 
                return 
            for i in range(len(laser_pos)):

                # for a laser that reached edge of grid, the direction will be None
                if laser_dir[i] is not None:
                    cur_pos = laser_pos[i][-1]
                    vx, vy = laser_dir[i]
                    next_pos = (cur_pos[0] + vx, cur_pos[1] + vy)
                    laser_pos[i].append(next_pos)

                    if self.check_boundary(next_pos):
                        laser_dir[i] = None

                    block, face = self.check_collision(next_pos)

                    # if collision occurred
                    if block is not None:
                        print(block.type, next_pos, face)
                        new_dir = block.laser_directions(vx, vy, face)
                        # update direction based on type of block
                        if block.type == "A":
                            laser_dir[i] = new_dir[0]
                        elif block.type == "B":
                            laser_dir[i] = None
                        elif block.type == "C":
                            laser_pos.append(laser_pos[i][:])
                            laser_dir.append(new_dir[1])
                            
            if count < 10: 
                print(laser_pos)

            # check if all lasers reached the end
            complete = all(d is None for d in laser_dir)
            count += 1
            
        return laser_pos, laser_dir
        

    def __str__(self):
        # might delete, feels useless
        grid_str = ""   # initialize str for grid
        
        for row in self.block_grid:   # loop through all blocks in the grid
            row_str = ""   # intialize str for row
            
            for col in row:   # add o for empty space or type of block
                if col is None:
                    row_str += "o "
                else:
                    row_str += f"{col.type} "
                    
            grid_str += row_str.strip() + "\n"   # add row to grid
            
        return grid_str

    def draw_puzzle(self, solved=False):
        fig, ax = plt.subplots()

        rows = len(self.block_grid)
        cols = len(self.block_grid[0])

        # plot grid lines
        for i in range(rows + 1):
            ax.plot([0, cols * 2], [i * 2, i * 2], linewidth=5, color="gray",
                    zorder=1)
        for j in range(cols + 1):
            ax.plot([j * 2, j * 2], [0, rows * 2], linewidth=5, color="gray",
                    zorder=1)

        # plot blocks
        for i in range(rows):
            for j in range(cols):
                b = self.block_grid[i][j]   # get the block at that coordinate

                if b is not None:   # if there is a block present
                    if b.type == "A":   # reflect
                        color = "whitesmoke"
                        line_color = 'black'
                        order = 2
                    elif b.type == "B":   # opaque
                        color = 'dimgrey'
                        line_color = 'black'
                        order = 2
                    elif b.type == "C":   # refract
                        color = 'lightgrey'
                        line_color = 'black'
                        order = 2
                    elif b.type == "x":   # block not allowed
                        color = 'gray'
                        line_color = 'gray'
                        order = 1

                    rect = patches.Rectangle((j * 2, (rows - i - 1) * 2), 2, 2,
                                             linewidth=5,
                                             edgecolor=line_color,
                                             facecolor=color, zorder=order)

                else:
                    color = 'darkgrey'
                    rect = patches.Rectangle((j * 2, (rows - i - 1) * 2), 2, 2,
                                             linewidth=5, edgecolor="gray",
                                             facecolor=color)
                ax.add_patch(rect)

        # plot goal coordinates
        x_goal = [coords[0] for coords in self.goal_coords]
        y_goal = [rows * 2 - coords[1] for coords in self.goal_coords]

        ax.scatter(x_goal, y_goal, color="black", s=100, zorder=3)

        # plot laser starting points
        # for i, pos in enumerate(self.laser_pos):
        #     x = [p[0] for p in pos]
        #     y = [rows * 2 - p[1] for p in pos]

        #     ax.scatter(x, y, linewidth=2, color='red', zorder=4)

        # TODO: need to add laser directions (how to account for diverging paths???)
        for i, path in enumerate(self.laser_pos):
            x = [p[0] for p in path]
            y = [rows * 2 - p[1] for p in path]
            ax.scatter(x, y, linewidth=2, color='white', zorder=4,
                       edgecolor="red", s=20)

            for j, pos in enumerate(path):
                # 
                if j != len(path) - 1:
                    next_pos = path[j+1]
                    ax.plot([pos[0], next_pos[0]],
                            [rows * 2 - pos[1], rows * 2 - next_pos[1]],
                            color="red", linewidth=2)
                # TODO: fix the logic for the last point in a path to extend 
                else:
                    ax.plot([pos[0], pos[0] - 1],
                            [rows * 2 - pos[1], rows * 2 - pos[1] + 1],
                            color="red", linewidth=2)

        # edit axes
        ax.set_xlim(-1, cols * 2 + 6)
        ax.set_ylim(-1, rows * 2 + 1)
        ax.set_aspect('equal')
        plt.axis('off')

        # add the legend
        legend_elements = [patches.Patch(facecolor='whitesmoke',
                                         edgecolor='black',
                                         label='Reflect block'),
                           patches.Patch(facecolor='dimgrey',
                                         edgecolor='black',
                                         label='Opaque block'),
                           patches.Patch(facecolor='lightgrey',
                                         edgecolor='black',
                                         label='Refract block'),
                           patches.Patch(facecolor='darkgrey',
                                         edgecolor='black',
                                         label='No block'),
                           patches.Patch(facecolor='gray',
                                         edgecolor='black',
                                         label='No block allowed')]
        ax.legend(handles=legend_elements, loc='center right')

        # TODO: add what blocks are available to use to a table

        # naming the plot and saving based on if puzzle is solved
        if solved:
            plt.savefig(f"{self.file} solved.png")
            plt.title(f"{self.file[:-4]} solved")

        # plt.savefig(f"{self.file}.png")
        plt.title(f"{self.file[:-4]}")

        plt.show()



if __name__ == "__main__":
    filenames = ['dark_1.bff', 'mad_1.bff', 'mad_4.bff', 'mad_7.bff',
                 'numbered_6.bff', 'showstopper_4.bff', 'tiny_5.bff',
                 'yarn_5.bff']
    p = Puzzle(filenames[1])
    p.block_grid = [[None, None, Refract((2, 0), True), None],
                    [None, None, None, Reflect((3, 1), True)],
                    [Reflect((0, 2), True), None, None, None],
                    [None, None, None, None]]
    p.laser_pos = [[(2, 7), (6, 3), (5, 2), (4, 1), (3, 0)], [(5, 2), (4, 3), (2, 5), (4, 7)]]
    p.draw_puzzle()
    # print(p)
