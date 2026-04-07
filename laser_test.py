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

class TestPuzzle(unittest.TestCase):
    """unit tests for the Puzzle class methods."""
    
    def create_empty_puzzle(self):
        """
        create a puzzle instance without reading from a file.
        allows us to manually set attributes for testing.
        """
        p = Puzzle(file=None)
        return p
    
    def create_mock_block(self, block_type, position, fixed=False):
        """
        create a mock block for testing purposes.
        
        args:
            block_type: 'A' (reflect), 'B' (opaque), 'C' (refract), 'x' (transparent)
            position: (row, col) tuple or None
            fixed: whether block is fixed in place
        """
        if block_type == 'A':
            block = Reflect(position, fixed)
        elif block_type == 'B':
            block = Opaque(position, fixed)
        elif block_type == 'C':
            block = Refract(position, fixed)
        else:
            block = Transparent(position, fixed)
        return block
    
    
    def test_generate_configs_base_case_empty_type_list(self):
        """
        test base case: when type_list is empty, current config should be added to results.
        """
        p = self.create_empty_puzzle()
        results = []
        current = [(0, 0), (1, 1)]
        
        # empty type_list should trigger base case
        p._generate_configs(
            avail_pos=[(2, 2)],
            type_list=[],
            current=current,
            results=results
        )
        
        # should have one result matching current
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], [(0, 0), (1, 1)])
    
    def test_generate_configs_single_block_type(self):
        """
        test placing a single block type with multiple positions available.
        """
        p = self.create_empty_puzzle()
        results = []
        avail_pos = [(0, 0), (0, 1), (1, 0)]
        type_list = [('A', 2)]  # place 2 'A' blocks
        
        p._generate_configs(avail_pos, type_list, [], results)
        
        # c(3,2) = 3 combinations
        expected_count = 3
        self.assertEqual(len(results), expected_count)
        
        # verify all results have exactly 2 positions
        for config in results:
            self.assertEqual(len(config), 2)
    
    def test_generate_configs_multiple_block_types(self):
        """
        test placing multiple block types.
        """
        p = self.create_empty_puzzle()
        results = []
        avail_pos = [(0, 0), (0, 1), (1, 0), (1, 1)]
        type_list = [('A', 1), ('B', 1)]  # 1 reflect, 1 opaque
        
        p._generate_configs(avail_pos, type_list, [], results)
        
        # c(4,1) * c(3,1) = 4 * 3 = 12 combinations
        expected_count = 12
        self.assertEqual(len(results), expected_count)
        
        # each config should have 2 positions (1 for a, 1 for b)
        for config in results:
            self.assertEqual(len(config), 2)
    
    def test_generate_configs_no_available_positions(self):
        """
        test when there are no available positions but blocks need placing.
        should return no configurations.
        """
        p = self.create_empty_puzzle()
        results = []
        avail_pos = []
        type_list = [('A', 1)]
        
        p._generate_configs(avail_pos, type_list, [], results)
        
        # no way to place blocks, so no configs
        self.assertEqual(len(results), 0)
    
    def test_generate_configs_no_blocks_to_place(self):
        """
        test when there are no blocks to place.
        should return one empty configuration.
        """
        p = self.create_empty_puzzle()
        results = []
        avail_pos = [(0, 0), (0, 1)]
        type_list = []  # no blocks to place
        
        p._generate_configs(avail_pos, type_list, [], results)
        
        # one config: empty placement
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], [])
    
    def test_generate_configs_positions_not_reused(self):
        """
        test that positions are not reused across block types.
        """
        p = self.create_empty_puzzle()
        results = []
        avail_pos = [(0, 0), (0, 1)]
        type_list = [('A', 1), ('B', 1)]
        
        p._generate_configs(avail_pos, type_list, [], results)
        
        # verify no config has duplicate positions
        for config in results:
            self.assertEqual(len(config), len(set(config)))
    
    def test_get_configurations_finds_empty_cells(self):
        """
        test that get_configurations correctly identifies empty cells.
        """
        p = self.create_empty_puzzle()
        
        # create a 2x2 grid with one empty cell
        p.block_grid = [
            [self.create_mock_block('A', (0, 0), True), None],
            [None, self.create_mock_block('B', (1, 1), True)]
        ]
        p.blocks = [self.create_mock_block('A', None, False)]  # 1 movable block
        
        configs = p.get_configurations()
        
        # should have 2 configs: block at (0,1) or (1,0)
        self.assertEqual(len(configs), 2)
    
    def test_get_configurations_all_cells_empty(self):
        """
        test grid where all cells are empty.
        """
        p = self.create_empty_puzzle()
        
        # 2x2 grid, all empty
        p.block_grid = [[None, None], [None, None]]
        p.blocks = [
            self.create_mock_block('A', None, False),
            self.create_mock_block('A', None, False)
        ]
        
        configs = p.get_configurations()
        
        # c(4,2) = 6 ways to place 2 blocks in 4 spots
        self.assertEqual(len(configs), 6)
    
    def test_get_configurations_no_empty_cells(self):
        """
        test grid where no cells are empty.
        """
        p = self.create_empty_puzzle()
        
        # 2x2 grid, all filled
        p.block_grid = [
            [self.create_mock_block('A', (0, 0), True), self.create_mock_block('B', (0, 1), True)],
            [self.create_mock_block('A', (1, 0), True), self.create_mock_block('B', (1, 1), True)]
        ]
        p.blocks = [self.create_mock_block('A', None, False)]  # 1 movable
        
        configs = p.get_configurations()
        
        # no empty cells, no valid configs
        self.assertEqual(len(configs), 0)
    
    def test_get_configurations_only_fixed_blocks(self):
        """
        test when all blocks are fixed (none movable).
        """
        p = self.create_empty_puzzle()
        
        p.block_grid = [[None, None], [None, None]]
        p.blocks = [
            self.create_mock_block('A', (0, 0), True),  # fixed
            self.create_mock_block('B', (0, 1), True)   # fixed
        ]
        
        configs = p.get_configurations()
        
        # no movable blocks, should return one empty config
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0], [])
    
    def test_get_configurations_mixed_block_types(self):
        """
        test with multiple different block types.
        """
        p = self.create_empty_puzzle()
        
        p.block_grid = [[None, None, None], [None, None, None]]  # 6 empty
        p.blocks = [
            self.create_mock_block('A', None, False),
            self.create_mock_block('A', None, False),
            self.create_mock_block('B', None, False)
        ]
        
        configs = p.get_configurations()
        
        # c(6,2) for a blocks * c(4,1) for b block = 15 * 4 = 60
        self.assertEqual(len(configs), 60)
    
    def test_build_block_lookup_single_block(self):
        """
        test lookup table creation with a single block.
        """
        p = self.create_empty_puzzle()
        
        block = self.create_mock_block('A', (1, 1), False)
        p.blocks = [block]
        
        p.build_block_lookup()
        
        # lookup should not be empty
        self.assertIsInstance(p.block_lookup, dict)
        self.assertGreater(len(p.block_lookup), 0)
    
    def test_build_block_lookup_skips_none_position(self):
        """
        test that blocks with none position are skipped.
        """
        p = self.create_empty_puzzle()
        
        block = self.create_mock_block('A', None, False)  # no position
        p.blocks = [block]
        
        p.build_block_lookup()
        
        # lookup should be empty
        self.assertEqual(len(p.block_lookup), 0)
    
    def test_build_block_lookup_skips_transparent(self):
        """
        test that transparent blocks (type 'x') are skipped.
        """
        p = self.create_empty_puzzle()
        
        block = self.create_mock_block('x', (1, 1), True)
        p.blocks = [block]
        
        p.build_block_lookup()
        
        # lookup should be empty
        self.assertEqual(len(p.block_lookup), 0)
    
    def test_build_block_lookup_multiple_blocks(self):
        """
        test lookup with multiple blocks at different positions.
        """
        p = self.create_empty_puzzle()
        
        block1 = self.create_mock_block('A', (0, 0), False)
        block2 = self.create_mock_block('B', (1, 1), False)
        p.blocks = [block1, block2]
        
        p.build_block_lookup()
        
        # both blocks should have entries
        self.assertGreater(len(p.block_lookup), 0)
    
    def test_build_block_lookup_specific_case(self):
        """
        test lookup table with specific expected values.
        """
        
        p = self.create_empty_puzzle()
        
        # create block at grid position (1, 2)
        block = self.create_mock_block('A', (1, 2), False)
        p.blocks = [block]
        
        p.build_block_lookup()
        
        # expected face positions based on grid position (row=1, col=2)
        # formula: laser_x = col * 2 + 1, laser_y = row * 2 + 1 for center
        # top:    (col * 2 + 1, row * 2)     = (5, 2)
        # bottom: (col * 2 + 1, row * 2 + 2) = (5, 4)
        # left:   (col * 2, row * 2 + 1)     = (4, 3)
        # right:  (col * 2 + 2, row * 2 + 1) = (6, 3)
        
        expected_faces = {
            (5, 2): 'top',
            (5, 4): 'bottom',
            (4, 3): 'left',
            (6, 3): 'right'
        }
        
        # verify all expected faces are in lookup
        for coord, expected_face in expected_faces.items():
            self.assertIn(coord, p.block_lookup)
            
            # find the entry for our block
            found = False
            for lookup_block, lookup_face in p.block_lookup[coord]:
                if lookup_block == block:
                    self.assertEqual(lookup_face, expected_face)
                    found = True
                    break
            
            self.assertTrue(found, f"block not found at coordinate {coord}")
        
        # verify no extra coordinates in lookup
        self.assertEqual(len(p.block_lookup), 4)
    
    def test_build_block_lookup_adjacent_blocks_share_face(self):
        """
        test that adjacent blocks share a face coordinate.
        """
        p = self.create_empty_puzzle()
        
        block1 = self.create_mock_block('A', (0, 0), False)
        block2 = self.create_mock_block('B', (0, 1), False)
        p.blocks = [block1, block2]
        
        p.build_block_lookup()
        
        # block1 right face: (col * 2 + 2, row * 2 + 1) = (2, 1)
        # block2 left face:  (col * 2, row * 2 + 1)     = (2, 1)
        shared_coord = (2, 1)
        
        # verify shared coordinate exists
        self.assertIn(shared_coord, p.block_lookup)
        
        # verify both blocks are at this coordinate
        blocks_at_coord = [b for b, f in p.block_lookup[shared_coord]]
        self.assertIn(block1, blocks_at_coord)
        self.assertIn(block2, blocks_at_coord)
        
        # verify correct faces
        for lookup_block, lookup_face in p.block_lookup[shared_coord]:
            if lookup_block == block1:
                self.assertEqual(lookup_face, 'right')
            elif lookup_block == block2:
                self.assertEqual(lookup_face, 'left')
    
    def test_no_collision_empty_lookup(self):
        """
        test collision check when lookup table is empty.
        """
        p = self.create_empty_puzzle()
        p.block_lookup = {}
        
        block, face = p.check_collision((3, 3), (2, 2))
        
        self.assertIsNone(block)
        self.assertIsNone(face)
    
    def test_no_collision_position_not_in_lookup(self):
        """
        test collision check when position is not in lookup.
        """
        p = self.create_empty_puzzle()
        p.block_lookup = {(1, 1): [(self.create_mock_block('A', (0, 0), False), 'top')]}
        
        block, face = p.check_collision((5, 5), (4, 4))
        
        self.assertIsNone(block)
        self.assertIsNone(face)
    
    def test_no_collision_laser_inside_block(self):
        """
        test that collision is ignored when laser is inside block (prev_pos hits same block).
        """
        p = self.create_empty_puzzle()
        
        block = self.create_mock_block('A', (0, 0), False)
        
        # both current and previous position hit same block
        p.block_lookup = {
            (1, 2): [(block, 'bottom')],
            (1, 1): [(block, 'top')]
        }
        
        result_block, result_face = p.check_collision((1, 2), (1, 1))
        
        # should return none because laser is "inside" the block
        self.assertIsNone(result_block)
    
    def test_yes_collision_valid_hit(self):
        """
        test collision detection when laser hits a block face.
        """
        p = self.create_empty_puzzle()
        
        block = self.create_mock_block('A', (0, 0), False)
        p.block_lookup = {(1, 2): [(block, 'top')]}
        
        result_block, result_face = p.check_collision((1, 2), (1, 3))
        
        self.assertEqual(result_block, block)
        self.assertEqual(result_face, 'top')
    
    def test_yes_collision_prev_pos_not_in_lookup(self):
        """
        test collision when previous position is not in lookup (valid external hit).
        """
        p = self.create_empty_puzzle()
        
        block = self.create_mock_block('B', (1, 1), False)
        p.block_lookup = {(3, 2): [(block, 'left')]}
        
        result_block, result_face = p.check_collision((3, 2), (2, 2))
        
        self.assertEqual(result_block, block)
        self.assertEqual(result_face, 'left')
    
    def test_yes_collision_multiple_blocks_at_position(self):
        """
        test collision when multiple blocks share a face coordinate.
        returns first valid collision.
        """
        p = self.create_empty_puzzle()
        
        block1 = self.create_mock_block('A', (0, 0), False)
        block2 = self.create_mock_block('B', (0, 1), False)
        
        # two blocks at same laser coordinate
        p.block_lookup = {
            (1, 2): [(block1, 'right'), (block2, 'left')]
        }
        
        result_block, result_face = p.check_collision((1, 2), (0, 2))
        
        # should return first valid block
        self.assertIsNotNone(result_block)
        self.assertIn(result_block, [block1, block2])
    
    def test_check_boundary_at_origin(self):
        """
        test boundary check at origin (0, y) and (x, 0).
        """
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]  # 2x2 grid
        
        # x = 0 should be boundary
        self.assertTrue(p.check_boundary((0, 2)))
        
        # y = 0 should be boundary
        self.assertTrue(p.check_boundary((2, 0)))
        
        # origin
        self.assertTrue(p.check_boundary((0, 0)))
    
    def test_check_boundary_at_max_edge(self):
        """
        test boundary check at maximum edges.
        """
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None, None], [None, None, None]]  # 2x3 grid
        
        # max_x = 3 * 2 = 6, max_y = 2 * 2 = 4
        self.assertTrue(p.check_boundary((6, 2)))  # right edge
        self.assertTrue(p.check_boundary((2, 4)))  # bottom edge
    
    def test_check_boundary_inside_grid(self):
        """
        test that positions inside grid are not boundaries.
        """
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None, None], [None, None, None]]  # 2x3 grid
        
        # inside positions
        self.assertFalse(p.check_boundary((1, 1)))
        self.assertFalse(p.check_boundary((2, 2)))
        self.assertFalse(p.check_boundary((3, 3)))
        self.assertFalse(p.check_boundary((5, 3)))
    
    def test_check_boundary_just_inside_edge(self):
        """
        test positions just inside the boundary.
        """
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]  # 2x2 grid
        
        # max_x = 4, max_y = 4
        # (3, 3) is inside
        self.assertFalse(p.check_boundary((3, 3)))
        
        # (1, 1) is inside
        self.assertFalse(p.check_boundary((1, 1)))
    
    
    def test_check_solved_all_goals_hit(self):
        """
        test when all goal coordinates are hit by laser.
        """
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1), (2, 2), (3, 3)]
        
        laser_pos = [
            [(0, 0), (1, 1), (2, 2)],  # path 1
            [(3, 3), (4, 4)]           # path 2
        ]
        
        self.assertTrue(p.check_solved(laser_pos))
    
    def test_check_solved_missing_goal(self):
        """
        test when some goal coordinates are not hit.
        """
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1), (5, 5), (3, 3)]
        
        laser_pos = [
            [(0, 0), (1, 1), (2, 2), (3, 3)]
        ]
        
        # (5, 5) is not in laser path
        self.assertFalse(p.check_solved(laser_pos))
    
    def test_check_solved_empty_goals(self):
        """
        test when there are no goal coordinates.
        """
        p = self.create_empty_puzzle()
        p.goal_coords = []
        
        laser_pos = [[(1, 1), (2, 2)]]
        
        # no goals to hit, so trivially solved
        self.assertTrue(p.check_solved(laser_pos))
    
    def test_check_solved_empty_laser_paths(self):
        """
        test when laser paths are empty but goals exist.
        """
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1)]
        
        laser_pos = [[]]
        
        self.assertFalse(p.check_solved(laser_pos))
    
    def test_check_solved_multiple_paths_combined(self):
        """
        test that goals can be hit by different laser paths.
        """
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1), (5, 5)]
        
        laser_pos = [
            [(0, 0), (1, 1)],  # hits first goal
            [(4, 4), (5, 5)]   # hits second goal
        ]
        
        self.assertTrue(p.check_solved(laser_pos))
    
    def test_check_solved_duplicate_positions_in_path(self):
        """
        test that duplicate positions in laser path don't cause issues.
        """
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1)]
        
        # laser passes through (1,1) multiple times
        laser_pos = [[(0, 0), (1, 1), (2, 2), (1, 1), (0, 0)]]
        
        self.assertTrue(p.check_solved(laser_pos))
    
    def test_place_blocks_single_block(self):
        """
        test placing a single block on the grid.
        """
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]
        
        block = self.create_mock_block('A', (0, 1), False)
        p.blocks = [block]
        
        p.place_blocks()
        
        self.assertEqual(p.block_grid[0][1], block)
    
    def test_place_blocks_multiple_blocks(self):
        """
        test placing multiple blocks on the grid.
        """
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]
        
        block1 = self.create_mock_block('A', (0, 0), False)
        block2 = self.create_mock_block('B', (1, 1), False)
        p.blocks = [block1, block2]
        
        p.place_blocks()
        
        self.assertEqual(p.block_grid[0][0], block1)
        self.assertEqual(p.block_grid[1][1], block2)
    
    def test_place_blocks_preserves_other_cells(self):
        """
        test that placing blocks doesn't affect other cells.
        """
        p = self.create_empty_puzzle()
        
        existing_block = self.create_mock_block('B', (0, 0), True)
        p.block_grid = [[existing_block, None], [None, None]]
        
        new_block = self.create_mock_block('A', (1, 1), False)
        p.blocks = [new_block]
        
        p.place_blocks()
        
        # existing block should still be there
        self.assertEqual(p.block_grid[0][0], existing_block)
        # new block placed
        self.assertEqual(p.block_grid[1][1], new_block)
    
    def test_place_blocks_overwrites_none(self):
        """
        test that blocks correctly overwrite none values.
        """
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]
        
        block = self.create_mock_block('C', (0, 0), False)
        p.blocks = [block]
        
        # verify it's none before
        self.assertIsNone(p.block_grid[0][0])
        
        p.place_blocks()
        
        # now it should be the block
        self.assertIsNotNone(p.block_grid[0][0])
        self.assertEqual(p.block_grid[0][0], block)

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
            """
            test that laser_pos contains all goal coordinates after solving.
            
            verifies that the laser path(s) pass through all required goal points.
            """
            self.p.solve_puzzle()
            
            # collect all positions from all laser paths
            all_positions = set()
            for path in self.p.laser_pos:
                for pos in path:
                    all_positions.add(pos)
            
            # verify all goal coordinates are in laser positions
            for goal in self.p.goal_coords:
                self.assertIn(goal, all_positions, 
                             f'goal coordinate {goal} not found in laser path.')
        
    def test_laser_dir_after_solving(self):
        """
        test that laser_dir has correct length after solving.
        
        each laser path should have a corresponding direction entry.
        directions should be none (laser terminated) or a valid (vx, vy) tuple.
        """
        self.p.solve_puzzle()
        
        # laser_dir length should match laser_pos length
        self.assertEqual(len(self.p.laser_dir), len(self.p.laser_pos),
                        'laser_dir and laser_pos length mismatch.')
        
        # each direction should be none or a tuple of two integers
        for i, direction in enumerate(self.p.laser_dir):
            if direction is not None:
                self.assertIsInstance(direction, tuple,
                                     f'laser_dir[{i}] should be tuple or none.')
                self.assertEqual(len(direction), 2,
                                f'laser_dir[{i}] should have 2 elements (vx, vy).')
                vx, vy = direction
                self.assertIn(vx, [-1, 1],
                             f'laser_dir[{i}] vx should be -1 or 1.')
                self.assertIn(vy, [-1, 1],
                             f'laser_dir[{i}] vy should be -1 or 1.')
    
    def test_block_positions_after_solving(self):
        """
        test that all blocks have correct positions after solving.
        verifies each block's position attribute matches its location in block_grid.
        """
        self.p.solve_puzzle()
        
        # expected positions for each block after solving
        expected_positions = {
            self.b1: (0, 2),  # refract block
            self.b2: (1, 3),  # reflect block
            self.b3: (2, 0)   # reflect block
        }
        
        # verify each block's position attribute
        for block, expected_pos in expected_positions.items():
            # check position attribute matches expected
            actual_pos = tuple(block.position) if isinstance(block.position, list) else block.position
            self.assertEqual(actual_pos, expected_pos,
                           f'block {block.type} position {actual_pos} does not match expected {expected_pos}.')
        
        # verify blocks are in correct grid locations
        for block in self.p.blocks:
            pos = block.position
            row, col = pos[0], pos[1]
            
            self.assertEqual(self.p.block_grid[row][col], block,
                           f'block {block.type} not found at grid position ({row}, {col}).')
        
        # verify all blocks are placed (no none positions)
        for block in self.p.blocks:
            self.assertIsNotNone(block.position,
                                f'block {block.type} has no position after solving.')

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