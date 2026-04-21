import queue
import threading
import chess
import tkinter as tk
from tkinter import messagebox
from typing import Optional

from Game.config import (
    BOARD_SIZE,
    SQUARE_SIZE,
    LIGHT_COLOR,
    DARK_COLOR,
    HIGHLIGHT_COLOR,
    MOVE_DOT_COLOR,
    LAST_MOVE_COLOR,
    CHECK_COLOR,
    SIDEBAR_WIDTH,
    WINDOW_PADDING,
    FONT_LARGE,
    FONT_MEDIUM,
    FONT_SMALL,
    FONT_PIECE,
    UNICODE_PIECES,
)
from Game.settings import GameSettings
from Game.move_provider import MoveProvider, RandomMoveProvider, model_moveProvider
from Game.game_controller import GameController

class ChessApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chess UI Foundation")
        self.root.resizable(False, False)

        self.current_frame: Optional[tk.Frame] = None
        self.show_start_menu()

    def clear_current_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def show_start_menu(self):
        self.clear_current_frame()

        frame = tk.Frame(self.root, padx=30, pady=30)
        frame.pack()
        self.current_frame = frame

        tk.Label(frame, text="Chess Game", font=FONT_LARGE).pack(pady=(0, 20))
        tk.Label(
            frame,
            text="Playable UI foundation for a future CNN opponent",
            font=FONT_MEDIUM,
        ).pack(pady=(0, 25))

        color_var = tk.StringVar(value="white")
        opponent_var = tk.BooleanVar(value=True)
        timer_var = tk.BooleanVar(value=True)
        time_var = tk.StringVar(value="10")

        options_frame = tk.Frame(frame)
        options_frame.pack(pady=10)

        tk.Label(options_frame, text="Choose your color:", font=FONT_MEDIUM).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        tk.Radiobutton(
            options_frame,
            text="White",
            variable=color_var,
            value="white",
            font=FONT_MEDIUM,
        ).grid(row=0, column=1, sticky="w")
        tk.Radiobutton(
            options_frame,
            text="Black",
            variable=color_var,
            value="black",
            font=FONT_MEDIUM,
        ).grid(row=0, column=2, sticky="w")

        tk.Checkbutton(
            options_frame,
            text="Enable AI opponent",
            variable=opponent_var,
            font=FONT_MEDIUM,
        ).grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=10)

        tk.Checkbutton(
            options_frame,
            text="Enable timer",
            variable=timer_var,
            font=FONT_MEDIUM,
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

        tk.Label(options_frame, text="Minutes per side:", font=FONT_MEDIUM).grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        tk.Entry(options_frame, textvariable=time_var, width=8, font=FONT_MEDIUM).grid(
            row=3, column=1, sticky="w", padx=5, pady=5
        )

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=(20, 10))

        tk.Button(
            button_frame,
            text="Start Game",
            font=FONT_MEDIUM,
            width=16,
            command=lambda: self.start_game(
                GameSettings(
                    player_color=chess.WHITE if color_var.get() == "white" else chess.BLACK,
                    opponent_enabled=opponent_var.get(),
                    use_timer=timer_var.get(),
                    initial_time_seconds=max(1, int(time_var.get())) * 60,
                )
            ),
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            button_frame,
            text="Quit",
            font=FONT_MEDIUM,
            width=16,
            command=self.root.destroy,
        ).pack(side=tk.LEFT, padx=8)

    def start_game(self, settings: GameSettings):
        self.clear_current_frame()
        frame = GameFrame(self.root, settings, self.show_start_menu)
        frame.pack(padx=WINDOW_PADDING, pady=WINDOW_PADDING)
        self.current_frame = frame


class GameFrame(tk.Frame):
    def __init__(self, parent, settings: GameSettings, back_to_menu_callback):
        super().__init__(parent)
        self.settings = settings
        self.back_to_menu_callback = back_to_menu_callback

        self.controller = GameController(
            initial_time_seconds=settings.initial_time_seconds,
            use_timer=settings.use_timer,
        )

        self.selected_square: Optional[chess.Square] = None
        self.legal_targets: list[chess.Square] = []

        self.move_queue: "queue.Queue[object]" = queue.Queue()
        self.ai_thinking = False

        self.opponent: Optional[MoveProvider] = model_moveProvider if settings.opponent_enabled else None

        self.status_var = tk.StringVar(value=self.controller.status_text())
        self.info_var = tk.StringVar(value="Select a piece to begin.")

        self.white_timer_var = tk.StringVar()
        self.black_timer_var = tk.StringVar()
        self.white_score_var = tk.StringVar()
        self.black_score_var = tk.StringVar()
        self.advantage_var = tk.StringVar()

        self._build_layout()
        self._draw_board()
        self._refresh_history()
        self._update_labels()
        self._start_timer_loop()
        self._maybe_trigger_ai_turn()

    def _build_layout(self):
        left_panel = tk.Frame(self)
        left_panel.grid(row=0, column=0, padx=(0, 15), sticky="n")

        right_panel = tk.Frame(self, width=SIDEBAR_WIDTH)
        right_panel.grid(row=0, column=1, sticky="n")
        right_panel.grid_propagate(False)

        self.canvas = tk.Canvas(
            left_panel,
            width=BOARD_SIZE * SQUARE_SIZE,
            height=BOARD_SIZE * SQUARE_SIZE,
            highlightthickness=1,
            highlightbackground="black",
            bg="#EEE8E1",
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        self.status_label = tk.Label(
            right_panel,
            textvariable=self.status_var,
            font=FONT_LARGE,
            wraplength=300,
            justify="left",
        )
        self.status_label.pack(anchor="w", pady=(0, 12))

        self.info_label = tk.Label(
            right_panel,
            textvariable=self.info_var,
            font=FONT_MEDIUM,
            wraplength=300,
            justify="left",
        )
        self.info_label.pack(anchor="w", pady=(0, 12))

        tk.Label(right_panel, text="Clock", font=FONT_MEDIUM).pack(anchor="w")
        tk.Label(right_panel, textvariable=self.white_timer_var, font=FONT_MEDIUM).pack(anchor="w", pady=(2, 0))
        tk.Label(right_panel, textvariable=self.black_timer_var, font=FONT_MEDIUM).pack(anchor="w", pady=(2, 10))

        tk.Label(right_panel, text="Material Score", font=FONT_MEDIUM).pack(anchor="w")
        tk.Label(right_panel, textvariable=self.white_score_var, font=FONT_MEDIUM).pack(anchor="w", pady=(2, 0))
        tk.Label(right_panel, textvariable=self.black_score_var, font=FONT_MEDIUM).pack(anchor="w", pady=(2, 0))
        tk.Label(right_panel, textvariable=self.advantage_var, font=FONT_MEDIUM).pack(anchor="w", pady=(2, 10))

        tk.Label(right_panel, text="Move History", font=FONT_MEDIUM).pack(anchor="w")

        self.move_listbox = tk.Listbox(
            right_panel,
            width=46,
            height=16,
            font=FONT_SMALL,
        )
        self.move_listbox.pack(anchor="w", pady=(5, 15), fill="y")

        controls = tk.Frame(right_panel)
        controls.pack(anchor="w", pady=(5, 0))

        tk.Button(controls, text="Restart", width=12, command=self._restart_game).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(controls, text="Undo", width=12, command=self._undo_move).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(controls, text="Main Menu", width=12, command=self.back_to_menu_callback).grid(row=1, column=0, columnspan=2, padx=4, pady=4)

    def _draw_board(self):
        self.canvas.delete("all")
        board = self.controller.board
        last_move = self.controller.last_move

        for rank in range(8):
            for file in range(8):
                x1 = file * SQUARE_SIZE
                y1 = rank * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                square = self._display_to_square(file, rank)
                base_color = LIGHT_COLOR if (file + rank) % 2 == 0 else DARK_COLOR
                fill = base_color

                if last_move and square in (last_move.from_square, last_move.to_square):
                    fill = LAST_MOVE_COLOR

                if self.selected_square == square:
                    fill = HIGHLIGHT_COLOR

                if board.is_check() and board.piece_at(square) == chess.Piece(chess.KING, board.turn):
                    fill = CHECK_COLOR

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="black")

                piece = board.piece_at(square)
                if piece:
                    self.canvas.create_text(
                        x1 + SQUARE_SIZE / 2,
                        y1 + SQUARE_SIZE / 2,
                        text=UNICODE_PIECES[piece.symbol()],
                        font=FONT_PIECE,
                    )

                if square in self.legal_targets:
                    self.canvas.create_oval(
                        x1 + SQUARE_SIZE * 0.4,
                        y1 + SQUARE_SIZE * 0.4,
                        x1 + SQUARE_SIZE * 0.6,
                        y1 + SQUARE_SIZE * 0.6,
                        fill=MOVE_DOT_COLOR,
                        outline=MOVE_DOT_COLOR,
                    )

        self._draw_coordinates()

    def _draw_coordinates(self):
        for file in range(8):
            label = chr(ord("a") + file)
            if self.settings.player_color == chess.BLACK:
                label = chr(ord("a") + (7 - file))
            x = file * SQUARE_SIZE + 5
            y = 8 * SQUARE_SIZE - 12
            self.canvas.create_text(x, y, text=label, anchor="w", font=("Segoe UI", 9, "bold"))

        for rank in range(8):
            label = str(8 - rank)
            if self.settings.player_color == chess.BLACK:
                label = str(rank + 1)
            x = 5
            y = rank * SQUARE_SIZE + 5
            self.canvas.create_text(x, y, text=label, anchor="nw", font=("Segoe UI", 9, "bold"))

    def _display_to_square(self, display_file: int, display_rank: int) -> chess.Square:
        if self.settings.player_color == chess.WHITE:
            file_index = display_file
            rank_index = 7 - display_rank
        else:
            file_index = 7 - display_file
            rank_index = display_rank
        return chess.square(file_index, rank_index)

    def _event_to_square(self, event) -> Optional[chess.Square]:
        file = event.x // SQUARE_SIZE
        rank = event.y // SQUARE_SIZE

        if not (0 <= file < 8 and 0 <= rank < 8):
            return None

        return self._display_to_square(file, rank)

    def _on_canvas_click(self, event):
        if self.controller.game_over or self.ai_thinking:
            return

        board = self.controller.board

        if self.opponent is not None and board.turn != self.settings.player_color:
            self.info_var.set("It is not your turn.")
            return

        clicked_square = self._event_to_square(event)
        if clicked_square is None:
            return

        piece = board.piece_at(clicked_square)
        allowed_color = self.settings.player_color if self.opponent is not None else board.turn

        if self.selected_square is None:
            if piece is None:
                self.info_var.set("Select one of your pieces.")
                return
            if piece.color != allowed_color:
                self.info_var.set("That is not your piece.")
                return
            self._select_square(clicked_square)
            return

        if clicked_square == self.selected_square:
            self._clear_selection()
            self.info_var.set("Selection cleared.")
            return

        result = self.controller.try_make_move(self.selected_square, clicked_square)
        if result.success:
            self._clear_selection()
            self._refresh_history()
            self._update_labels()
            self._draw_board()
            self._maybe_trigger_ai_turn()
            return

        if piece and piece.color == allowed_color:
            self._select_square(clicked_square)
            return

        self.info_var.set(result.message)

    def _select_square(self, square: chess.Square):
        self.selected_square = square
        self.legal_targets = self.controller.legal_targets_for(square)
        self.info_var.set(f"Selected {chess.square_name(square)}.")
        self._draw_board()

    def _clear_selection(self):
        self.selected_square = None
        self.legal_targets = []
        self._draw_board()

    def _refresh_history(self):
        self.move_listbox.delete(0, tk.END)
        for line in self.controller.history_lines():
            self.move_listbox.insert(tk.END, line)
        self.move_listbox.yview_moveto(1.0)

    def _update_labels(self):
        self.status_var.set(self.controller.status_text())
        self.info_var.set(self.controller.info_text())

        self.white_timer_var.set(f"White: {self.controller.get_timer_text(chess.WHITE)}")
        self.black_timer_var.set(f"Black: {self.controller.get_timer_text(chess.BLACK)}")

        self.white_score_var.set(self.controller.get_white_score_text())
        self.black_score_var.set(self.controller.get_black_score_text())
        self.advantage_var.set(f"Advantage: {self.controller.get_material_advantage_text()}")

    def _start_timer_loop(self):
        if self.settings.use_timer:
            self.after(1000, self._timer_tick)

    def _timer_tick(self):
        if self.controller.game_over:
            self._update_labels()
            return

        timed_out = self.controller.tick()
        self._update_labels()

        if timed_out:
            self._draw_board()
            return

        self.after(1000, self._timer_tick)

    def _maybe_trigger_ai_turn(self):
        if self.controller.game_over or not self.opponent:
            return

        if self.controller.board.turn == self.settings.player_color:
            return

        self.ai_thinking = True
        self.info_var.set("Opponent is thinking...")

        def worker():
            try:
                move = self.opponent.choose_move(self.controller.board.copy())
                self.move_queue.put(move)
            except Exception as exc:
                self.move_queue.put(exc)

        threading.Thread(target=worker, daemon=True).start()
        self.after(100, self._poll_ai_move)

    def _poll_ai_move(self):
        try:
            result = self.move_queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_ai_move)
            return

        self.ai_thinking = False

        if isinstance(result, Exception):
            messagebox.showerror("Opponent Error", str(result))
            self.info_var.set("Opponent failed to move.")
            return

        if result is None:
            self.info_var.set("Opponent has no move.")
            self._update_labels()
            return

        move_result = self.controller.push_external_move(result)
        if not move_result.success:
            messagebox.showerror("Opponent Error", move_result.message)
            self.info_var.set(move_result.message)
            return

        self._refresh_history()
        self._update_labels()
        self._draw_board()

    def _undo_move(self):
        if self.ai_thinking:
            self.info_var.set("Wait for the opponent to finish.")
            return

        success = self.controller.undo(against_opponent=self.opponent is not None)
        if not success:
            self.info_var.set("No moves to undo.")
            return

        self.selected_square = None
        self.legal_targets = []
        self._refresh_history()
        self._update_labels()
        self._draw_board()
        self.info_var.set("Move undone.")

    def _restart_game(self):
        self.controller.reset()
        self.selected_square = None
        self.legal_targets = []
        self.ai_thinking = False
        self._refresh_history()
        self._update_labels()
        self.info_var.set("Select a piece to begin.")
        self._draw_board()
        self._start_timer_loop()
        self._maybe_trigger_ai_turn()