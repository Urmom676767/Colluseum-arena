import pygame
import sys
import random
import asyncio
import math

# 1. Initialize Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Colosseum: Chronicles of the Arena")
clock = pygame.time.Clock()

# Initialize Fonts
pygame.font.init()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# 2. Player (Gladiator) Setup
player_width, player_height = 40, 40
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
normal_speed = 5
dash_speed = 20

# Player Stats & Leveling
player_level = 1
player_exp = 0
player_exp_needed = 100
player_max_health = 100
player_health = 100
base_damage = 15

# Action Variables
is_dashing = False
dash_timer = 0
dash_duration = 10  
dash_dir_x = 0
dash_dir_y = 0

is_blocking = False
attack_timer = 0
attack_duration = 15  

# 3. Historical Spectacle Data Setup
SPECTACLES = [
    {
        "stage_name": "SPECTACLE I: THE VENATIO",
        "boss_name": "Raging Gorilla",      
        "health": 150, "speed": 2.4, "width": 65,  "height": 65,  
        "color": (160, 82, 45), "env": (45, 75, 40) # Jungle green arena floor
    },
    {
        "stage_name": "SPECTACLE II: THE EXECUTION",
        "boss_name": "Grand Executioner", 
        "health": 280, "speed": 3.0, "width": 55,  "height": 55,  
        "color": (40, 40, 40), "env": (90, 80, 70) # Rocky dark stone
    },
    {
        "stage_name": "SPECTACLE III: MYTHOLOGICAL DRAMA",
        "boss_name": "The Manticore Beast",   
        "health": 420, "speed": 2.2, "width": 80,  "height": 80,  
        "color": (180, 50, 50), "env": (110, 85, 65) # Scorched mud
    },
    {
        "stage_name": "SPECTACLE IV: THE NAUMACHIA",
        "boss_name": "Roman War Galley",   
        "health": 600, "speed": 2.5, "width": 110, "height": 60,  
        "color": (100, 60, 30), "env": (25, 65, 120) # Flooded deep blue water
    },
    {
        "stage_name": "SPECTACLE V: IMPERIAL FINALE",
        "boss_name": "EMPEROR COMMODUS",    
        "health": 900, "speed": 3.4, "width": 95,  "height": 95,  
        "color": (212, 175, 55), "env": (120, 25, 25) # Imperial royal crimson
    }
]

current_spectacle_idx = 0
boss_x = 100
boss_y = 100

def load_spectacle(index):
    global boss_x, boss_y, boss_max_health, boss_health, boss_speed, boss_width, boss_height, boss_color
    boss_x = 100
    boss_y = 100
    data = SPECTACLES[index]
    boss_max_health = data["health"]
    boss_health = boss_max_health
    boss_speed = data["speed"]
    boss_width = data["width"]
    boss_height = data["height"]
    boss_color = data["color"]

load_spectacle(current_spectacle_idx)

# 4. Arena Hazards & Pickup Items
health_packs = []
health_pack_width, health_pack_height = 20, 20

def spawn_health_pack():
    x = random.randint(50, SCREEN_WIDTH - 50)
    y = random.randint(50, SCREEN_HEIGHT - 50)
    pack = pygame.Rect(x, y, health_pack_width, health_pack_height)
    health_packs.append(pack)

for _ in range(3):
    spawn_health_pack()

# 5. Main Loop
async def main():
    global player_x, player_y, player_health, player_max_health, is_dashing, dash_timer, dash_dir_x, dash_dir_y
    global is_blocking, attack_timer, boss_x, boss_y, boss_health, player_level, player_exp, player_exp_needed, base_damage
    global current_spectacle_idx, boss_width, boss_height, boss_color
    
    game_over = False
    victory = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not game_over and not victory:
            # --- LEVEL UP SYSTEM ---
            player_exp += 0.05  
            if player_exp >= player_exp_needed:
                player_level += 1
                player_exp = 0
                player_exp_needed = int(player_exp_needed * 1.5)
                player_max_health += 20
                player_health = player_max_health  
                base_damage += 5

            # --- LIFE DRAIN ---
            if player_health > 0:
                player_health -= 0.03  
            else:
                player_health = 0
                game_over = True

            # --- CHAMPION CAMPAIGN PROGRESSION ---
            if boss_health <= 0:
                if current_spectacle_idx < len(SPECTACLES) - 1:
                    current_spectacle_idx += 1
                    load_spectacle(current_spectacle_idx)
                    player_exp += 75  
                    player_health = min(player_max_health, player_health + 50) 
                else:
                    victory = True

            # --- PLAYER MOVEMENT & DRIFT CONTROLS ---
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                is_blocking = True
                current_speed = normal_speed * 0.5  
            else:
                is_blocking = False
                current_speed = normal_speed

            move_x = 0
            move_y = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: move_x = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_x = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]: move_y = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: move_y = 1

            # Dash Trigger
            if keys[pygame.K_SPACE] and not is_dashing and (move_x != 0 or move_y != 0):
                is_dashing = True
                dash_timer = dash_duration
                dash_dir_x = move_x
                dash_dir_y = move_y

            # Knife Input
            if keys[pygame.K_f] and attack_timer <= 0 and not is_dashing:
                attack_timer = attack_duration

            # Movement Handling
            if is_dashing:
                player_x += dash_dir_x * dash_speed
                player_y += dash_dir_y * dash_speed
                dash_timer -= 1
                if dash_timer <= 0:
                    is_dashing = False
            else:
                player_x += move_x * current_speed
                player_y += move_y * current_speed
                
                # WATER DRIFT EFFECT: Spectacle IV (Naumachia) causes movement to slip slightly
                if current_spectacle_idx == 3:
                    player_y += 0.3 # Pushes the player downwards mimicking water currents

            player_x = max(0, min(SCREEN_WIDTH - player_width, player_x))
            player_y = max(0, min(SCREEN_HEIGHT - player_height, player_y))

            # --- RUTHLESS AI BEHAVIOR ---
            dx = player_x - boss_x
            dy = player_y - boss_y
            dist = math.hypot(dx, dy)
            
            if dist != 0:
                boss_x += (dx / dist) * boss_speed
                boss_y += (dy / dist) * boss_speed

            # --- ARENA DAMAGE OVERLAPS ---
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            boss_rect = pygame.Rect(boss_x, boss_y, boss_width, boss_height)
            
            if player_rect.colliderect(boss_rect):
                damage = 1.5 + (current_spectacle_idx * 0.6)
                if is_blocking:
                    damage *= 0.15  
                player_health = max(0, player_health - damage)

            # Attack Checking
            if attack_timer > 0:
                attack_timer -= 1
                knife_rect = pygame.Rect(player_x - 20, player_y - 20, player_width + 40, player_height + 40)
                if knife_rect.colliderect(boss_rect) and attack_timer == attack_duration - 1:
                    boss_health = max(0, boss_health - base_damage)
                    player_exp += 25  

            # Health Collection
            for pack in health_packs[:]:
                if player_rect.colliderect(pack):
                    health_packs.remove(pack)
                    player_health = min(player_max_health, player_health + 30)
                    spawn_health_pack()

        # --- DRAWING / RENDERING STAGE ---
        screen.fill(SPECTACLES[current_spectacle_idx]["env"])  
        
        if not game_over and not victory:
            for pack in health_packs:
                pygame.draw.rect(screen, (0, 255, 100), pack)
                
            # Draw Boss
            pygame.draw.rect(screen, boss_color, boss_rect)
            
            # Draw Player
            player_color = (255, 215, 0) if is_blocking else (0, 100, 255)
            pygame.draw.rect(screen, player_color, player_rect)
            
            if attack_timer > 0:
                pygame.draw.rect(screen, (0, 255, 255), (player_x - 10, player_y - 10, player_width + 20, player_height + 20), 3)

            # --- USER INTERFACE (UI) ---
            # Gladiator HP
            health_bar_width = int((player_health / player_max_health) * 200)
            pygame.draw.rect(screen, (150, 0, 0), (20, 20, 200, 20))
            if player_health > 0:
                pygame.draw.rect(screen, (0, 200, 0), (20, 20, health_bar_width, 20))
            player_lbl = font.render(f"LVL {player_level} GLADIATOR", True, (255, 255, 255))
            screen.blit(player_lbl, (20, 45))

            # Experience Display
            exp_bar_width = int((player_exp / player_exp_needed) * 200)
            pygame.draw.rect(screen, (50, 50, 50), (20, 75, 200, 10))
            pygame.draw.rect(screen, (0, 150, 255), (20, 75, exp_bar_width, 10))

            # Current Event Info Displays
            stage_lbl = font.render(SPECTACLES[current_spectacle_idx]["stage_name"], True, (255, 240, 150))
            screen.blit(stage_lbl, (SCREEN_WIDTH // 2 - 160, 20))

            # Boss Health Output
            boss_bar_width = int((boss_health / boss_max_health) * 200)
            pygame.draw.rect(screen, (150, 0, 0), (SCREEN_WIDTH - 220, 20, 200, 20))
            if boss_health > 0:
                pygame.draw.rect(screen, (255, 50, 50), (SCREEN_WIDTH - 220, 20, boss_bar_width, 20))
