import pygame
import sys

# --- 1. INITIALIZE ---
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Warden's Trial")
clock = pygame.time.Clock()

# Colors
GOLD = (255, 215, 100)
WHITE = (255, 255, 255)
DARK_BG = (10, 15, 15)
RED_TEXT = (255, 100, 100)


# --- 2. ASSETS & FONTS ---
def get_font(name, size, fallback="georgia"):
    try:
        return pygame.font.SysFont(name, size)
    except:
        return pygame.font.SysFont(fallback, size)


font_main = get_font("vampirewars", 80)
font_menu = get_font("vampirewars", 25)
font_hint = get_font("georgia", 22)

# Audio
try:
    pygame.mixer.music.load("No Time.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except:
    pass


# Image Loading (200x200 pixels)
def load_shard(path):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (200, 200))
    except:
        s = pygame.Surface((200, 200));
        s.fill((100, 0, 0))
        return s


shard1_img = load_shard("patience.png")
shard2_img = load_shard("endurance.png")
shard3_img = load_shard("discipline.png")

try:
    raw_bg = pygame.image.load("JGdpHb.png").convert()
    raw_bg = pygame.transform.scale(raw_bg, (WIDTH, HEIGHT))
except:
    raw_bg = pygame.Surface((WIDTH, HEIGHT))


# --- 3. CLASSES ---
class Slider:
    def __init__(self, x, y, w, h, label, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.label, self.val, self.grabbed = label, initial_val, False

    def draw(self, surface):
        txt = font_hint.render(f"{self.label}: {int(self.val * 100)}%", True, WHITE)
        surface.blit(txt, (self.rect.x, self.rect.y - 35))
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        pygame.draw.rect(surface, GOLD, self.rect, 1)
        knob_x = self.rect.x + (self.val * self.rect.w)
        pygame.draw.rect(surface, GOLD, (knob_x - 5, self.rect.y - 5, 10, self.rect.h + 10))

    def update(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos): self.grabbed = True
        if event.type == pygame.MOUSEBUTTONUP: self.grabbed = False
        if self.grabbed:
            pos_x = max(self.rect.x, min(mouse_pos[0], self.rect.right))
            self.val = (pos_x - self.rect.x) / self.rect.w
            return self.val
        return None


class MenuButton:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = (40, 80, 80) if self.rect.collidepoint(mouse_pos) else (20, 30, 30)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, GOLD, self.rect, 2, border_radius=5)
        text_surf = font_menu.render(self.text, True, WHITE)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


# --- 4. DATA & STATE ---
scene = "MENU"
target_scene = "MENU"
is_fading = False
fade_alpha, brightness_alpha = 0, 0
fade_speed = 7

story_lines = [
    "The Sanctum of Hollow Saints has fallen into silence...",
    "Agnosia, Warden of Purity, wanders its broken bridges.",
    "The Cursed Mist is rising, clouding the mind with shadows.",
    "Wield the Mind Cleaver. Shatter the Neuro Shards.",
    "Endurance. Discipline. Patience.",
    "Restore the Warden's clarity... or fade into the hollow."
]
current_line, char_index, typing_timer = 0, 0, 0
trial_text = "THE TRIAL BEGINS"
trial_char_index = 0
tenet_text =   "CLEAR THE THREE TRIALS: PATIENCE, ENDURANCE, AND DISCIPLINE."
tenet_char_index = 0
shard_text = "REMOVE THE THREE NEURO SHARDS TO CLEAR AGNOSIA'S MIND."
shard_char_index = 0

bgm_slider = Slider(400, 200, 200, 10, "MUSIC VOLUME", 0.2)
bright_slider = Slider(400, 350, 200, 10, "BRIGHTNESS", 1.0)
main_buttons = [
    MenuButton(720, 300, 220, 50, "START"),
    MenuButton(720, 370, 220, 50, "SETTINGS"),
    MenuButton(720, 440, 220, 50, "QUIT")
]

# --- 5. MAIN LOOP ---
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT: running = False

        if not is_fading:
            if scene == "MENU":
                for btn in main_buttons:
                    if btn.is_clicked(event):
                        if btn.text == "QUIT":
                            running = False
                        else:
                            is_fading, target_scene = True, ("STORY_INTRO" if btn.text == "START" else "SETTINGS")

            elif scene == "SETTINGS":
                v = bgm_slider.update(event)
                if v is not None: pygame.mixer.music.set_volume(v)
                b = bright_slider.update(event)
                if b is not None: brightness_alpha = int((1.0 - b) * 255)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: is_fading, target_scene = True, "MENU"

            elif scene == "STORY_INTRO":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if char_index < len(story_lines[current_line]):
                        char_index = len(story_lines[current_line])
                    elif current_line < len(story_lines) - 1:
                        current_line += 1; char_index = 0
                    else:
                        is_fading, target_scene = True, "TRIAL_START"

            elif scene == "TRIAL_START":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if trial_char_index < len(trial_text):
                            trial_char_index = len(trial_text)
                        else:
                            is_fading, target_scene = True, "TENETS"
                    if event.key == pygame.K_ESCAPE: is_fading, target_scene = True, "MENU"

            elif scene == "TENETS":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if tenet_char_index < len(tenet_text):
                        tenet_char_index = len(tenet_text)
                    else:
                        is_fading, target_scene = True, "SHARD_HINT"

            elif scene == "SHARD_HINT":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if shard_char_index < len(shard_text):
                            shard_char_index = len(shard_text)
                        else:
                            print("LOADING LEVEL 1...")
                    if event.key == pygame.K_ESCAPE: is_fading, target_scene = True, "MENU"

    # Typing Logic
    if not is_fading:
        typing_timer += 1
        if typing_timer >= 2:
            if scene == "STORY_INTRO" and char_index < len(story_lines[current_line]):
                char_index += 1
            elif scene == "TRIAL_START" and trial_char_index < len(trial_text):
                trial_char_index += 1
            elif scene == "TENETS" and tenet_char_index < len(tenet_text):
                tenet_char_index += 1
            elif scene == "SHARD_HINT" and shard_char_index < len(shard_text):
                shard_char_index += 1
            typing_timer = 0

    if is_fading:
        fade_alpha += fade_speed
        if fade_alpha >= 255: fade_alpha, scene, is_fading = 255, target_scene, False
    elif fade_alpha > 0:
        fade_alpha -= fade_speed

    # --- DRAWING ---
    screen.fill(DARK_BG)

    if scene == "MENU":
        screen.blit(raw_bg, (0, 0))
        screen.blit(font_main.render("THE WARDEN'S", True, GOLD), (80, 160))
        screen.blit(font_main.render("TRIAL", True, GOLD), (80, 240))
        for btn in main_buttons: btn.draw(screen)

    elif scene == "SETTINGS":
        screen.blit(raw_bg, (0, 0))
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA);
        ov.fill((0, 0, 0, 180));
        screen.blit(ov, (0, 0))
        bgm_slider.draw(screen);
        bright_slider.draw(screen)
        screen.blit(font_hint.render("[ ESC ] Back to Menu", True, GOLD), (WIDTH // 2 - 90, 500))

    elif scene == "STORY_INTRO":
        line = font_hint.render(story_lines[current_line][:char_index], True, WHITE)
        screen.blit(line, line.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        if char_index >= len(story_lines[current_line]):
            screen.blit(font_hint.render("[ SPACE ]", True, GOLD), (WIDTH // 2 - 40, HEIGHT - 80))

    elif scene == "TRIAL_START":
        txt = font_main.render(trial_text[:trial_char_index], True, GOLD)
        screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        if trial_char_index >= len(trial_text):
            h1 = font_hint.render("[ SPACE ] Begin Trial", True, WHITE)
            screen.blit(h1, h1.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
            h2 = font_hint.render("[ ESC ] Back to Main Menu", True, GOLD)
            screen.blit(h2, h2.get_rect(center=(WIDTH // 2, HEIGHT - 60)))

    elif scene == "TENETS":
        screen.fill((10, 5, 5))

        tenet_surf = font_hint.render(tenet_text[:tenet_char_index], True, RED_TEXT)
        tenet_rect = tenet_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(tenet_surf, tenet_rect)

        if tenet_char_index >= len(tenet_text):
            hint_surf = font_hint.render("[ SPACE ] To View Shards", True, GOLD)
            hint_rect = hint_surf.get_rect(center=(WIDTH // 2, HEIGHT - 80))
            screen.blit(hint_surf, hint_rect)

    elif scene == "SHARD_HINT":
        screen.fill((5, 10, 15))
        hdr = font_hint.render(shard_text[:shard_char_index], True, (200, 230, 255))
        screen.blit(hdr, hdr.get_rect(center=(WIDTH // 2, 80)))

        if shard_char_index >= len(shard_text):
            # Layout for Shards
            shards_data = [(shard1_img, "PATIENCE", 100), (shard2_img, "ENDURANCE", 400),
                           (shard3_img, "DISCIPLINE", 700)]
            for img, name, x in shards_data:
                screen.blit(img, (x, 200))
                lbl = font_menu.render(name, True, GOLD)
                screen.blit(lbl, lbl.get_rect(center=(x + 100, 430)))

            # --- INDICATORS RE-ADDED HERE ---
            hint_space = font_hint.render("[ SPACE ] Begin Trial", True, WHITE)
            screen.blit(hint_space, hint_space.get_rect(center=(WIDTH // 2, 520)))

            hint_esc = font_hint.render("[ ESC ] Back to Main Menu", True, GOLD)
            screen.blit(hint_esc, hint_esc.get_rect(center=(WIDTH // 2, 560)))

    # Master Fade & Brightness Overlay
    master_overlay = pygame.Surface((WIDTH, HEIGHT))
    master_overlay.fill((0, 0, 0))
    master_overlay.set_alpha(max(fade_alpha, brightness_alpha))
    screen.blit(master_overlay, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
