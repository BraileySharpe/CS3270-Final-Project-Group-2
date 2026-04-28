import queue
import threading
import chess
import tkinter as tk
import ttkbootstrap as ttk
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
    APP_BG,
    PANEL_BG,
    PANEL_BORDER,
    TEXT_PRIMARY,
    TEXT_MUTED,
    SELECTED_BLUE,
    UNSELECTED_BG,
    UNSELECTED_TEXT,
    HOVER_BG
)
from Game.settings import GameSettings
from Game.move_provider import model_moveProvider
from Game.game_controller import GameController

APP_BG = "#111827"
PANEL_BG = "#1f2937"
TEXT_PRIMARY = "#f9fafb"
TEXT_MUTED = "#9ca3af"
BOARD_BORDER = "#374151"

FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_SUBTITLE = ("Segoe UI", 11)
FONT_SECTION = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)


class ChessApp:
    def __init__(self, root: ttk.Window):
        self.root = root
        self.root.title("Modern Chess Engine")
        self.root.resizable(False, False)
        self.root.configure(bg=APP_BG)

        self.current_frame: Optional[tk.Frame] = None
        self.show_start_menu()

    def clear_current_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def show_start_menu(self):
        self.clear_current_frame()

        frame = tk.Frame(self.root, bg=APP_BG)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        card = tk.Frame(
            frame,
            bg=PANEL_BG,
            padx=42,
            pady=36,
            highlightbackground=PANEL_BORDER,
            highlightthickness=1,
        )
        card.pack(expand=True)

        tk.Label(
            card,
            text="Chess Engine",
            font=("Segoe UI", 26, "bold"),
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
        ).pack(anchor="center", pady=(0, 6))

        tk.Label(
            card,
            text="Choose your setup and start playing",
            font=("Segoe UI", 11),
            bg=PANEL_BG,
            fg=TEXT_MUTED,
        ).pack(anchor="center", pady=(0, 28))

        color_var = tk.StringVar(value="white")
        opponent_var = tk.BooleanVar(value=True)
        timer_var = tk.BooleanVar(value=True)
        time_var = tk.StringVar(value="10")

        options_frame = tk.Frame(card, bg=PANEL_BG)
        options_frame.pack(anchor="center")

        tk.Label(
            options_frame,
            text="Choose your color",
            font=("Segoe UI", 12, "bold"),
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
        ).pack(anchor="center", pady=(0, 10))

        color_button_frame = tk.Frame(options_frame, bg=PANEL_BG)
        color_button_frame.pack(anchor="center", pady=(0, 18))

        def style_color_buttons():
            if color_var.get() == "white":
                white_button.configure(
                    bg=SELECTED_BLUE,
                    fg="white",
                    activebackground=SELECTED_BLUE,
                )
                black_button.configure(
                    bg=UNSELECTED_BG,
                    fg=UNSELECTED_TEXT,
                    activebackground=HOVER_BG,
                )
            else:
                black_button.configure(
                    bg=SELECTED_BLUE,
                    fg="white",
                    activebackground=SELECTED_BLUE,
                )
                white_button.configure(
                    bg=UNSELECTED_BG,
                    fg=UNSELECTED_TEXT,
                    activebackground=HOVER_BG,
                )

        def select_color(color):
            color_var.set(color)
            style_color_buttons()

        def on_hover(button, is_selected):
            if not is_selected:
                button.configure(bg=HOVER_BG)

        def on_leave(button, is_selected):
            if not is_selected:
                button.configure(bg=UNSELECTED_BG)

        white_button = tk.Button(
            color_button_frame,
            text="White",
            font=("Segoe UI", 11, "bold"),
            width=14,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            bg=UNSELECTED_BG,
            fg=UNSELECTED_TEXT,
            command=lambda: select_color("white"),
        )
        white_button.grid(row=0, column=0, padx=(0, 8))

        black_button = tk.Button(
            color_button_frame,
            text="Black",
            font=("Segoe UI", 11, "bold"),
            width=14,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            bg=UNSELECTED_BG,
            fg=UNSELECTED_TEXT,
            command=lambda: select_color("black"),
        )
        black_button.grid(row=0, column=1, padx=(8, 0))

        white_button.bind(
            "<Enter>",
            lambda event: on_hover(white_button, color_var.get() == "white"),
        )
        white_button.bind(
            "<Leave>",
            lambda event: on_leave(white_button, color_var.get() == "white"),
        )

        black_button.bind(
            "<Enter>",
            lambda event: on_hover(black_button, color_var.get() == "black"),
        )
        black_button.bind(
            "<Leave>",
            lambda event: on_leave(black_button, color_var.get() == "black"),
        )

        style_color_buttons()

        toggle_frame = tk.Frame(options_frame, bg=PANEL_BG)
        toggle_frame.pack(anchor="center", pady=(0, 18))

        ttk.Checkbutton(
            toggle_frame,
            text="Enable AI opponent",
            variable=opponent_var,
            bootstyle="success-round-toggle",
        ).pack(anchor="center", pady=4)

        ttk.Checkbutton(
            toggle_frame,
            text="Enable timer",
            variable=timer_var,
            bootstyle="info-round-toggle",
        ).pack(anchor="center", pady=4)

        time_frame = tk.Frame(options_frame, bg=PANEL_BG)
        time_frame.pack(anchor="center", pady=(2, 24))

        tk.Label(
            time_frame,
            text="Minutes per side",
            font=("Segoe UI", 12, "bold"),
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
        ).pack(anchor="center", pady=(0, 8))

        ttk.Entry(
            time_frame,
            textvariable=time_var,
            width=12,
            justify="center",
            bootstyle="secondary",
            font=("Segoe UI", 11),
        ).pack(anchor="center")

        button_frame = tk.Frame(card, bg=PANEL_BG)
        button_frame.pack(anchor="center", pady=(4, 0))

        ttk.Button(
            button_frame,
            text="Start Game",
            bootstyle="primary",
            width=18,
            command=lambda: self._safe_start_game(
                color_var,
                opponent_var,
                timer_var,
                time_var,
            ),
        ).grid(row=0, column=0, padx=(0, 8))

        ttk.Button(
            button_frame,
            text="Quit",
            bootstyle="danger",
            width=18,
            command=self.root.destroy,
        ).grid(row=0, column=1, padx=(8, 0))

    def _safe_start_game(self, color_var, opponent_var, timer_var, time_var):
        try:
            minutes = max(1, int(time_var.get()))
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter a valid number of minutes.")
            return

        self.start_game(
            GameSettings(
                player_color=chess.WHITE if color_var.get() == "white" else chess.BLACK,
                opponent_enabled=opponent_var.get(),
                use_timer=timer_var.get(),
                initial_time_seconds=minutes * 60,
            )
        )

    def start_game(self, settings: GameSettings):
        self.clear_current_frame()
        frame = GameFrame(self.root, settings, self.show_start_menu)
        frame.pack(padx=WINDOW_PADDING, pady=WINDOW_PADDING)
        self.current_frame = frame


class GameFrame(tk.Frame):
    def __init__(self, parent, settings: GameSettings, back_to_menu_callback):
        super().__init__(parent, bg=APP_BG)
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
        self.timer_after_id: Optional[str] = None

        self.opponent: Optional[MoveProvider] = (
            model_moveProvider if settings.opponent_enabled else None
        )

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
        self.configure(bg=APP_BG)

        main = tk.Frame(self, bg=APP_BG)
        main.pack(padx=8, pady=8)

        left_panel = tk.Frame(main, bg=APP_BG)
        left_panel.grid(row=0, column=0, padx=(0, 10), sticky="n")

        board_card = tk.Frame(
            left_panel,
            bg=PANEL_BORDER,
            padx=6,
            pady=6,
        )
        board_card.pack()

        self.canvas = tk.Canvas(
            board_card,
            width=BOARD_SIZE * SQUARE_SIZE,
            height=BOARD_SIZE * SQUARE_SIZE,
            highlightthickness=0,
            bg=LIGHT_COLOR,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        right_panel = tk.Frame(
            main,
            bg=PANEL_BG,
            width=SIDEBAR_WIDTH,
            padx=16,
            pady=16,
            highlightbackground=PANEL_BORDER,
            highlightthickness=1,
        )
        right_panel.grid(row=0, column=1, sticky="n")
        right_panel.grid_propagate(False)

        self.status_label = tk.Label(
            right_panel,
            textvariable=self.status_var,
            font=FONT_LARGE,
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            wraplength=290,
            justify="left",
        )
        self.status_label.pack(anchor="w", pady=(0, 8))

        self.info_label = tk.Label(
            right_panel,
            textvariable=self.info_var,
            font=FONT_MEDIUM,
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            wraplength=290,
            justify="left",
        )
        self.info_label.pack(anchor="w", pady=(0, 14))

        tk.Label(
            right_panel,
            text="Clock",
            font=("Segoe UI", 12, "bold"),
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(4, 4))

        tk.Label(
            right_panel,
            textvariable=self.white_timer_var,
            font=FONT_MEDIUM,
            bg=PANEL_BG,
            fg=TEXT_MUTED
        ).pack(anchor="w")

        tk.Label(
            right_panel,
            textvariable=self.black_timer_var,
            font=FONT_MEDIUM,
            bg=PANEL_BG,
            fg=TEXT_MUTED
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            right_panel,
            text="Material Score",
            font=("Segoe UI", 12, "bold"),
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(4, 4))

        tk.Label(
            right_panel,
            textvariable=self.white_score_var,
            font=FONT_MEDIUM,
            bg=PANEL_BG,
            fg=TEXT_MUTED
        ).pack(anchor="w")

        tk.Label(
            right_panel,
            textvariable=self.black_score_var,
            font=FONT_MEDIUM,
            bg=PANEL_BG,
            fg=TEXT_MUTED
        ).pack(anchor="w")

        tk.Label(
            right_panel,
            textvariable=self.advantage_var,
            font=FONT_MEDIUM,
            bg=PANEL_BG,
            fg=TEXT_MUTED
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            right_panel,
            text="Move History",
            font=("Segoe UI", 12, "bold"),
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(4, 4))

        self.move_listbox = tk.Listbox(
            right_panel,
            width=40,
            height=15,
            font=FONT_SMALL,
            bg="#FFFFFF",
            fg=TEXT_PRIMARY,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=PANEL_BORDER,
            selectbackground="#DBEAFE",
            selectforeground=TEXT_PRIMARY,
            activestyle="none",
        )
        self.move_listbox.pack(anchor="w", pady=(4, 14), fill="both")

        controls = ttk.Frame(right_panel)
        controls.pack(anchor="w", fill="x")

        ttk.Button(
            controls,
            text="Restart",
            bootstyle="primary",
            width=12,
            command=self._restart_game
        ).grid(row=0, column=0, padx=(0, 6), pady=4)

        ttk.Button(
            controls,
            text="Undo",
            bootstyle="secondary",
            width=12,
            command=self._undo_move
        ).grid(row=0, column=1, pady=4)

        ttk.Button(
            controls,
            text="Main Menu",
            bootstyle="secondary",
            width=26,
            command=self._return_to_menu
        ).grid(row=1, column=0, columnspan=2, pady=(6, 0), sticky="ew")

    def _return_to_menu(self):
        self._stop_timer_loop()
        self.back_to_menu_callback()

    def _sidebar_section(self, parent, text):
        tk.Label(
            parent,
            text=text,
            font=FONT_SECTION,
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(4, 4))

    def _sidebar_value(self, parent, variable, bottom=4):
        tk.Label(
            parent,
            textvariable=variable,
            font=FONT_BODY,
            bg=PANEL_BG,
            fg=TEXT_MUTED,
        ).pack(anchor="w", pady=(0, bottom))

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

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill,
                    outline=fill,
                )

                piece = board.piece_at(square)
                if piece:
                    piece_color = "#111827" if piece.color == chess.WHITE else "#030712"
                    self.canvas.create_text(
                        x1 + SQUARE_SIZE / 2,
                        y1 + SQUARE_SIZE / 2,
                        text=UNICODE_PIECES[piece.symbol()],
                        font=FONT_PIECE,
                        fill=piece_color,
                    )

                if square in self.legal_targets:
                    self.canvas.create_oval(
                        x1 + SQUARE_SIZE * 0.38,
                        y1 + SQUARE_SIZE * 0.38,
                        x1 + SQUARE_SIZE * 0.62,
                        y1 + SQUARE_SIZE * 0.62,
                        fill=MOVE_DOT_COLOR,
                        outline="",
                    )

        self._draw_coordinates()

    def _draw_coordinates(self):
        for file in range(8):
            label = chr(ord("a") + file)
            if self.settings.player_color == chess.BLACK:
                label = chr(ord("a") + (7 - file))

            x = file * SQUARE_SIZE + 6
            y = 8 * SQUARE_SIZE - 14

            self.canvas.create_text(
                x,
                y,
                text=label,
                anchor="w",
                font=("Segoe UI", 9, "bold"),
                fill="#374151",
            )

        for rank in range(8):
            label = str(8 - rank)
            if self.settings.player_color == chess.BLACK:
                label = str(rank + 1)

            x = 6
            y = rank * SQUARE_SIZE + 6

            self.canvas.create_text(
                x,
                y,
                text=label,
                anchor="nw",
                font=("Segoe UI", 9, "bold"),
                fill="#374151",
            )

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
        if not self.settings.use_timer:
            return

        self._stop_timer_loop()
        self.timer_after_id = self.after(1000, self._timer_tick)

    def _stop_timer_loop(self):
        if self.timer_after_id is not None:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None

    def _timer_tick(self):
        self.timer_after_id = None

        if self.controller.game_over:
            self._update_labels()
            return

        timed_out = self.controller.tick()
        self._update_labels()

        if timed_out:
            self._draw_board()
            return

        self.timer_after_id = self.after(1000, self._timer_tick)

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
        self._stop_timer_loop()

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
