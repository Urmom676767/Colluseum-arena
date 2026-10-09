import pygame
import sys
import random
import asyncio

# 1. Initialize Pygame Components cleanly
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Colosseum: Chronicles of the Arena")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 18)

# 2. Player (Gladiator) Setup
player_width = 40
player_height = 40
player_x = 400
player_y = 300
normal_speed = 5
dash_speed = 18

player_level = 1
player_exp = 0
player_exp_needed = 100
player_max_health = 100
player_health = 100
base_damage = 15

# States
is_dashing = False
dash_timer = 0
dash_duration = 10  
dash_dir_x = 0
dash_dir_y = 0

is_blocking = False
attack_timer = 0
attack_duration = 12  

# 3. Arena Spectacle Configurations
SPECTACLES = [
    {"stage": "SPECTACLE I: THE VENATIO", "boss": "Raging Gorilla", "health": 150, "speed": 2.2, "size": 60, "color": (160, 82, 45), "env": (45, 75, 40)},
    {"stage": "SPECTACLE II: THE EXECUTION", "boss": "Grand Executioner", "health": 260, "speed": 2.8, "size": 55, "color": (40, 40, 40), "env": (90, 80, 70)},
    {"stage": "SPECTACLE III: MYTHOLOGICAL DRAMA", "boss": "The Manticore Beast", "health": 400, "speed": 2.0, "size": 75, "color": (180, 50, 50), "env": (110, 85, 65)},
    {"stage": "SPECTACLE IV: THE NAUMACHIA", "boss": "Roman War Galley", "health": 550, "speed": 2.4, "size": 90, "color": (100, 60, 30), "env": (25, 65, 120)},
    {"stage": "SPECTACLE V: IMPERIAL FINALE", "boss": "EMPEROR COMMODUS", "health": 800, "speed": 3.2, "size": 95, "color": (212, 175, 55), "env": (120, 25, 25)}
]

current_spectacle_idx = 0
boss_x = 100
boss_y = 100

boss_max_health = SPECTACLES[0]["health"]
boss_health = boss_max_health
boss_speed = SPECTACLES[0]["speed"]
boss_size = SPECTACLES[0]["size"]
boss_color = SPECTACLES[0]["color"]

def load_spectacle(index):
    global boss_x, boss_y, boss_max_health, boss_health, boss_speed, boss_size, boss_color
    boss_x = 100
    boss_y = 100
    data = SPECTACLES[index]
    boss_max_health = data["health"]
    boss_health = boss_max_health
    boss_speed = data["speed"]
    boss_size = data["size"]
    boss_color = data["color"]

# 4. Items (X and Y lists are safer for Brython than raw Rect arrays)
pack_x = [random.randint(50, 750) for _ in range(3)]
pack_y = [random.randint(50, 550) for _ in range(3)]
pack_size = 20

# 5. Main Clean Loop Engine
async def main():
    global player_x, player_y, player_health, player_max_health, is_dashing, dash_timer, dash_dir_x, dash_dir_y
    global is_blocking, attack_timer, boss_x, boss_y, boss_health, player_level, player_exp, player_exp_needed, base_damage
    global current_spectacle_idx, boss_size, boss_color, boss_max_health, boss_speed
    
    game_over = False
    victory = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not game_over and not victory:
            # --- EXP STAT LEVELS ---
            player_exp += 0.05  
            if player_exp >= player_exp_needed:
                player_level += 1
                player_exp = 0
                player_exp_needed = int(player_exp_needed * 1.5)
                player_max_health += 20
                player_health = player_max_health  
                base_damage += 5

            # --- LIFE RATIO CHECKS ---
            if player_health > 0:
                player_health -= 0.03  
            else:
                player_health = 0
                game_over = True

            if boss_health <= 0:
                if current_spectacle_idx < 4:
                    current_spectacle_idx += 1
                    load_spectacle(current_spectacle_idx)
                    player_exp += 75  
                    player_health = min(player_max_health, player_health + 50) 
                else:
                    victory = True

            # --- CONTROL HOOKS ---
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

            if keys[pygame.K_SPACE] and not is_dashing and (move_x != 0 or move_y != 0):
                is_dashing = True
                dash_timer = dash_duration
                dash_dir_x = move_x
                dash_dir_y = move_y

            if keys[pygame.K_f] and attack_timer <= 0 and not is_dashing:
                attack_timer = attack_duration

            # --- VECTORS ---
            if is_dashing:
                player_x += dash_dir_x * dash_speed
                player_y += dash_dir_y * dash_speed
                dash_timer -= 1
                if dash_timer <= 0:
                    is_dashing = False
            else:
                player_x += move_x * current_speed
                player_y += move_y * current_speed
                
                # Naumachia Sea Drift Handling
                if current_spectacle_idx == 3:
                    player_y += 0.3 

            player_x = max(0, min(SCREEN_WIDTH - player_width, player_x))
            player_y = max(0, min(SCREEN_HEIGHT - player_height, player_y))

            # --- CLEAN TRACKING (Using simple distance instead of math.hypot) ---
            dx = player_x - boss_x
            dy = player_y - boss_y
            abs_dist = abs(dx) + abs(dy) # Safer web logic fallback
            
            if abs_dist > 0:
                boss_x += (dx / abs_dist) * boss_speed
                boss_y += (dy / abs_dist) * boss_speed

            # --- DAMAGE OVERLAPS ---
            # Player Box
            p_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            # Boss Box
            b_rect = pygame.Rect(boss_x, boss_y, boss_size, boss_size)
            
            if p_rect.colliderect(b_rect):
                damage = 1.2 + (current_spectacle_idx * 0.5)
                if is_blocking:
                    damage *= 0.15  
                player_health = max(0, player_health - damage)

            # Attack Slash
            if attack_timer > 0:
                attack_timer -= 1
                k_rect = pygame.Rect(player_x - 15, player_y - 15, player_width + 30, player_height + 30)
                if k_rect.colliderect(b_rect) and attack_timer == attack_duration - 1:
                    boss_health = max(0, boss_health - base_damage)
                    player_exp += 25  

            # Items Collection Loop
            for i in range(len(pack_x)):
                pack_rect = pygame.Rect(pack_x[i], pack_y[i], pack_size, pack_size)
                if p_rect.colliderect(pack_rect):
                    player_health = min(player_max_health, player_health + 30)
                    pack_x[i] = random.randint(50, SCREEN_WIDTH - 50)
                    pack_y[i] = random.randint(50, SCREEN_HEIGHT - 50)

        # --- RENDERING SCENE ---
        screen.fill(SPECTACLES[current_spectacle_idx]["env"])  
        
        if not game_over and not victory:
            # Draw Green Food Squares
            for i in range(len(pack_x)):
                pygame.draw.rect(screen, (0, 255, 100), (pack_x[i], pack_y[i], pack_size, pack_size))
                
            # Draw Target Opponent
            pygame.draw.rect(screen, boss_color, b_rect)
            
            # Draw Player Rect (Gold if Blocking, Blue if Moving)
            player_color = (255, 215, 0) if is_blocking else (0, 100, 255)
            pygame.draw.rect(screen, player_color, p_rect)
            
            if attack_timer > 0:
                pygame.draw.rect(screen, (0, 255, 255), (player_x - 10, player_y - 10, player_width + 20, player_height + 20), 2)

            # --- HUD LAYOUTS ---
            # HP Bar
            h_width = int((player_health / player_max_health) * 200)
            pygame.draw.rect(screen, (150, 0, 0), (20, 20, 200, 15))
            if player_health > 0:
                pygame.draw.rect(screen, (0, 200, 0), (20, 20, h_width, 15))
            player_lbl = font.render("GLADIATOR Lvl " + str(player_level), True, (255, 255, 255))
            screen.blit(player_lbl, (20, 40))

            # EXP Line Bar
            e_width = int((player_exp / player_exp_needed) * 200)
            pygame.draw.rect(screen, (50, 50, 50), (20, 70, 200, 8))
            pygame.draw.rect(screen, (0, 150, 255), (20, 70, e_width, 8))

            # Center Stage Level Title
            stage_lbl = font.render(SPECTACLES[current_spectacle_idx]["stage"], True, (255, 240, 150))
            screen.blit(stage_lbl, (220, 20))

            # Boss HP Bar
            if boss_health > 0:
                b_width = int((boss_health / boss_max_health) * 200)
                pygame.draw.rect(screen, (150, 0, 0), (SCREEN_WIDTH - 220, 20, 200, 15))
                pygame.draw.rect(screen, (255, 50, 50), (SCREEN_WIDTH - 220, 20, b_width, 15))
            
            boss_lbl = font.render(SPECTACLES[current_spectacle_idx]["boss"], True, (255, 255, 255))
            screen.blit(boss_lbl, (SCREEN_WIDTH - 250, 40))
            
        elif game_over:
            txt = font.render("DEFEAT! The Arena floor claims you.", True, (255, 50, 50))
            screen.blit(txt, (200, 280))
            
        elif victory:
            txt = font.render("👑 RUDIS CHAMPION! Freedom is yours!", True, (50, 255, 50))
            screen.blit(txt, (180, 280))

        pygame.display.flip()  
        clock.tick(60)  

