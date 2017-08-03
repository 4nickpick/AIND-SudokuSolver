import pygame

assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    """Cross product of elements in A and elements in B."""
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

# Configure the diagonal sets to satisfy the diagonal constraint
diagonal_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'],
                  ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - {s}) for s in boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # print("Before Naked Twins ------------")
    # display(values)

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # Loop through each row, column square and diagonal one at a time in order to fine naked twins in these units
    for unit_collection in [row_units, column_units, square_units, diagonal_units]:

        # The unit is either a row, column, square or diagonal
        for unit in unit_collection:

            # collect boxes that have just two possible values
            potential_naked_twins = [box for box in unit if len(values[box]) == 2]

            # there aren't enough potential naked twins to keep checking this unit
            if len(potential_naked_twins) < 2:
                continue

            # set up a dictionary for storing valid naked twin pairs
            naked_twin_sets = {}

            # store each potential naked twin in a dictionary, paired together by their possible values as the key
            for potential_naked_twin in potential_naked_twins:
                if values[potential_naked_twin] not in naked_twin_sets:
                    naked_twin_sets[values[potential_naked_twin]] = [potential_naked_twin]
                else:
                    naked_twin_sets[values[potential_naked_twin]].append(potential_naked_twin)

            # look to see if we have any pairs of matching twins
            valid_naked_twins = {}
            for naked_twin_shared_value, naked_twin_pair in naked_twin_sets.items():
                if len(naked_twin_pair) != 2:
                    continue

                if naked_twin_shared_value not in valid_naked_twins:
                    valid_naked_twins[naked_twin_shared_value] = [naked_twin_pair]
                else:
                    valid_naked_twins[naked_twin_shared_value].append(naked_twin_pair)

            if len(valid_naked_twins) > 0:
                for valid_naked_twin_set in valid_naked_twins:

                    for box_in_unit in unit:
                        if box_in_unit in naked_twin_sets[valid_naked_twin_set]:
                            continue

                        for digit in valid_naked_twin_set:
                            if digit in values[box_in_unit]:
                                assign_value(values, box_in_unit, values[box_in_unit].replace(digit, ''))

    # print("After Naked Twins ------------")
    # display(values)

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    if not hasattr(values, "__getitem__"):
        print("This grid cannot be displayed")
        return

    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values


def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, try all possible values."""
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    values = grid_values(grid)
    # print("Initial Values ------------")
    # display(values)

    values = search(values)

    return values


def printd(str_to_print):
    debug = True
    if debug:
        print(str_to_print)

if __name__ == '__main__':
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'

    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
