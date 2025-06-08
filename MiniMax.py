import random

# Define evaluation scores
WIN_SCORE = 1000000
POTENTIAL_WIN_SCORES = {4: 50000, 3: 5000, 2: 500, 1: 50}

def get_relevant_moves(board, board_size, radius=1):
    Place_not_empty = False
    moves = []
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] != '.':
                Place_not_empty = True
                break
        if Place_not_empty:
            break
    if not Place_not_empty:
        center = board_size // 2
        return [(center, center)]
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] == '.':   
                is_relevant = False  
                for di in range(-radius, radius + 1): 
                    for dj in range(-radius, radius + 1): 
                        ni, nj = i + di, j + dj 
                        if 0 <= ni < board_size and 0 <= nj < board_size and board[ni][nj] != '.':
                            is_relevant = True
                            break
                    if is_relevant:
                        break
                if is_relevant:
                    moves.append((i, j))
    # Ensure we always return a list
    result = moves if moves else [(i, j) for i in range(board_size) for j in range(board_size) if board[i][j] == '.']
    return result



def evaluate_board(board, board_size, win_length):
    score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    # Check each position on the board as a potential start of a winning line
    for i in range(board_size):
        for j in range(board_size):
            # For each direction
            for di, dj in directions:
                # Skip if this position can't be the start of a winning line
                end_i, end_j = i + (win_length-1)*di, j + (win_length-1)*dj
                if not (0 <= end_i < board_size and 0 <= end_j < board_size):
                    continue
                
                # Count pieces in this line
                x_count = o_count = empty_count = 0
                
                for k in range(win_length):
                    cell = board[i + k*di][j + k*dj]
                    if cell == 'X':
                        x_count += 1
                    elif cell == 'O':
                        o_count += 1
                    else:  
                        empty_count += 1
                
                # Only evaluate lines that could lead to a win
                if x_count > 0 and o_count == 0:  
                    if x_count == win_length: 
                        return -WIN_SCORE
                    score -= POTENTIAL_WIN_SCORES[x_count]
                    
                    # Increase defensive score for near-wins but don't overemphasize
                    if x_count == win_length - 1 and empty_count == 1:
                        score -= 90000  
                        
                elif o_count > 0 and x_count == 0: 
                    if o_count == win_length: 
                        return WIN_SCORE
                    
                    # Increase offensive score to prioritize winning
                    score += POTENTIAL_WIN_SCORES[o_count] * 1.2  
                    
                    # Make AI more aggressive about completing its own wins
                    if o_count == win_length - 1 and empty_count == 1:
                        score += 120000  
    
    return score

def minimax_no_pruning(board, board_size, win_length, is_maximizing, get_legal_moves, is_terminal, check_win, depth, max_depth):
    if check_win(board, 'X'):
        return -WIN_SCORE
    if check_win(board, 'O'):
        return WIN_SCORE
    if is_terminal(board):
        return 0
    if depth == max_depth:
        return evaluate_board(board, board_size, win_length)

    moves = get_relevant_moves(board, board_size)

    move_scores = []
    for move in moves:
        row, col = move
        board[row][col] = 'O' if is_maximizing else 'X'
        score = evaluate_board(board, board_size, win_length)
        board[row][col] = '.'
        move_scores.append((score, move))
    moves = [move for _, move in sorted(move_scores, key=lambda x: x[0], reverse=is_maximizing)]

    if is_maximizing:
        best_score = float('-inf')
        for move in moves:
            row, col = move
            board[row][col] = 'O'
            score = minimax_no_pruning(board, board_size, win_length, False, get_legal_moves, is_terminal, check_win, depth + 1, max_depth)
            board[row][col] = '.'
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for move in moves:
            row, col = move
            board[row][col] = 'X'
            score = minimax_no_pruning(board, board_size, win_length, True, get_legal_moves, is_terminal, check_win, depth + 1, max_depth)
            board[row][col] = '.'
            best_score = min(score, best_score)
        return best_score

def find_best_move_minimax(board, board_size, get_legal_moves, is_terminal, check_win, max_depth=3):
    win_length = 5
    best_move = None
    best_score = float('-inf')
    moves = get_relevant_moves(board, board_size)
    
    if not isinstance(moves, list):
        print(f"Error: find_best_move_minimax received non-list moves: {moves}")
        return None
    
    # Check for immediate winning moves first
    for move in moves:
        row, col = move
        board[row][col] = 'O'
        if check_win(board, 'O'):
            board[row][col] = '.'
            return move
        board[row][col] = '.'
    
    # Check for moves that block opponent's immediate win
    for move in moves:
        row, col = move
        board[row][col] = 'X'  
        if check_win(board, 'X'):  
            board[row][col] = '.'  
            board[row][col] = 'O'  
            score = minimax_no_pruning(board, board_size, win_length, False, get_legal_moves, is_terminal, check_win, 1, max_depth)
            board[row][col] = '.'
            if score > best_score:
                best_score = score
                best_move = move
    
    # If we found a blocking move, return it
    if best_move is not None:
        return best_move
        
    # Otherwise, evaluate all moves as before
    move_scores = []
    for move in moves:
        row, col = move
        board[row][col] = 'O'
        try:
            score = evaluate_board(board, board_size, win_length)
        finally:
            board[row][col] = '.'
        move_scores.append((score, move))
    
    # Sort moves by score from highest to lowest
    moves = [move for _, move in sorted(move_scores, key=lambda x: x[0], reverse=True)]
    
    for move in moves:
        row, col = move
        board[row][col] = 'O'
        score = minimax_no_pruning(board, board_size, win_length, False, get_legal_moves, is_terminal, check_win, 1, max_depth)
        board[row][col] = '.'
        if score > best_score:
            best_score = score
            best_move = move
        if best_score >= WIN_SCORE:
            break
    
    return best_move


def  minimax_With_pruning(board, board_size, win_length, is_maximizing, get_legal_moves, is_terminal, check_win, 
            depth, max_depth, alpha, beta):
    if check_win(board, 'X'):
        return -WIN_SCORE
    if check_win(board, 'O'):
        return WIN_SCORE
    if is_terminal(board):
        return 0
    if depth == max_depth:
        return evaluate_board(board, board_size, win_length)

    moves = get_relevant_moves(board, board_size)
    move_scores = []

    for move in moves:
        row, col = move
        board[row][col] = 'O' if is_maximizing else 'X'
        score = evaluate_board(board, board_size, win_length)
        board[row][col] = '.'
        move_scores.append((score, move))
    moves = [move for _, move in sorted(move_scores, key=lambda x: x[0], reverse=is_maximizing)]

    if is_maximizing:
        best_score = float('-inf')
        for move in moves:
            row, col = move
            board[row][col] = 'O'
            score = minimax_With_pruning(board, board_size, win_length, False, get_legal_moves, is_terminal, 
                                    check_win, depth + 1, max_depth, alpha, beta)
            board[row][col] = '.'
            best_score = max(score, best_score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = float('inf')
        for move in moves:
            row, col = move
            board[row][col] = 'X'
            score = minimax_With_pruning(board, board_size, win_length, True, get_legal_moves, is_terminal, 
                                    check_win, depth + 1, max_depth, alpha, beta)
            board[row][col] = '.'
            best_score = min(score, best_score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score

def find_best_move_with_alpha_beta(board, board_size, get_legal_moves, is_terminal, check_win, max_depth=3):
    win_length = 5
    best_move = None
    best_score = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    moves = get_relevant_moves(board, board_size)
    
    # Check for immediate winning moves first
    for move in moves:
        row, col = move
        board[row][col] = 'O'
        if check_win(board, 'O'):
            board[row][col] = '.'
            return move
        board[row][col] = '.'
    
    # Check for moves that block opponent's immediate win
    for move in moves:
        row, col = move
        board[row][col] = 'X'  
        if check_win(board, 'X'):  
            board[row][col] = '.' 
            board[row][col] = 'O' 
            score = minimax_With_pruning(board, board_size, win_length, False, get_legal_moves, is_terminal, 
                                    check_win, 1, max_depth, alpha, beta)
            board[row][col] = '.'
            if score > best_score:
                best_score = score
                best_move = move
    
    # If we found a blocking move, return it
    if best_move is not None:
        return best_move
    
    # Otherwise, evaluate all moves as before
    move_scores = []
    for move in moves:
        row, col = move
        board[row][col] = 'O'
        try:
            score = evaluate_board(board, board_size, win_length)
        finally:
            board[row][col] = '.'
        move_scores.append((score, move))
    
    # Sort moves by score from highest to lowest
    moves = [move for _, move in sorted(move_scores, key=lambda x: x[0], reverse=True)]
    
    for move in moves:
        row, col = move
        board[row][col] = 'O'
        score = minimax_With_pruning(board, board_size, win_length, False, get_legal_moves, is_terminal, 
                                check_win, 1, max_depth, alpha, beta)
        board[row][col] = '.'
        if score > best_score:
            best_score = score
            best_move = move
        if best_score >= WIN_SCORE:
            break
    
    return best_move


