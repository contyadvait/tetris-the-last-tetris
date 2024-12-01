import pygame
import random
import os
import sys
import json
import time

pygame.init()

BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris: The Last Tetris')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

BLOCK_IMAGES = {
    'I': pygame.image.load('cyan.png'),
    'O': pygame.image.load('yellow.png'),
    'T': pygame.image.load('purple.png'),
    'S': pygame.image.load('green.png'),
    'Z': pygame.image.load('red.png'),
    'J': pygame.image.load('blue.png'),
    'L': pygame.image.load('orange.png')
}

for key in BLOCK_IMAGES:
    BLOCK_IMAGES[key] = pygame.transform.scale(BLOCK_IMAGES[key], (BLOCK_SIZE, BLOCK_SIZE))

def load_font(size):
    try:
        return pygame.font.Font("neuebit.ttf", size)
    except:
        return pygame.font.Font(None, size)

def draw_centered_text(screen, text, font, color, y_position):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_position))
    screen.blit(text_surface, text_rect)


def start_screen():
    screen.fill(BLACK)
    try:
        logo = pygame.image.load('logo.png')
        logo_width = min(SCREEN_WIDTH * 0.8, logo.get_width())
        logo_height = int(logo.get_height() * (logo_width / logo.get_width()))
        logo = pygame.transform.scale(logo, (int(logo_width), int(logo_height)))
        
        logo_rect = logo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(logo, logo_rect)
    except Exception as e:
        print(f"Could not load logo: {e}")
        
    title_font = load_font(min(72, SCREEN_WIDTH // 10))
    subtitle_font = load_font(min(56, SCREEN_WIDTH // 12))
    
    draw_centered_text(screen, 'Press SPACEBAR to Start', subtitle_font, WHITE, SCREEN_HEIGHT * 2 // 3)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True


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
        self.moves = [] 
        self.replay_mode = False
        self.current_piece_index = 0
        self.piece_sequence = [] 
        self.spawn_piece()

    def spawn_piece(self):
        if self.replay_mode and self.current_piece_index < len(self.piece_sequence):
            shape_data = self.piece_sequence[self.current_piece_index]
            self.current_piece = Piece(shape_data)
            self.current_piece_index += 1
        else:
            self.current_piece = Piece()
            if not self.replay_mode:
                self.piece_sequence.append(self.current_piece.shape_data)
                self.current_piece_index += 1
        
        if self.check_collision():
            self.game_over = True

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
        
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell is not None:
                    screen.blit(BLOCK_IMAGES[cell],
                              (x * BLOCK_SIZE, y * BLOCK_SIZE))

        if self.current_piece:
            for y, row in enumerate(self.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        screen.blit(BLOCK_IMAGES[self.current_piece.image_key],
                                  ((self.current_piece.x + x) * BLOCK_SIZE,
                                   (self.current_piece.y + y) * BLOCK_SIZE))

class Blocker:
    def __init__(self):
        self.x = GRID_WIDTH // 2 
        self.y = GRID_HEIGHT - 1 
        self.image = pygame.image.load('character.png')
        self.velocity = 0
        self.game_over = False

    def move(self):
        self.x = max(0, min(GRID_WIDTH - 1, self.x + self.velocity))
        self.velocity = 0

    def draw(self):
        screen.blit(self.image, (self.x * BLOCK_SIZE, self.y * BLOCK_SIZE))
        
    def check_collision(self, game):
        if game.grid[self.y][self.x] is not None:
            return True
        return False

def play_replay(replay_data):
    clock = pygame.time.Clock()
    game = Tetris()
    game.replay_mode = True
    game.piece_sequence = replay_data['piece_sequence']
    moves = replay_data['moves']
    move_index = 0
    
    hit = False

    player_blocker = Blocker()
    
    blockers = []
    blocker_spawn_interval = 120
    frame_count = 0
    blocker_fall_speed = 0
    
    while not game.game_over and not player_blocker.game_over:
        clock.tick(15)
        frame_count += 1
        
        if frame_count % blocker_spawn_interval == 0:
            new_blocker = Blocker()
            new_blocker.x = random.randint(0, GRID_WIDTH - 1)
            new_blocker.y = 0
            blockers.append(new_blocker)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    player_blocker.velocity = -1
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    player_blocker.velocity = 1
        
        if move_index < len(moves):
            move = moves[move_index]
            
            if move['type'] == 'move':
                dx = move['data']['dx']
                dy = move['data']['dy']
                
                if dx != 0:
                    while not game.check_collision(dx, 0):
                        game.current_piece.x += dx
                        break
                
                if dy != 0:
                    while not game.check_collision(0, dy):
                        game.current_piece.y += dy
                        break
                
                move_index += 1
            
            elif move['type'] == 'rotate':
                game.rotate_piece()
                move_index += 1
        
        blocker_fall_speed += 1
        if blocker_fall_speed >= 10:
            for blocker in blockers[:]:
                blocker.move()
                blocker.y += 1
                
                if blocker.y >= GRID_HEIGHT:
                    blockers.remove(blocker)
                    continue
            
            blocker_fall_speed = 0
        
        player_blocker.move()
        
        if player_blocker.check_collision(game):
            player_blocker.game_over = True
            hit = True
            break
        
        game.update()
        game.draw()
        
        for blocker in blockers:
            blocker.draw()
        
        player_blocker.draw()
        
        pygame.display.flip()
    
    while True:
        screen.fill(BLACK)
        game_over_font = load_font(min(72, SCREEN_WIDTH // 10))
        subtitle_font = load_font(min(56, SCREEN_WIDTH // 12))

        if hit:
            draw_centered_text(screen, 'Game Over', game_over_font, RED, SCREEN_HEIGHT // 3)
            draw_centered_text(screen, f'You died because you got hit by the blocks', subtitle_font, WHITE, SCREEN_HEIGHT // 2)
            draw_centered_text(screen, f'Final Score: {game.score}', subtitle_font, WHITE, SCREEN_HEIGHT * 2 // 3)
        else:
            draw_centered_text(screen, 'You win!', game_over_font, WHITE, SCREEN_HEIGHT // 3)
            draw_centered_text(screen, f'Final Score: {game.score}', subtitle_font, WHITE, SCREEN_HEIGHT // 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

def main():
    if not start_screen():
        return

    clock = pygame.time.Clock()
    game = Tetris()
    fall_time = 0
    fall_speed = 240

    score_font = load_font(min(72, SCREEN_WIDTH // 15))

    while not game.game_over:
        fall_time += clock.get_rawtime()
        clock.tick(fall_speed)

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
        
        score_text = score_font.render(f'Score: {game.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()

    game.save_replay()

    screen.fill(BLACK)
    game_over_font = load_font(min(72, SCREEN_WIDTH // 10))
    subtitle_font = load_font(min(56, SCREEN_WIDTH // 12))

    draw_centered_text(screen, 'Game Over', game_over_font, RED, SCREEN_HEIGHT // 3)
    draw_centered_text(screen, f'Final Score: {game.score}', subtitle_font, WHITE, SCREEN_HEIGHT // 2)
    draw_centered_text(screen, 'Press SPACEBAR to continue', subtitle_font, WHITE, SCREEN_HEIGHT * 2 // 3)
    
    pygame.display.flip()

    # Wait for spacebar to continue to replay
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

    # Load and play the replay
    replay_data = Tetris.load_replay()
    play_replay(replay_data)
    clock = pygame.time.Clock()
    game = Tetris()
    fall_time = 0
    fall_speed = 240

    while not game.game_over:
        fall_time += clock.get_rawtime()
        clock.tick(fall_speed)

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
        
        font = pygame.font.Font("neuebit.ttf", 36)
        score_text = font.render(f'Score: {game.score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()

    # Save replay when game is over
    game.save_replay()

    while True:
        screen.fill((0, 0, 0))
        font = pygame.font.Font("neuebit.ttf", 72)
        game_over_text = font.render('Part 2', True, (255, 0, 0))
        game_over_text2 = font.render('Dodge the blocks!', True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
        pygame.display.flip()
        time.sleep(2)   

        # Load and play the replay
        replay_data = Tetris.load_replay()
        play_replay(replay_data)
        break

if __name__ == '__main__':
    main()
    pygame.quit()