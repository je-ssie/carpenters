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
    def __init__(self, position, fixed):
        self.position = position
        self.fixed = fixed

    def get_all_faces(self):
        bx, by = self.position
        return [(bx, by + 1), (bx + 2, by + 1), (bx + 1, by), (bx + 1, by + 2)]

    def get_face(self, x, y):

        # block coordinates
        bx, by = self.position

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
"""


class Reflect(Block):

    def __init__(self, position, fixed):
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

    def __init__(self, position, fixed):
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

    def __init__(self, position, fixed):
        super().__init__(position, fixed)
        self.type = "B"

    def laser_directions(self, vx, vy, face):

        # no laser path after collision with opaque block
        new_dir = None

        return new_dir


class Transparent(Block):

    def __init__(self, position, fixed):
        super().__init__(position, fixed)
        self.type = "x"

    def laser_directions(self, vx, vy, face):

        # to store new direction of laser after collision
        # laser passes through block
        new_dir = [(vx, vy)]

        return new_dir


class Puzzle:
    def __init__(self, file):
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

    def check_collision(self, x, y):
        # check if current position collides with a block in game
        # TODO: what if it collides with 2 adjacent blocks ?
        for block in self.blocks:
            face = block.get_face(x, y)
            if face is not None:
                return block, face
        return None, None

    def check_boundary(self, position):
        # TODO: check if position is on the boundary of the grid
        # True if it is on edge, False if not

        return

    def check_solved(self, laser_pos):
        # TODO: check if all of goal coordinates are present in laser_pos
        return

    def solve_puzzle(self):
        # all permutations of block placements
        # TODO: deal with duplicate configs
        configs = self.get_configurations()

        # list of movable blocks
        movable = [block for block in self.blocks if block.fixed == False]

        for config in configs:

            # make copy of position and direction
            laser_pos = [pos[:] for pos in self.laser_pos]
            laser_dir = self.laser_dir[:]

            complete = False
            # update block positions
            for i in range(len(config)):
                self.movable[i].set_position(config[i])

            # do laser tracing
            while not complete:
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
                            new_dir = block.laser_directions(vx, vy, face)
                            # update direction based on type of block
                            if block.type == "A":
                                laser_dir[i] = new_dir[0]
                            elif block.type == "B":
                                laser_dir[i] = None
                            elif block.type == "C":
                                laser_pos.append(laser_pos[i][:])
                                laser_dir.append(new_dir[1])

                # check if all lasers reached the end
                complete = all(d is None for d in laser_dir)

            # if this configuration solves the puzzle
            if self.solve_puzzle():
                # TODO: check what the format of the solution needs to be
                # update self.laser_pos, self.laser_dir
                return

        pass

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

    def draw_puzzle(self):
        fig, ax = plt.subplots()

        rows = len(self.block_grid)
        cols = len(self.block_grid[0])

        # plot grid lines
        for i in range(rows + 1):
            ax.plot([0, cols], [i, i], linewidth=0.5, color="black")
        for j in range(cols + 1):
            ax.plot([j, j], [0, rows], linewidth=0.5, color="black")

        # plot blocks
        for i in range(rows):
            for j in range(cols):
                b = self.block_grid[i][j]   # get the block at that coordinate

                if b is not None:   # if there is a block present
                    if b.type == "A":
                        color = 'blue'
                    elif b.type == "B":
                        color = 'darkgrey'
                    elif b.type == "C":
                        color = 'whitesmoke'
                    elif b.type == "x":
                        color = 'red'
                else:
                    color = 'dimgrey'

                rect = patches.Rectangle((j, rows - i - 1), 1, 1,
                                             linewidth=1, edgecolor="black", facecolor=color)
                ax.add_patch(rect)
        
        # plot goal coordinates
        x_goal = [coords[0] for coords in self.goal_coords]
        y_goal = [coords[1] for coords in self.goal_coords]

        ax.scatter(x_goal, y_goal, color = "gold")
        
        # plot lasers
        for i, pos in enumerate(self.laser_pos):
            x = [p[0] for p in pos]
            y = [p[1] for p in pos]
            
            ax.plot(x, y, linewidth=2, color='red')
            
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        #plt.axis('off')
        
        legend_elements = [patches.Patch(facecolor='blue', edgecolor='black', label='Reflect block'),
                           patches.Patch(facecolor='darkgrey', edgecolor='black', label='Opaque block'),
                           patches.Patch(facecolor='whitesmoke', edgecolor='black', label='Refract block'),
                           patches.Patch(facecolor='red', edgecolor='black', label='No block allowed'),
                           patches.Patch(facecolor='dimgrey', edgecolor='black', label='No block')]
        #ax.legend(handles=legend_elements, loc='lower right')
        
        plt.title(f"{self.file[:-4]}")
        
        plt.show()



if __name__ == "__main__":
    p = Puzzle('showstopper_4.bff')
    p.draw_puzzle()
