#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 15:42:30 2026

@author: jessie
"""
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

from itertools import permutations

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
        
    
    def read_bff(self, file):
        # read in .bff and assign attributes 
        
        # for block_grid, if it is an empty cell leave it as None type
        
        pass
    
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


        