import tkinter
from Game.ui import ChessApp

def main():
    root = tkinter.Tk()
    app = ChessApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()