import pygame
import sys

# 1. INITIALIZE
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Warden's Trial UI")
clock = pygame.time.Clock()

# Colors
GOLD = (255, 215, 100)
WHITE = (255, 255, 255)
DARK_BG = (10, 15, 15)
SLIDER_BG = (50, 50, 50)


# Fonts - Fallback to 'serif' if vampirewars isn't found
def get_font(name, size):
    try:
        return pygame.font.SysFont(name, size)
    except:
        return pygame.font.SysFont("serif", size)


font_main = get_font("vampirewars", 80)
font_menu = get_font("vampirewars", 25)
font_hint = get_font("georgia", 20)

# Assets
try:
    bg_image = pygame.image.load("JGdpHb.png").convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
except:
    bg_image = None


# --- 2. CLASSES ---
class Slider:
    def __init__(self, x, y, w, h, label, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.val = initial_val
        self.grabbed = False

    def draw(self, surface):
        txt = font_hint.render(f"{self.label}: {int(self.val * 100)}%", True, WHITE)
        surface.blit(txt, (self.rect.x, self.rect.y - 30))
        pygame.draw.rect(surface, SLIDER_BG, self.rect)
        pygame.draw.rect(surface, GOLD, self.rect, 1)
        knob_x = self.rect.x + (self.val * self.rect.w)
        knob_rect = pygame.Rect(knob_x - 5, self.rect.y - 5, 10, self.rect.h + 10)
        pygame.draw.rect(surface, GOLD, knob_rect)

    def update(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(mouse_pos):
                self.grabbed = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False
        if self.grabbed:
            pos_x = max(self.rect.x, min(mouse_pos[0], self.rect.right))
            self.val = (pos_x - self.rect.x) / self.rect.w
            return self.val
        return None


class MenuButton:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = (20, 30, 30)
        self.hover_color = (40, 80, 80)
        self.border_color = GOLD

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        bg_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=5)
        text_surf = font_menu.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos): return True
        return False


# --- 3. SETUP ---
scene = "MENU"
brightness_alpha = 0  # 0 is fully visible, 255 is pitch black
volume_val = 0.5

main_buttons = [
    MenuButton(720, 300, 220, 50, "START"),
    MenuButton(720, 370, 220, 50, "SETTINGS"),
    MenuButton(720, 440, 220, 50, "QUIT")
]

# Back button for Settings
back_btn = MenuButton(400, 450, 200, 50, "BACK")

audio_slider = Slider(400, 250, 200, 10, "VOLUME", volume_val)
bright_slider = Slider(400, 350, 200, 10, "BRIGHTNESS", 1.0)  # Start at 1.0 (Bright)

# --- 4. MAIN LOOP ---
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if scene == "MENU":
            for btn in main_buttons:
                if btn.is_clicked(event):
                    if btn.text == "QUIT":
                        running = False
                    elif btn.text == "START":
                        scene = "TRIAL_START"
                    elif btn.text == "SETTINGS":
                        scene = "SETTINGS"

        elif scene == "SETTINGS":
            if back_btn.is_clicked(event):
                scene = "MENU"

            new_vol = audio_slider.update(event)
            if new_vol is not None:
                # Assuming music is loaded elsewhere: pygame.mixer.music.set_volume(new_vol)
                pass

            new_bright = bright_slider.update(event)
            if new_bright is not None:
                # If slider is 1.0 (Right), alpha is 0 (Bright)
                # If slider is 0.0 (Left), alpha is 255 (Dark)
                brightness_alpha = int((1.0 - new_bright) * 255)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            scene = "MENU"

    # --- DRAWING ---
    screen.fill(DARK_BG)  # Base clear

    if scene == "MENU":
        if bg_image: screen.blit(bg_image, (0, 0))
        # Drawing full title
        screen.blit(font_main.render("THE WARDEN'S", True, GOLD), (80, 160))
        screen.blit(font_main.render("TRIAL", True, GOLD), (250, 240))
        for btn in main_buttons: btn.draw(screen)

    elif scene == "TRIAL_START":
        txt = font_main.render("THE TRIAL BEGINS", True, GOLD)
        screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(font_hint.render("Press ESC to return", True, WHITE), (WIDTH // 2 - 80, HEIGHT - 100))

    elif scene == "SETTINGS":
        title = font_main.render("SETTINGS", True, GOLD)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
        audio_slider.draw(screen)
        bright_slider.draw(screen)
        back_btn.draw(screen)

    # --- BRIGHTNESS OVERLAY ---
    # Draw this LAST so it dims everything
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(brightness_alpha)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()