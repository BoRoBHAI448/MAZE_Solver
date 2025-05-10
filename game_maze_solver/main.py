import tkinter as tk
import random
import time
from collections import deque

CELL_SIZE = 40
EASY_GRID_SIZE = 10
MEDIUM_GRID_SIZE = 15
HARD_GRID_SIZE = 20
START = (0, 0)

root = None

class MazeSolver:
    def __init__(self, master, grid_size):
        self.master = master
        self.grid_size = grid_size

        # Layout frames
        self.main_frame = tk.Frame(master)
        self.main_frame.pack()

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        # Canvas for maze
        self.canvas = tk.Canvas(self.left_frame, width=grid_size * CELL_SIZE, height=grid_size * CELL_SIZE, bg="white")
        self.canvas.pack()

        # Timer
        self.start_time = time.time()
        self.timer_running = True
        self.timer_label = tk.Label(self.right_frame, text="Time: 0 sec", font=("Arial", 12))
        self.timer_label.pack(pady=10)
        self.update_timer()

        # Help Button
        help_button = tk.Button(self.right_frame, text="Help", command=self.show_help_menu)
        help_button.pack(pady=5)

        # Maze data
        self.grid = [[1 for _ in range(grid_size)] for _ in range(grid_size)]
        self.end = (grid_size - 2, grid_size - 1)
        self.create_maze()
        self.draw_maze()

        # Player
        self.player_position = list(START)
        self.canvas.bind("<Key>", self.move_player)
        self.canvas.focus_set()
        self.draw_player()

    def create_maze(self):
        self._recursive_backtrack(0, 0)
        self.grid[START[0]][START[1]] = 0
        self.grid[self.end[0]][self.end[1]] = 0

    def _recursive_backtrack(self, x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and self.grid[nx][ny] == 1:
                self.grid[nx][ny] = 0
                self.grid[x + dx][y + dy] = 0
                self._recursive_backtrack(nx, ny)

    def draw_maze(self):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                color = "skyblue" if self.grid[y][x] == 1 else "yellow"
                self.canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE,
                    (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                    fill=color
                )
        self.canvas.create_rectangle(
            START[1] * CELL_SIZE, START[0] * CELL_SIZE,
            (START[1] + 1) * CELL_SIZE, (START[0] + 1) * CELL_SIZE,
            fill="green"
        )
        self.canvas.create_rectangle(
            self.end[1] * CELL_SIZE, self.end[0] * CELL_SIZE,
            (self.end[1] + 1) * CELL_SIZE, (self.end[0] + 1) * CELL_SIZE,
            fill="red"
        )

    def draw_player(self):
        self.canvas.delete("player")
        self.canvas.create_oval(
            self.player_position[1] * CELL_SIZE + 5,
            self.player_position[0] * CELL_SIZE + 5,
            (self.player_position[1] + 1) * CELL_SIZE - 5,
            (self.player_position[0] + 1) * CELL_SIZE - 5,
            fill="blue", tags="player"
        )

    def move_player(self, event):
        if not self.timer_running:
            return

        if event.keysym == 'Up':
            new_position = (self.player_position[0] - 1, self.player_position[1])
        elif event.keysym == 'Down':
            new_position = (self.player_position[0] + 1, self.player_position[1])
        elif event.keysym == 'Left':
            new_position = (self.player_position[0], self.player_position[1] - 1)
        elif event.keysym == 'Right':
            new_position = (self.player_position[0], self.player_position[1] + 1)
        else:
            return

        if self.is_move_valid(new_position):
            self.player_position = list(new_position)
            self.draw_player()
            self.check_win()

    def is_move_valid(self, position):
        x, y = position
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size and self.grid[x][y] == 0

    def check_win(self):
        if tuple(self.player_position) == self.end:
            self.timer_running = False
            elapsed_time = round(time.time() - self.start_time, 2)
            self.canvas.create_text(
                self.grid_size * CELL_SIZE // 2,
                self.grid_size * CELL_SIZE // 2,
                text=f"Congratulations! Solved in {elapsed_time} sec!",
                fill="Black",
                font=("Arial", 20)
            )

    def update_timer(self):
        if self.timer_running:
            elapsed_time = round(time.time() - self.start_time, 2)
            self.timer_label.config(text=f"Time: {elapsed_time} sec")
        self.master.after(1000, self.update_timer)

    def show_help_menu(self):
        self.timer_running = False  # Stop timer on help
        help_window = tk.Toplevel(self.master)
        help_window.title("Help Options")

        tk.Label(help_window, text="Choose solving algorithm:", font=("Arial", 12)).pack(pady=10)
        tk.Button(help_window, text="wanna solve with BFS?", command=lambda: [self.reset_timer(), self.solve_with_bfs(), help_window.destroy()]).pack(pady=5)
        tk.Button(help_window, text="wanna solve with DFS?", command=lambda: [self.reset_timer(), self.solve_with_dfs(), help_window.destroy()]).pack(pady=5)

    def reset_timer(self):
        self.start_time = time.time()
        self.timer_running = True

    def solve_with_bfs(self):
        path = self.bfs()
        if path:
            self.animate_path(path)

    def solve_with_dfs(self):
        path = self.dfs()
        if path:
            self.animate_path(path)

    def bfs(self):
        queue = deque()
        queue.append((START, [START]))
        visited = set()
        visited.add(START)

        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == self.end:
                return path
            for dx, dy in [(0,1),(1,0),(-1,0),(0,-1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    if self.grid[nx][ny] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + [(nx, ny)]))
        return None

    def dfs(self):
        stack = [(START, [START])]
        visited = set()
        visited.add(START)

        while stack:
            (x, y), path = stack.pop()
            if (x, y) == self.end:
                return path
            for dx, dy in [(0,1),(1,0),(-1,0),(0,-1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    if self.grid[nx][ny] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        stack.append(((nx, ny), path + [(nx, ny)]))
        return None

    def animate_path(self, path):
        def step(index):
            if index < len(path):
                self.player_position = list(path[index])
                self.draw_player()
                self.master.after(100, lambda: step(index + 1))
            else:
                self.check_win()
        step(0)

# Game Starter
def start_game(level):
    global root
    if root:
        root.destroy()
    root = tk.Tk()
    root.title("Maze Game")
    if level == "Easy":
        MazeSolver(root, EASY_GRID_SIZE)
    elif level == "Medium":
        MazeSolver(root, MEDIUM_GRID_SIZE)
    elif level == "Hard":
        MazeSolver(root, HARD_GRID_SIZE)
    root.mainloop()

# Main Menu
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maze Game")

    tk.Label(root, text="Select Difficulty Level:", font=("Arial", 14)).pack(pady=10)
    tk.Button(root, text="Easy", command=lambda: start_game("Easy")).pack(pady=5)
    tk.Button(root, text="Medium", command=lambda: start_game("Medium")).pack(pady=5)
    tk.Button(root, text="Hard", command=lambda: start_game("Hard")).pack(pady=5)

    root.mainloop()
