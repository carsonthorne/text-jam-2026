from board_layout import HEX_DIRECTIONS, HOME_ZONES

def add_coords(a, b):
    
        return (a[0] + b[0], a[1] + b[1])

def get_zone_for_coord(coord):
    
    for zone_name, coords in HOME_ZONES.items():

        if coord in coords:
            return zone_name
        
    return None

def is_adjacent_move(move_from, move_to):

    for direction in HEX_DIRECTIONS:

        neighbor = add_coords(move_from, direction)

        if neighbor == move_to:
            return True
    
    return False

def is_jump_move(board, move_from, move_to):

    for direction in HEX_DIRECTIONS:

        middle = add_coords(move_from, direction)

        landing = add_coords(middle, direction)

        if landing == move_to and middle in board and board[middle] is not None:

            return True
    
    return False