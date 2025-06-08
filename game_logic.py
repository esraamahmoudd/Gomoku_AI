import threading
import time
import random
import copy
from MiniMax import *

# Debug: Confirm MiniMax module path
print(f"Using MiniMax.py from: {__import__('MiniMax').__file__}")

BOARD_SIZE = 15
WIN_LENGTH = 5

def setboardsize():
    global BOARD_SIZE, WIN_LENGTH
    while True:
        try:
            size = int(input("Enter board size (min 5, default 15): ") or 15)
            if size > 4:
                BOARD_SIZE = size
                break
            else:
                print("Size must be at least 5.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def createboard():
    board = []
    for i in range(BOARD_SIZE):
        row = []
        for j in range(BOARD_SIZE):
            row.append('.')
        board.append(row)
    return board

def printboard(board):
    print("   " + " ".join(f"{j:2}" for j in range(BOARD_SIZE)))
    for i, row in enumerate(board):
        print(f"{i:2} " + "  ".join(row))
    print()


def check_win(board, player):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if all(col + i < BOARD_SIZE and board[row][col + i] == player for i in range(WIN_LENGTH)) or \
               all(row + i < BOARD_SIZE and board[row + i][col] == player for i in range(WIN_LENGTH)) or \
               all(row + i < BOARD_SIZE and col + i < BOARD_SIZE and board[row + i][col + i] == player for i in range(WIN_LENGTH)) or \
               all(row + i < BOARD_SIZE and col - i >= 0 and board[row + i][col - i] == player for i in range(WIN_LENGTH)):
                return True
    return False

def is_terminal(board):
    return check_win(board, 'X') or check_win(board, 'O') or all(cell != '.' for row in board for cell in row)

def get_legal_moves(board):
    return [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if board[i][j] == '.']

def human_move(board, player):
    while True:
        try:
            move = input(f"Player {player}, enter your move (row,col): ")
            row, col = map(int, move.strip().split(','))
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[row][col] == '.':
                board[row][col] = player
                break
            else:
                print("Invalid move.")
        except:
            print("Invalid input format. Use row,col (e.g. 3,4)")
    printboard(board)

def simple_move_strategy(board, player):
    opponent = 'X' if player == 'O' else 'O'
    # Check for immediate win
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == '.':
                board[i][j] = player
                if check_win(board, player):
                    board[i][j] = '.'
                    return (i, j)
                board[i][j] = '.'
    # Check for immediate block (opponent win)
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == '.':
                board[i][j] = opponent
                if check_win(board, opponent):
                    board[i][j] = '.'
                    return (i, j)
                board[i][j] = '.'
    # Check for opponent’s four-in-a-row threat
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == '.':
                board[i][j] = opponent
                if (
                    sum(1 for k in range(WIN_LENGTH) if i+k < BOARD_SIZE and board[i+k][j] == opponent) == 4 or
                    sum(1 for k in range(WIN_LENGTH) if j+k < BOARD_SIZE and board[i][j+k] == opponent) == 4 or
                    sum(1 for k in range(WIN_LENGTH) if i+k < BOARD_SIZE and j+k < BOARD_SIZE and board[i+k][j+k] == opponent) == 4 or
                    sum(1 for k in range(WIN_LENGTH) if i+k < BOARD_SIZE and j-k >= 0 and board[i+k][j-k] == opponent) == 4
                ):

                    board[i][j] = '.'
                    return (i, j)
                board[i][j] = '.'
    # Prefer moves near existing pieces
    valid_moves = get_relevant_moves(board, BOARD_SIZE, radius=1)
    if valid_moves:
        return random.choice(valid_moves)
    if board[BOARD_SIZE//2][BOARD_SIZE//2] == '.':
        return (BOARD_SIZE//2, BOARD_SIZE//2)
    legal_moves = get_legal_moves(board)
    return random.choice(legal_moves) if legal_moves else None


def AI_move(board, player, difficulty, use_alpha_beta=True):
    board_size = len(board)

    max_depth = {1: 1, 2: 2, 3: 3, 4: 4}.get(difficulty, 2)

    if difficulty == 1 and random.random() < 0.3:
        legal_moves = get_legal_moves(board)
        if legal_moves:
            row, col = random.choice(legal_moves)
            board[row][col] = player
            print(f"AI ({player}) placed at position ({row}, {col}) [random easy]")
            return

    if difficulty >= 3:
        global POTENTIAL_WIN_SCORES
        original_scores = POTENTIAL_WIN_SCORES.copy()
        POTENTIAL_WIN_SCORES = {4: 60000, 3: 6000, 2: 600, 1: 60}

    move_result = [None]
    timer_event = threading.Event()

    def find_move_thread():
        try:
            board_copy = copy.deepcopy(board)
            find_best = find_best_move_with_alpha_beta if use_alpha_beta else find_best_move_minimax
            move_result[0] = find_best(board_copy, board_size, get_legal_moves, is_terminal, check_win, max_depth)
        finally:
            timer_event.set()

    thread = threading.Thread(target=find_move_thread)
    thread.start()
    thread.join(timeout=10.0)

    if thread.is_alive():
        print("AI took too long. Using fallback move.")
        move = simple_move_strategy(board, player)
    else:
        move = move_result[0]

    if difficulty >= 3:
        POTENTIAL_WIN_SCORES = original_scores

    if move:
        row, col = move
        board[row][col] = player
        print(f"AI ({player}) placed at position ({row}, {col})")
        printboard(board)
    else:
        print("AI couldn't find a valid move.")


def playgame():
    setboardsize()
    board = createboard()
    print("Select Game Mode:")
    print("1 --> Human vs Human")
    print("2 --> Human vs AI (Hard, Minimax)")
    print("3 --> AI vs AI (Minimax vs Alpha-Beta)")

    while True:
        mode = input("Enter mode (1-3): ").strip()
        if mode in ['1', '2', '3']:
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 3.")

    current_player = 'X'
    if mode == '2':
        difficulty = 3
    elif mode == '3':
        difficulty = 2

    printboard(board)

    while not is_terminal(board):
        print(f"{current_player}'s turn")
        if mode == '1':
            human_move(board, current_player)
        elif mode == '3':
            use_alpha_beta = (current_player == 'O')
            AI_move(board, current_player, difficulty, use_alpha_beta)
        else:
            if current_player == 'X':
                human_move(board, current_player)
            else:
                AI_move(board, current_player, difficulty, use_alpha_beta=False)  # Minimax without pruning

        if check_win(board, current_player):
            print(f"{current_player} wins!")
            return

        current_player = 'O' if current_player == 'X' else 'X'

    print("Game over. It's a draw.")

if __name__ == "__main__":
    try:
        print("Welcome to Five-in-a-Row (Gomoku)!")
        print("Connect 5 pieces in a row (horizontally, vertically, or diagonally) to win.")
        while True:
            playgame()
            again = input("Do you want to play again? (y/n): ").strip().lower()
            if again != 'y':
                print("Thanks for playing! Exit...")
                break
    except KeyboardInterrupt:
        print("\nGame terminated by user. Goodbye!")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        input("Press Enter to exit...")