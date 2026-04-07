#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 11:10:49 2026.

@author: sabrinachen
"""

import unittest
from laserproject import *
from unittest.mock import patch, MagicMock
import os


class TestPuzzle(unittest.TestCase):
    """
    Unit tests for the Puzzle class methods except draw_puzzle().

    These tests verifies configuration generation, block placement, collision
    detection, boundary checking, puzzle solving logic, and file parsing and
    puzzle construction.
    """

    def create_empty_puzzle(self):
        """
        Create a puzzle instance without reading from a file which allows us to
        manually set attributes for testing.
        """
        p = Puzzle(file=None)
        return p

    def create_mock_block(self, block_type, position, fixed=False):
        """
        Create a mock block for testing purposes.

        Parameters
        ----------
        block_type : str
            The string representation of the block.
            'A' (reflect), 'B' (opaque), 'C' (refract), 'x' (transparent)
        position : tuple, None
            Represents the location of the block in a (row, column) tuple.
        fixed : Boolean, optional
            Whether the block is fixed in place. The default is False.

        Returns
        -------
        block : Reflect, Opaque, Refract, Transparent
            The Block object given the string representation mentioned above.

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
        Test the base case. When type_list is empty, current config should be
        added to results.
        """
        p = self.create_empty_puzzle()
        results = []
        current = [(0, 0), (1, 1)]

        # Empty type_list should trigger base case.
        p._generate_configs(
            avail_pos=[(2, 2)],
            type_list=[],
            current=current,
            results=results
        )

        # Should have one result matching current.
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], [(0, 0), (1, 1)])

    def test_generate_configs_single_block_type(self):
        """
        Test the placement of a single block type with multiple positions
        available.
        """
        p = self.create_empty_puzzle()
        results = []
        avail_pos = [(0, 0), (0, 1), (1, 0)]
        type_list = [('A', 2)]  # place 2 'A' blocks

        p._generate_configs(avail_pos, type_list, [], results)

        # c(3,2) = 3 combinations.
        expected_count = 3
        self.assertEqual(len(results), expected_count)

        # Verify all results have exactly 2 positions.
        for config in results:
            self.assertEqual(len(config), 2)

    def test_generate_configs_multiple_block_types(self):
        """
        test placing multiple block types.
        """
        p = self.create_empty_puzzle()
        results = []
        avail_pos = [(0, 0), (0, 1), (1, 0), (1, 1)]
        type_list = [('A', 1), ('B', 1)]  # 1 reflect, 1 opaque block

        p._generate_configs(avail_pos, type_list, [], results)

        # c(4,1) * c(3,1) = 4 * 3 = 12 combinations.
        expected_count = 12
        self.assertEqual(len(results), expected_count)

        # Each configuration should have 2 positions (1 for a, 1 for b).
        for config in results:
            self.assertEqual(len(config), 2)

    def test_generate_configs_no_available_positions(self):
        """
        Test when there are no available positions but blocks need placing.
        Should return no configurations.
        """
        p = self.create_empty_puzzle()
        results = []
        avail_pos = []
        type_list = [('A', 1)]

        p._generate_configs(avail_pos, type_list, [], results)

        # There is no way to place blocks, so no configurations.
        self.assertEqual(len(results), 0)

    def test_generate_configs_no_blocks_to_place(self):
        """
        Test when there are no blocks to place.
        Should return one empty configuration.
        """
        p = self.create_empty_puzzle()
        results = []
        avail_pos = [(0, 0), (0, 1)]
        type_list = []  # No blocks to place

        p._generate_configs(avail_pos, type_list, [], results)

        # One configuration: empty placement
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], [])

    def test_generate_configs_positions_not_reused(self):
        """Test that positions are not reused across block types."""
        p = self.create_empty_puzzle()
        results = []
        avail_pos = [(0, 0), (0, 1)]
        type_list = [('A', 1), ('B', 1)]

        p._generate_configs(avail_pos, type_list, [], results)

        # Verify no configuration has duplicate positions.
        for config in results:
            self.assertEqual(len(config), len(set(config)))

    def test_get_configurations_finds_empty_cells(self):
        """Test that get_configurations correctly identifies empty cells."""
        p = self.create_empty_puzzle()

        # Create a 2x2 grid with one empty cell.
        p.block_grid = [
            [self.create_mock_block('A', (0, 0), True), None],
            [None, self.create_mock_block('B', (1, 1), True)]
        ]
        p.blocks = [self.create_mock_block(
            'A', None, False)]  # 1 movable block

        configs = p.get_configurations()

        # Should have 2 configs: block at (0,1) or (1,0).
        self.assertEqual(len(configs), 2)

    def test_get_configurations_all_cells_empty(self):
        """Test grid where all cells are empty."""
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
        """Test grid where no cells are empty."""
        p = self.create_empty_puzzle()

        # 2x2 grid, all filled
        p.block_grid = [
            [self.create_mock_block('A', (0, 0), True),
             self.create_mock_block('B', (0, 1), True)],
            [self.create_mock_block('A', (1, 0), True),
             self.create_mock_block('B', (1, 1), True)]
        ]
        p.blocks = [self.create_mock_block('A', None, False)]  # 1 movable

        configs = p.get_configurations()

        # No empty cells, no valid configs.
        self.assertEqual(len(configs), 0)

    def test_get_configurations_only_fixed_blocks(self):
        """Test when all blocks are fixed (none movable)."""
        p = self.create_empty_puzzle()

        p.block_grid = [[None, None], [None, None]]
        p.blocks = [
            self.create_mock_block('A', (0, 0), True),  # fixed
            self.create_mock_block('B', (0, 1), True)   # fixed
        ]

        configs = p.get_configurations()

        # No movable blocks, should return one empty config.
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0], [])

    def test_get_configurations_mixed_block_types(self):
        """Test with multiple different block types."""
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
        """Test lookup table creation with a single block."""
        p = self.create_empty_puzzle()

        block = self.create_mock_block('A', (1, 1), False)
        p.blocks = [block]

        p.build_block_lookup()

        # lookup should not be empty
        self.assertIsInstance(p.block_lookup, dict)
        self.assertGreater(len(p.block_lookup), 0)

    def test_build_block_lookup_skips_none_position(self):
        """Test that blocks with none position are skipped."""
        p = self.create_empty_puzzle()

        block = self.create_mock_block('A', None, False)  # no position
        p.blocks = [block]

        p.build_block_lookup()

        # Lookup should be empty.
        self.assertEqual(len(p.block_lookup), 0)

    def test_build_block_lookup_skips_transparent(self):
        """Test that transparent blocks (type 'x') are skipped."""
        p = self.create_empty_puzzle()

        block = self.create_mock_block('x', (1, 1), True)
        p.blocks = [block]

        p.build_block_lookup()

        # Lookup should be empty.
        self.assertEqual(len(p.block_lookup), 0)

    def test_build_block_lookup_multiple_blocks(self):
        """Test lookup with multiple blocks at different positions."""
        p = self.create_empty_puzzle()

        block1 = self.create_mock_block('A', (0, 0), False)
        block2 = self.create_mock_block('B', (1, 1), False)
        p.blocks = [block1, block2]

        p.build_block_lookup()

        # Both blocks should have entries.
        self.assertGreater(len(p.block_lookup), 0)

    def test_build_block_lookup_specific_case(self):
        """Test lookup table with specific expected values."""
        p = self.create_empty_puzzle()

        # Create block at grid position (1, 2).
        block = self.create_mock_block('A', (1, 2), False)
        p.blocks = [block]

        p.build_block_lookup()

        # Expected face positions based on grid position (row=1, col=2).
        # Formula: laser_x = col * 2 + 1, laser_y = row * 2 + 1 for center
        # Top:    (col * 2 + 1, row * 2)     = (5, 2).
        # Bottom: (col * 2 + 1, row * 2 + 2) = (5, 4).
        # Left:   (col * 2, row * 2 + 1)     = (4, 3).
        # Right:  (col * 2 + 2, row * 2 + 1) = (6, 3).

        expected_faces = {
            (5, 2): 'top',
            (5, 4): 'bottom',
            (4, 3): 'left',
            (6, 3): 'right'
        }

        # Verify all expected faces are in lookup.
        for coord, expected_face in expected_faces.items():
            self.assertIn(coord, p.block_lookup)

            # Find the entry for our block.
            found = False
            for lookup_block, lookup_face in p.block_lookup[coord]:
                if lookup_block == block:
                    self.assertEqual(lookup_face, expected_face)
                    found = True
                    break

            self.assertTrue(found, f"block not found at coordinate {coord}")

        # Verify no extra coordinates in lookup.
        self.assertEqual(len(p.block_lookup), 4)

    def test_build_block_lookup_adjacent_blocks_share_face(self):
        """Test that adjacent blocks share a face coordinate."""
        p = self.create_empty_puzzle()

        block1 = self.create_mock_block('A', (0, 0), False)
        block2 = self.create_mock_block('B', (0, 1), False)
        p.blocks = [block1, block2]

        p.build_block_lookup()

        # block1 right face: (col * 2 + 2, row * 2 + 1) = (2, 1)
        # block2 left face:  (col * 2, row * 2 + 1)     = (2, 1)
        shared_coord = (2, 1)

        # Verify shared coordinate exists.
        self.assertIn(shared_coord, p.block_lookup)

        # Verify both blocks are at this coordinate.
        blocks_at_coord = [b for b, f in p.block_lookup[shared_coord]]
        self.assertIn(block1, blocks_at_coord)
        self.assertIn(block2, blocks_at_coord)

        # Verify correct faces.
        for lookup_block, lookup_face in p.block_lookup[shared_coord]:
            if lookup_block == block1:
                self.assertEqual(lookup_face, 'right')
            elif lookup_block == block2:
                self.assertEqual(lookup_face, 'left')

    def test_no_collision_empty_lookup(self):
        """Test collision check when lookup table is empty."""
        p = self.create_empty_puzzle()
        p.block_lookup = {}

        block, face = p.check_collision((3, 3), (2, 2))

        self.assertIsNone(block)
        self.assertIsNone(face)

    def test_no_collision_position_not_in_lookup(self):
        """Test collision check when position is not in lookup."""
        p = self.create_empty_puzzle()
        p.block_lookup = {
            (1, 1): [(self.create_mock_block('A', (0, 0), False), 'top')]}

        block, face = p.check_collision((5, 5), (4, 4))

        self.assertIsNone(block)
        self.assertIsNone(face)

    def test_no_collision_laser_inside_block(self):
        """
        Test that collision is ignored when laser is inside block (prev_pos
        hits same block).
        """
        p = self.create_empty_puzzle()

        block = self.create_mock_block('A', (0, 0), False)

        # Both current and previous position hit same block.
        p.block_lookup = {
            (1, 2): [(block, 'bottom')],
            (1, 1): [(block, 'top')]
        }

        result_block, result_face = p.check_collision((1, 2), (1, 1))

        # Should return none because laser is "inside" the block.
        self.assertIsNone(result_block)

    def test_yes_collision_valid_hit(self):
        """Test collision detection when laser hits a block face."""
        p = self.create_empty_puzzle()

        block = self.create_mock_block('A', (0, 0), False)
        p.block_lookup = {(1, 2): [(block, 'top')]}

        result_block, result_face = p.check_collision((1, 2), (1, 3))

        self.assertEqual(result_block, block)
        self.assertEqual(result_face, 'top')

    def test_yes_collision_prev_pos_not_in_lookup(self):
        """
        Test collision when previous position is not in lookup (valid external
        hit).
        """
        p = self.create_empty_puzzle()

        block = self.create_mock_block('B', (1, 1), False)
        p.block_lookup = {(3, 2): [(block, 'left')]}

        result_block, result_face = p.check_collision((3, 2), (2, 2))

        self.assertEqual(result_block, block)
        self.assertEqual(result_face, 'left')

    def test_yes_collision_multiple_blocks_at_position(self):
        """
        Test collision when multiple blocks share a face coordinate.

        Returns first valid collision.
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
        """Test boundary check at origin (0, y) and (x, 0)."""
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]  # 2x2 grid

        # x = 0 should be boundary.
        self.assertTrue(p.check_boundary((0, 2)))

        # y = 0 should be boundary.
        self.assertTrue(p.check_boundary((2, 0)))

        # Origin.
        self.assertTrue(p.check_boundary((0, 0)))

    def test_check_boundary_at_max_edge(self):
        """Test boundary check at maximum edges."""
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None, None], [None, None, None]]  # 2x3 grid

        # max_x = 3 * 2 = 6, max_y = 2 * 2 = 4
        self.assertTrue(p.check_boundary((6, 2)))  # Right edge
        self.assertTrue(p.check_boundary((2, 4)))  # Bottom edge

    def test_check_boundary_inside_grid(self):
        """Test that positions inside grid are not boundaries."""
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None, None], [None, None, None]]  # 2x3 grid

        # Inside positions.
        self.assertFalse(p.check_boundary((1, 1)))
        self.assertFalse(p.check_boundary((2, 2)))
        self.assertFalse(p.check_boundary((3, 3)))
        self.assertFalse(p.check_boundary((5, 3)))

    def test_check_boundary_just_inside_edge(self):
        """Test positions just inside the boundary."""
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]  # 2x2 grid

        # max_x = 4, max_y = 4
        # (3, 3) is inside.
        self.assertFalse(p.check_boundary((3, 3)))

        # (1, 1) is inside.
        self.assertFalse(p.check_boundary((1, 1)))

    def test_check_solved_all_goals_hit(self):
        """Test when all goal coordinates are hit by laser."""
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1), (2, 2), (3, 3)]

        laser_pos = [
            [(0, 0), (1, 1), (2, 2)],  # path 1
            [(3, 3), (4, 4)]           # path 2
        ]

        self.assertTrue(p.check_solved(laser_pos))

    def test_check_solved_missing_goal(self):
        """Test when some goal coordinates are not hit."""
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1), (5, 5), (3, 3)]

        laser_pos = [
            [(0, 0), (1, 1), (2, 2), (3, 3)]
        ]

        # (5, 5) is not in laser path.
        self.assertFalse(p.check_solved(laser_pos))

    def test_check_solved_empty_goals(self):
        """Test when there are no goal coordinates."""
        p = self.create_empty_puzzle()
        p.goal_coords = []

        laser_pos = [[(1, 1), (2, 2)]]

        # No goals to hit, so trivially solved.
        self.assertTrue(p.check_solved(laser_pos))

    def test_check_solved_empty_laser_paths(self):
        """Test when laser paths are empty but goals exist."""
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1)]

        laser_pos = [[]]

        self.assertFalse(p.check_solved(laser_pos))

    def test_check_solved_multiple_paths_combined(self):
        """Test that goals can be hit by different laser paths."""
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1), (5, 5)]

        laser_pos = [
            [(0, 0), (1, 1)],  # Hits first goal.
            [(4, 4), (5, 5)]   # Hits second goal.
        ]

        self.assertTrue(p.check_solved(laser_pos))

    def test_check_solved_duplicate_positions_in_path(self):
        """Test that duplicate positions in laser path don't cause issues."""
        p = self.create_empty_puzzle()
        p.goal_coords = [(1, 1)]

        # Laser passes through (1,1) multiple times.
        laser_pos = [[(0, 0), (1, 1), (2, 2), (1, 1), (0, 0)]]

        self.assertTrue(p.check_solved(laser_pos))

    def test_place_blocks_single_block(self):
        """Test placing a single block on the grid."""
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]

        block = self.create_mock_block('A', (0, 1), False)
        p.blocks = [block]

        p.place_blocks()

        self.assertEqual(p.block_grid[0][1], block)

    def test_place_blocks_multiple_blocks(self):
        """Test placing multiple blocks on the grid."""
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]

        block1 = self.create_mock_block('A', (0, 0), False)
        block2 = self.create_mock_block('B', (1, 1), False)
        p.blocks = [block1, block2]

        p.place_blocks()

        self.assertEqual(p.block_grid[0][0], block1)
        self.assertEqual(p.block_grid[1][1], block2)

    def test_place_blocks_preserves_other_cells(self):
        """Test that placing blocks doesn't affect other cells."""
        p = self.create_empty_puzzle()

        existing_block = self.create_mock_block('B', (0, 0), True)
        p.block_grid = [[existing_block, None], [None, None]]

        new_block = self.create_mock_block('A', (1, 1), False)
        p.blocks = [new_block]

        p.place_blocks()

        # Existing block should still be there.
        self.assertEqual(p.block_grid[0][0], existing_block)
        # New block placed.
        self.assertEqual(p.block_grid[1][1], new_block)

    def test_place_blocks_overwrites_none(self):
        """Test that blocks correctly overwrite none values."""
        p = self.create_empty_puzzle()
        p.block_grid = [[None, None], [None, None]]

        block = self.create_mock_block('C', (0, 0), False)
        p.blocks = [block]

        # Verify it's none before.
        self.assertIsNone(p.block_grid[0][0])

        p.place_blocks()

        # Now it should be the block.
        self.assertIsNotNone(p.block_grid[0][0])
        self.assertEqual(p.block_grid[0][0], block)

    def setUp(self):
        """
        Set up a Puzzle instance using a sample .bff file.

        This runs before each test method and initializes the Puzzle object
        that will be used across all tests.
        """
        self.file = 'mad_1.bff'
        self.p = Puzzle(self.file)

    def test_read_file_lines_removes_empty_lines(self):
        """Test read_file_lines removes empty lines from the file output."""
        lines = self.p.read_file_lines(self.file)
        self.assertNotIn("", lines)

    def test_read_file_lines_strips_newlines(self):
        """Test read_file_lines removes newline characters from each line."""
        lines = self.p.read_file_lines(self.file)
        for line in lines:
            self.assertNotIn('\n', line)

    def test_split_sections_removes_grid_markers(self):
        """
        Test that split_sections excludes GRID START and GRID STOP markers
        from both returned sections.
        """
        lines = self.p.read_file_lines(self.file)
        grid_lines, other_lines = self.p.split_sections(lines)

        self.assertNotIn("GRID START", grid_lines)
        self.assertNotIn("GRID STOP", grid_lines)
        self.assertNotIn("GRID START", other_lines)
        self.assertNotIn("GRID STOP", other_lines)

    def test_split_sections_returns_nonempty_sections(self):
        """Test split_sections returns non-empty grid and other sections."""
        lines = self.p.read_file_lines(self.file)
        grid_lines, other_lines = self.p.split_sections(lines)

        self.assertGreater(len(grid_lines), 0)
        self.assertGreater(len(other_lines), 0)

    def test_parse_grid_is_2d(self):
        """Test parse_grid returns a 2D list structure."""
        lines = self.p.read_file_lines(self.file)
        grid_lines, _ = self.p.split_sections(lines)

        block_grid, _ = self.p.parse_grid(grid_lines)

        self.assertIsInstance(block_grid, list)
        self.assertTrue(all(isinstance(row, list) for row in block_grid))

    def test_parse_grid_row_lengths_consistent(self):
        """Test that all rows in the parsed grid have the same length."""
        lines = self.p.read_file_lines(self.file)
        grid_lines, _ = self.p.split_sections(lines)

        block_grid, _ = self.p.parse_grid(grid_lines)

        row_lengths = [len(row) for row in block_grid]
        self.assertTrue(all(length == row_lengths[0]
                            for length in row_lengths))

    def test_parse_grid_cells_are_valid(self):
        """Test that all grid cells are either None or valid block objects."""
        lines = self.p.read_file_lines(self.file)
        grid_lines, _ = self.p.split_sections(lines)

        block_grid, _ = self.p.parse_grid(grid_lines)

        for row in block_grid:
            for cell in row:
                self.assertTrue(cell is None or
                                isinstance(cell, (Reflect, Opaque, Refract,
                                                  Transparent)))

    def test_parse_grid_fixed_blocks_have_positions(self):
        """Test that all fixed blocks have valid positions assigned."""
        lines = self.p.read_file_lines(self.file)
        grid_lines, _ = self.p.split_sections(lines)

        _, blocks = self.p.parse_grid(grid_lines)

        for b in blocks:
            self.assertTrue(b.fixed)
            self.assertIsNotNone(b.position)

    def test_parse_rest_laser_positions(self):
        """Test that laser positions are correctly parsed."""
        lines = self.p.read_file_lines(self.file)
        _, other_lines = self.p.split_sections(lines)

        _, laser_pos, _, _ = self.p.parse_rest(other_lines, [])

        self.assertTrue(all(isinstance(lp, list) for lp in laser_pos))

    def test_parse_rest_laser_directions(self):
        """Test that laser directions are correctly parsed as tuples."""
        lines = self.p.read_file_lines(self.file)
        _, other_lines = self.p.split_sections(lines)

        _, _, laser_dir, _ = self.p.parse_rest(other_lines, [])

        for d in laser_dir:
            self.assertIsInstance(d, tuple)
            self.assertEqual(len(d), 2)

    def test_parse_rest_goal_coordinates(self):
        """
        Test that goal coordinates are correctly parsed as tuples with a
        length of 2.
        """
        lines = self.p.read_file_lines(self.file)
        _, other_lines = self.p.split_sections(lines)

        _, _, _, goal_coords = self.p.parse_rest(other_lines, [])

        for g in goal_coords:
            self.assertIsInstance(g, tuple)
            self.assertEqual(len(g), 2)

    def test_parse_rest_adds_blocks(self):
        """Test that movable blocks are added when specified in the file."""
        lines = self.p.read_file_lines(self.file)
        _, other_lines = self.p.split_sections(lines)

        blocks, _, _, _ = self.p.parse_rest(other_lines, [])

        self.assertGreater(len(blocks), 0)

    def test_read_bff_populates_all_attributes(self):
        """
        Test to check that read_bff successfully populates all puzzle
        attributes.
        """
        self.assertIsNotNone(self.p.block_grid)
        self.assertIsNotNone(self.p.blocks)
        self.assertIsNotNone(self.p.laser_pos)
        self.assertIsNotNone(self.p.laser_dir)
        self.assertIsNotNone(self.p.goal_coords)

    def test_read_bff_nonempty_data(self):
        """Test to check that the parsed puzzle contains data."""
        self.assertGreater(len(self.p.blocks), 0)
        self.assertGreater(len(self.p.laser_dir), 0)
        self.assertGreater(len(self.p.goal_coords), 0)

    def test_read_bff_grid_dimensions_consistent(self):
        """Test that the grid loaded by read_bff has consistent row lengths."""
        grid = self.p.block_grid
        self.assertTrue(all(len(row) == len(grid[0]) for row in grid))


class TestBlock(unittest.TestCase):
    """
    Unit tests for the Block class methods.

    These tests verify correct behavior of the face coordinate computation,
    position updates, fixed block constraints, and initialization flags.
    """

    def test_get_all_faces_coordinates(self):
        """
        Test that get_all_faces returns correct face coordinates and directions
        for a block at position [1, 2].
        """
        b = Block([1, 2])
        faces = b.get_all_faces()

        expected = {(4, 3): "left", (6, 3): "right",
                    (5, 2): "top", (5, 4): "bottom"}

        self.assertEqual(faces, expected)

    def test_get_all_faces_different_position(self):
        """
        Test that get_all_faces returns correct face coordinates for a block
        placed at a different position.
        """
        b = Block([0, 0])
        faces = b.get_all_faces()

        expected = {(0, 1): "left", (2, 1): "right",
                    (1, 0): "top", (1, 2): "bottom"}

        self.assertEqual(faces, expected)

    def test_set_position_updates_position(self):
        """Test that set_position correctly updates the block's position."""
        b = Block([1, 2])
        b.set_position([3, 4])
        self.assertEqual(b.position, [3, 4])

    def test_set_position_raises_for_fixed_block(self):
        """Test that moving a fixed block raises an AssertionError."""
        b = Block([1, 2], fixed=True)

        with self.assertRaises(AssertionError):
            b.set_position([3, 4])

    def test_block_initialization_fixed_flag(self):
        """Test that the fixed flag is properly set during initialization."""
        b1 = Block([1, 2])
        b2 = Block([1, 2], fixed=True)

        self.assertFalse(b1.fixed)
        self.assertTrue(b2.fixed)


class TestBlockDirections(unittest.TestCase):
    """
    Unit tests for laser direction behavior of different Block subclasses.

    These tests verify how each block type (Opaque, Transparent, Reflect,
    Refract) transforms or responds to incoming laser directions.
    """

    def test_opaque(self):
        """Test that Opaque blocks absorb the laser and return None."""
        b = Opaque([0, 0])
        self.assertIsNone(b.laser_directions(1, 1, "top"))

    def test_transparent(self):
        """
        Test that Transparent blocks allow the laser to pass through
        unchanged.
        """
        b = Transparent([0, 0])
        self.assertEqual(b.laser_directions(1, 1, "top"), [(1, 1)])

    def test_reflect(self):
        """
        Checks reflections from all four sides.

        Reflect blocks should reflect the laser depending on the incoming side.
        """
        b = Reflect([0, 0])
        directions = b.laser_directions(1, 1, "top")
        directions.extend(b.laser_directions(1, 1, "bottom"))
        directions.extend(b.laser_directions(1, 1, "left"))
        directions.extend(b.laser_directions(1, 1, "right"))

        # Expected reflections for each incoming direction.
        expected = [(1, -1), (1, -1), (-1, 1), (-1, 1)]
        self.assertEqual(directions, expected)

    def test_refract_top(self):
        """
        Test that Refract blocks split the laser into two lasers when hit from
        the top.

        One laser shines through the block while the other reflects.
        """
        b = Refract([0, 0])
        directions = b.laser_directions(1, 1, "top")
        expected = [(1, 1), (1, -1)]
        self.assertEqual(directions, expected)

    def test_refract_left(self):
        """Test that refract blocks split a laser from the left correctly."""
        b = Refract([0, 0])
        directions = b.laser_directions(1, -1, "left")
        expected = [(1, -1), (-1, -1)]
        self.assertEqual(directions, expected)


class TestLaserTrace(unittest.TestCase):
    """
    Unit tests for laser tracing and puzzle solving behavior.

    These tests verify correct laser path generation (positions and directions)
    and puzzle solving validation.
    """

    def setUp(self):
        """
        Initialize a Puzzle instance with a predefined grid, blocks,
        laser configuration, and goal coordinates.

        This setup is used across all laser tracing and solving tests.
        """
        self.p = Puzzle()

        # Define blocks.
        self.b1 = Refract([0, 2])
        self.b2 = Reflect([1, 3])
        self.b3 = Reflect([2, 0])

        # Construct block grid
        block_grid = [[None, None, self.b1, None],
                      [None, None, None, self.b2],
                      [self.b3, None, None, None],
                      [None, None, None, None]]

        self.p.block_grid = block_grid
        self.p.blocks = [self.b1, self.b2, self.b3]

        # Laser initial positions and directions
        self.p.laser_pos = [[(2, 7)]]
        self.p.laser_dir = [(1, -1)]

        # Goal coordinates to be hit by the laser
        self.p.goal_coords = [(4, 7), (2, 5), (3, 0), (4, 3)]

        # Build lookup structure for collision detection
        self.p.build_block_lookup()

    def test_laser_trace_position(self):
        """Test that laser_trace returns the correct sequence of positions."""
        pos_solution = [[(2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (5, 2), (4, 1), (3, 0)],
                        [(2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (5, 2), (4, 3), (3, 4), (2, 5), (3, 6), (4, 7), (5, 8)]]
        laser_pos, _ = self.p.laser_trace()
        self.assertEqual(laser_pos, pos_solution,
                         'laser positions do not match solution.')

    def test_laser_trace_direction(self):
        """Test that laser_trace returns the correct direction outputs."""
        dir_solution = [None, None]
        _, laser_dir = self.p.laser_trace()
        self.assertEqual(laser_dir, dir_solution,
                         'laser directions do not match solution.')

    def test_check_solved_True(self):
        """Test that check_solved returns True when all goals are hit."""
        laser_pos, _ = self.p.laser_trace()
        self.assertTrue(self.p.check_solved(laser_pos),
                        'puzzle is solved, but check_solved returns False.')

    def test_check_solved_False(self):
        """Test that check_solved returns False when a goal is missing."""
        laser_pos, _ = self.p.laser_trace()
        laser_pos[1].remove((4, 7))
        self.assertFalse(self.p.check_solved(laser_pos),
                         'puzzle is not solved, but check_solved returns True.')


class TestMad1(unittest.TestCase):
    """Integration tests for solving the full Mad: 1 puzzle.

    These tests verify that the puzzle can be solved successfully, blocks are
    placed correctly in the grid, laser paths cover all goal coordinates, laser
    directions are consistent after solving, block positions are correctly
    updated and consistent with the grid.
    """

    def setUp(self):
        """
        Initialize a Puzzle instance with: a predefined set of blocks, an empty
        block grid, laser starting configuration, goal coordinates

        The solver is places blocks into the grid to satisfy the goals.
        """
        self.p = Puzzle()

        # Define blocks.
        self.b1 = Refract([0, 2])
        self.b2 = Reflect([1, 3])
        self.b3 = Reflect([2, 0])

        # Empty grid initially (solve_puzzle() will populate it)
        block_grid = [[None, None, None, None],
                      [None, None, None, None],
                      [None, None, None, None],
                      [None, None, None, None]]

        self.p.block_grid = block_grid
        self.p.blocks = [self.b1, self.b2, self.b3]

        # Laser initial positions and directions
        self.p.laser_pos = [[(2, 7)]]
        self.p.laser_dir = [(1, -1)]

        # Goal coordinates that must be reached by laser paths
        self.p.goal_coords = [(4, 7), (2, 5), (3, 0), (4, 3)]

    def test_solve_puzzle(self):
        """Test that the puzzle solver successfully finds a solution."""
        self.assertTrue(self.p.solve_puzzle(), 'failed to solve puzzle.')

    def test_blockgrid_after_solving(self):
        """Test that the block grid matches expected solution after solving."""
        self.p.solve_puzzle()
        solution = [[None, None, self.b1, None],
                    [None, None, None, self.b2],
                    [self.b3, None, None, None],
                    [None, None, None, None]]
        self.assertEqual(self.p.block_grid, solution,
                         'solution grid does not match.')

    def test_laser_pos_after_solving(self):
        """
        Test that laser_pos contains all goal coordinates after solving.

        Verifies that the laser path(s) pass through all required goal points.
        """
        self.p.solve_puzzle()

        # Collect all positions from all laser paths.
        all_positions = set()
        for path in self.p.laser_pos:
            for pos in path:
                all_positions.add(pos)

        # Verify all goal coordinates are in laser positions.
        for goal in self.p.goal_coords:
            self.assertIn(goal, all_positions,
                          f'goal coordinate {goal} not found in laser path.')

    def test_laser_dir_after_solving(self):
        """
        Test that laser_dir has correct length after solving.

        Each laser path should have a corresponding direction entry.
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
                                      f'laser_dir[{i}] must be tuple or None.')
                self.assertEqual(len(direction), 2,
                                 f'laser_dir[{i}] must be length 2 (vx, vy).')
                vx, vy = direction
                self.assertIn(vx, [-1, 1],
                              f'laser_dir[{i}] vx should be -1 or 1.')
                self.assertIn(vy, [-1, 1],
                              f'laser_dir[{i}] vy should be -1 or 1.')

    def test_block_positions_after_solving(self):
        """
        Test that all blocks have correct positions after solving.

        Verifies each block's position attribute matches its location in
        block_grid.
        """
        self.p.solve_puzzle()

        # Expected positions for each block after solving.
        expected_positions = {
            self.b1: (0, 2),  # Refract block
            self.b2: (1, 3),  # Reflect block
            self.b3: (2, 0)   # Reflect block
        }

        # Verify each block's position attribute.
        for block, expected_pos in expected_positions.items():
            # Check position attribute matches expected.
            actual_pos = tuple(block.position) if isinstance(
                block.position, list) else block.position
            self.assertEqual(actual_pos, expected_pos,
                             (f'Block {block.type} position mismatch: '
                              f'{actual_pos} does not match {expected_pos}.'))
        # Verify blocks are in correct grid locations.
        for block in self.p.blocks:
            pos = block.position
            row, col = pos[0], pos[1]

            self.assertEqual(self.p.block_grid[row][col], block,
                             f'block {block.type} not found at grid position ({row}, {col}).')

        # Verify all blocks are placed (no none positions).
        for block in self.p.blocks:
            self.assertIsNotNone(block.position,
                                 f'block {block.type} has no position after solving.')


class TestAllFiles(unittest.TestCase):
    """
    Tests for solving multiple .bff puzzle files.

    Each test loads a puzzle from a file and verifies that solve_puzzle() can
    find a valid solution for that specific input configuration.
    """

    def test_Mad1(self):
        """Test that mad_1.bff can be solved."""
        p = Puzzle('mad_1.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')

    def test_Mad4(self):
        """Test that mad_4.bff can be solved."""
        p = Puzzle('mad_4.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')

    def test_Mad7(self):
        """Test that mad_7.bff can be solved."""
        p = Puzzle('mad_7.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')

    def test_dark1(self):
        """Test that dark_1.bff can be solved."""
        p = Puzzle('dark_1.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')

    def test_numbered6(self):
        """Test that numbered_6.bff can be solved."""
        p = Puzzle('numbered_6.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')

    def test_showstopper4(self):
        """Test that showstopper_4.bff can be solved."""
        p = Puzzle('showstopper_4.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')

    def test_yarn5(self):
        """Test that yarn_5.bff can be solved."""
        p = Puzzle('yarn_5.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')

    def test_tiny5(self):
        """Test that tiny_5.bff can be solved."""
        p = Puzzle('tiny_5.bff')
        self.assertTrue(p.solve_puzzle(), 'failed to solve puzzle.')


class TestDrawPuzzle(unittest.TestCase):
    """
    Unit tests for the draw_puzzle visualization function.

    These tests mock matplotlib components to verify that the correct plotting
    functions are called, the figure is configured properly, grid, blocks,
    goals, and laser paths are rendered, saving behavior works when the puzzle
    is solved.
    """

    def setUp(self):
        """
        Set up a mocked Puzzle instance with predefined grid, blocks, goals,
        and laser paths for visualization testing.
        """
        # Create a Puzzle instance without calling its __init__.
        self.puzzle = Puzzle.__new__(Puzzle)
        self.puzzle.file = "mad_1.bff"

        # Mock a 2x2 block grid with different block types.
        self.puzzle.block_grid = [[MagicMock(type="A"), None],
                                  [MagicMock(type="B"), MagicMock(type="C")]]

        # Mock blocks list (used for counting/legend/table).
        block_a = MagicMock(type="A")
        block_b = MagicMock(type="B")
        block_c = MagicMock(type="C")
        self.puzzle.blocks = [block_a, block_b, block_c, block_a]

        # Set goal coordinates.
        self.puzzle.goal_coords = [(0, 0), (2, 2)]

        # Set laser paths.
        self.puzzle.laser_pos = [[(0, 0), (1, 1)]]
        self.puzzle.laser_dir = [(1, 1)]

    @patch("laserproject.plt.show")
    @patch("laserproject.plt.savefig")
    @patch("laserproject.plt.subplots")
    def test_draw_puzzle_basic_calls(self, mock_subplots, mock_savefig,
                                     mock_show):
        """Test that draw_puzzle() makes the expected matplotlib calls."""
        # Mock subplots returning figure and axes.
        fig = MagicMock()
        ax = MagicMock()
        ax_table = MagicMock()

        mock_subplots.return_value = (fig, (ax, ax_table))

        # Run draw_puzzle() function.
        self.puzzle.draw_puzzle(solved=False)

        # Verify subplot creation.
        mock_subplots.assert_called_once()

        # Ensure the figure is displayed.
        mock_show.assert_called_once()

        # Ensure grid/blocks are drawn.
        self.assertTrue(ax.add_patch.called)

        # Ensure goals and laser paths are plotted.
        self.assertTrue(ax.scatter.called)

        # Ensure legend/table are created.
        self.assertTrue(ax_table.table.called)
        self.assertTrue(ax_table.legend.called)

    @patch("laserproject.plt.show")
    @patch("laserproject.plt.savefig")
    @patch("laserproject.plt.subplots")
    def test_draw_puzzle_solved_saves_figure(self, mock_subplots, mock_savefig,
                                             mock_show):
        """Test that the figure is saved when the puzzle is solved."""
        fig = MagicMock()
        ax = MagicMock()
        ax_table = MagicMock()

        mock_subplots.return_value = (fig, (ax, ax_table))

        self.puzzle.draw_puzzle(solved=True)

        # When solved=True, the figure should be saved with a filename
        mock_savefig.assert_called_once_with("mad_1_solved.png")

    @patch("laserproject.plt.show")
    @patch("laserproject.plt.subplots")
    def test_block_colors_and_patches(self, mock_subplots, mock_show):
        """Test that grid cells are plotted as patches."""
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
        """Test that laser paths are plotted using scatter and line plots."""
        fig = MagicMock()
        ax = MagicMock()
        ax_table = MagicMock()

        mock_subplots.return_value = (fig, (ax, ax_table))

        self.puzzle.draw_puzzle(solved=False)

        # Laser visualization should involve scatter and line plotting
        self.assertTrue(ax.scatter.called)
        self.assertTrue(ax.plot.called)

    @patch("laserproject.plt.show")
    @patch("laserproject.plt.subplots")
    def test_axes_properties(self, mock_subplots, mock_show):
        """Test that axes are configured correctly for visualization."""
        fig = MagicMock()
        ax = MagicMock()
        ax_table = MagicMock()

        mock_subplots.return_value = (fig, (ax, ax_table))

        self.puzzle.draw_puzzle()

        # Verify axis formatting.
        ax.set_xlim.assert_called()
        ax.set_ylim.assert_called()
        ax.set_aspect.assert_called_with('equal')
        ax.axis.assert_called_with('off')
        ax_table.axis.assert_called_with('off')


if __name__ == "__main__":
    unittest.main()
