import tkinter as tk
from ui import ChessApp

def main():
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()