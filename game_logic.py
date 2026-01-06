def is_valid_move(board, row, col):
    if row < 0 or row >= 10 or col < 0 or col >= 10:
        return False
    if board['grid'][row][col] != 0:
        return False
    return True

def check_win(board):
    if check_player1_win(board):
        return 1
    if check_player2_win(board):
        return 2
    return None

def check_player1_win(board):
    grid = board['grid']
    visited = [[False] * 10 for _ in range(10)]
    
    for col in range(10):
        if grid[0][col] == 1:
            if dfs_vertical(grid, visited, 0, col, 1):
                return True
    return False

def check_player2_win(board):
    grid = board['grid']
    visited = [[False] * 10 for _ in range(10)]
    
    for row in range(10):
        if grid[row][0] == 2:
            if dfs_horizontal(grid, visited, row, 0, 2):
                return True
    return False

def dfs_vertical(grid, visited, row, col, player):
    if row == 9:
        return True
    
    visited[row][col] = True
    
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        
        if (0 <= new_row < 10 and 0 <= new_col < 10 and 
            not visited[new_row][new_col] and 
            grid[new_row][new_col] == player):
            
            if dfs_vertical(grid, visited, new_row, new_col, player):
                return True
    
    return False

def dfs_horizontal(grid, visited, row, col, player):
    if col == 9:
        return True
    
    visited[row][col] = True
    
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        
        if (0 <= new_row < 10 and 0 <= new_col < 10 and 
            not visited[new_row][new_col] and 
            grid[new_row][new_col] == player):
            
            if dfs_horizontal(grid, visited, new_row, new_col, player):
                return True
    
    return False