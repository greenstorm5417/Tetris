import pygame
from shape import TETROMINO_DATA
from color import BLACK, WHITE, RED, GREEN, BLUE, CYAN, NEON_BLUE, YELLOW, MAGENTA, ORANGE, LIGHT_GRAY

def draw_grid(self, GRID_WIDTH, GRID_HEIGHT, BLOCK_SIZE):
    # Fill the screen with a light grey background
    self.screen.fill(LIGHT_GRAY)
    
    # Draw each block in the grid with highlights for placed blocks
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            # If the grid cell is not empty (i.e., contains a locked block), draw it with a highlight
            if self.grid[y][x] != BLACK:
                draw_clean_block(self, self.grid[y][x], 
                                (self.play_area_x + x * BLOCK_SIZE, self.play_area_y + y * BLOCK_SIZE),
                                BLOCK_SIZE)
            else:
                # Otherwise, draw an empty grid cell
                pygame.draw.rect(self.screen, BLACK,
                                 (self.play_area_x + x * BLOCK_SIZE, self.play_area_y + y * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE), 0)

    # After drawing blocks, draw the grid lines in white, but only for empty spaces
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            # Only draw grid lines (white) on empty cells
            if self.grid[y][x] == BLACK:
                pygame.draw.rect(self.screen, WHITE,
                                 (self.play_area_x + x * BLOCK_SIZE, self.play_area_y + y * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE), 1)

    # Draw an outline for the play area outside the blocks, ensuring it doesn't overlap with the blocks
    pygame.draw.rect(self.screen, WHITE, (self.play_area_x - 2, self.play_area_y - 2, GRID_WIDTH * BLOCK_SIZE + 4, GRID_HEIGHT * BLOCK_SIZE + 4), 4)

def draw_held_piece(self, BLOCK_SIZE):
    # Draw the box around the held piece with a label
    label = self.font.render('Hold', True, WHITE)
    self.screen.blit(label, (self.play_area_x - 6 * BLOCK_SIZE, self.play_area_y - 2 * BLOCK_SIZE))

    # Draw the box for the held piece
    pygame.draw.rect(self.screen, WHITE, (self.play_area_x - 6 * BLOCK_SIZE, self.play_area_y, 5 * BLOCK_SIZE, 5 * BLOCK_SIZE), 3)

    if self.hold_tetromino is None:
        return

    # Get the held tetromino data (rotations, color, and rotation point)
    tetromino_data = TETROMINO_DATA[self.hold_tetromino]
    
    # Always display the first rotation
    shape = tetromino_data['rotations'][0]  
    color = tetromino_data['color']


    # Center the held tetromino inside the box
    shape_width = max(x for x, _ in shape) + 1
    shape_height = max(y for _, y in shape) + 1
    offset_x = (5 - shape_width) // 2
    offset_y = (5 - shape_height) // 2

    for x, y in shape:
        draw_clean_block(self, color, 
                         (self.play_area_x - 6 * BLOCK_SIZE + (x + offset_x) * BLOCK_SIZE,
                          self.play_area_y + (y + offset_y) * BLOCK_SIZE), BLOCK_SIZE)

def draw_next_piece(self, BLOCK_SIZE):
    # Draw the box around the next piece with a label
    label = self.font.render('Next', True, WHITE)
    self.screen.blit(label, (self.play_area_x + 11 * BLOCK_SIZE, self.play_area_y - 2 * BLOCK_SIZE))

    pygame.draw.rect(self.screen, WHITE, (self.play_area_x + 11 * BLOCK_SIZE, self.play_area_y, 5 * BLOCK_SIZE, 5 * BLOCK_SIZE), 3)

    # Get the held tetromino data (rotations, color, and rotation point)
    tetromino_data = TETROMINO_DATA[self.next_tetromino]
    
    # Always display the first rotation
    shape = tetromino_data['rotations'][0]  
    color = tetromino_data['color']


    # Calculate the width and height of the tetromino in blocks
    shape_width = max(x for x, _ in shape) + 1
    shape_height = max(y for _, y in shape) + 1

    # The box is 5x5, calculate the offset to center the shape inside the box
    offset_x = (5 - shape_width) * BLOCK_SIZE // 2
    offset_y = (5 - shape_height) * BLOCK_SIZE // 2

    # Draw the next tetromino centered in the box
    for x, y in shape:
        draw_clean_block(self, color, 
                         (self.play_area_x + 11 * BLOCK_SIZE + offset_x + x * BLOCK_SIZE,
                          self.play_area_y + offset_y + y * BLOCK_SIZE), BLOCK_SIZE)

def draw_tetromino(self, tetromino, position, color, BLOCK_SIZE):
    # Draw the tetromino blocks
    for x, y in tetromino:
        draw_clean_block(self, color, (self.play_area_x + (x + position[0]) * BLOCK_SIZE,
                                       self.play_area_y + (y + position[1]) * BLOCK_SIZE), BLOCK_SIZE)

    # Draw the rotation point based on the current tetromino type if the flag is set
    if self.show_rotation_points:
        tetromino_data = TETROMINO_DATA[self.current_tetromino]
        rotation_point = tetromino_data['rotation_point']

        pygame.draw.circle(self.screen, NEON_BLUE,
                           (self.play_area_x + (position[0] + rotation_point[0]) * BLOCK_SIZE,
                            self.play_area_y + (position[1] + rotation_point[1]) * BLOCK_SIZE), 5)

def draw_clean_block(self, color, position, BLOCK_SIZE):
    # Draw the base block with a solid color
    pygame.draw.rect(self.screen, color, (position[0], position[1], BLOCK_SIZE, BLOCK_SIZE))

    # Create highlight and shadow colors based on the block's original color
    r, g, b = color
    highlight = (min(r + 80, 255), min(g + 80, 255), min(b + 80, 255))  # Brighter highlight for the top/left
    mid_highlight = (min(r + 40, 255), min(g + 40, 255), min(b + 40, 255))  # Slightly less bright for blending
    shadow_right = (max(r - 30, 0), max(g - 30, 0), max(b - 30, 0))  # Slightly darker shadow for the right
    shadow_bottom = (max(r - 60, 0), max(g - 60, 0), max(b - 60, 0))  # Stronger shadow for the bottom

    # Add highlights (top and left sides) with thicker lines
    pygame.draw.polygon(self.screen, highlight, [(position[0], position[1]), (position[0] + BLOCK_SIZE, position[1]), (position[0] + BLOCK_SIZE - 4, position[1] + 4), (position[0] + 4, position[1] + 4)])  # Top
    pygame.draw.polygon(self.screen, highlight, [(position[0], position[1]), (position[0], position[1] + BLOCK_SIZE), (position[0] + 4, position[1] + BLOCK_SIZE - 4), (position[0] + 4, position[1] + 4)])  # Left

    # Add mid-highlight further towards the center for smoother blending
    pygame.draw.line(self.screen, mid_highlight, (position[0] + 4, position[1] + 4), (position[0] + BLOCK_SIZE - 4, position[1] + 4), 3)  # Top blend
    pygame.draw.line(self.screen, mid_highlight, (position[0] + 4, position[1] + 4), (position[0] + 4, position[1] + BLOCK_SIZE - 4), 3)  # Left blend

    # Add shadows (bottom and right sides)
    pygame.draw.polygon(self.screen, shadow_bottom, [(position[0], position[1] + BLOCK_SIZE - 1), (position[0] + BLOCK_SIZE, position[1] + BLOCK_SIZE - 1), (position[0] + BLOCK_SIZE - 4, position[1] + BLOCK_SIZE - 5), (position[0] + 4, position[1] + BLOCK_SIZE - 5)])  # Bottom
    pygame.draw.polygon(self.screen, shadow_right, [(position[0] + BLOCK_SIZE - 1, position[1]), (position[0] + BLOCK_SIZE - 1, position[1] + BLOCK_SIZE), (position[0] + BLOCK_SIZE - 5, position[1] + BLOCK_SIZE - 4), (position[0] + BLOCK_SIZE - 5, position[1] + 4)])  # Right

    # Final shadow blending
    pygame.draw.line(self.screen, shadow_right, (position[0] + BLOCK_SIZE - 5, position[1] + 4), (position[0] + BLOCK_SIZE - 5, position[1] + BLOCK_SIZE - 4), 2)  # Right blend
    pygame.draw.line(self.screen, shadow_bottom, (position[0] + 4, position[1] + BLOCK_SIZE - 5), (position[0] + BLOCK_SIZE - 4, position[1] + BLOCK_SIZE - 5), 2)  # Bottom blend

def draw_best_move(self, BLOCK_SIZE):
    if hasattr(self, 'best_move') and self.best_move:
        # Extract the tetromino shape and position from the best move
        best_tetromino_shape = self.best_move['tetromino_shape']
        best_position = self.best_move['position']

        # Create a transparent surface for the best move tetromino
        best_move_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        
        # Calculate a 50% transparent orange color (for the best move)
        transparent_orange = (255, 165, 0, 128)  # 128 is the alpha value (50% transparency)
        
        # Fill the surface with the transparent orange color
        best_move_surface.fill(transparent_orange)

        # Draw the best move's tetromino as both filled (with transparency) and outlined
        for x, y in best_tetromino_shape:
            # Draw the transparent block
            self.screen.blit(best_move_surface, (self.play_area_x + (x + best_position[0]) * BLOCK_SIZE,
                                                 self.play_area_y + (y + best_position[1]) * BLOCK_SIZE))
            
            # Draw the outline (not transparent)
            best_rect = pygame.Rect(self.play_area_x + (x + best_position[0]) * BLOCK_SIZE,
                                    self.play_area_y + (y + best_position[1]) * BLOCK_SIZE,
                                    BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(self.screen, ORANGE, best_rect, 2)  # Draw border with thickness 2


def draw_game_info(self):
    # Render the text for score, level, and fall speed
    score_text = self.font.render(f"Score: {self.score}", True, WHITE)
    level_text = self.font.render(f"Level: {self.level}", True, WHITE)
    speed_text = self.font.render(f"Fall Speed: {self.fall_speed}ms", True, WHITE)

    # Blit the text to the screen (position them above the game area)
    self.screen.blit(score_text, (self.play_area_x, self.play_area_y - 75))  # Above the game area
    self.screen.blit(level_text, (self.play_area_x, self.play_area_y - 50))  # Next to the score
    self.screen.blit(speed_text, (self.play_area_x, self.play_area_y - 25))  # Next to the level

def draw_ghost_piece(self, tetromino, position, color, BLOCK_SIZE):
    # Make a copy of the current position for the ghost piece
    ghost_position = position.copy()
    
    # Simulate dropping the tetromino down to the furthest valid position
    ghost_position = self.simulate_instant_drop(tetromino, ghost_position)

    # Create a transparent surface for the ghost tetromino
    ghost_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
    
    # Calculate a 50% transparent version of the color
    r, g, b = color
    transparent_color = (r, g, b, 128)  # 128 is the alpha value (50% transparency)
    
    # Fill the surface with the transparent color
    ghost_surface.fill(transparent_color)
    
    # Draw the ghost piece as both filled (with transparency) and outlined
    for x, y in tetromino:
        # Draw the transparent block
        self.screen.blit(ghost_surface, (self.play_area_x + (x + ghost_position[0]) * BLOCK_SIZE,
                                         self.play_area_y + (y + ghost_position[1]) * BLOCK_SIZE))
        
        # Draw the outline (not transparent)
        ghost_rect = pygame.Rect(self.play_area_x + (x + ghost_position[0]) * BLOCK_SIZE,
                                 self.play_area_y + (y + ghost_position[1]) * BLOCK_SIZE,
                                 BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.screen, color, ghost_rect, 1)  # Draw outline (thinner than real blocks)


