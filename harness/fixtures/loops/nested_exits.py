# feature: loops
# summary: breaking out of nested loops via flags/else/return, continue in nested loops, early returns


def find_pair(grid, target):
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value == target:
                return (r, c)
    return None


def flag_exit(grid):
    found = None
    for row in grid:
        for value in row:
            if value < 0:
                found = value
                break
        if found is not None:
            break
    return found


def else_exit(grid):
    for row in grid:
        for value in row:
            if value == 0:
                break
        else:
            continue
        return 'zero found in %r' % (row,)
    return 'no zero'


def skip_odd_rows(grid):
    acc = []
    for i, row in enumerate(grid):
        if i % 2:
            continue
        for value in row:
            if value % 2 == 0:
                continue
            acc.append(value)
    return acc


def observe():
    grid = [[1, 2, 3], [4, -5, 6], [7, 0, 9]]
    return [find_pair(grid, 6), find_pair(grid, 42), flag_exit(grid), flag_exit([[1]]),
            else_exit(grid), else_exit([[1, 2]]), skip_odd_rows(grid)]
