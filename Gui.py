import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import copy
import random
from PIL import Image, ImageTk


from MiniMax import find_best_move_with_alpha_beta, find_best_move_minimax, POTENTIAL_WIN_SCORES

BOARD_SIZE = 15
WIN_LENGTH = 5
sizeofceil = 35

def check_win(board, player):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if all(col + i < BOARD_SIZE and board[row][col + i] == player for i in range(WIN_LENGTH)) or \
               all(row + i < BOARD_SIZE and board[row + i][col] == player for i in range(WIN_LENGTH)) or \
               all(row + i < BOARD_SIZE and col + i < BOARD_SIZE and board[row + i][col + i] == player for i in range(WIN_LENGTH)) or \
               all(row + i < BOARD_SIZE and col - i >= 0 and board[row + i][col - i] == player for i in range(WIN_LENGTH)):
                return True
    return False

class GomokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku Game")
        self.board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'
        self.game_mode = None
        self.ai_difficulty = 3
        self.ai_thinking = False
        self.canvas = tk.Canvas(root, width=sizeofceil * BOARD_SIZE, height=sizeofceil * BOARD_SIZE, bg='#EAEAEA')
        self.canvas.pack()
        self.reset_button = tk.Button(root, text="Reset", command=self.reset_board)
        self.exit_button = tk.Button(root, text="Exit", command=root.quit)
        self.reset_button.pack(side=tk.LEFT, padx=20, pady=10)
        self.exit_button.pack(side=tk.RIGHT, padx=20, pady=10)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.drawboard()
        self.gamemode()

    def gamemode(self):
        mode = simpledialog.askstring("game Mode", "Enter mode:\n1 - human vs human\n2 - human vs AI\n3 - AI vs AI")
        if mode == '1':
            self.game_mode = 1
        elif mode == '2':
            self.game_mode = 2
        elif mode == '3':
            self.game_mode = 3
            self.start_ai_vs_ai()
        else:
            messagebox.showinfo("info", "invalid mode selected")
            self.game_mode = 1

    def start_ai_vs_ai(self):
        self.ai_thinking = True
        threading.Thread(target=self.ai_vs_ai_thread, daemon=True).start()

    def ai_vs_ai_thread(self):
        while True:
            if self.is_terminal(self.board):
                winner = None
                if check_win(self.board, 'X'):
                    winner = 'X'
                elif check_win(self.board, 'O'):
                    winner = 'O'

                if winner:
                    self.root.after(0, lambda: messagebox.showinfo("game Over", f"Player {winner} win"))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("try again", "It's a draw!"))

                self.ai_thinking = False
                self.canvas.unbind("<Button-1>")
                break

            board_copy = copy.deepcopy(self.board)
            if self.current_player == 'X':
                move = find_best_move_with_alpha_beta(
                    board_copy, BOARD_SIZE,
                    lambda b: [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if b[i][j] == '.'],
                    self.is_terminal, check_win, 3
                )
            else:
                move = find_best_move_minimax(
                    board_copy, BOARD_SIZE,
                    lambda b: [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if b[i][j] == '.'],
                    self.is_terminal, check_win, 3
                )

            if move:
                row, col = move
                self.board[row][col] = self.current_player
                self.root.after(0, self.draw_piece, row, col, self.current_player)

            self.switch_player()
            threading.Event().wait(0.7)


    def drawboard(self):
        self.canvas.delete("all")
        for i in range(BOARD_SIZE):

            self.canvas.create_line(sizeofceil // 2, sizeofceil // 2 + i * sizeofceil,
                                    sizeofceil // 2 + (BOARD_SIZE - 1) * sizeofceil, sizeofceil // 2 + i * sizeofceil)

            self.canvas.create_line(sizeofceil // 2 + i * sizeofceil, sizeofceil // 2,
                                    sizeofceil // 2 + i * sizeofceil, sizeofceil // 2 + (BOARD_SIZE - 1) * sizeofceil)


        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] != '.':
                    self.draw_piece(row, col, self.board[row][col])

    def draw_piece(self, row, col, player):
        x = sizeofceil // 2 + col * sizeofceil
        y = sizeofceil // 2 + row * sizeofceil
        radius = sizeofceil // 2-2
        x1 = x - radius
        y1 = y - radius
        x2 = x + radius
        y2 = y + radius
        color = 'pink' if player == 'X' else 'lavender'

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray", width=1)

    def handle_click(self, event):
        if self.ai_thinking or self.game_mode == 3:
            return

        col = int((event.x - sizeofceil // 2 ) // sizeofceil)
        row = int((event.y - sizeofceil // 2 ) // sizeofceil)

        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and self.board[row][col] == '.':

            if self.game_mode == 2 and self.current_player == 'O':
                return

            self.board[row][col] = self.current_player
            self.draw_piece(row, col, self.current_player)

            if self.check_win_local(self.current_player):
                messagebox.showinfo("game Over", f"Player {self.current_player} win")
                self.canvas.unbind("<Button-1>")
                return
            elif self.is_draw():
                messagebox.showinfo("game Over", "it is a draw")
                self.canvas.unbind("<Button-1>")
                return

            self.switch_player()

            if self.game_mode == 2 and self.current_player == 'O':
                self.ai_thinking = True
                self.root.after(100, self.ai_move_thread)

    def ai_move_thread(self):

        def run_ai():
            board_copy = copy.deepcopy(self.board)
            move = find_best_move_minimax(
                board_copy, BOARD_SIZE,
                lambda b: [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if b[i][j] == '.'],
                self.is_terminal, check_win, 3
            )
            if move:
                row, col = move
                self.board[row][col] = self.current_player

            self.root.after(0, self.finish_ai_move, move)

        threading.Thread(target=run_ai).start()

    def finish_ai_move(self, move):
        if move:
            row, col = move
            self.draw_piece(row, col, self.current_player)

            if self.check_win_local(self.current_player):
                messagebox.showinfo("game Over", f" ai wins")
                self.canvas.unbind("<Button-1>")
                self.ai_thinking = False
                return
            elif self.is_draw():
                messagebox.showinfo("game Over", "it is draw")
                self.canvas.unbind("<Button-1>")
                self.ai_thinking = False
                return

            self.switch_player()

        self.ai_thinking = False

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def check_win_local(self, player):
        return check_win(self.board, player)

    def is_draw(self):
        return all(cell != '.' for row in self.board for cell in row)

    def is_terminal(self, board):
        return check_win(board, 'X') or check_win(board, 'O') or all(cell != '.' for row in board for cell in row)

    def reset_board(self):
        self.board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'
        self.drawboard()
        self.canvas.bind("<Button-1>", self.handle_click)
        self.ai_thinking = False

        if self.game_mode == 2 and self.current_player == 'O':
            self.ai_thinking = True
            self.root.after(100, self.ai_move_thread)
        elif self.game_mode == 3:
            self.start_ai_vs_ai()

if __name__ == "__main__":
    root = tk.Tk()
    app = GomokuGUI(root)
    root.mainloop()
