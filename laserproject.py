#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 15:42:30 2026

@author: jessie
"""
class Block:
    def __init__(self, position):
        self.position = position
    
    def get_face(self, x, y):
        
        # block coordinates
        bx, by = position
        
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
            # delete this later
            print("Check formula something is wrong")
    
    def set_position(self, new_pos):
        self.position = new_pos


"""
(0,0) block -> left(0, 1) right(2, 1) top(1, 0) bottom(1, 2)
"""
        

class Reflect(Block):
    
    def __init__(self, position):
        super().__init__(position)
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
    
    def __init__(self, position):
        super().__init__(position)
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
    
    def __init__(self, position):
        super().__init__(position)
        self.type = "B"
    
    def laser_directions(self, vx, vy, face):
        
        # no laser path after collision with opaque block
        new_dir = []
    
        return new_dir

from itertools import permutations

class Puzzle:
    def __init__(self, file):
        self.file = file
        
        # may need to change certain attributes as we go along
        self.block_grid = None
        self.blocks = []
        self.laser_pos = []
        self.laser_dir = []
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
                        
        # get all possible permutation of length # of blocks
        return list(permutations(avail_pos, len(self.blocks)))
    
    def solve_puzzle(self):
        # all permutations of block placements
        configs = self.get_configurations()
        
        for config in configs:
            
            # update block positions
            for i in range(len(config)):
                self.blocks[i].set_position(config[i])
            
            # do laser tracing
        pass


        