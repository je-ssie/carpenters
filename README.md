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

## Interpreting solution board

This is the produced solution image for tiny_5.bff:

<img width="400" height="300" alt="tiny_5 bff solved" src="https://github.com/user-attachments/assets/8d812bca-38a2-402d-9c4b-532bdebd1aca" />

The laser point coordinate system works as follows: 
- upper left corner is the origin (0,0), where +x is to the right and +y is towards the bottom.
- every half of a block is one coordinate unit.

How to read the board:
- Using this coordinate system, the starting laser point (filled red dot) is at coordinate ```(4, 5)```.
- As per the legend, the starting point is on the face of a ```Refract``` block. Therefore the laser splits its path to two, one going through the block along the initial direction and one reflecting off of the block into another direction. The laser points along each path is marked by the small white dots, and are connected by red lines to indicate its path.
- The goal points are marked by bigger white circles, and are positioned at ```(1, 2)```, ```(6, 3)```. The red laser paths pass through all goal points, confirming that it is a solution.
- The solution block placements can clearly be read from the image. For this board, the block grid in .bff-style would be:
  ```bash
  A B A
  o o o
  A C o
  ```

## Testing

All unit tests are in laser_tests.py. Tests verify that all methods produce expected results and handle edge cases.

To run all tests, run this on terminal or simply run the script on any IDE:
```bash 
python3 laser_tests.py
```

## Authors
Jessie Huh (shuh4@jh.edu)

Sabrina Chen (schen286@jh.edu)
