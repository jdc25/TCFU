import pygame
import sys
import random
import math

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
        self.image = pygame.Surface((5, 10))
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

# Enemy class with spaceship design
class Enemy(pygame.sprite.Sprite):
    def __init__(self, angle):
        super(Enemy, self).__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Transparent background

        # Draw a simple spaceship shape
        pygame.draw.polygon(self.image, RED, [(20, 0), (40, 30), (0, 30)])
        pygame.draw.rect(self.image, RED, (15, 20, 10, 5))  # Add a small rectangle for detail

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
                    show_instructions()
        
        pygame.display.flip()
        clock.tick(60)

def show_instructions():
    instruction_font = pygame.font.SysFont(None, 48)
    instructions = [
        "Use LEFT and RIGHT arrow keys to rotate.",
        "Press SPACE to shoot.",
        "Avoid enemies and survive as long as possible.",
        "Press ESC to return to the main menu."
    ]
    instructions_texts = [instruction_font.render(line, True, WHITE) for line in instructions]
    
    while True:
        screen.fill(BLACK)
        y_offset = 50
        for text in instructions_texts:
            screen.blit(text, (20, y_offset))
            y_offset += 50
        
        quit_text = font.render("Press ESC to return", True, WHITE)
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT - 50))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        
        pygame.display.flip()
        clock.tick(60)

# Main game loop
def main_game():
    global score, lives
    score = 0
    lives = 3

    initialize_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        all_sprites.update()

        # Check for bullet-enemy collisions
        if pygame.sprite.groupcollide(enemies, bullets, True, True):
            score += 50  # Increase score by 50 for each enemy destroyed

        # Check for enemy-player collisions
        if pygame.sprite.spritecollideany(player, enemies):
            lives -= 1  # Lose a life
            if lives <= 0:
                running = False  # End game if no lives left
            else:
                # Reset player position
                player.rect.centerx = SCREEN_WIDTH // 2
                player.rect.centery = SCREEN_HEIGHT // 2
                player.angle = 0

        # Fill the screen with black color
        screen.fill(BLACK)

        # Draw all sprites
        all_sprites.draw(screen)

        # Display the score and lives
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (10, 50))

        pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    while True:
        start_menu()
        main_game()