import tkinter as tk
from tkinter import messagebox
import random
import csv
import os
import time
import pickle

class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("MIND MATRIX")
        self.root.geometry("500x700")
        self.root.configure(bg="#F0F8FF")

        # Initialize game variables
        self.cells = {}
        self.score = 0
        self.start_time = time.time()
        self.timer_running = True
        self.solution_file_path = 'sudoku_solution.csv'
        self.leaderboard = self.load_leaderboard()

        # Create UI elements
        self.create_ui()

        # Generate initial puzzle
        self.puzzle, self.solution = self.generate_sudoku(difficulty_var.get())
        self.save_solution_to_csv(self.solution, self.solution_file_path)

    def create_ui(self):
        # Title
        self.title_label = tk.Label(self.root, text="MIND MATRIX", font=("Helvetica", 24, "bold"), fg="#4682B4", bg="#F0F8FF")
        self.title_label.pack(pady=20)

        # Front Page Elements
        self.start_frame = tk.Frame(self.root, bg="#F0F8FF")
        self.start_frame.pack()

        tk.Label(self.start_frame, text="Enter your name:", font=("Helvetica", 12), bg="#F0F8FF").pack(pady=5)
        self.player_name_var = tk.StringVar()
        self.player_name_entry = tk.Entry(self.start_frame, textvariable=self.player_name_var, font=("Helvetica", 12), justify='center')
        self.player_name_entry.pack()

        tk.Label(self.start_frame, text="Select difficulty:", font=("Helvetica", 12), bg="#F0F8FF").pack(pady=5)
        global difficulty_var
        difficulty_var = tk.StringVar(value='medium')
        self.difficulty_menu = tk.OptionMenu(self.start_frame, difficulty_var, 'easy', 'medium', 'hard')
        self.difficulty_menu.pack()

        self.start_button = tk.Button(self.start_frame, text="Start Playing", font=("System", 20), bg="#FFA07A", command=self.start_playing)
        self.start_button.pack(pady=15)

        # Game Page Elements
        self.game_frame = tk.Frame(self.root, bg="#F0F8FF")
        self.player_info_label = tk.Label(self.game_frame, font=("Helvetica", 12), bg="#F0F8FF")
        self.player_info_label.pack()

        self.timer_label = tk.Label(self.game_frame, text="Time: 00:00", font=('Helvetica', 12), bg="#F0F8FF")
        self.score_label = tk.Label(self.game_frame, text="Score: 0", font=('Helvetica', 12), bg="#F0F8FF")

        self.grid_frame = tk.Frame(self.game_frame, bg="#F0F8FF")
        self.reset_button = tk.Button(self.game_frame, text="Reset Game", font=("Helvetica", 12), bg="#FFA07A", command=self.reset_game)

        self.leaderboard_frame = tk.Frame(self.root, bg="#FFFACD")

    def generate_sudoku(self, difficulty='medium'):
        base = 3
        side = base * base

        def pattern(r, c):
            return (base * (r % base) + r // base + c) % side

        def shuffle(s):
            return random.sample(s, len(s))

        rBase = range(base)
        rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
        cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
        nums = shuffle(range(1, base * base + 1))

        solution = [[nums[pattern(r, c)] for c in cols] for r in rows]
        puzzle = [row[:] for row in solution]

        squares = side * side
        filled_squares = squares * {'easy': 0.5, 'medium': 0.4, 'hard': 0.3}[difficulty]

        for p in random.sample(range(squares), int(squares - filled_squares)):
            puzzle[p // side][p % side] = 0

        return puzzle, solution

    def save_solution_to_csv(self, solution, file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(solution)

    def check_input_against_solution(self, file_path, row, col, value):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            solution = [list(map(int, row)) for row in reader]
        
        return value == solution[row][col]

    def save_leaderboard(self):
        with open('leaderboard.dat', 'wb') as file:
            pickle.dump(self.leaderboard, file)

    def load_leaderboard(self):
        if os.path.exists('leaderboard.dat'):
            with open('leaderboard.dat', 'rb') as file:
                return pickle.load(file)
        return []

    def show_leaderboard(self):
        # Clear previous leaderboard entries
        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()

        tk.Label(self.leaderboard_frame, text="Leaderboard", font=("Helvetica", 16, "bold"), bg="#FFD700").pack(pady=10)
        
        # Sort and display top 5 entries
        sorted_leaderboard = sorted(self.leaderboard, key=lambda x: x['time'])[:5]
        for entry in sorted_leaderboard:
            tk.Label(self.leaderboard_frame, 
                     text=f"{entry['name']} - Time: {entry['time']}s", 
                     font=("Helvetica", 12), 
                     bg="#FFFACD").pack()

    def end_game(self):
        self.timer_running = False
        elapsed_time = int(time.time() - self.start_time)
        player_name = self.player_name_var.get()

        # Add the player to the leaderboard and save
        self.leaderboard.append({'name': player_name, 'score': self.score, 'time': elapsed_time})
        self.leaderboard.sort(key=lambda x: x['time'])
        self.save_leaderboard()

        # Clear the grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        messagebox.showinfo("Congratulations!", f"Well done, {player_name}! Your time: {elapsed_time} seconds. Score: {self.score}")

        # Show leaderboard and navigation buttons
        self.leaderboard_frame.pack(pady=10)
        self.show_leaderboard()

        # Create navigation buttons
        play_again_button = tk.Button(self.grid_frame, text="Play Again", font=("Helvetica", 14), bg="#90EE90", command=self.play_again)
        play_again_button.pack(pady=10)

        home_button = tk.Button(self.grid_frame, text="Go to Home", font=("Helvetica", 14), bg="#ADD8E6", command=self.go_to_home)
        home_button.pack(pady=10)

    def go_to_home(self):
        # Reset game state
        self.reset_game()

        # Hide game elements
        self.leaderboard_frame.pack_forget()
        self.timer_label.pack_forget()
        self.score_label.pack_forget()
        self.grid_frame.pack_forget()
        self.game_frame.pack_forget()

        # Show home screen
        self.title_label.pack()
        self.start_frame.pack()

    def start_playing(self):
        player_name = self.player_name_var.get().strip()
        if not player_name:
            messagebox.showwarning("Name Missing", "Please enter your name.")
            return

        # Show player name and difficulty during gameplay
        self.game_frame.pack(side=tk.TOP, pady=5)
        self.player_info_label.config(text=f"Player: {player_name} | Difficulty: {difficulty_var.get()}")

        # Hide initial input elements
        self.title_label.pack_forget()
        self.start_frame.pack_forget()

        # Show game elements
        self.timer_label.pack(side=tk.TOP, pady=5)
        self.score_label.pack(side=tk.TOP, pady=5)
        self.grid_frame.pack(pady=10)
        self.reset_button.pack(pady=10)

        # Create grid and start game
        self.create_grid()
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def play_again(self):
        # Reset game state and create a new grid
        self.reset_game()
        
        # Hide leaderboard
        self.leaderboard_frame.pack_forget()

        # Show game elements
        self.timer_label.pack(side=tk.TOP, pady=5)
        self.score_label.pack(side=tk.TOP, pady=5)
        self.grid_frame.pack(pady=10)

        # Create a new grid with a new puzzle
        self.create_grid()

    def update_timer(self):
        if not self.timer_running:
            return

        elapsed_time = int(time.time() - self.start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        self.timer_label.config(text=f"Time: {minutes:02}:{seconds:02}")
        self.root.after(1000, self.update_timer)

    def is_sudoku_solved(self):
        for row in range(9):
            for col in range(9):
                cell_value = self.cells[(row, col)].get()
                if not cell_value.isdigit() or int(cell_value) != self.solution[row][col]:
                    return False
        return True

    def create_grid(self):
        # Clear existing grid if any
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Create new grid
        for row in range(9):
            for col in range(9):
                cell = tk.Entry(self.grid_frame, width=2, font=('Helvetica', 18), justify='center')
                cell.grid(row=row, column=col, padx=1, pady=1)
                cell.bind('<KeyRelease>', self.check_input)
                self.cells[(row, col)] = cell

        # Fill grid with puzzle
        self.fill_grid_with_puzzle()

    def fill_grid_with_puzzle(self):
        for row in range(9):
            for col in range(9):
                cell = self.cells[(row, col)]
                cell.delete(0, tk.END)

                if self.puzzle[row][col] != 0:
                    cell.insert(0, self.puzzle[row][col])
                    cell.config(state='disabled', bg="#D3D3D3")
                else:
                    cell.config(state='normal', bg="white")

    def check_input(self, event):
        row, col = None, None
        for r in range(9):
            for c in range(9):
                if self.cells[(r, c)] == event.widget:
                    row, col = r, c
                    break

        value = event.widget.get()

        if value.isdigit() and 1 <= int(value) <= 9:
            value = int(value)

            if self.check_input_against_solution(self.solution_file_path, row, col, value):
                self.score += 1
                self.score_label.config(text=f"Score: {self.score}")
                event.widget.config(bg="#ADFF2F")
            else:
                event.widget.config(bg="red")
                self.root.after(500, lambda: event.widget.config(bg="white"))
                event.widget.delete(0, tk.END)

            # Check if the Sudoku is completely solved
            if self.is_sudoku_solved():
                self.timer_running = False
                self.end_game()
        else:
            messagebox.showwarning("Invalid Input", "Please enter a number between 1 and 9.")
            event.widget.delete(0, tk.END)

    def reset_game(self):
        # Reset game state
        self.score = 0
        self.start_time = time.time()
        self.timer_running = True

        # Update labels
        self.score_label.config(text="Score: 0")
        self.timer_label.config(text="Time: 00:00")

        # Regenerate puzzle and solution
        self.puzzle, self.solution = self.generate_sudoku(difficulty_var.get())
        self.save_solution_to_csv(self.solution, self.solution_file_path)

        # Recreate the grid
        self.create_grid()

def main():
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()