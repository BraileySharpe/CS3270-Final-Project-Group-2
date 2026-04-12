from dataclasses import dataclass
import chess

@dataclass
class GameSettings:
    player_color: chess.Color = chess.WHITE
    opponent_enabled: bool = True
    opponent_name: str = "AI Opponent"
    use_timer: bool = True
    initial_time_seconds: int = 10 * 60