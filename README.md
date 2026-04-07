# Laser Puzzle Solver

A Python solver for laser puzzles in board file format (.bff). Given a puzzle with a grid, fixed blocks, laser starting point and direction, goal points, and movable blocks, the code finds the correct placement of blocks so that the laser path passes through all goal points.

## How It Works

The solver reads a `.bff` file containing:
- grid layout with fixed and empty cells
- fixed blocks already placed on the board
- laser starting position and direction
- goal points the laser must pass through
- movable blocks (Reflect, Refract, Opaque) to place

The solution is found by checking all possible block placement combinations until the laser path hits every goal point.

## Features

- solves laser puzzles by testing all valid block configurations
- visualizes the board before and after solving
- saves solution as a PNG image

## Requirements

This code uses the following Python packages:
- `itertools` (combinations)
- `matplotlib` (pyplot, patches, lines)
- `collections` (Counter)
- `unittest` (unittest.mock patch, MagicMock)

## Usage

Example of solving a puzzle (`mad_1.bff`) in `laserproject.py`:

```python
file = 'mad_1.bff'
p = Puzzle(file)  # load in the puzzle
p.draw_puzzle()  # view the initial board before solving

solve = p.solve_puzzle()  # solve; True if solution found, False otherwise

if solve:
    p.draw_puzzle(solved=True)  # view the board after solving
```

If the puzzle is solved, the solution image is saved as ```{board name} solved.png```.

## Testing

All unit tests are in laser_tests.py. Tests verify that all methods produce expected results and handle edge cases.

To run all tests, run this on terminal or simply run the script on any IDE:
```bash 
python3 laser_tests.py
```

## Authors
Jessie Huh (shuh4@jh.edu)

Sabrina Chen (schen286@jh.edu)
