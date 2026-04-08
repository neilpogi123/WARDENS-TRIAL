import pygame
import sys
import math

# --- 1. INITIALIZE ---
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Warden's Trial - The Patience Shard")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GOLD = (255, 215, 100)
BLACK = (0, 0, 0)
BLOCK_COLOR = (45, 50, 60)
PROGRESS_BLUE = (0, 150, 255)

f_hint = pygame.font.SysFont("georgia", 22)


# --- 2. ASSETS ---
def load_img(path, size, fallback_color):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        s = pygame.Surface(size);
        s.fill(fallback_color);
        return s


# Assets (Siguraduhin na nandoon ang files sa folder)
player_img = load_img("warden_char.png", (40, 60), (150, 20, 20))
parkour_bg = load_img("parkour_bg.png", (WIDTH, HEIGHT), (20, 25, 30))
shard_img = load_img("patience.png", (50, 50), GOLD)  # Yung shard na kukunin


# --- 3. CLASSES ---
class Player:
    def __init__(self, x, y, img):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.image = img
        self.vel_y = 0
        self.speed = 6
        self.jump_power = -17
        self.on_ground = False
        self.is_moving = False

    def handle_movement(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        self.is_moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -self.speed; self.is_moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = self.speed; self.is_moving = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        self.vel_y += 0.8
        self.rect.x += dx
        for p in platforms:
            if self.rect.colliderect(p):
                if dx > 0:
                    self.rect.right = p.left
                elif dx < 0:
                    self.rect.left = p.right

        self.rect.y += self.vel_y
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top; self.vel_y = 0; self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = p.bottom; self.vel_y = 0

    def draw(self, surface, offset_x):
        # Walking animation swing
        t = pygame.time.get_ticks() * 0.01
        swing = math.sin(t) * 12 if self.is_moving else 0
        # Draw Feet
        pygame.draw.circle(surface, (30, 30, 30), (int(self.rect.centerx - offset_x + swing), self.rect.bottom - 5), 7)
        pygame.draw.circle(surface, (20, 20, 20), (int(self.rect.centerx - offset_x - swing), self.rect.bottom - 5), 7)
        # Body
        surface.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Shard:
    def __init__(self, x, y, img):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.image = img
        self.collected = False
        self.float_offset = 0

    def draw(self, surface, offset_x):
        if not self.collected:
            # Floating effect using Sine
            self.float_offset = math.sin(pygame.time.get_ticks() * 0.005) * 10
            surface.blit(self.image, (self.rect.x - offset_x, self.rect.y + self.float_offset))


class Chandelier:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.start_y = y
        self.vel_y, self.triggered, self.active = 0, False, True

    def update(self, player_rect):
        if not self.triggered and abs(player_rect.centerx - self.rect.centerx) < 200:
            self.triggered = True
        if self.triggered:
            self.vel_y += 0.7;
            self.rect.y += self.vel_y
        if self.rect.y > HEIGHT: self.active = False

    def draw(self, surface, offset_x):
        if self.active:
            draw_pos = self.rect.move(-offset_x, 0)
            pygame.draw.polygon(surface, (255, 255, 150),
                                [(draw_pos.centerx, draw_pos.bottom), (draw_pos.left, draw_pos.top),
                                 (draw_pos.right, draw_pos.top)])


# --- 4. SETUP ---
player = Player(100, 400, player_img)
LEVEL_GOAL_X = 2200
camera_x = 0
shard = Shard(LEVEL_GOAL_X + 175, 80, shard_img)

# Box-style platforms (Fixed positions)
platforms = [
    pygame.Rect(0, 550, 500, 100),  # Start
    pygame.Rect(600, 450, 180, 50),  # Box 1
    pygame.Rect(450, 300, 150, 50),  # Box 2
    pygame.Rect(850, 300, 200, 50),  # Box 3
    pygame.Rect(1150, 400, 150, 50),  # Box 4
    pygame.Rect(1450, 320, 200, 50),  # Box 5
    pygame.Rect(1750, 420, 180, 50),  # Box 6
    pygame.Rect(2000, 300, 100, 50),  # Box 7
    pygame.Rect(LEVEL_GOAL_X, 150, 400, 600)  # Goal Pillar
]

chandeliers = [Chandelier(900, 0), Chandelier(1500, 0), Chandelier(1800, 0)]

# --- 5. MAIN LOOP ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # Updates
    player.handle_movement(platforms)
    camera_x += (player.rect.x - camera_x - 300) * 0.1

    for c in chandeliers: c.update(player.rect)

    # Check Shard Collection
    if not shard.collected and player.rect.colliderect(shard.rect):
        shard.collected = True
        print("Patience Shard Collected!")

    # Respawn Logic
    if player.rect.top > HEIGHT:
        player.rect.topleft = (100, 400);
        camera_x = 0
        for c in chandeliers: c.triggered, c.active, c.rect.y, c.vel_y = False, True, c.start_y, 0

    # DRAWING
    screen.fill(BLACK)
    screen.blit(parkour_bg, (-camera_x * 0.3, 0))  # Background parallax

    # Draw Boxes (Obstacles)
    for p in platforms:
        p_offset = p.move(-camera_x, 0)
        pygame.draw.rect(screen, BLOCK_COLOR, p_offset)  # The Solid Box
        pygame.draw.rect(screen, WHITE, p_offset, 2)  # Border for clarity

    for c in chandeliers: c.draw(screen, camera_x)
    shard.draw(screen, camera_x)
    player.draw(screen, camera_x)

    # HUD
    if shard.collected:
        txt = f_hint.render("TRIAL OF PATIENCE COMPLETE - SHARD RESTORED", True, GOLD)
        screen.blit(txt, (WIDTH // 2 - 200, 30))
    else:
        prog = min(max(player.rect.x / LEVEL_GOAL_X, 0), 1)
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 100, 30, 200, 15), 1)
        pygame.draw.rect(screen, PROGRESS_BLUE, (WIDTH // 2 - 98, 32, int(196 * prog), 11))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()