import pygame
import random
import os
import sys
import json
import time

# Initialize Pygame
pygame.init()

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Load block images - Replace these paths with your actual image paths
BLOCK_IMAGES = {
    'I': pygame.image.load('cyan.png'),
    'O': pygame.image.load('yellow.png'),
    'T': pygame.image.load('purple.png'),
    'S': pygame.image.load('green.png'),
    'Z': pygame.image.load('red.png'),
    'J': pygame.image.load('blue.png'),
    'L': pygame.image.load('orange.png')
}

# Scale images to match BLOCK_SIZE
for key in BLOCK_IMAGES:
    BLOCK_IMAGES[key] = pygame.transform.scale(BLOCK_IMAGES[key], (BLOCK_SIZE, BLOCK_SIZE))

# Tetromino shapes with their corresponding image keys
SHAPES = [
    {'shape': [[1, 1, 1, 1]], 'key': 'I'},
    {'shape': [[1, 1], [1, 1]], 'key': 'O'},
    {'shape': [[0, 1, 0], [1, 1, 1]], 'key': 'T'},
    {'shape': [[0, 1, 1], [1, 1, 0]], 'key': 'S'},
    {'shape': [[1, 1, 0], [0, 1, 1]], 'key': 'Z'},
    {'shape': [[0, 0, 1], [1, 1, 1]], 'key': 'J'},
    {'shape': [[1, 0, 0], [1, 1, 1]], 'key': 'L'}
]

class Piece:
    def __init__(self, shape_data=None):
        if shape_data is None:
            self.shape_data = random.choice(SHAPES)
        else:
            self.shape_data = shape_data
        self.shape = self.shape_data['shape']
        self.image_key = self.shape_data['key']
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))

class Tetris:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.game_over = False
        self.score = 0
        self.moves = []  # Store moves for replay
        self.replay_mode = False
        self.current_piece_index = 0  # Track which piece we're on
        self.piece_sequence = []  # Initialize piece_sequence before spawning piece
        self.spawn_piece()

    def spawn_piece(self):
        if self.replay_mode and self.current_piece_index < len(self.piece_sequence):
            # In replay mode, use the stored piece sequence
            shape_data = self.piece_sequence[self.current_piece_index]
            self.current_piece = Piece(shape_data)
            self.current_piece_index += 1
        else:
            # In normal mode, generate a random piece and store it
            self.current_piece = Piece()
            if not self.replay_mode:
                self.piece_sequence.append(self.current_piece.shape_data)
                self.current_piece_index += 1
        
        if self.check_collision():
            self.game_over = True

    # ... rest of the Tetris class remains the same ...

    def record_move(self, move_type, data=None):
        if not self.replay_mode:
            timestamp = time.time()
            self.moves.append({
                'type': move_type,
                'time': timestamp,
                'data': data
            })

    def save_replay(self):
        replay_data = {
            'piece_sequence': self.piece_sequence,
            'moves': self.moves,
            'final_score': self.score
        }
        with open('tetris_replay.json', 'w') as f:
            json.dump(replay_data, f)

    @staticmethod
    def load_replay():
        with open('tetris_replay.json', 'r') as f:
            return json.load(f)

    def check_collision(self, offset_x=0, offset_y=0):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_piece.x + x + offset_x
                    new_y = self.current_piece.y + y + offset_y

                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x] is not None)):
                        return True
        return False

    def merge_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.image_key

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                lines_cleared += 1
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
            else:
                y -= 1
        self.score += lines_cleared * 100

    def move(self, dx, dy):
        if not self.check_collision(dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            if not self.replay_mode:
                self.record_move('move', {'dx': dx, 'dy': dy})
            return True
        return False

    def rotate_piece(self):
        original_shape = self.current_piece.shape
        self.current_piece.rotate()
        if self.check_collision():
            self.current_piece.shape = original_shape
        else:
            if not self.replay_mode:
                self.record_move('rotate')

    def update(self):
        if not self.move(0, 1):
            self.merge_piece()
            self.clear_lines()
            self.spawn_piece()

    def draw(self):
        screen.fill((0, 0, 0))
        
        # Draw the grid
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell is not None:
                    screen.blit(BLOCK_IMAGES[cell],
                              (x * BLOCK_SIZE, y * BLOCK_SIZE))

        # Draw the current piece
        if self.current_piece:
            for y, row in enumerate(self.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        screen.blit(BLOCK_IMAGES[self.current_piece.image_key],
                                  ((self.current_piece.x + x) * BLOCK_SIZE,
                                   (self.current_piece.y + y) * BLOCK_SIZE))

class Blocker:
    def __init__(self):
        self.x = random.randint(0, GRID_WIDTH - 1)
        self.y = 0
        self.image = pygame.image.load('character.png')
        self.velocity = 0
        self.game_over = False

    def move(self):
        self.x = self.x + self.velocity * 5
        self.velocity = 0

    def draw(self):
        pygame.draw.rect(screen, self.image, (self.x * BLOCK_SIZE, self.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        
    def check_blocker_collision(self):
        # Check if blocker collides with any blocks in the grid
        for y, row in enumerate(game.grid):
            if y == self.y and row[self.x] is not None:
                # Collision with block at same level
                if y == 0 or game.grid[y-1][self.x] is not None:
                    # Game over if block above or at top
                    self.game_over = True        

def play_replay(replay_data):
    clock = pygame.time.Clock()
    game = Tetris()
    game.replay_mode = True
    game.piece_sequence = replay_data['piece_sequence']
    moves = replay_data['moves']
    move_index = 0
    blocker = Blocker()
    
    while move_index < len(moves) and not blocker.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    blocker.velocity = -1
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    blocker.velocity = 1

        # Process the next move
        if move_index < len(moves):
            move = moves[move_index]
            if move['type'] == 'move':
                game.move(move['data']['dx'], move['data']['dy'])
            elif move['type'] == 'rotate':
                game.rotate_piece()
            move_index += 1

        blocker.move()
        blocker.check_blocker_collision()
        if blocker.game_over:
            break
        game.update()
        game.draw()
        
        # Draw score and replay indicator
        font = pygame.font.Font(None, 36)
        
        pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    game = Tetris()
    fall_time = 0
    fall_speed = 500

    while not game.game_over:
        fall_time += clock.get_rawtime()
        clock.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    game.move(0, 1)
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    while game.move(0, 1):
                        pass

        if fall_time >= fall_speed:
            game.update()
            fall_time = 0

        game.draw()
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {game.score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()

    # Save replay when game is over
    game.save_replay()

    while True:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 72)
        game_over_text = font.render('PART 2: \nDODGE THE BLOCKS!', True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
        pygame.display.flip()

        # Load and play the replay
        replay_data = Tetris.load_replay()
        play_replay(replay_data)
        break

if __name__ == '__main__':
    main()
    pygame.quit()