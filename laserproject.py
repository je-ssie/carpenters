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


class Block:
    """
    Base class representing a generic block on the puzzle grid.

    A Block has a position on the grid and may be fixed.
    Subclasses define specific behaviors when interacting with a laser.

    Attributes
    ----------
    position : tuple of int
        The (row, column) position of the block on the grid.
    fixed : bool
        Whether the block is fixed in place and cannot be moved.

    Methods
    -------
    get_all_faces()
        Returns the coordinates of the four faces (sides) of the block.
    set_position(new_pos)
        Updates the block's position if it is not fixed.
    """

    def __init__(self, position, fixed=False):
        """
        Initialize an instance of the Block class with a position.

        Parameters
        ----------
        position : tuple of int
            The (rw, column) position of the block on the grid..
        fixed : book, optional
            Whether the block is fixed in place and cannot be moved.
            The default is False.

        Returns
        -------
        None.

        """
        self.position = position
        self.fixed = fixed

    def get_all_faces(self):
        """
        Compute the coordinates of the four faces of the block.

        The block is treated as occupying a 2x2 unit in a finer grid,
        so each block position is scaled accordingly to determine face
        locations.

        Returns
        -------
        dict
            A dictionary mapping face coordinates (tuple) to face labels:
            "left", "right", "top", and "bottom".
        """
        by, bx = self.position

        # Scale block position to a finer grid representation.
        x = bx * 2
        y = by * 2

        # Map each face coordinate to its corresponding face label
        return {(x, y + 1): "left", (x + 2, y + 1): "right",
                (x + 1, y): "top", (x + 1, y + 2): "bottom"}

    def set_position(self, new_pos):
        """
        Set a new position for the block.

        Parameters
        ----------
        new_pos : tuple of int
            The new (row, column) position to assign to the block.

        Raises
        ------
        AssertionError
            If the block is fixed and cannot be moved.
        """
        # Prevent moving fixed block.
        assert self.fixed is not True, "Trying to move a fixed block."

        self.position = new_pos


class Reflect(Block):
    """
    Block that reflects a laser.

    A reflect block changes the direction of an incoming laser depending
    on which face it hits.

    Parameters
    ----------
    position : tuple of int
        The (row, column) position of the block.
    fixed : bool, optional
        Whether the block is fixed in place (default is False).

    Attributes
    ----------
    type : str
        Identifier for the block type ("A").

    Methods
    -------
    laser_directions(vx, vy, face)
        Returns the reflected laser direction(s) based on the incoming
        direction and the face of the block that is hit.
    """

    def __init__(self, position, fixed=False):
        """
        Initialize an instance of the Reflect block.

        Parameters
        ----------
        position : tuple of int
            The (row, column) position of the block.
        fixed : bool, optional
            Whether the block is fixed in place. The default is False.

        Returns
        -------
        None.

        """
        super().__init__(position, fixed)
        self.type = "A"

    def laser_directions(self, vx, vy, face):
        """
        Compute the outgoing laser direction(s) after hitting a reflect block.

        The laser is reflected depending which face it hits. Inverted vertical
        direction for top/bottom and inverted horizontal direction for
        left/right.

        Parameters
        ----------
        vx : int
            Horizontal component of the incoming laser direction.
        vy : int
            Vertical component of the incoming laser direction.
        face : str
            The face of the block that the laser hits ("top", "bottom", "left",
                                                       "right").

        Returns
        -------
        list of tuple
            A list containing the reflected laser direction as (vx, vy).
        """
        # Inialize a list to store new direction of laser after collision.
        new_dir = []

        if (face == "top") or (face == "bottom"):
            # Reflect vertically.
            new_dir.append((vx, -vy))
        elif (face == "left") or (face == "right"):
            # Reflect horizontally.
            new_dir.append((-vx, vy))

        return new_dir


class Refract(Block):
    """
    Block that both reflects a laser and lets it pass through.

    A refract block allows the laser to continue in its original direction
    while also producing a reflected beam.

    Parameters
    ----------
    position : tuple of int
        The (row, column) position of the block.
    fixed : bool, optional
        Whether the block is fixed in place (default is False).

    Attributes
    ----------
    type : str
        Identifier for the block type ("C").

    Methods
    -------
    laser_directions(vx, vy, face)
        Returns both the transmitted and reflected laser directions.
    """

    def __init__(self, position, fixed=False):
        """
        Initialize an instance of the Refract block.

        Parameters
        ----------
        position : tuple of int
            The (row, column) position of the block.
        fixed : bool, optional
            Whether the block is fixed in place (default is False).

        Returns
        -------
        None.

        """
        super().__init__(position, fixed)
        self.type = "C"

    def laser_directions(self, vx, vy, face):
        """
        Compute the outgoing laser directions after hitting a refract block.

        The laser produces two paths:
        1. The original direction (transmission)
        2. A reflected direction depending on the face it hits

        Parameters
        ----------
        vx : int
            Horizontal component of the incoming laser direction.
        vy : int
            Vertical component of the incoming laser direction.
        face : str
            The face of the block that the laser hits.

        Returns
        -------
        list of tuple
            A list of outgoing laser directions.
        """
        # Inialize a list to store new direction of laser after collision.
        # For refract block, one laser path stays in the same direction.
        new_dir = [(vx, vy)]

        # Add reflected direction based on face.
        if (face == "top") or (face == "bottom"):
            new_dir.append((vx, -vy))
        elif (face == "left") or (face == "right"):
            new_dir.append((-vx, vy))

        return new_dir


class Opaque(Block):
    """
    Block that absorbs a laser beam meaning no laser continues past this block.

    Parameters
    ----------
    position : tuple of int
        The (row, column) position of the block.
    fixed : bool, optional
        Whether the block is fixed in place (default is False).

    Attributes
    ----------
    type : str
        Identifier for the block type ("B").

    Methods
    -------
    laser_directions(vx, vy, face)
        Returns None since the laser is absorbed.
    """

    def __init__(self, position, fixed=False):
        """
        Initialize an instance of the Opaque block.

        Parameters
        ----------
        position : tuple of int
            The (row, column) position of the block.
        fixed : bool, optional
            Whether the block is fixed in place (default is False).

        Returns
        -------
        None.

        """
        super().__init__(position, fixed)
        self.type = "B"

    def laser_directions(self, vx, vy, face):
        """
        Determine laser behavior upon hitting an opaque block.

        The laser is fully absorbed and does not continue.

        Parameters
        ----------
        vx : int
            Horizontal component of the incoming laser direction.
        vy : int
            Vertical component of the incoming laser direction.
        face : str
            The face of the block that the laser hits.

        Returns
        -------
        None
            Indicates that no laser exits the block.
        """
        # No laser path after collision with opaque block.
        new_dir = None

        return new_dir


class Transparent(Block):
    """
    Block that allows a laser to pass through without changing direction.

    Parameters
    ----------
    position : tuple of int
        The (row, column) position of the block.
    fixed : bool, optional
        Whether the block is fixed in place (default is True).

    Attributes
    ----------
    type : str
        Identifier for the block type ("x").

    Methods
    -------
    laser_directions(vx, vy, face)
        Returns the unchanged laser direction.
    """

    def __init__(self, position, fixed=True):
        """
        Initialize an instance of the Transparent block.

        Parameters
        ----------
        position : tuple of int
            The (row, column) position of the block.
        fixed : bool, optional
            Whether the block is fixed in place (default is True).

        Returns
        -------
        None.

        """
        super().__init__(position, fixed)
        self.type = "x"

    def laser_directions(self, vx, vy, face):
        """
        Compute the laser direction after passing through a transparent block.

        The laser continues in the same direction.

        Parameters
        ----------
        vx : int
            Horizontal component of the incoming laser direction.
        vy : int
            Vertical component of the incoming laser direction.
        face : str
            The face of the block that the laser hits.

        Returns
        -------
        list of tuple
            A list containing the unchanged laser direction.
        """
        # Laser passes through block with direction unchanged.
        new_dir = [(vx, vy)]

        return new_dir


class Puzzle:
    """
    Represents a Laser puzzle.

    Includes the board configuration, blocks, lasers, and goal positions.
    Provides functionality to parse puzzle files, generate configurations,
    simulate laser paths, and solve the puzzle.

    Parameters
    ----------
    file : str, optional
        Path to the .bff file containing the puzzle definition.

    Attributes
    ----------
    file : str
        File path for the puzzle input.
    block_grid : list of list
        2D grid representing the board layout with Block objects or None.
    blocks : list
        List of all blocks (fixed and movable).
    laser_pos : list of list
        Nested list storing laser paths as coordinate sequences.
    laser_dir : list of tuple
        List of laser direction vectors corresponding to each laser path.
    goal_coords : list of tuple
        Coordinates that must be intersected by lasers to solve the puzzle.
    block_lookup : dict
        Maps coordinates to (block, face) pairs for fast collision lookup.

    Methods
    -------
    read_bff(file)
        Reads and parses a .bff puzzle file.
    get_configurations()
        Generates all valid placements of movable blocks.
    solve_puzzle()
        Attempts to solve the puzzle by testing configurations.
    laser_trace()
        Simulates laser movement through the board.
    check_solved(laser_pos)
        Checks if all goal coordinates are reached.
    draw_puzzle(solved=False)
        Visualizes the puzzle and optionally the solution.
    """

    def __init__(self, file=None):
        """
        Initialize an instance of the Puzzle object.

        Parameters
        ----------
        file : str, optional
            The file name. The default is None.

        Returns
        -------
        None.

        """
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

    def read_file_lines(self, file):
        """
        Read a file and returns non-empty lines.

        Parameters
        ----------
        file : str
            Path to the file.

        Returns
        -------
        list of str
            List of non-empty lines with newline characters removed.
        """
        with open(file, "r") as f:
            # Read in lines and strip the new line ending.
            lines = [line.rstrip('\n') for line in f.readlines()]

        # Removing new lines.
        return [line for line in lines if line != ""]

    def split_sections(self, lines):
        """
        Split file lines into grid section and remaining configuration data.

        Parameters
        ----------
        lines : list of str
            Lines from the puzzle file.

        Returns
        -------
        tuple
            (grid_lines, other_lines)
        """
        # Find the indices for the beginning and end of the grid.
        grid_start = lines.index("GRID START")
        grid_stop = lines.index("GRID STOP")

        # Get only the lines corresponding with the board grid.
        grid_lines = lines[grid_start+1:grid_stop]
        other_lines = lines[grid_stop+1:]
        return grid_lines, other_lines

    def parse_grid(self, grid_lines):
        """
        Convert grid text into a 2D block grid and initializes fixed blocks.

        Parameters
        ----------
        grid_lines : list of str
            Lines representing the grid.

        Returns
        -------
        tuple
            (block_grid, blocks)
        """
        # Split each row to get the 2D rep of the grid from the bff file.
        block_grid = [line.split() for line in grid_lines]

        # Initialize blocks list.
        blocks = []

        # Loop through block_grid and replace the string rep with objects.
        # Add all the blocks (reflect, refract, opaque) to the blocks list.
        for i in range(len(block_grid)):   # row
            for j in range(len(block_grid[0])):   # column
                block = block_grid[i][j]

                if block == 'x':
                    b = Transparent([i, j], True)
                    block_grid[i][j] = Transparent([i, j], True)
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

        return block_grid, blocks

    def parse_rest(self, lines, blocks):
        """
        Parse non-grid lines to extract movable blocks, lasers, and goals.

        Parameters
        ----------
        lines : list of str
            Remaining lines after grid section.
        blocks : list
            Existing list of fixed blocks.

        Returns
        -------
        tuple
            Updated (blocks, laser_pos, laser_dir, goal_coords)
        """
        # Initialize laser positions, laser directions, goal coordinates lists.
        laser_pos = []
        laser_dir = []
        goal_coords = []

        for line in lines:
            # Split the line by space.
            part = line.split()

            # If new line or not a block,laser point, or goal coordinate.
            if not part:
                continue

            indicator = part[0]

            # Add the specified amount of the block to the blocks list.
            if indicator in ('A', 'B', 'C'):
                count = int(part[1])
                block_dict = {'A': Reflect, 'B': Opaque, 'C': Refract}
                block = block_dict[indicator]
                blocks += [block(None, False) for _ in range(count)]

            # Add the specified lasers to their respective laser lists.
            # Order of the list is ["L", x, y, vx, vy].
            elif indicator == 'L':
                laser_pos.append([(int(part[1]), int(part[2]))])
                laser_dir.append((int(part[3]), int(part[4])))

            # Add the specified points lasers need to intersect
            elif indicator == 'P':
                goal_coords.append((int(part[1]), int(part[2])))

        return blocks, laser_pos, laser_dir, goal_coords

    def read_bff(self, file):
        """
        Read and parse a .bff puzzle file.

        Parameters
        ----------
        file : str
            The file name.

        Returns
        -------
        None.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the file contents are malformed.
        Exception
            For any unexpected errors during parsing.
        """
        try:
            # Read in .bff and assign attributes.
            lines = self.read_file_lines(file)

            # Get the lines corresponding with the board and other section.
            grid_lines, other_lines = self.split_sections(lines)

            # Get the block grid and blocks used.
            block_grid, blocks = self.parse_grid(grid_lines)

            # Get blocks, laser_pos, laser_dir, goal_coords.
            blocks, laser_pos, laser_dir, goal_coords = self.parse_rest(
                other_lines, blocks)

            # Update attributes with copies of the lists.
            self.block_grid = [row[:] for row in block_grid]
            self.blocks = blocks[:]
            self.laser_pos = [laser[:] for laser in laser_pos]
            self.laser_dir = laser_dir[:]
            self.goal_coords = goal_coords[:]

        except FileNotFoundError:
            print(f"File '{file}' could not be found.")

        except ValueError as ve:
            print(f"Error parsing '{file}': {ve}")

        except Exception as e:
            print(f"Unexpected error while reading '{file}': {e}")

    def get_configurations(self):
        """
        Generate all valid placements of movable blocks.

        Returns
        -------
        list
            List of configurations (each is a list of positions).
        """
        avail_pos = []

        # Check if a cell in block_grid is empty (None) and add to avail_pos.
        for i in range(len(self.block_grid)):
            for j in range(len(self.block_grid[0])):
                if self.block_grid[i][j] is None:
                    avail_pos.append((i, j))

        # Group movable blocks by type.
        movable = [b for b in self.blocks if not b.fixed]
        type_counts = {}
        for block in movable:
            type_counts[block.type] = type_counts.get(block.type, 0) + 1

        # Generate all valid configurations using helper function.
        configs = []
        self._generate_configs(avail_pos, list(
            type_counts.items()), [], configs)

        return configs

    def _generate_configs(self, avail_pos, type_list, current, results):
        """
        Generate all valid block placements.

        It works by placing one block type at a time. For each type, it tries
        all possible combinations of configurations, then recursively handles
        the remaining block types using leftover available positions.

        Parameters
        ----------
        avail_pos : list
            available positions that haven't been used yet.
        type_list : list
            remaining block types to place. Each item is a tuple (block_type,
            count) like ('A', 3).
        current : list
            positions chosen so far in this configuration.
        results : list
            accumulator list where complete configurations are stored.

        Returns
        -------
        None.

        """
        # Base case: no types left to assign positions to.
        # Add configuration to results.
        if not type_list:
            results.append(current[:])
            return

        # Recursive case: place next block type blocks.
        block_type, count = type_list[0]
        remaining_types = type_list[1:]

        for positions in combinations(avail_pos, count):

            # Updated available positions after current configuration.
            new_avail = [p for p in avail_pos if p not in positions]

            # Recursive call to place the next block types.
            self._generate_configs(
                new_avail, remaining_types, current + list(positions), results)

    def build_block_lookup(self):
        """
        Build a dictionary of positions mapped to corresponding block and face.

        Returns
        -------
        None.

        """
        self.block_lookup = {}

        # For every block, we find the positions of their faces.
        for block in self.blocks:
            if block.position is None or block.type == "x":
                continue

            # Map laser coordinates to (block, face) pairs.
            faces = block.get_all_faces()

            # Build dictionary of (x, y): [(block, face), (block2, face2), ...]
            for coord, face in faces.items():
                if coord not in self.block_lookup:
                    self.block_lookup[coord] = []
                self.block_lookup[coord].append((block, face))

    def check_collision(self, pos, prev_pos):
        """
        Check if a laser collides with a block at a given position.

        Parameters
        ----------
        pos : tuple
            Current laser position.
        prev_pos : tuple
            Previous laser position.

        Returns
        -------
        tuple
            (block, face) if collision occurs, otherwise (None, None).
        """
        # Check current position. No block at this coordinate.
        if pos not in self.block_lookup:
            return None, None

        for block, face in self.block_lookup[pos]:

            # Only valid if previous position doesn't hit same block.
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
        """
        Check if the position is at the edge of the board.

        Parameters
        ----------
        position : tuple of int
            The position in x, y.

        Returns
        -------
        bool
            Whether the position is at the edge of the board.

        """
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
        """
        Check if the board has been solved.

        Parameters
        ----------
        laser_pos : list of list
            Nested list storing laser paths as coordinate sequences.

        Returns
        -------
        bool
            Whether the board is solved. True if the board is solved.

        """
        all_laser_pos = set()

        # Add all the coordinates from all laser paths into one set.
        for path in laser_pos:
            for coord in path:
                all_laser_pos.add(coord)

        # Check if all goal coordinates are present in laser_pos.
        for coord in self.goal_coords:
            if coord not in all_laser_pos:
                return False
        return True

    def place_blocks(self):
        """
        Place all blocks onto the board grid based on their current positions.

        This method updates `self.block_grid` so that each block object is
        stored at its corresponding (row, col) position.

        Returns
        -------
        None
        """
        # Iterate through all blocks and assign them to their grid positions.
        for block in self.blocks:
            x, y = block.position
            self.block_grid[x][y] = block

    def solve_puzzle(self):
        """
        Solve the puzzle by trying all valid configurations of movable blocks.

        For each configuration:
        - Update positions of movable blocks
        - Rebuild lookup structures for fast collision detection
        - Simulate laser paths
        - Check if goal conditions are satisfied

        If a valid solution is found, update the puzzle state and return True.

        Returns
        -------
        bool
            True if a solution is found, False otherwise.
        """
        # All configurations possible of block placements.
        configs = self.get_configurations()

        # List of movable blocks.
        movable = [block for block in self.blocks if block.fixed is False]

        for config in configs:

            # Update block positions.
            for i, pos in enumerate(config):
                movable[i].set_position(pos)

            # Update the block faces with this configuration for quick lookup.
            self.build_block_lookup()

            # Do laser tracing.
            laser_pos, laser_dir = self.laser_trace()

            # If this configuration solves the puzzle.
            if self.check_solved(laser_pos):
                # Update self.laser_pos, self.laser_dir.
                self.laser_pos = laser_pos
                self.laser_dir = laser_dir
                self.place_blocks()
                return True

        print("No solution found.")
        return False

    def laser_trace(self):
        """
        Simulate laser propagation through the grid until all beams terminate.

        Handles:
        - Reflection, absorption, and refraction based on block types
        - Splitting of lasers (refract blocks)
        - Infinite loop detection using visited states
        - Boundary termination

        Returns
        -------
        list of list of tuple
            Laser paths (each path is a list of (x, y) positions)
        list of tuple or None
            Final directions of each laser (None if terminated)
        """
        # Copy initial directions to avoid changing original state.
        laser_dir = self.laser_dir[:]
        laser_pos = []

        for i, pos in enumerate(self.laser_pos):
            vx, vy = laser_dir[i]
            # One step before the initial starting point.
            laser_pos.append([(pos[0][0] - vx, pos[0][1] - vy)])

        # Track (position, direction) states for each laser to detect loops.
        laser_states = [set() for _ in laser_pos]

        complete = False

        while not complete:

            for i in range(len(laser_pos)):

                if laser_dir[i] is not None:

                    vx, vy = laser_dir[i]

                    cur_pos = laser_pos[i][-1]

                    # Check if this state was seen before (infinite loop).
                    state = (cur_pos, (vx, vy))
                    if state in laser_states[i]:
                        # Stop this laser if it is looping.
                        laser_dir[i] = None
                        continue

                    laser_states[i].add(state)

                    # Compute next position.
                    next_pos = (cur_pos[0] + vx, cur_pos[1] + vy)

                    # Stop if hitting boundary (after at least one move).
                    if self.check_boundary(next_pos) and len(laser_pos[i]) > 1:
                        laser_pos[i].append(next_pos)
                        laser_dir[i] = None
                        continue

                    # Check collision with block faces.
                    block, face = self.check_collision(next_pos, cur_pos)

                    if face is not None:
                        if block is None:
                            # Hit an invalid face.
                            laser_dir[i] = None
                        else:
                            # Compute new direction(s) from block interaction.
                            new_dir = block.laser_directions(vx, vy, face)
                            laser_pos[i].append(next_pos)

                            if block.type == "A":
                                laser_dir[i] = new_dir[0]
                            elif block.type == "B":
                                laser_dir[i] = None
                            elif block.type == "C":
                                laser_pos.append(laser_pos[i][:])
                                laser_dir.append(new_dir[1])
                                # New laser needs tracker.
                                laser_states.append(set())
                    else:
                        # No collision
                        laser_pos[i].append(next_pos)
            # Stop when all lasers are terminated
            complete = all(d is None for d in laser_dir)

        # Remove artificial starting point before returning
        return [pos[1:] for pos in laser_pos], laser_dir

    def draw_puzzle(self, solved=False):
        """
        Visualize the puzzle grid, blocks, laser paths, and goals.

        Parameters
        ----------
        solved : bool, optional
            If True, adjusts visualization to reflect completed solution state
            and saves the figure as a solved image.

        Returns
        -------
        None
        """
        fig, (ax, ax_table) = plt.subplots(1, 2,
                                           gridspec_kw={'width_ratios': [5, 1]}
                                           )

        rows = len(self.block_grid)
        cols = len(self.block_grid[0])

        # Draw grid lines.
        for i in range(rows + 1):
            ax.plot([0, cols * 2], [i * 2, i * 2], linewidth=5, color="gray",
                    zorder=1)
        for j in range(cols + 1):
            ax.plot([j * 2, j * 2], [0, rows * 2], linewidth=5, color="gray",
                    zorder=1)

        # Draw blocks.
        for i in range(rows):
            for j in range(cols):
                b = self.block_grid[i][j]   # Get the block at that coordinate.

                # Assign visual styles based on block type
                if b is not None:   # If there is a block present
                    if b.type == "A":   # Reflect
                        color = "lightsteelblue"
                        line_color = 'black'
                        order = 2
                    elif b.type == "B":   # Opaque
                        color = 'navy'
                        line_color = 'black'
                        order = 2
                    elif b.type == "C":   # Refract
                        color = 'cornflowerblue'
                        line_color = 'black'
                        order = 2
                    elif b.type == "x":   # Block not allowed
                        color = 'gray'
                        line_color = 'gray'
                        order = 1

                    rect = patches.Rectangle((j * 2, (rows - i - 1) * 2), 2, 2,
                                             linewidth=5,
                                             edgecolor=line_color,
                                             facecolor=color, zorder=order)

                else:
                    # Empty cell
                    color = 'darkgrey'
                    rect = patches.Rectangle((j * 2, (rows - i - 1) * 2), 2, 2,
                                             linewidth=5, edgecolor="gray",
                                             facecolor=color)
                ax.add_patch(rect)

        # Plot goal coordinates.
        x_goal = [coords[0] for coords in self.goal_coords]
        y_goal = [rows * 2 - coords[1] for coords in self.goal_coords]
        ax.scatter(x_goal, y_goal, color="black", s=100, zorder=3)

        # Plot laser positions and paths.
        for i, path in enumerate(self.laser_pos):
            for j, pos in enumerate(path):

                # Converting to plotting coordinates.
                x = pos[0]
                y = rows * 2 - pos[1]

                # Plot laser positions.
                if pos in self.goal_coords:   # Laser goes through goal points.
                    ax.scatter(x, y, c='white', zorder=4, edgecolor="red",
                               s=100)
                elif j == 0:   # Starting laser position.
                    ax.scatter(x, y, c='red', zorder=4, edgecolor="red",
                               s=100)
                else:   # All other laser positions.
                    ax.scatter(x, y, c='white', zorder=4, edgecolor="red",
                               s=10)

                # Draw connecting lines.
                if j != len(path) - 1:
                    next_pos = path[j+1]
                    x_next = next_pos[0]
                    y_next = rows * 2 - next_pos[1]

                    ax.plot([x, x_next], [y, y_next], color="red", linewidth=2)

                # Extend final laser.
                elif solved is False:
                    ax.plot([x, x + 2 * rows * self.laser_dir[i][0]],
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

        # Formatting.
        ax.set_xlim(-1, cols * 2 + 1)
        ax.set_ylim(-1, rows * 2 + 1)
        ax.set_aspect('equal')
        ax.axis('off')
        ax_table.axis('off')

        # Create the block count table.
        # Add what blocks are to be used/are used to a table.
        all_b = [blocks.type for blocks in self.blocks]
        cell_text = [('Reflect', all_b.count("A")),
                     ('Opaque', all_b.count("B")),
                     ('Refract', all_b.count("C"))]
        table = ax_table.table(cellText=cell_text,
                               colLabels=["Block", "Count"],
                               bbox=[-0.4, 0.6, 1.8, 0.3], cellLoc='center',
                               fontsize=10)
        table.scale(1.5, 1)

        # Add the legend
        legend_elements = [patches.Patch(facecolor='lightsteelblue',
                                         edgecolor='black',
                                         label='Reflect Block'),
                           patches.Patch(facecolor='navy',
                                         edgecolor='black',
                                         label='Opaque Block'),
                           patches.Patch(facecolor='cornflowerblue',
                                         edgecolor='black',
                                         label='Refract Block'),
                           patches.Patch(facecolor='darkgrey',
                                         edgecolor='gray',
                                         label='No Block'),
                           patches.Patch(facecolor='gray',
                                         edgecolor='gray',
                                         label='No Block Allowed'),
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
                        bbox_to_anchor=(0.52, 0.6),
                        fontsize=9, handlelength=1,
                        handleheight=1)

        # Naming the plot and saving based on if puzzle is solved.
        title = self.file[:-4].split("_")

        if solved:
            plt.savefig(f"{self.file[:-4]}_solved.png")
            ax.set_title(f"{title[0].capitalize()}: {title[1]} Solution",
                         fontsize=15)
        else:
            ax.set_title(f"{title[0].capitalize()}: {title[1]}",
                         fontsize=15)

        plt.show()

    def save_solution(self):
        """
        Save the solved puzzle in .bff format.

        Raises
        ------
        ValueError
            No solution has been given.

        Returns
        -------
        None.

        """
        # self.laser_dir will have None if it has been solved.
        if not self.laser_dir:
            raise ValueError("No solution to save. Run solve_puzzle() first.")

        filename = self.file[:-4] + "_solution.bff"

        with open(filename, "w") as f:

            # Write the board grid section.
            f.write("GRID START\n")

            # Iterate through the block grid and add each cell type.
            for row in self.block_grid:
                line = []
                for cell in row:
                    if cell is None:
                        line.append('o')
                    else:
                        line.append(cell.type)
                f.write(" ".join(line) + "\n")

            f.write("GRID STOP\n\n")

            # Count the movable counts (specified blocks).
            movable_counts = {'A': 0, 'B': 0, 'C': 0}

            # Iterate through all the blocks used.
            for block in self.blocks:
                # Add the block to the movable blocks if it is not fixed.
                if not block.fixed:
                    movable_counts[block.type] += 1

            # Write movable block counts.
            for btype in ['A', 'B', 'C']:
                if movable_counts[btype] > 0:
                    f.write(f"{btype} {movable_counts[btype]}\n")

            f.write("\n")

            # Write the laser positions and directions.
            for i, path in enumerate(self.laser_pos):

                # Need at least 2 points to infer direction.
                if len(path) < 2:
                    continue

                # Infer direction from first two positions in the path.
                x0, y0 = path[0]
                x1, y1 = path[1]

                vx = x1 - x0
                vy = y1 - y0

                # Starting point of the laser (first coordinate in path).
                start_x, start_y = path[0]

                # Add every point with that direction to the file.
                for j, pos in enumerate(path):
                    f.write(f"L {pos[0]} {pos[1]} {vx} {vy}\n")

            # Write the goal coordinates
            for coord in self.goal_coords:
                f.write(f"P {coord[0]} {coord[1]}\n")


if __name__ == "__main__":
    filenames = ['dark_1.bff', 'mad_1.bff', 'mad_4.bff', 'mad_7.bff',
                 'numbered_6.bff', 'showstopper_4.bff', 'tiny_5.bff',
                 'yarn_5.bff']
    # p = Puzzle(filenames[6])
    # # p.draw_puzzle()
    # p.solve_puzzle()
    # p.draw_puzzle(solved=True)
    # # p.save_solution()

    # p2 = Puzzle("tiny_5_solution.bff")
    # p2.draw_puzzle(solved=True)
    # print(p2.laser_dir)
    # print(p2.laser_pos)

    p3 = Puzzle('rat_9')
