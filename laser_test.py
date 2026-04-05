#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 16:25:10 2026

@author: jessie
"""
import unittest
from laserproject import *

# # test get all face
# b = Block([1, 2], False)
# print(b.get_all_faces())

class TestLaserTrace(unittest.TestCase):
    
    def setUp(self):
        self.p = Puzzle()
        self.b1 = Refract([0, 2])
        self.b2 = Reflect([1, 3])
        self.b3 = Reflect([2, 0])
        block_grid = [[None, None, self.b1, None],
                      [None, None, None, self.b2],
                      [self.b3, None, None, None],
                      [None, None, None, None]]
        self.p.block_grid = block_grid
        self.p.blocks = [self.b1, self.b2, self.b3]
        self.p.laser_pos = [[(2, 7)]]
        self.p.laser_dir = [(1, -1)]
        self.p.goal_coords = [(4, 7), (2, 5), (3, 0), (4, 3)]
        self.p.build_block_lookup()
    
    def test_laser_trace_position(self):
        pos_solution = [[(2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (5, 2), (4, 1), (3, 0)], 
                        [(2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (5, 2), (4, 3), (3, 4), (2, 5), (3, 6), (4, 7), (5, 8)]]
        laser_pos, _ = self.p.laser_trace()
        self.assertEqual(laser_pos, pos_solution, 'laser positions do not match solution.')
    
    def test_laser_trace_direction(self):
        dir_solution = [None, None]
        _, laser_dir = self.p.laser_trace()
        self.assertEqual(laser_dir, dir_solution, 'laser directions do not match solution.')
    
    def test_check_solved_True(self):
        laser_pos, _ = self.p.laser_trace()
        self.assertTrue(self.p.check_solved(laser_pos), 'puzzle is solved, but check_solved returns False.')
    
    def test_check_solved_False(self):
        laser_pos, _ = self.p.laser_trace()
        laser_pos[1].remove((4, 7))
        self.assertFalse(self.p.check_solved(laser_pos), 'puzzle is not solved, but check_solved returns True.')

class TestMad1(unittest.TestCase):
    def setUp(self):
        self.p = Puzzle()
        self.b1 = Refract([0, 2])
        self.b2 = Reflect([1, 3])
        self.b3 = Reflect([2, 0])
        block_grid = [[None, None, None, None],
                      [None, None, None, None],
                      [None, None, None, None],
                      [None, None, None, None]]
        self.p.block_grid = block_grid
        self.p.blocks = [self.b1, self.b2, self.b3]
        self.p.laser_pos = [[(2, 7)]]
        self.p.laser_dir = [(1, -1)]
        self.p.goal_coords = [(4, 7), (2, 5), (3, 0), (4, 3)]
    
    def test_solve_puzzle(self):
        self.assertTrue(self.p.solve_puzzle(), 'failed to solve puzzle.')
        
    def test_blockgrid_after_solving(self):
        self.p.solve_puzzle()
        solution = [[None, None, self.b1, None],
                      [None, None, None, self.b2],
                      [self.b3, None, None, None],
                      [None, None, None, None]]
        self.assertEqual(self.p.block_grid, solution, 'solution grid does not match.')
        
    def test_laser_pos_after_solving(self):
        pass
    
    def test_laser_dir_after_solving(self):
        pass
    
    def test_block_positions_after_solving(self):
        pass
    
class TestAllFiles(unittest.TestCase):
    
    def test_Mad1(self):
        p = Puzzle('mad_1.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')
        
    def test_Mad4(self):
        p = Puzzle('mad_4.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')
        
    def test_Mad7(self):
        p = Puzzle('mad_7.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')
    
    def test_dark1(self):
        p = Puzzle('dark_1.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')
        
    def test_numbered6(self):
        p = Puzzle('numbered_6.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')
        
    def test_showstopper4(self):
        p = Puzzle('showstopper_4.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')
    
    def test_yarn5(self):
        p = Puzzle('yarn_5.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')
        
    
        
if __name__ == "__main__":
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestMad1)
    # unittest.TextTestRunner().run(suite)
    # file = 'mad_4.bff'
    # p = Puzzle(file)
    # print(p.solve_puzzle())
    # print(p.block_grid)
    
# # test check_boundary()
# assert p.check_boundary((3, 8)) == True, "Check_boundary() failed for (3, 8)"
