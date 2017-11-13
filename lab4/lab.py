"""
6.009 Lab 4 -- HyperMines
an n-dimensional game of minesweeper
"""

import sys
sys.setrecursionlimit(10000)


def dump(game):
    """Print a human-readable representation of game.

    Arguments:
       game (dict): Game state


    >>> dump({'dimensions': [1, 2], 'mask': [[False, False]], 'board': [['.', 1]], 'state': 'ongoing'})
    dimensions: [1, 2]
    board: ['.', 1]
    mask:  [False, False]
    state: ongoing
    """
    lines = ["dimensions: {}".format(game["dimensions"]),
             "board: {}".format("\n       ".join(map(str, game["board"]))),
             "mask:  {}".format("\n       ".join(map(str, game["mask"]))),
             "state: {}".format(game["state"])]
    print("\n".join(lines))

def nd_new_game(dims, bombs):
    """Start a new game.

    Return a game state dictionary, with the "board" and "mask" fields
    adequately initialized.  This is an N-dimensional version of new_game().

    Args:
       dims (list): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> dump(nd_new_game([2, 4, 2], [[0, 0, 1], [1, 0, 0], [1, 1, 1]]))
    dimensions: [2, 4, 2]
    board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
           [['.', 3], [3, '.'], [1, 1], [0, 0]]
    mask:  [[False, False], [False, False], [False, False], [False, False]]
           [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """

    board = make_board(dims, val = 0)
    mask = make_board(dims, val = False)
    for coords in bombs: #place bombs
        place_bombs(board, coords, True)

    return {'dimensions': dims, 'board': board, 'mask': mask, 'state': 'ongoing'}


def nd_dig(game, coords):
    """Recursively dig up square at coords and neighboring squares.

    Update game["mask"] to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No action
    should be taken and 0 returned if the incoming state of the game is not "ongoing".

    The updated state is "defeat" when at least one bomb is visible on the board
    after digging (i.e. game["mask"][bomb_location] == True), "victory" when all
    safe squares (squares that do not contain a bomb) and no bombs are visible,
    and "ongoing" otherwise.

    This is an N-dimensional version of dig().

    Args:
       game (dict): Game state
       coords (list): Where to start digging

    Returns:
       int: number of squares revealed

    >>> game = {"dimensions": [2, 4, 2],
    ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
    ...                  [[False, False], [False, False], [False, False], [False, False]]],
    ...         "state": "ongoing"}
    >>> nd_dig(game, [0, 3, 0])
    8
    >>> dump(game)
    dimensions: [2, 4, 2]
    board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
           [['.', 3], [3, '.'], [1, 1], [0, 0]]
    mask:  [[False, False], [False, True], [True, True], [True, True]]
           [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> game = {"dimensions": [2, 4, 2],
    ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
    ...                  [[False, False], [False, False], [False, False], [False, False]]],
    ...         "state": "ongoing"}
    >>> nd_dig(game, [0, 0, 1])
    1
    >>> dump(game)
    dimensions: [2, 4, 2]
    board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
           [['.', 3], [3, '.'], [1, 1], [0, 0]]
    mask:  [[False, True], [False, True], [False, False], [False, False]]
           [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    if game['state'] in ["defeat","victory"]: #dont do anything
        return 0

    if tile_op(game['board'], coords, sett = False) == '.': #if tile chosen is a bomb, dig and lose game
        tile_op(game['mask'], coords, sett = True)
        game['state'] = 'defeat'
        return 1

    revealed = 0
    coords = [coords]
    while len(coords) > 0:
        new_coords, r = dig_tile(game['mask'], game['board'], game['dimensions'], coords.pop())
        revealed += r #add number revealed by opperation, either 1 or 0
        coords += new_coords #add new coords if a 0 which was covered

    if is_victory(game['board'], game['mask']): #check if they won
        game['state'] = 'victory'

    return revealed

def nd_render(game, xray=False):
    """Prepare a game for display.

    Returns an N-dimensional array (nested lists) of "_" (hidden squares), "."
    (bombs), " " (empty squares), or "1", "2", etc. (squares neighboring bombs).
    game["mask"] indicates which squares should be visible.  If xray is True (the
    default is False), game["mask"] is ignored and all cells are shown.

    This is an N-dimensional version of render().

    Args:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game["mask"]

    Returns:
       An n-dimensional array (nested lists)

    >>> nd_render({"dimensions": [2, 4, 2],
    ...            "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                      [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...            "mask": [[[False, False], [False, True], [True, True], [True, True]],
    ...                     [[False, False], [False, False], [True, True], [True, True]]],
    ...            "state": "ongoing"},
    ...           False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> nd_render({"dimensions": [2, 4, 2],
    ...            "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                      [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...            "mask": [[[False, False], [False, True], [False, False], [False, False]],
    ...                     [[False, False], [False, False], [False, False], [False, False]]],
    ...            "state": "ongoing"},
    ...           True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    return render_helper(game['board'], game['mask'], xray)

######################
## HELPER FUNCTIONS ##
######################

def make_board(dim, val):
    '''
    recursively generate a non-linked nest of lists with dimensions given

    Args:
        dim (list): dimensions of board
        val: value to make homogenous board from

    >>> print(make_board([1, 3, 2, 2], False))
    [[[[False, False], [False, False]], [[False, False], [False, False]], [[False, False], [False, False]]]]
    '''
    if len(dim) == 1: #row of zeros
        return [val for i in range(dim[0])]
    else: #row of sublists
        return [make_board(dim[1:], val) for i in range(dim[0])]

def place_bombs(fragment, dim, bomb):
    '''
    puts bomb in the grid and adds one to each neighbor

    Args:
        fragment (nested list): n-dimensional list
        dim (list): location of the bomb
        bomb (bool): keeps track of whether recursion is on the path to correct location to place bomb

    Returns:
        None

    >>> board = make_board([2, 4, 2], 0)
    >>> place_bombs(board, [1,1,1], True)
    >>> print(board)
    [[[1, 1], [1, 1], [1, 1], [0, 0]], [[1, 1], [1, '.'], [1, 1], [0, 0]]]
    '''
    d0 = dim[0]
    if len(dim) == 1:
        for d in range(max(d0-1, 0), min(d0+2, len(fragment))):
            try: fragment[d] +=1 #add one to bomb neighbors
            except: pass #for when yiu hit a bomb
        if bomb: fragment[d0] = '.' #place bomb in middle
    else:
        for i in range(max(d0-1, 0), min(d0+2, len(fragment))):
            place_bombs(fragment[i], dim[1:], bomb and i == d0) #recurse on range of 3 indices centered at bomb

def get_hypercube(cen, mins, maxs):
    '''
    generates a hypercube or side length 3 centered about a single location

    Args:
        cen (list): center location
        mins (list): list of minimum value for each dimension
        maxs (list): list of maximum allowed values for each dimension

    Returns:
        indices (list): list of locations in hypercube

    >>> print(get_hypercube([0, 4, 3], [0,0,0,0], [4, 4, 4]))
    [[0, 3, 2], [0, 3, 3], [1, 3, 2], [1, 3, 3]]
    '''
    c = cen[0]
    indices = []
    if len(cen) == 1:
        for i in range(c-1, c+2): #3 dimensions about the center
            if mins[0] <= i < maxs[0]:
                indices += [[i]] #start with single diemsnional locations
    else:
        sub = get_hypercube(cen[1:], mins[1:], maxs[1:])
        for d in [c-1, c, c+1]:
            if mins[0] <= d < maxs[0]: #make sure the dimension is within the bounds
                for s in sub:
                   indices.append([d]+s) #get 3 new n+1 dimensional locations for each n-dimensional sub_location
    return indices

def tile_op(tile, dim, sett = False):
    '''
    either get or set a value for a tile

    Args:
        tile (list): the board which will eventually become the tile of interest
        dim (list): location
        sett: value to set to the tile (unless it's false, in which case it returns the value at the tile)

    Returns:
        if sett == False: value of tile
        elif tile already was equal to value being set: 1
        else: 0

    >>> game = nd_new_game([2, 4, 2], [[0, 0, 1], [1, 0, 0], [1, 1, 1]])
    >>> dim = [1, 3, 0]
    >>> print(tile_op(game['board'], dim, sett = 5))
    1
    >>> print(tile_op(game['board'], dim, sett = 5))
    0
    '''
    if len(dim) == 1:
        if sett: #if it is supposed to assign a particular value
            if tile[dim[0]] == sett:
                return 0 #return 0 if the tile is unchanged
            else:
                tile[dim[0]] = sett
                return 1 #return 1 if the tile is changed
        else:
            return tile[dim[0]] #return value of tile
    else:
        return tile_op(tile[dim[0]], dim[1:], sett) #recursvely find tile

def dig_tile(mask, board, board_dim, dim):
    '''
    Dig a tile by revelain gits mask

    Args:
        mask (list):board mask
        board (list): board
        board_dim (list): board dimensions
        dim (list): location of the dig

    Returns:
        cube (list): list of indices around tile
            only returned if the tile was dug and was a 0
        revealed (int): 1 if the tile was dug, otherwise zero

    >>> game = nd_new_game([2, 4, 2], [[0, 0, 1], [1, 0, 0], [1, 1, 1]])
    >>> dim = [1, 3, 0]
    >>> print(dig_tile(game['board'], game['mask'], game['dimensions'], dim))
    ([[0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [1, 2, 0], [1, 2, 1], [1, 3, 0], [1, 3, 1]], 1)
    >>> print(dig_tile(game['board'], game['mask'], game['dimensions'], dim))
    ([], 0)
    '''
    revealed = tile_op(mask, dim, True)
    value = tile_op(board, dim)
    if value == 0 and revealed: #if it was covered and the board value is zero
        cube = get_hypercube(dim, [0] * len(board_dim), board_dim)
    else:
        cube = [] #no new indices otherwise
    return (cube, revealed)

def is_victory(board, mask):
    '''
    Checks if the board is in a state of victory

    Args:
        board (list): game board
        mask: (list): game mask
    Returns:
        boolean value of whether game was won

    >>> game = nd_new_game([3, 3, 3], [[0, 0, 0]])
    >>> print(is_victory(game['board'], game['mask']))
    False
    >>> nd_dig(game, [2, 2, 2])
    26
    >>> print(is_victory(game['board'], game['mask']))
    True
    '''
    if type(board[0]) != list:
        bombs = len(list(filter(lambda x: x == '.', board)))
        covered = len(mask) - sum(mask)
        if bombs == covered: #checks if number of bombs is equal to the number of covered tiles
            #doesnt need to check that bombs and covered tiles are aligned since dig_tile checks if defeat
            return True
    else:
        for i in range(len(board)):
            if not is_victory(board[i], mask[i]):
                return False
        return True #only return true if none of the recursions returned false

def render_helper(board, mask, xray):
        '''
        recursively render a board and mask

        Args:
            board (list): n-dimenisonal list for board values
            mask (list): n dimensional list for whether board values are covered
            xray (boolean): tells it whether to just reveal everything

        Return:
            rend (list):An n-dimensional array render

        >>> game = nd_new_game([3, 3, 3], [[0, 1, 0]])
        >>> print(render_helper(game['board'], game['mask'], True))
        [[['1', '1', ' '], ['.', '1', ' '], ['1', '1', ' ']], [['1', '1', ' '], ['1', '1', ' '], ['1', '1', ' ']], [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]]
        >>> print(render_helper(game['board'], game['mask'], False))
        [[['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']], [['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']], [['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']]]
        >>> nd_dig(game, [2, 1, 2])
        24
        >>> print(render_helper(game['board'], game['mask'], False))
        [[['_', '1', ' '], ['_', '1', ' '], ['_', '1', ' ']], [['1', '1', ' '], ['1', '1', ' '], ['1', '1', ' ']], [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]]
        '''
        rend = []
        if type(board[0]) != list: #once fully recursed, evaluate each value in board/mask pair to render
            for i in range(len(board)):
                if (not xray) and (not mask[i]): #if masked and xray is false, put a '_'
                    rend.append('_')
                elif board[i] == 0: #else, if there is a zero, just put a space
                    rend.append(' ')
                else: #otherwise put a string representation of the number
                    rend.append(str(board[i]))
        else:
            for i in range(len(board)): #recurse until reach last dimension
                rend.append(render_helper(board[i], mask[i], xray))
        return rend

if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
