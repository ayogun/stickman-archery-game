import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 100, 0)

# Player Constants
PLAYER_HEALTH = 100
BODY_DAMAGE = 25
HEAD_DAMAGE = 50
GRAVITY = 0.5
MAX_POWER = 20

class Terrain:
    """Handles the game terrain with hills and mountains"""
    
    def __init__(self):
        self.points = []
        self.generate_terrain()
    
    def generate_terrain(self):
        """Generate random hilly terrain"""
        # Create terrain points across the screen
        for x in range(0, SCREEN_WIDTH + 50, 50):
            # Create hills with some randomness
            base_height = SCREEN_HEIGHT - 150
            hill_height = random.randint(-100, 100)
            y = base_height + hill_height
            
            # Keep terrain within reasonable bounds
            y = max(SCREEN_HEIGHT - 300, min(SCREEN_HEIGHT - 50, y))
            self.points.append((x, y))
    
    def get_height_at_x(self, x):
        """Get terrain height at specific x coordinate"""
        if x < 0:
            return self.points[0][1]
        if x >= SCREEN_WIDTH:
            return self.points[-1][1]
        
        # Find the two points to interpolate between
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            if x1 <= x <= x2:
                # Linear interpolation
                ratio = (x - x1) / (x2 - x1)
                return y1 + ratio * (y2 - y1)
        
        return SCREEN_HEIGHT - 100
    
    def draw(self, screen):
        """Draw the terrain"""
        if len(self.points) > 1:
            # Draw terrain as filled polygon
            terrain_points = self.points + [(SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)]
            pygame.draw.polygon(screen, DARK_GREEN, terrain_points)
            
            # Draw terrain outline
            pygame.draw.lines(screen, BLACK, False, self.points, 3)

class Player:
    """Represents a stickman archer player"""
    
    def __init__(self, x, y, facing_right=True):
        self.x = x
        self.y = y
        self.health = PLAYER_HEALTH
        self.facing_right = facing_right
        self.head_radius = 15
        self.body_height = 40
        self.arm_length = 25
        self.leg_length = 30
    
    def draw(self, screen):
        """Draw the stickman player"""
        # Head
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y - self.body_height - self.head_radius)), self.head_radius, 3)
        
        # Body
        body_start = (int(self.x), int(self.y - self.body_height))
        body_end = (int(self.x), int(self.y))
        pygame.draw.line(screen, BLACK, body_start, body_end, 3)
        
        # Arms
        arm_y = int(self.y - self.body_height * 0.7)
        if self.facing_right:
            arm_end = (int(self.x + self.arm_length), arm_y - 10)
        else:
            arm_end = (int(self.x - self.arm_length), arm_y - 10)
        pygame.draw.line(screen, BLACK, (int(self.x), arm_y), arm_end, 3)
        
        # Legs
        leg_left = (int(self.x - 15), int(self.y + self.leg_length))
        leg_right = (int(self.x + 15), int(self.y + self.leg_length))
        pygame.draw.line(screen, BLACK, (int(self.x), int(self.y)), leg_left, 3)
        pygame.draw.line(screen, BLACK, (int(self.x), int(self.y)), leg_right, 3)
    
    def get_head_rect(self):
        """Get rectangle for head hitbox"""
        head_x = self.x - self.head_radius
        head_y = self.y - self.body_height - self.head_radius * 2
        return pygame.Rect(head_x, head_y, self.head_radius * 2, self.head_radius * 2)
    
    def get_body_rect(self):
        """Get rectangle for body hitbox"""
        body_x = self.x - 10
        body_y = self.y - self.body_height
        return pygame.Rect(body_x, body_y, 20, self.body_height)
    
    def take_damage(self, damage):
        """Apply damage to player"""
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def is_alive(self):
        """Check if player is still alive"""
        return self.health > 0

class BloodParticle:
    """Blood particle for hit effects"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Random velocity for particle spread
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-4, -1)
        self.life = 60  # Frames to live
        self.max_life = 60
        self.size = random.randint(2, 5)
    
    def update(self):
        """Update particle position and life"""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1  # Gravity on particles
        self.life -= 1
    
    def draw(self, screen):
        """Draw blood particle"""
        if self.life <= 0:
            return
        
        # Fade out over time
        alpha = self.life / self.max_life
        red_intensity = int(255 * alpha)
        color = (red_intensity, 0, 0)
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 
                         max(1, int(self.size * alpha)))
    
    def is_alive(self):
        """Check if particle is still alive"""
        return self.life > 0

class Arrow:
    """Represents an arrow projectile"""
    
    def __init__(self, x, y, velocity_x, velocity_y, shooter_id):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.active = True
        self.trail = []  # For visual trail effect
        self.shooter_id = shooter_id  # Track who shot this arrow
        self.initial_speed = math.sqrt(velocity_x**2 + velocity_y**2)  # Store initial speed
    
    def update(self, wind_force):
        """Update arrow position with physics"""
        if not self.active:
            return
        
        # Store position for trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 15:  # Longer trail for better visibility
            self.trail.pop(0)
        
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Apply wind force
        self.velocity_x += wind_force * 0.1
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Check if arrow is off screen or hit ground
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y > SCREEN_HEIGHT):
            self.active = False
    
    def draw(self, screen):
        """Draw the arrow and its trail with better visibility"""
        if not self.active:
            return
        
        # Draw trail with better colors
        for i, pos in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail)
            # More visible trail colors
            color = (int(200 * alpha), int(100 * alpha), 0)
            size = max(1, int(3 * alpha))
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), size)
        
        # Calculate arrow angle based on velocity
        angle = math.atan2(self.velocity_y, self.velocity_x)
        
        # Draw arrow shaft (longer and more visible)
        arrow_length = 20
        shaft_width = 4
        
        # Arrow tip and tail positions
        tip_x = self.x + arrow_length * 0.6 * math.cos(angle)
        tip_y = self.y + arrow_length * 0.6 * math.sin(angle)
        tail_x = self.x - arrow_length * 0.4 * math.cos(angle)
        tail_y = self.y - arrow_length * 0.4 * math.sin(angle)
        
        # Draw arrow shaft (brown wooden part)
        pygame.draw.line(screen, BROWN, (int(tail_x), int(tail_y)), (int(tip_x), int(tip_y)), shaft_width)
        
        # Draw arrowhead (metal tip)
        head_length = 8
        head_tip_x = self.x + (arrow_length * 0.6 + head_length) * math.cos(angle)
        head_tip_y = self.y + (arrow_length * 0.6 + head_length) * math.sin(angle)
        
        # Arrowhead triangle
        perpendicular_angle = angle + math.pi / 2
        head_width = 4
        
        head_left_x = tip_x + head_width * math.cos(perpendicular_angle)
        head_left_y = tip_y + head_width * math.sin(perpendicular_angle)
        head_right_x = tip_x - head_width * math.cos(perpendicular_angle)
        head_right_y = tip_y - head_width * math.sin(perpendicular_angle)
        
        # Draw arrowhead as triangle
        arrow_points = [
            (int(head_tip_x), int(head_tip_y)),
            (int(head_left_x), int(head_left_y)),
            (int(head_right_x), int(head_right_y))
        ]
        pygame.draw.polygon(screen, GRAY, arrow_points)
        pygame.draw.polygon(screen, BLACK, arrow_points, 2)  # Outline
        
        # Draw fletching (feathers at back)
        fletch_start_x = tail_x
        fletch_start_y = tail_y
        fletch_length = 6
        
        fletch_left_x = fletch_start_x + fletch_length * math.cos(angle + 2.8)
        fletch_left_y = fletch_start_y + fletch_length * math.sin(angle + 2.8)
        fletch_right_x = fletch_start_x + fletch_length * math.cos(angle - 2.8)
        fletch_right_y = fletch_start_y + fletch_length * math.sin(angle - 2.8)
        
        pygame.draw.line(screen, RED, (int(fletch_start_x), int(fletch_start_y)), 
                        (int(fletch_left_x), int(fletch_left_y)), 2)
        pygame.draw.line(screen, RED, (int(fletch_start_x), int(fletch_start_y)), 
                        (int(fletch_right_x), int(fletch_right_y)), 2)
    
    def get_rect(self):
        """Get collision rectangle for arrow"""
        return pygame.Rect(self.x - 3, self.y - 3, 6, 6)

class Game:
    """Main game class that handles all game logic"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Stickman Archery Game")
        self.clock = pygame.time.Clock()
        
        # Initialize game objects
        self.terrain = Terrain()
        
        # Position players on terrain
        player1_x = 150
        player1_y = self.terrain.get_height_at_x(player1_x) - 50
        player2_x = SCREEN_WIDTH - 150
        player2_y = self.terrain.get_height_at_x(player2_x) - 50
        
        self.player1 = Player(player1_x, player1_y, facing_right=True)
        self.player2 = Player(player2_x, player2_y, facing_right=False)
        
        # Game state
        self.current_player = 1
        self.arrows = []
        self.blood_particles = []  # Add blood particles list
        self.charging = False
        self.charge_power = 0
        self.charge_start_pos = None
        
        # Wind system
        self.wind_strength = 0
        self.wind_direction = 1  # 1 for right, -1 for left
        self.generate_new_wind()
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game over state
        self.game_over = False
        self.winner = None
    
    def generate_new_wind(self):
        """Generate new wind conditions"""
        self.wind_strength = random.uniform(0, 3)
        self.wind_direction = random.choice([-1, 1])
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.start_charging(pygame.mouse.get_pos())
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.charging:
                    self.shoot_arrow(pygame.mouse.get_pos())
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.switch_turn()
        
        return True
    
    def start_charging(self, mouse_pos):
        """Start charging the arrow shot"""
        if not self.charging and not self.game_over:
            self.charging = True
            self.charge_start_pos = mouse_pos
            self.charge_power = 0
    
    def shoot_arrow(self, mouse_pos):
        """Shoot arrow based on mouse position and charge"""
        if not self.charging:
            return
        
        current_player_obj = self.player1 if self.current_player == 1 else self.player2
        
        # Calculate angle and power
        dx = mouse_pos[0] - current_player_obj.x
        dy = mouse_pos[1] - current_player_obj.y
        
        # Prevent shooting if power is too low (fixes the instant hit bug)
        if self.charge_power < 1:
            self.charging = False
            self.charge_power = 0
            return
        
        angle = math.atan2(dy, dx)
        
        # Calculate velocity based on charge power
        power = min(self.charge_power, MAX_POWER)
        velocity_x = power * math.cos(angle)
        velocity_y = power * math.sin(angle)
        
        # Start arrow slightly away from player to prevent immediate collision
        start_offset = 30
        start_x = current_player_obj.x + start_offset * math.cos(angle)
        start_y = current_player_obj.y - 20 + start_offset * math.sin(angle)
        
        # Create arrow with shooter ID
        arrow = Arrow(start_x, start_y, velocity_x, velocity_y, self.current_player)
        self.arrows.append(arrow)
        
        # Reset charging
        self.charging = False
        self.charge_power = 0
        
        # Switch turns after shooting
        self.switch_turn()
    
    def create_blood_effect(self, x, y, is_headshot=False):
        """Create blood particle effect at hit location"""
        particle_count = 15 if is_headshot else 10
        for _ in range(particle_count):
            self.blood_particles.append(BloodParticle(x, y))
    
    def update_blood_particles(self):
        """Update all blood particles"""
        for particle in self.blood_particles[:]:
            particle.update()
            if not particle.is_alive():
                self.blood_particles.remove(particle)
    
    def switch_turn(self):
        """Switch to the other player's turn"""
        self.current_player = 2 if self.current_player == 1 else 1
        self.generate_new_wind()
    
    def update_charging(self):
        """Update charging power"""
        if self.charging:
            self.charge_power += 0.5
            if self.charge_power > MAX_POWER:
                self.charge_power = MAX_POWER
    
    def update_arrows(self):
        """Update all arrows and check for collisions"""
        wind_force = self.wind_strength * self.wind_direction
        
        for arrow in self.arrows[:]:  # Create copy to safely remove items
            if not arrow.active:
                continue
            
            arrow.update(wind_force)
            
            # Check terrain collision
            if arrow.y >= self.terrain.get_height_at_x(arrow.x):
                arrow.active = False
                continue
            
            # Check player collisions
            arrow_rect = arrow.get_rect()
            
            # Check collision with player 1 (only if arrow was not shot by player 1)
            if (arrow.shooter_id != 1 and 
                (arrow_rect.colliderect(self.player1.get_head_rect()) or 
                 arrow_rect.colliderect(self.player1.get_body_rect()))):
                
                # Determine if it's a headshot
                if arrow_rect.colliderect(self.player1.get_head_rect()):
                    self.player1.take_damage(HEAD_DAMAGE)
                    self.create_blood_effect(self.player1.x, self.player1.y - 40, True)
                else:
                    self.player1.take_damage(BODY_DAMAGE)
                    self.create_blood_effect(self.player1.x, self.player1.y - 20, False)
                
                arrow.active = False
                self.check_game_over()
            
            # Check collision with player 2 (only if arrow was not shot by player 2)
            elif (arrow.shooter_id != 2 and 
                  (arrow_rect.colliderect(self.player2.get_head_rect()) or 
                   arrow_rect.colliderect(self.player2.get_body_rect()))):
                
                # Determine if it's a headshot
                if arrow_rect.colliderect(self.player2.get_head_rect()):
                    self.player2.take_damage(HEAD_DAMAGE)
                    self.create_blood_effect(self.player2.x, self.player2.y - 40, True)
                else:
                    self.player2.take_damage(BODY_DAMAGE)
                    self.create_blood_effect(self.player2.x, self.player2.y - 20, False)
                
                arrow.active = False
                self.check_game_over()
        
        # Remove inactive arrows
        self.arrows = [arrow for arrow in self.arrows if arrow.active]
    
    def check_game_over(self):
        """Check if the game is over"""
        if not self.player1.is_alive():
            self.game_over = True
            self.winner = 2
        elif not self.player2.is_alive():
            self.game_over = True
            self.winner = 1
    
    def restart_game(self):
        """Restart the game"""
        self.__init__()
    
    def draw_ui(self):
        """Draw all UI elements"""
        # Health bars
        self.draw_health_bar(50, 50, self.player1.health, "Player 1")
        self.draw_health_bar(SCREEN_WIDTH - 250, 50, self.player2.health, "Player 2")
        
        # Wind indicator
        self.draw_wind_indicator()
        
        # Current player indicator
        current_text = f"Player {self.current_player}'s Turn"
        text_surface = self.font.render(current_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(text_surface, text_rect)
        
        # Charging bar
        if self.charging:
            self.draw_charging_bar()
        
        # Game over screen
        if self.game_over:
            self.draw_game_over()
    
    def draw_health_bar(self, x, y, health, label):
        """Draw a health bar for a player"""
        # Label
        label_surface = self.small_font.render(label, True, BLACK)
        self.screen.blit(label_surface, (x, y))
        
        # Health bar background
        bar_rect = pygame.Rect(x, y + 25, 200, 20)
        pygame.draw.rect(self.screen, RED, bar_rect)
        
        # Health bar fill
        health_width = int((health / PLAYER_HEALTH) * 200)
        health_rect = pygame.Rect(x, y + 25, health_width, 20)
        pygame.draw.rect(self.screen, GREEN, health_rect)
        
        # Health bar border
        pygame.draw.rect(self.screen, BLACK, bar_rect, 2)
        
        # Health text
        health_text = f"{health}/{PLAYER_HEALTH}"
        health_surface = self.small_font.render(health_text, True, BLACK)
        text_rect = health_surface.get_rect(center=(x + 100, y + 35))
        self.screen.blit(health_surface, text_rect)
    
    def draw_wind_indicator(self):
        """Draw wind strength and direction indicator with custom arrow"""
        # Draw wind text
        wind_text = f"Wind: {self.wind_strength:.1f}"
        wind_surface = self.font.render(wind_text, True, BLACK)
        wind_rect = wind_surface.get_rect(center=(SCREEN_WIDTH // 2, 70))
        self.screen.blit(wind_surface, wind_rect)
        
        # Draw custom arrow next to wind text
        arrow_x = wind_rect.right + 10
        arrow_y = wind_rect.centery
        
        if self.wind_direction > 0:  # Right arrow
            # Draw right-pointing triangle
            arrow_points = [
                (arrow_x, arrow_y),
                (arrow_x + 15, arrow_y - 8),
                (arrow_x + 15, arrow_y - 3),
                (arrow_x + 25, arrow_y),
                (arrow_x + 15, arrow_y + 3),
                (arrow_x + 15, arrow_y + 8)
            ]
        else:  # Left arrow
            # Draw left-pointing triangle
            arrow_points = [
                (arrow_x + 25, arrow_y),
                (arrow_x + 10, arrow_y - 8),
                (arrow_x + 10, arrow_y - 3),
                (arrow_x, arrow_y),
                (arrow_x + 10, arrow_y + 3),
                (arrow_x + 10, arrow_y + 8)
            ]
        
        # Draw the arrow
        pygame.draw.polygon(self.screen, RED, arrow_points)
        pygame.draw.polygon(self.screen, BLACK, arrow_points, 2)  # Outline
    
    def draw_charging_bar(self):
        """Draw the power charging bar"""
        if not self.charging:
            return
        
        # Charging bar background
        bar_x = SCREEN_WIDTH // 2 - 100
        bar_y = SCREEN_HEIGHT - 100
        bar_rect = pygame.Rect(bar_x, bar_y, 200, 30)
        pygame.draw.rect(self.screen, GRAY, bar_rect)
        
        # Charging bar fill
        charge_width = int((self.charge_power / MAX_POWER) * 200)
        charge_rect = pygame.Rect(bar_x, bar_y, charge_width, 30)
        
        # Color changes based on power level
        if self.charge_power < MAX_POWER * 0.3:
            color = GREEN
        elif self.charge_power < MAX_POWER * 0.7:
            color = YELLOW
        else:
            color = RED
        
        pygame.draw.rect(self.screen, color, charge_rect)
        pygame.draw.rect(self.screen, BLACK, bar_rect, 2)
        
        # Power text
        power_text = f"Power: {int((self.charge_power / MAX_POWER) * 100)}%"
        power_surface = self.small_font.render(power_text, True, BLACK)
        text_rect = power_surface.get_rect(center=(SCREEN_WIDTH // 2, bar_y - 20))
        self.screen.blit(power_surface, text_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = f"Player {self.winner} Wins!"
        game_over_surface = pygame.font.Font(None, 72).render(game_over_text, True, WHITE)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_surface, game_over_rect)
        
        # Restart instruction
        restart_text = "Press R to Restart"
        restart_surface = self.font.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_surface, restart_rect)
    
    def draw(self):
        """Draw everything on screen"""
        # Clear screen
        self.screen.fill(WHITE)
        
        # Draw terrain
        self.terrain.draw(self.screen)
        
        # Draw players
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        
        # Draw arrows
        for arrow in self.arrows:
            arrow.draw(self.screen)
        
        # Draw blood particles
        for particle in self.blood_particles:
            particle.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw aiming line when charging
        if self.charging and self.charge_start_pos:
            current_player_obj = self.player1 if self.current_player == 1 else self.player2
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, RED, 
                           (current_player_obj.x, current_player_obj.y - 20), 
                           mouse_pos, 2)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            
            if not self.game_over:
                self.update_charging()
                self.update_arrows()
                self.update_blood_particles()  # Update blood particles
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
