import random
import json
import time
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class GameAction:
    timestamp: float  # Time since game start
    action_type: str  # 'spawn', 'move', 'rotate', 'lock', 'clear'
    piece_type: str = None  # 'I', 'O', 'T', etc.
    position: Tuple[int, int] = None  # (x, y)
    rotation_state: List[List[int]] = None
    lines_cleared: List[int] = None  # For clear actions
    score: int = 0

class ReplayRecorder:
    def __init__(self):
        self.actions: List[GameAction] = []
        self.start_time = time.time()
        
    def record_action(self, action_type: str, **kwargs):
        action = GameAction(
            timestamp=time.time() - self.start_time,
            action_type=action_type,
            **kwargs
        )
        self.actions.append(action)
    
    def save_replay(self, filename):
        replay_data = {
            'start_time': self.start_time,
            'actions': [(
                action.timestamp,
                action.action_type,
                action.piece_type,
                action.position,
                action.rotation_state,
                action.lines_cleared,
                action.score
            ) for action in self.actions]
        }
        with open(filename, 'w') as f:
            json.dump(replay_data, f)

class Piece:
    def __init__(self):
        self.shape_data = random.choice(SHAPES)
        self.shape = self.shape_data['shape']
        self.image_key = self.shape_data['key']
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.rotation_state = 0  # Track rotation state (0-3)

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))
        self.rotation_state = (self.rotation_state + 1) % 4

class Tetris:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.game_over = False
        self.score = 0
        self.recorder = ReplayRecorder()
        self.spawn_piece()

    def spawn_piece(self):
        self.current_piece = Piece()
        if self.check_collision():
            self.game_over = True
        else:
            self.recorder.record_action(
                'spawn',
                piece_type=self.current_piece.image_key,
                position=(self.current_piece.x, self.current_piece.y),
                rotation_state=self.current_piece.shape,
                score=self.score
            )

    # Additional methods like move, rotate_piece, merge_piece, clear_lines, etc.
