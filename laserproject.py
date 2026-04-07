#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 15:42:30 2026.

@author: jessie and sabrina
"""


from itertools import combinations
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from collections import Counter


class Block:
    def __init__(self, position, fixed = False):
        self.position = position
        self.fixed = fixed

    def get_all_faces(self):
        by, bx = self.position
        x = bx * 2
        y = by * 2
        return {(x, y + 1): "left", 
                (x + 2, y + 1): "right", 
                (x + 1, y): "top", 
                (x + 1, y + 2): "bottom"}

    def set_position(self, new_pos):

        assert self.fixed != True, "Trying to move a fixed block."

        self.position = new_pos

    def __repr__(self):
        return f"{self.type}"


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

    def __init__(self, position, fixed=False):
        super().__init__(position, fixed)
        self.type = "B"

    def laser_directions(self, vx, vy, face):

        # no laser path after collision with opaque block
        new_dir = None

        return new_dir


class Transparent(Block):

    def __init__(self, position, fixed=True):
        super().__init__(position, fixed)
        self.type = "x"

    def laser_directions(self, vx, vy, face):

        # to store new direction of laser after collision
        # laser passes through block
        new_dir = [(vx, vy)]

        return new_dir


class Puzzle:
    def __init__(self, file=None):
        self.file = file

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
        
        self.block_lookup = {}

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

            # loop through block_grid and replace the string rep with objects
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
                    blocks += [Reflect(None, False) for i in range(num_A)]
                elif split_line[0] == 'B':
                    num_B = int(split_line[1])
                    blocks += [Opaque(None, False) for i in range(num_B)]
                elif split_line[0] == 'C':
                    num_C = int(split_line[1])
                    blocks += [Refract(None, False) for i in range(num_C)]

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
        avail_pos = []
        
        # check if a cell in block_grid is empty (None) and add to avail_pos
        for i in range(len(self.block_grid)):
            for j in range(len(self.block_grid[0])):
                if self.block_grid[i][j] is None:
                    avail_pos.append((i, j))
        
        # group movable blocks by type
        movable = [b for b in self.blocks if not b.fixed]
        type_counts = {}
        for block in movable:
            type_counts[block.type] = type_counts.get(block.type, 0) + 1
        
        # generate all valid configurations using helper function
        configs = []
        self._generate_configs(avail_pos, list(type_counts.items()), [], configs)
        
        return configs
    
    def _generate_configs(self, avail_pos, type_list, current, results):
        """
        a recursive helper function to generate all valid block placements.
        
        it works by placing one block type at a time. for each type, it tries
        all possible combinations of configurations, then recursively handles
        the remaining block types using leftover available positions.

        Parameters
        ----------
        avail_pos : list
            available positions that haven't been used yet.
        type_list : list
            remaining block types to place. Each item is a tuple (block_type, count) like ('A', 3).
        current : list
            positions chosen so far in this configuration.
        results : list
            accumulator list where complete configurations are stored.

        Returns
        -------
        None.

        """
        # base case: no types left to assign positions to
        # add configuration to results
        if not type_list:
            results.append(current[:])
            return
        
        # recursive case: place next block type blocks
        block_type, count = type_list[0]
        remaining_types = type_list[1:]
        
        for positions in combinations(avail_pos, count):
            
            # updated available positions after current configuration
            new_avail = [p for p in avail_pos if p not in positions]
            
            # recursive call to place the next block types
            self._generate_configs(new_avail, remaining_types, current + list(positions), results)
            
    def build_block_lookup(self):
        """
        Builds a dictionary of positions mapped to corresponding block and face.

        Returns
        -------
        None.

        """
        
        self.block_lookup = {}
        
        # for every block, we find the positions of their faces
        for block in self.blocks:
            if block.position is None or block.type == "x":
                continue
            
            # map laser coordinates to (block, face) pairs
            faces = block.get_all_faces()
            
            # build dictionary of (x, y): [(block, face), (block2, face2), ...]
            for coord, face in faces.items():
                if coord not in self.block_lookup:
                    self.block_lookup[coord] = []
                self.block_lookup[coord].append((block, face))

    def check_collision(self, pos, prev_pos):

        # check current position
        if pos not in self.block_lookup:
            return None, None
        
        for block, face in self.block_lookup[pos]:
            
            # only valid if previous position doesn't hit same block
            prev_hits_same = False
            if prev_pos in self.block_lookup:
                for prev_block, _ in self.block_lookup[prev_pos]:
                    if prev_block == block:
                        prev_hits_same = True
                        break
            
            if not prev_hits_same:
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
    
    def place_blocks(self):
        for block in self.blocks:
            x, y = block.position
            self.block_grid[x][y] = block

    def solve_puzzle(self):
        # all configurations possible of block placements
        configs = self.get_configurations()

        # list of movable blocks
        movable = [block for block in self.blocks if block.fixed is False]

        for config in configs:
        
            # update block positions
            for i, pos in enumerate(config):
                movable[i].set_position(pos)
            
            # update the block faces with this configuration for quick lookup
            self.build_block_lookup()

            # do laser tracing
            laser_pos, laser_dir = self.laser_trace()

            # if this configuration solves the puzzle
            if self.check_solved(laser_pos):
                # update self.laser_pos, self.laser_dir
                self.laser_pos = laser_pos
                self.laser_dir = laser_dir
                self.place_blocks()
                return True

        print("No solution found.")
        return False
    
    def laser_trace(self):
        laser_dir = self.laser_dir[:]
        laser_pos = []
        
        for i, pos in enumerate(self.laser_pos):
            vx, vy = laser_dir[i]
            # one step before the initial starting point
            laser_pos.append([(pos[0][0] - vx, pos[0][1] - vy)])

        # track (position, direction) states for each laser to detect loops
        laser_states = [set() for _ in laser_pos]
    
        complete = False
        
        while not complete:
    
            for i in range(len(laser_pos)):
                
                if laser_dir[i] is not None:
                    
                    vx, vy = laser_dir[i]
                    
                    cur_pos = laser_pos[i][-1]
                    
                    # check if this state was seen before (infinite loop)
                    state = (cur_pos, (vx, vy))
                    if state in laser_states[i]:
                        # stop this laser if it is looping
                        laser_dir[i] = None  
                        continue
                    
                    laser_states[i].add(state)
                    
                    next_pos = (cur_pos[0] + vx, cur_pos[1] + vy)
    
                    if self.check_boundary(next_pos) and len(laser_pos[i]) > 1:
                        laser_pos[i].append(next_pos)
                        laser_dir[i] = None
                        continue
    
                    block, face = self.check_collision(next_pos, cur_pos)

    
                    if face is not None:
                        if block is None:
                            laser_dir[i] = None
                        else:
                            new_dir = block.laser_directions(vx, vy, face)
                            laser_pos[i].append(next_pos)
                            
                            if block.type == "A":
                                laser_dir[i] = new_dir[0]
                            elif block.type == "B":
                                laser_dir[i] = None
                            elif block.type == "C":
                                laser_pos.append(laser_pos[i][:])
                                laser_dir.append(new_dir[1])
                                # new laser needs tracker
                                laser_states.append(set())  
                    else:
                        laser_pos[i].append(next_pos)
    
            complete = all(d is None for d in laser_dir)
            
        
        return [pos[1:] for pos in laser_pos], laser_dir

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
        fig, (ax, ax_table) = plt.subplots(1, 2,
                                           gridspec_kw={'width_ratios': [5, 1],})

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
                        color = "lightsteelblue"
                        line_color = 'black'
                        order = 2
                    elif b.type == "B":   # opaque
                        color = 'navy'
                        line_color = 'black'
                        order = 2
                    elif b.type == "C":   # refract
                        color = 'cornflowerblue'
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

        for i, path in enumerate(self.laser_pos):

            # plot the lasers position and paths
            for j, pos in enumerate(path):

                # converting to plotting coordinates
                x = pos[0]
                y = rows * 2 - pos[1]

                # plot laser positions
                if pos in self.goal_coords:   # laser goes through goal points
                    ax.scatter(x, y, c='white', zorder=4, edgecolor="red",
                               s=100)
                elif j == 0:   # starting laser position
                    ax.scatter(x, y, c='red', zorder=4, edgecolor="red",
                               s=100)
                else:   # all other laser positions
                    ax.scatter(x, y, c='white', zorder=4, edgecolor="red",
                               s=10)

                # draw line to the next point
                if j != len(path) - 1:
                    next_pos = path[j+1]
                    x_next = next_pos[0]
                    y_next = rows * 2 - next_pos[1]

                    ax.plot([x, x_next], [y, y_next], color="red", linewidth=2)
                # laser will extend past the last point in the path
                elif solved is False:
                    ax.plot([x, x - 2 * rows * - self.laser_dir[i][0]],
                            [y, y - 2 * rows * self.laser_dir[i][1]],
                            color="red", linewidth=2)
                elif self.check_boundary(path[j]) is True:
                    prev_pos = path[j-1]
                    x_prev, y_prev = prev_pos[0], rows * 2 - prev_pos[1]
                    x_dir = x - x_prev
                    y_dir = y - y_prev
                    ax.plot([x, x - 2 * rows * -x_dir],
                            [y, y - 2 * rows * -y_dir],
                            color="red", linewidth=2)

        # edit axes
        ax.set_xlim(-1, cols * 2 + 1)
        ax.set_ylim(-1, rows * 2 + 1)
        ax.set_aspect('equal')
        ax.axis('off')
        ax_table.axis('off')

        # add what blocks are to be used/are used to a table
        all_b = [blocks.type for blocks in self.blocks]
        cell_text = [('Reflect', all_b.count("A")),
                     ('Opaque', all_b.count("B")),
                     ('Refract', all_b.count("C"))]
        table = ax_table.table(cellText=cell_text,
                               colLabels=["Block", "Count"],
                               bbox=[-0.4, 0.65, 1.8, 0.3], cellLoc='center',
                               fontsize=10)
        table.scale(1.5, 1)

        # add the legend
        legend_elements = [patches.Patch(facecolor='lightsteelblue',
                                         edgecolor='black',
                                         label='Reflect block'),
                           patches.Patch(facecolor='navy',
                                         edgecolor='black',
                                         label='Opaque block'),
                           patches.Patch(facecolor='cornflowerblue',
                                         edgecolor='black',
                                         label='Refract block'),
                           patches.Patch(facecolor='darkgrey',
                                         edgecolor='gray',
                                         label='No block'),
                           patches.Patch(facecolor='gray',
                                         edgecolor='gray',
                                         label='No block allowed'),
                           Line2D([0], [0], color='red', lw=2,
                                  label='Laser Path'),
                           Line2D([0], [0], marker='o', color='w',
                                  markerfacecolor='red', markeredgecolor='red',
                                  markersize=8, label='Laser Start'),
                           Line2D([0], [0], marker='o', color='w',
                                  markerfacecolor='white',
                                  markeredgecolor='red',
                                  markersize=3, label='Laser Position'),
                           Line2D([0], [0], marker='o', color='w',
                                  markerfacecolor='black',
                                  markeredgecolor='black', markersize=8,
                                  label='Goal'),
                           Line2D([0], [0], marker='o', color='w',
                                  markerfacecolor='white',
                                  markeredgecolor='red',
                                  markersize=8, label='Laser Hits Goal')]

        ax_table.legend(handles=legend_elements, loc='upper center',
                        frameon=False,
                        bbox_to_anchor=(0.52, 0.65),
                        fontsize=9, handlelength=1,
                        handleheight=1)

        # naming the plot and saving based on if puzzle is solved
        title = self.file[:-4].split("_")

        if solved:
            plt.savefig(f"{self.file} solved.png")
            ax.set_title(f"{title[0].capitalize()}: {title[1]} Solution",
                         fontsize=15)
        else:
            ax.set_title(f"{title[0].capitalize()}: {title[1]}",
                         fontsize=15)

        plt.show()

if __name__ == "__main__":
    filenames = ['dark_1.bff', 'mad_1.bff', 'mad_4.bff', 'mad_7.bff',
                 'numbered_6.bff', 'showstopper_4.bff', 'tiny_5.bff',
                 'yarn_5.bff']
    p = Puzzle(filenames[4])
    p.draw_puzzle()
    p.solve_puzzle()
    p.draw_puzzle(solved=True)
