import pygame
import sys
import random
import math
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("They Crawled from Uranus Replica")

# Clock object to control the frame rate
clock = pygame.time.Clock()

# Font for displaying the score and lives
font = pygame.font.SysFont(None, 36)

# Print current working directory for debugging
print("Current Working Directory:", os.getcwd())

# Verify the assets path
assets_path = os.path.join(os.getcwd(), 'assets', 'enemy_jet.png')
if not os.path.exists(assets_path):
    print(f"File not found: {assets_path}")
    pygame.quit()
    sys.exit()

# Starfield class
class Star(pygame.sprite.Sprite):
    def __init__(self):
        super(Star, self).__init__()
        self.image = pygame.Surface((2, 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH)
        self.rect.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.randint(1, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = 0
            self.rect.x = random.randint(0, SCREEN_WIDTH)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.original_image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.original_image, WHITE, [(25, 0), (50, 50), (0, 50)])
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.angle = 0
        self.radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2 - 50
        self.speed = 0.05  # Rotation speed in radians
        self.visible = True  # Player visibility flag

    def update(self):
        # Update player position in a circular path around the center
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle -= self.speed
        if keys[pygame.K_RIGHT]:
            self.angle += self.speed

        # Convert angle to radians
        radians = self.angle
        self.rect.centerx = self.center[0] + int(self.radius * math.cos(radians))
        self.rect.centery = self.center[1] + int(self.radius * math.sin(radians))

        # Apply rotation to the player image
        self.image = pygame.transform.rotate(self.original_image, -math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def flicker(self):
        # Toggle visibility
        self.visible = not self.visible
        if self.visible:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)

    def shoot(self):
        # Bullet direction should be towards the center
        radians = self.angle
        dx = -math.cos(radians)
        dy = -math.sin(radians)

        firing_x = self.rect.centerx + dx * 10  # 10 is an offset to position the bullet correctly
        firing_y = self.rect.centery + dy * 10

        bullet = Bullet(firing_x, firing_y, dx, dy)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super(Bullet, self).__init__()
        self.image = pygame.Surface((5, 10), pygame.SRCALPHA)  # Use SRCALPHA for transparency
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.dx = dx * 10
        self.dy = dy * 10

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if (self.rect.bottom < 0 or
            self.rect.top > SCREEN_HEIGHT or
            self.rect.left < 0 or
            self.rect.right > SCREEN_WIDTH):
            self.kill()

# Enemy class with image loading
class Enemy(pygame.sprite.Sprite):
    def __init__(self, angle):
        super(Enemy, self).__init__()
        try:
            # Load the enemy sprite from the 'assets' folder with transparency support
            self.original_image = pygame.image.load(assets_path).convert_alpha()
            # Resize the image to match the original Gyruss size
            self.image = pygame.transform.scale(self.original_image, (32, 32))
        except pygame.error as e:
            print(f"Error loading image: {e}")
            pygame.quit()
            sys.exit()
        self.rect = self.image.get_rect()
        self.angle = angle
        self.radius = 0  # Start from the center
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.speed = 2  # Speed of angle change
        self.radial_speed = 0.5  # Speed of radius change (move outwards first)
        self.update_position()

    def update_position(self):
        self.rect.x = self.center_x + int(self.radius * math.cos(math.radians(self.angle)))
        self.rect.y = self.center_y + int(self.radius * math.sin(math.radians(self.angle)))

    def update(self):
        self.angle += self.speed

        # Move outwards
        self.radius += self.radial_speed

        self.update_position()

        # Check if enemy is off-screen and re-enter from the opposite side
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0
        elif self.rect.bottom < 0:
            self.rect.top = SCREEN_HEIGHT
        elif self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

        # Optionally reset the radius and angle to create a looping effect
        if (self.rect.top > SCREEN_HEIGHT or
            self.rect.bottom < 0 or
            self.rect.left > SCREEN_WIDTH or
            self.rect.right < 0):
            self.radius = 0
            self.angle = random.randint(0, 360)
            self.update_position()

# Initialize Pygame sprite groups
def initialize_game():
    global all_sprites, enemies, bullets, stars, player
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    stars = pygame.sprite.Group()

    # Create star instances
    for _ in range(100):
        star = Star()
        all_sprites.add(star)
        stars.add(star)

    # Create a player instance
    player = Player()
    all_sprites.add(player)

    # Create enemy instances
    for i in range(8):
        angle = random.randint(0, 360)
        enemy = Enemy(angle)
        all_sprites.add(enemy)
        enemies.add(enemy)

def start_menu():
    menu_font = pygame.font.SysFont(None, 74)
    title_text = menu_font.render("TCFU", True, WHITE)
    start_text = font.render("Press ENTER to Start", True, WHITE)
    instructions_text = font.render("Press I for Instructions", True, WHITE)
    quit_text = font.render("Press ESC to Quit", True, WHITE)
    
    while True:
        screen.fill(BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_i:
                    instructions_menu()
        
        pygame.display.flip()
        clock.tick(60)

def instructions_menu():
    instructions_font = pygame.font.SysFont(None, 36)
    instructions_lines = [
        "Use the LEFT and RIGHT arrow keys to rotate the player.",
        "Press SPACE to shoot bullets towards the center.",
        "Avoid enemy ships and shoot them down.",
        "Press ESC to return to the main menu."
    ]
    
    while True:
        screen.fill(BLACK)
        for i, line in enumerate(instructions_lines):
            instruction_text = instructions_font.render(line, True, WHITE)
            screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 3 + i * 40))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        
        pygame.display.flip()
        clock.tick(60)

def game_over():
    over_font = pygame.font.SysFont(None, 74)
    over_text = over_font.render("Game Over", True, RED)
    restart_text = font.render("Press ENTER to Restart", True, WHITE)
    quit_text = font.render("Press ESC to Quit", True, WHITE)
    
    while True:
        screen.fill(BLACK)
        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()
        clock.tick(60)

# Main game loop
def main():
    initialize_game()
    score = 0
    lives = 3
    invincible = False
    invincible_timer = 0
    flicker_timer = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                elif event.key == pygame.K_ESCAPE:
                    game_over()
        
        if invincible:
            flicker_timer += 1
            if flicker_timer % 5 == 0:
                player.flicker()
            invincible_timer += 1
            if invincible_timer > 120:  # Invincible for 2 seconds
                invincible = False
                player.image.set_alpha(255)
        
        # Update all sprites
        all_sprites.update()
        
        # Check for collisions between bullets and enemies
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in hits:
            score += 10
            enemy = Enemy(random.randint(0, 360))
            all_sprites.add(enemy)
            enemies.add(enemy)
        
        # Check for collisions between player and enemies
        if not invincible:
            hits = pygame.sprite.spritecollide(player, enemies, True)
            for hit in hits:
                lives -= 1
                if lives <= 0:
                    game_over()
                else:
                    invincible = True
                    invincible_timer = 0
                    flicker_timer = 0
                enemy = Enemy(random.randint(0, 360))
                all_sprites.add(enemy)
                enemies.add(enemy)
        
        # Draw everything
        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        # Draw score and lives
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))
        
        pygame.display.flip()
        clock.tick(60)

start_menu()
main()