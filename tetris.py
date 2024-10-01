import pygame
import random
from shape import TETROMINO_DATA
from color import BLACK, WHITE, RED, GREEN, BLUE, CYAN, NEON_BLUE, YELLOW, MAGENTA, ORANGE
from draw import draw_grid, draw_held_piece, draw_next_piece, draw_tetromino, draw_best_move, draw_game_info, draw_ghost_piece
import copy
from brain import Brain

# Initialize Pygame
pygame.init()

# Official Tetris play area dimensions
PLAY_WIDTH = 10 * 30  # 10 blocks wide
PLAY_HEIGHT = 20 * 30  # 20 blocks high
BLOCK_SIZE = 30
GRID_WIDTH = PLAY_WIDTH // BLOCK_SIZE
GRID_HEIGHT = PLAY_HEIGHT // BLOCK_SIZE

# Fullscreen dimensions
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h


def get_new_bag():
    return random.sample(list(TETROMINO_DATA.keys()), len(TETROMINO_DATA))


class BlockMatrix:
    def __init__(self, grid):
        self.grid = grid

    def count_holes(self):
        holes = 0
        for col in range(len(self.grid[0])):  # Iterate through each column
            block_found = False
            for row in range(len(self.grid)):  # Iterate through each row in the column
                if self.grid[row][col] != BLACK:  # Block found
                    block_found = True
                elif block_found:  # Hole found below a block
                    holes += 1
        return holes

    def count_pillars(self):
        pillar_holes = 0

        # Iterate through all columns except the first and last (since they can't have holes with blocks on both sides)
        for col in range(1, len(self.grid[0]) - 1):
            depth = 0
            in_hole = False

            for row in range(len(self.grid)):  # Iterate through each row in the column
                if self.grid[row][col] == BLACK:  # Empty cell (potential hole)
                    # Check if there's a block on both the left and right sides of this hole
                    if self.grid[row][col - 1] != BLACK and self.grid[row][col + 1] != BLACK:
                        if in_hole:  # Continue tracking depth
                            depth += 1
                        else:  # Start a new hole
                            in_hole = True
                            depth = 1
                    else:
                        in_hole = False  # Not a valid hole, reset tracking
                else:  # Block encountered
                    if in_hole and depth >= 3:  # If we finished a valid hole (3 or more blocks deep)
                        pillar_holes += 1
                    in_hole = False  # Reset hole tracking when a block is found
                    depth = 0

            # Check if the column ends with a valid hole
            if in_hole and depth >= 3:
                pillar_holes += 1

        return pillar_holes

    def calculate_maximum_line_height(self, tetromino, position):
        max_y = 0
        for x, y in tetromino:
            # Calculate the global Y position of each block in the tetromino
            global_y = y + position[1]
            # Update max_y if the current block is higher (greater Y value)
            if global_y > max_y:
                max_y = global_y
        finalY= (PLAY_HEIGHT//BLOCK_SIZE)-max_y
        return finalY

    def calculate_bumpiness(self):
        bumpiness = 0
        heights = [self.calculate_column_height(col) for col in range(len(self.grid[0]))]
        for i in range(len(heights) - 1):
            bumpiness += abs(heights[i] - heights[i + 1])
        return bumpiness

    def calculate_column_height(self, col):
        for row in range(len(self.grid)):
            if self.grid[row][col] != BLACK:
                return len(self.grid) - row  # Return height from the bottom
        return 0  # No blocks found in the column

    def count_number_of_blocks_in_rightmost_lane(self):
        blocks = 0
        rightmost_col = len(self.grid[0]) - 1
        for row in range(len(self.grid)):
            if self.grid[row][rightmost_col] != BLACK:
                blocks += 1
        return blocks

    def count_blocks_above_holes(self):
        blocks_above_holes = 0

        for col in range(len(self.grid[0])):  # Iterate through each column
            hole_found = False

            for row in range(len(self.grid)):  # Iterate through each row
                if self.grid[row][col] == BLACK:  # Hole found
                    hole_found = True
                elif hole_found:  # Block found above a hole
                    blocks_above_holes += 1

        return blocks_above_holes

    def calculate_lines_cleared(self, grid):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(grid[y][x] != BLACK for x in range(GRID_WIDTH)):
                lines_cleared += 1
        return lines_cleared


class Tetris:
    def __init__(self):
        Brain.adjust_multipliers(self,holes_weight=4.5, blocks_above_holes_weight=0, pillars_weight=2.0, max_height_weight=2, bumpiness_weight=0, blocks_in_rightmost_lane_weight=0)

        self.show_rotation_points = False
        self.hold_used = False

        # Borderless fullscreen but with official play area size
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)

        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.total_lines_cleared = 0 
        self.fall_speed = 500 
        self.bag = get_new_bag()
        
        # Initialize current and next tetromino
        self.rotation = 0
        self.current_tetromino = self.get_next_tetromino()
        self.next_tetromino = self.get_next_tetromino()
        
        # Now set the color and shape based on the current tetromino
        tetromino_data = TETROMINO_DATA[self.current_tetromino]
        self.tetromino_color = tetromino_data['color']
        self.tetromino_shape = tetromino_data['rotations'][self.rotation]




        # Initialize other game variables
        self.hold_tetromino = None
        self.locked_positions = {}
        self.rotation = 0  # Rotation state for the current tetromino
        self.play_area_x = (SCREEN_WIDTH - PLAY_WIDTH) // 2  # Center play area horizontally
        self.play_area_y = (SCREEN_HEIGHT - PLAY_HEIGHT) // 2  # Center play area vertically

        # Initialize the BlockMatrix with the current grid
        self.blockMatrix = BlockMatrix(self.grid)

        self.possible_moves = self.generate_moves_for_current_piece()

    def generate_possible_moves(self, tetromino, initial_position):
        possible_moves = []

        # Loop through all possible rotations for the current tetromino
        for rotation_index in range(len(TETROMINO_DATA[tetromino]['rotations'])):
            rotated_tetromino = TETROMINO_DATA[tetromino]['rotations'][rotation_index]



            # Compute the minimal and maximal x-values of the tetromino shape
            min_x = min([x for x, y in rotated_tetromino])
            max_x = max([x for x, y in rotated_tetromino])

            # Now, compute the range of possible columns where the tetromino can be placed
            for col in range(-min_x, GRID_WIDTH - max_x):
                # Start from the top row at the given column position
                tetromino_position = [col, 0]

                # Check for collision at the starting position
                if not self.check_collision(rotated_tetromino, tetromino_position):
                    # Apply the instant drop to this position and rotation
                    drop_position = self.simulate_instant_drop(rotated_tetromino, tetromino_position)

                    # Check if the drop position is valid (no collision)
                    if not self.check_collision(rotated_tetromino, drop_position):
                        # Clone the grid to simulate the tetromino placement
                        cloned_grid = copy.deepcopy(self.grid)

                        # Simulate locking the tetromino on the cloned grid
                        self.simulate_lock_tetromino(cloned_grid, rotated_tetromino, drop_position)

                        # Calculate the grid state statistics for the cloned grid
                        block_matrix = BlockMatrix(cloned_grid)
                        holes = block_matrix.count_holes()
                        pillars = block_matrix.count_pillars()
                        max_height = block_matrix.calculate_maximum_line_height(rotated_tetromino, drop_position)
                        bumpiness = block_matrix.calculate_bumpiness()
                        blocks_above_holes = block_matrix.count_blocks_above_holes()
                        blocks_in_rightmost_lane = block_matrix.count_number_of_blocks_in_rightmost_lane()
                        lines_cleared = block_matrix.calculate_lines_cleared(cloned_grid)


                        total_weight = Brain.compute_weight(
                            self, holes, blocks_above_holes, pillars, max_height, bumpiness, blocks_in_rightmost_lane, lines_cleared
                        )

                        # Save the move, including the final block matrix (grid) and its weight
                        possible_moves.append({
                            'rotation': rotation_index,
                            'position': drop_position,
                            'tetromino_shape': rotated_tetromino,
                            'grid_state': cloned_grid,  # Save the cloned grid state
                            'holes': holes,
                            'pillars': pillars,
                            'max_height': max_height,
                            'bumpiness': bumpiness,
                            'blocks_above_holes': blocks_above_holes,
                            'weight': total_weight  # Add this line to store the computed weight
                        })

        return possible_moves

    def simulate_lock_tetromino(self, grid, tetromino, position):
        for x, y in tetromino:
            grid[y + position[1]][x + position[0]] = TETROMINO_DATA[self.current_tetromino]['color']
        
    def instant_drop(self, tetromino_shape, tetromino_position):
        # Perform the drop by continuously moving the piece down until collision
        while not self.check_collision(tetromino_shape, [tetromino_position[0], tetromino_position[1] + 1]):
            tetromino_position[1] += 1

        # Once it collides, lock the piece in place
        self.lock_tetromino(tetromino_shape, tetromino_position, TETROMINO_DATA[self.current_tetromino]['color'])
        
        # Clear any completed lines after locking
        self.clear_lines(self.current_tetromino)
        
        # Reset tetromino position, color, and shape for the next piece
        self.hold_used = False  # Allow holding again for the next piece
        self.current_tetromino = self.next_tetromino
        self.next_tetromino = self.get_next_tetromino()
        
        # Reset rotation to 0 for the new tetromino
        self.rotation = 0
        
        # Ensure the new tetromino uses the correct shape and color
        self.tetromino_color = TETROMINO_DATA[self.current_tetromino]['color']
        self.tetromino_shape = TETROMINO_DATA[self.current_tetromino]['rotations'][self.rotation]
        
        # Reset position for the new tetromino
        tetromino_position[0], tetromino_position[1] = 4, 0

        # Check if the new piece immediately collides (game over condition)
        if self.check_collision(self.tetromino_shape, tetromino_position):
            return False  # Game over

        # Generate possible moves for the new piece
        self.generate_moves_for_current_piece()
        
        return True  # Continue playing

    def simulate_instant_drop(self, tetromino_shape, tetromino_position):
        while not self.check_collision(tetromino_shape, [tetromino_position[0], tetromino_position[1] + 1]):
            tetromino_position[1] += 1
        return tetromino_position

    def generate_moves_for_current_piece(self):
        # Get the possible moves for the current tetromino at its initial position
        possible_moves = self.generate_possible_moves(self.current_tetromino, [4, 0])

        if not possible_moves:
            return  # No possible moves, exit early

        # Find the move with the lowest weight (best move)
        best_move = min(possible_moves, key=lambda move: move['weight'])
        print(f"Best Move: Rotation: {best_move['rotation']}, Position: {best_move['position']}, Weight: {best_move['weight']}")

        # Store the best move for later use
        self.best_move = best_move

        # Generate the steps to execute the best move
        steps = self.generate_move_steps()
        print(f"Steps to Best Move: {steps}")

    def generate_move_steps(self):
        steps = []
        if not hasattr(self, 'best_move') or not self.best_move:
            return steps  # No best move available
        
        current_rotation = self.rotation
        current_position = [4, 0]  # Assuming the piece starts at this position

        # Step 1: Rotation
        best_rotation = self.best_move['rotation']
        rotations_needed = (best_rotation - current_rotation) % len(TETROMINO_DATA[self.current_tetromino]['rotations'])

        if rotations_needed > 0:
            for _ in range(rotations_needed):
                steps.append('Rotate Clockwise')

        # Step 2: Horizontal Movement
        best_position = self.best_move['position'][0]
        horizontal_moves = best_position - current_position[0]
        
        if horizontal_moves > 0:
            steps.extend(['Move Right' for _ in range(horizontal_moves)])
        elif horizontal_moves < 0:
            steps.extend(['Move Left' for _ in range(-horizontal_moves)])

        # Step 3: Instant Drop
        steps.append('Instant Drop')

        return steps

    def rotate(self, tetromino, position, clockwise=True):
        # Get the current shape rotations from SHAPES
        shape_rotations = TETROMINO_DATA[self.current_tetromino]['rotations']
        
        # Determine the new rotation index
        if clockwise:
            self.rotation = (self.rotation + 1) % len(shape_rotations)  # Cycle forward
        else:
            self.rotation = (self.rotation - 1) % len(shape_rotations)  # Cycle backward
        
        # Get the new rotated tetromino shape based on the updated rotation index
        rotated_tetromino = shape_rotations[self.rotation]

        # Check if the rotated tetromino collides with anything
        if not self.check_collision(rotated_tetromino, position):
            return rotated_tetromino
        return tetromino  # Return the original shape if collision happens

    def get_next_tetromino(self):
        if len(self.bag) == 0:
            self.bag = get_new_bag()
        return self.bag.pop(0)

    def check_collision(self, tetromino, position):
        for x, y in tetromino:
            grid_x = int(x + position[0])
            grid_y = int(y + position[1])

            # Check boundary conditions
            if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT:
                return True  # Collides with the boundary

            # Check for collisions with locked blocks
            if grid_y >= 0 and self.grid[grid_y][grid_x] != BLACK:
                return True  # Collides with existing blocks

        return False
    
    def perform_hold(self):
        if not self.hold_used:
            if self.hold_tetromino is None:
                # First time holding, swap current tetromino with next
                self.hold_tetromino = self.current_tetromino
                self.current_tetromino = self.next_tetromino
                self.next_tetromino = self.get_next_tetromino()
            else:
                # Swap the held tetromino with the current one
                self.current_tetromino, self.hold_tetromino = self.hold_tetromino, self.current_tetromino
            
            self.hold_used = True
            self.rotation = 0  # Reset rotation when holding a new piece
            
            # Generate moves for the held piece
            self.generate_moves_for_current_piece()

            # Always return the new tetromino color and shape
            return TETROMINO_DATA[self.current_tetromino]['color'], TETROMINO_DATA[self.current_tetromino]['rotations'][self.rotation]

        
        # If hold was already used in this round, return the current color and shape to avoid NoneType
        return TETROMINO_DATA[self.current_tetromino]['color'], TETROMINO_DATA[self.current_tetromino]['rotations'][self.rotation]

    def lock_tetromino(self, tetromino, position, color):
        for x, y in tetromino:
            self.grid[y + position[1]][x + position[0]] = color
            self.locked_positions[(x + position[0], y + position[1])] = color

        tetris_scored = self.clear_lines(self.current_tetromino)

        # After locking the tetromino, perform the grid state analysis
        holes = self.blockMatrix.count_holes()
        pillars = self.blockMatrix.count_pillars()
        max_height = self.blockMatrix.calculate_maximum_line_height(tetromino, position)
        bumpiness = self.blockMatrix.calculate_bumpiness()
        blocks_in_rightmost_lane = self.blockMatrix.count_number_of_blocks_in_rightmost_lane()

        # Print or log the results
        print(f"Holes: {holes}, Pillars: {pillars}, Max Height: {max_height}, Bumpiness: {bumpiness}, Rightmost Lane Blocks: {blocks_in_rightmost_lane}")
        print(f"Tetris scored: {tetris_scored}")

        self.clear_lines(self.current_tetromino)

        self.generate_moves_for_current_piece()

    def clear_lines(self, current_tetromino):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y][x] != BLACK for x in range(GRID_WIDTH)):
                lines_cleared += 1
                del self.grid[y]
                self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])

        # Scoring system
        points = 0

        if lines_cleared == 1:
            points = 100 * self.level
        elif lines_cleared == 2:
            points = 300 * self.level
        elif lines_cleared == 3:
            points = 500 * self.level
        elif lines_cleared == 4 and current_tetromino == 'I':
            points = 800 * self.level
        else:
            self.back_to_back_tetris = False

        self.score += points

        # Add cleared lines to the total
        self.total_lines_cleared += lines_cleared
        self.update_level()  # Check if the level should increase

        print(f"Lines cleared: {lines_cleared}, Total lines cleared: {self.total_lines_cleared}, Score: {self.score}, Level: {self.level}")

        return lines_cleared
    
    def update_level(self):
        # Increase the level every 10 lines cleared
        self.level = self.total_lines_cleared // 10 + 1
        print(f"Level updated: {self.level}")

    def game_loop(self):
        running = True
        tetromino_position = [4, 0]
        tetromino_color = self.tetromino_color
        tetromino_shape = self.tetromino_shape
        fall_time = 0
        move_down = False

        while running:
            self.screen.fill(BLACK)
            fall_time += self.clock.get_rawtime()
            self.clock.tick()

            if fall_time > self.fall_speed or move_down:
                tetromino_position[1] += 1
                if self.check_collision(tetromino_shape, tetromino_position):
                    tetromino_position[1] -= 1
                    self.lock_tetromino(tetromino_shape, tetromino_position, tetromino_color)
                    self.clear_lines(self.current_tetromino)  # Pass the current tetromino as argument
                    self.hold_used = False  # Allow holding again for the next piece
                    self.current_tetromino = self.next_tetromino
                    self.next_tetromino = self.get_next_tetromino()
                    tetromino_position = [4, 0]
                    tetromino_color = TETROMINO_DATA[self.current_tetromino]['color']
                    self.rotation = 0
                    tetromino_shape = TETROMINO_DATA[self.current_tetromino]['rotations'][self.rotation]
                    if self.check_collision(tetromino_shape, tetromino_position):
                        running = False  # Game over
                    else:
                        self.generate_moves_for_current_piece()  # Generate moves for the new tetromino
                fall_time = 0
                move_down = False


                fall_time = 0
                move_down = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        tetromino_position[0] -= 1
                        if self.check_collision(tetromino_shape, tetromino_position):
                            tetromino_position[0] += 1
                    if event.key == pygame.K_RIGHT:
                        tetromino_position[0] += 1
                        if self.check_collision(tetromino_shape, tetromino_position):
                            tetromino_position[0] -= 1
                    if event.key == pygame.K_DOWN:
                        move_down = True
                    if event.key == pygame.K_UP:
                        rotated_shape = self.rotate(tetromino_shape, tetromino_position, clockwise=True)
                        if not self.check_collision(rotated_shape, tetromino_position):
                            tetromino_shape = rotated_shape
                    if event.key == pygame.K_SPACE:  # Instant drop
                        if not self.instant_drop(tetromino_shape, tetromino_position):
                            running = False  # End game if game over after instant drop
                        else:
                            # Update the local variables after instant drop for the new piece
                            tetromino_shape = self.tetromino_shape
                            tetromino_position = [4, 0]
                            tetromino_color = self.tetromino_color
                    if event.key == pygame.K_c:  # Hold tetromino
                        tetromino_color, tetromino_shape = self.perform_hold()  # Update after holding
                        if not self.hold_used:
                            tetromino_position = [4, 0]
                    if event.key == pygame.K_r:  # Toggle rotation points
                        self.show_rotation_points = not self.show_rotation_points

            draw_grid(self, GRID_WIDTH, GRID_HEIGHT, BLOCK_SIZE)
            draw_tetromino(self, tetromino_shape, tetromino_position, tetromino_color, BLOCK_SIZE)
            draw_next_piece(self, BLOCK_SIZE)
            draw_held_piece(self, BLOCK_SIZE)

            draw_best_move(self, BLOCK_SIZE)
            draw_ghost_piece(self, tetromino_shape, tetromino_position, tetromino_color, BLOCK_SIZE)
            draw_game_info(self)

            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    tetris = Tetris()
    tetris.game_loop()
