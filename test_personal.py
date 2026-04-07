from laser_test import *
from unittest.mock import patch, MagicMock
import matplotlib

matplotlib.use("Agg")

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