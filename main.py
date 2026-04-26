import ttkbootstrap as ttk
from Game.ui import ChessApp

def main():
    root = ttk.Window(themename="darkly")
    ChessApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()