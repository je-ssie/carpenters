#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 11:10:49 2026

@author: sabrinachen
"""

import unittest
from laserproject import *
from unittest.mock import patch, MagicMock
import matplotlib

# Prevent the plot from showing up by forcing a non-GUI backend.
matplotlib.use("Agg")

class TestReadBFF(unittest.TestCase):
    
    def setUp(self):
        self.file = "mad_1.bff"
        self.p = Puzzle(self.file)
    
    def test_block_grid_structure(self):
        # Check dimensions.
        self.assertEqual(len(self.p.block_grid), 4)
        self.assertEqual(len(self.p.block_grid[0]), 4)

        # Check all None as expected for this board.
        for row in self.p.block_grid:
            for cell in row:
                self.assertIsNone(cell)
    
    def test_block_types(self):
        p_blocks = [type(block).__name__ for block in self.p.blocks]

        # Expected block types from file.
        expected_blocks = ['Reflect', 'Reflect', 'Refract']
        self.assertEqual(p_blocks, expected_blocks)
        
    def test_blocks_properties(self):
        # Fixed blocks from grid should have positions.
        for b in self.p.blocks:
            if b.fixed:
                self.assertIsNotNone(b.position)
            else:
                self.assertIsNone(b.position)
    
    def test_movable_block_counts(self):
        movable_reflect = [b for b in self.p.blocks if isinstance(b, Reflect) and not b.fixed]
        movable_opaque = [b for b in self.p.blocks if isinstance(b, Opaque) and not b.fixed]
        movable_refract = [b for b in self.p.blocks if isinstance(b, Refract) and not b.fixed]

        # Adjust these counts if your file differs.
        self.assertEqual(len(movable_reflect), 2)
        self.assertEqual(len(movable_opaque), 0)
        self.assertEqual(len(movable_refract), 1)
    
    def test_laser_positions(self):
        self.assertEqual(len(self.p.laser_pos), 1)
        self.assertEqual(self.p.laser_pos[0], [(2, 7)])

    def test_laser_directions(self):
        self.assertEqual(len(self.p.laser_dir), 1)
        self.assertEqual(self.p.laser_dir[0], (1, -1))
    
    def test_goal_coordinates(self):
        expected_goal = [(3, 0), (4, 3), (2, 5), (4, 7)]
        self.assertEqual(sorted(self.p.goal_coords), sorted(expected_goal))

    def test_goal_count(self):
        self.assertEqual(len(self.p.goal_coords), 4)
    
    def test_puzzle_loaded(self):
        self.assertTrue(self.p.block_grid is not None)
        self.assertTrue(self.p.blocks is not None)
        self.assertTrue(self.p.laser_pos is not None)
        self.assertTrue(self.p.laser_dir is not None)
        self.assertTrue(self.p.goal_coords is not None)

class TestBlockFaces(unittest.TestCase):
    def test_get_all_faces_coordinates(self):
        b = Block([1, 2])
        faces = b.get_all_faces()
        
        expected = {(4, 3): "left", (6, 3): "right",
                    (5, 2): "top", (5, 4): "bottom"}
        
        self.assertEqual(faces, expected)

class TestBlockDirections(unittest.TestCase):
    def test_opaque(self):
        b = Opaque([0, 0])
        self.assertIsNone(b.laser_directions(1, 1, "top"))
    
    def test_transparent(self):
        b = Transparent([0, 0])
        self.assertEqual(b.laser_directions(1, 1, "top"), [(1, 1)])
        
    def test_reflect(self):
        b = Reflect([0, 0])
        directions = b.laser_directions(1, 1, "top")
        directions.extend(b.laser_directions(1, 1, "bottom"))
        directions.extend(b.laser_directions(1, 1, "left"))
        directions.extend(b.laser_directions(1, 1, "right"))
        expected = [(1, -1), (1, -1), (-1, 1), (-1, 1)]
        self.assertEqual(directions, expected)
    
    def test_refract_top(self):
        b = Refract([0, 0])
        directions = b.laser_directions(1, 1, "top")
        expected = [(1, 1), (1, -1)]
        self.assertEqual(directions, expected)
        
    def test_refract_left(self):
        b = Refract([0, 0])
        directions = b.laser_directions(1, -1, "left")
        expected = [(1, -1), (-1, -1)]
        self.assertEqual(directions, expected)

class TestPuzzle(unittest.TestCase):
    def test_generate_configs(self):
        pass
    def test_get_configurations(self):
        pass
    def test_build_block_lookup(self):
        pass
    def test_no_collision(self):
        pass
    def test_yes_collision(self):
        pass
    def test_check_boundary(self):
        pass
    def test_check_solved(self):
        pass
    def test_place_blocks(self):
        pass

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
        
    def test_tiny5(self):
        p = Puzzle('tiny_5.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')

class TestDrawPuzzle(unittest.TestCase):
    def setUp(self):
        # Mock puzzle setup.
        self.puzzle = Puzzle.__new__(Puzzle)
        self.puzzle.file = "mad_1.bff"
        
        # 2x2 grid with different block types.
        self.puzzle.block_grid = [[MagicMock(type="A"), None],
                                  [MagicMock(type="B"), MagicMock(type="C")]]
        
        # Mock blocks list (for table counts).
        block_a = MagicMock(type="A")
        block_b = MagicMock(type="B")
        block_c = MagicMock(type="C")
        self.puzzle.blocks = [block_a, block_b, block_c, block_a]
        
        # Set goal coordinates.
        self.puzzle.goal_coords = [(0, 0), (2, 2)]

        # Set laser paths.
        self.puzzle.laser_pos = [[(0, 0), (1, 1)]]
        self.puzzle.laser_dir = [(1, 1)]

        # __str__ should reflect usage of blocks.
        self.puzzle.__str__ = MagicMock(return_value="AAB")
    
    @patch("laserproject.plt.show")
    @patch("laserproject.plt.savefig")
    @patch("laserproject.plt.subplots")
    
    def test_draw_puzzle_basic_calls(self, mock_subplots, mock_savefig, mock_show):
        # Mock axes.
        fig = MagicMock()
        ax = MagicMock()
        ax_table = MagicMock()

        mock_subplots.return_value = (fig, (ax, ax_table))

        # Run function.
        self.puzzle.draw_puzzle(solved=False)

        # Assert subplots created.
        mock_subplots.assert_called_once()

        # Ensure show was called.
        mock_show.assert_called_once()

        # Ensure patches were added (grid + blocks).
        self.assertTrue(ax.add_patch.called)

        # Ensure scatter used for goals/lasers.
        self.assertTrue(ax.scatter.called)

        # Ensure legend and table created.
        self.assertTrue(ax_table.table.called)
        self.assertTrue(ax_table.legend.called)

    @patch("laserproject.plt.show")
    @patch("laserproject.plt.savefig")
    @patch("laserproject.plt.subplots")
    def test_draw_puzzle_solved_saves_figure(self, mock_subplots, mock_savefig, mock_show):
        fig = MagicMock()
        ax = MagicMock()
        ax_table = MagicMock()

        mock_subplots.return_value = (fig, (ax, ax_table))

        self.puzzle.draw_puzzle(solved=True)

        # Should save figure when solved=True.
        mock_savefig.assert_called_once_with("mad_1.bff solved.png")

    @patch("laserproject.plt.show")
    @patch("laserproject.plt.subplots")
    def test_block_colors_and_patches(self, mock_subplots, mock_show):
        fig = MagicMock()
        ax = MagicMock()
        ax_table = MagicMock()

        mock_subplots.return_value = (fig, (ax, ax_table))

        self.puzzle.draw_puzzle(solved=False)

        # Verify rectangles were added for each grid cell.
        # 2x2 grid => 4 patches.
        self.assertEqual(ax.add_patch.call_count, 4)

    @patch("laserproject.plt.show")
    @patch("laserproject.plt.subplots")
    def test_laser_scatter_and_lines(self, mock_subplots, mock_show):
        fig = MagicMock()
        ax = MagicMock()
        ax_table = MagicMock()

        mock_subplots.return_value = (fig, (ax, ax_table))

        self.puzzle.draw_puzzle(solved=False)

        # Laser should create scatter + plot calls.
        self.assertTrue(ax.scatter.called)
        self.assertTrue(ax.plot.called)

    @patch("laserproject.plt.show")
    @patch("laserproject.plt.subplots")
    def test_axes_properties(self, mock_subplots, mock_show):
        fig = MagicMock()
        ax = MagicMock()
        ax_table = MagicMock()

        mock_subplots.return_value = (fig, (ax, ax_table))

        self.puzzle.draw_puzzle()

        # Check axis configuration.
        ax.set_xlim.assert_called()
        ax.set_ylim.assert_called()
        ax.set_aspect.assert_called_with('equal')
        ax.axis.assert_called_with('off')
        ax_table.axis.assert_called_with('off')
        
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