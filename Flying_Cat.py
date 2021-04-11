import pygame
import random


# Setting
IMG_DIR = './assets'
SOUND_DIR = './sounds'

WIDTH = 480
HEIGHT = 700
FPS = 60
POWERUP_TIME = 5000
BAR_LENGTH = 100
BAR_HEIGHT = 10

# ## 기본 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (252, 174, 30)
LIGHT_GRAY = (211, 211, 211)

TITLE_COLOR = (232, 255, 245)

# ## 게임 배경
BACKGROUND_COLOR_1 = (101, 92, 175) # (80, 42, 113) 
BACKGROUND_COLOR_2 = (195, 119, 224)  # (237, 219, 244) 

colour_rect = pygame.Surface((2, 2))                                   
pygame.draw.line(colour_rect, BACKGROUND_COLOR_1, (0, 0), (1, 0))         # top
pygame.draw.line(colour_rect, BACKGROUND_COLOR_2, (0, 1), (1, 1))         # bottom
BACKGROUND = pygame.transform.smoothscale(colour_rect, (WIDTH, HEIGHT))   # stretch

MINT = (119, 224, 153)
SKYBLUE = (239, 249, 253)

# ## 글씨체
FONT = pygame.font.match_font('arial')


# 기본 함수
def get_img(file):
    return pygame.image.load(f"{IMG_DIR}/{file}")


def get_sound(file, volume):
    sound = pygame.mixer.Sound(f"{SOUND_DIR}/{file}")
    sound.set_volume(volume)
    return sound


def set_music(file):
    return pygame.mixer.music.load(f"{SOUND_DIR}/{file}")


def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(FONT, size)
    
    text = font.render(text, True, color)  # True denotes the font to be anti-aliased
    text_rect = text.get_rect()
    text_rect.midtop = (x, y)
    
    surface.blit(text, text_rect)


# Game
# ## Initialize pygame and create window
pygame.init()
pygame.mixer.init()  # For sound

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hyeonjoo Jeong")

clock = pygame.time.Clock()  # For syncing the FPS


# ## Load images
MAIN = get_img("main.jpg").convert()

PLAYER = get_img('cat.png').convert()
PLAYER_IMG = pygame.transform.scale(PLAYER, (90, 90))
PLAYER_IMG.set_colorkey(BLACK)
PLAYER_MINI_IMG = pygame.transform.scale(PLAYER_IMG, (25, 19))
PLAYER_MINI_IMG.set_colorkey(BLACK)

BULLET_IMG = get_img('paw.png').convert()
MISSILE_IMG = get_img('missile.png').convert_alpha()

POWERUP_IMGS = {'fish': get_img('canned_fish.png').convert(), 
                'leaf': get_img('leaf.png').convert()}

MONSTERS = ['toy_yarn1.png', 'toy_yarn2.png', 'toy_yarn3.png', 'toy_yarn4.png',
            'toy_yarn5.png', 'toy_yarn6.png',
            'toy_rubber_duck.png']

MONSTER_IMGS = [get_img(image).convert() for image in MONSTERS]
MONSTER_SIZES = [80, 60, 40]

BUTTERFLIES = ['butterfly_large.png', 
               'butterfly_mid.png', 
               'butterfly_small.png']

BUTTERFLY_IMGS = [get_img(image).convert() for image in BUTTERFLIES]

EXPLOSION_ANIMATION = {'large': [], 'small': [], 'player': []}

for i in range(9):
    img = get_img(f'regularExplosion0{i}.png').convert()
    img.set_colorkey(BLACK)
    
    # resize the explosion
    img_lg = pygame.transform.scale(img, (75, 75))
    EXPLOSION_ANIMATION['large'].append(img_lg)
    
    img_sm = pygame.transform.scale(img, (32, 32))
    EXPLOSION_ANIMATION['small'].append(img_sm)

    # player explosion
    img = get_img(f'sonicExplosion0{i}.png').convert()
    img.set_colorkey(BLACK)
    EXPLOSION_ANIMATION['player'].append(img)


# ## Sounds
MAIN_SONG = "Cats And Spies.wav"
THEME_SONG = "copycat.mp3"

READY_SOUND = get_sound('ready.wav', 0.3)
GO_SOUND = get_sound('go.wav', 0.2)

ITEM_SOUND = get_sound('Meow.ogg', 0.2)
SHOOTING_SOUND = get_sound('pew.wav', 0.05)

expl_sounds = [get_sound('expl3.wav', 0.05), get_sound('expl6.wav', 0.05)]

player_die_sound = get_sound('rumble1.ogg', 0.1)

pygame.mixer.music.set_volume(0.2)


# ## Main
def main_menu():
    global screen
    
    # 메인 음악
    set_music(MAIN_SONG)
    pygame.mixer.music.play(-1)
    
    # 메인 화면
    title = pygame.transform.scale(MAIN, (WIDTH, HEIGHT), screen)
    screen.blit(title, (0, 0))
    pygame.display.update()

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
            elif ev.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
        elif ev.type == pygame.QUIT:
                pygame.quit()
                exit()
        else:
            draw_text(screen, "Flying Cat", 80, WIDTH/2, 80, TITLE_COLOR)
            draw_text(screen, "[ENTER] To Begin", 40, WIDTH/2, 220)
            draw_text(screen, "[Esc] To Quit", 40, WIDTH/2, 290)
            pygame.display.update()


# ## 기능
# ### 충돌
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, obj):
        pygame.sprite.Sprite.__init__(self)
        self.animation = EXPLOSION_ANIMATION[obj]
        self.center = center
        
        # 시작 이미지
        self.image = self.animation[0]
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        
        # frame 설정
        self.frame = 0
        self.frame_rate = 75
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.animation):
                self.kill()
            else:
                self.image = self.animation[self.frame]
                self.image.get_rect().center = self.center


# ### Monster
class Monster(pygame.sprite.Sprite):
    def __init__(self, speed_range=(4, 7)):
        pygame.sprite.Sprite.__init__(self)
        
        # 랜덤하게 이미지, 사이즈 설정
        image = random.choice(MONSTER_IMGS)
        size = random.choice(MONSTER_SIZES)
        self.image_orig = pygame.transform.scale(image, (size, size))
        
        self.image_orig.set_colorkey(WHITE)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width // 2
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        
        # speed
        self.speedy = random.randrange(*speed_range)
        self.speedx = random.randrange(-3, 3)

        # rotation
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:  # in milliseconds
            self.last_update = now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        # 몬스터가 화면 밖으로 나가는 경우
        if (self.rect.top > HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > WIDTH + 20):
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Butterfly(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.state = 0
        self.radius = 0
        self.set_image()
        
        self.last_update_x = pygame.time.get_ticks()
        self.last_update_y = pygame.time.get_ticks()
        
        self.speedy = random.randrange(1, 4) * (-1 + 2 * random.randrange(0, 2))
        self.speedx = -1 + 2 * random.randrange(0, 2)
        
    def set_image(self, x=None, y=None):
        self.image = BUTTERFLY_IMGS[self.state].copy()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = (self.rect.width * 0.9) // 2
        
        if x is None or y is None:
            x = random.randrange(0, WIDTH - self.rect.width)
            y = random.randrange(0, HEIGHT//3)
        self.rect.x = x
        self.rect.y = y

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update_x > 3000:  # in milliseconds
            self.speedx *= -1 ** random.randrange(0, 2)
            self.last_update_x = now
            
        if now - self.last_update_y > 500:  # in milliseconds
            self.speedy = random.randrange(1, 4) * (-1 + 2 * random.randrange(0, 2))
            self.last_update_y = now

        # check for the borders
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.speedx *= -1

        if self.rect.left < 0:
            self.rect.left = 0
            self.speedx *= -1

        if self.rect.bottom > HEIGHT/2:
            self.rect.bottom = HEIGHT/2
            self.speedy *= -1

        if self.rect.top < 0:
            self.rect.top = 0
            self.speedy *= -1
            
        self.rect.x += self.speedx
        self.rect.y += self.speedy
    
    def change_color(self):
        if self.state > 1:
            self.kill()
            return False
        else:
            self.state += 1
            self.set_image(self.rect.x, self.rect.y)
#            pygame.PixelArray(self.image).replace(BUTTERFLY_COLORS[self.state - 1], BUTTERFLY_COLORS[self.state])
        
        return True


# ### Item
class Item(pygame.sprite.Sprite):
    def __init__(self, type, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        self.image = POWERUP_IMGS[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        
        if self.rect.top > HEIGHT:
            self.kill()


class Potion(Item):
    def __init__(self, center):
        Item.__init__(self, 'fish', center)


class Powerup(Item):
    def __init__(self, center):
        Item.__init__(self, 'leaf', center)


# ### Player
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        
        if self.rect.bottom < 0:
            self.kill()


class Paw(Bullet):
    def __init__(self, x, y):
        Bullet.__init__(self, x, y, BULLET_IMG)


class Missile(Bullet):
    def __init__(self, x, y):
        Bullet.__init__(self, x, y, MISSILE_IMG)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        # 이미지
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        
        # 설정
        self.speedx = 0
        self.speedy = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        
        # power
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        # time out for powerup
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # unhide
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 30

        self.speedx = 0 
        self.speedy = 0

        # 키 입력
        key_states = pygame.key.get_pressed()

        if key_states[pygame.K_LEFT]:
            self.speedx = -5

        if key_states[pygame.K_RIGHT]:
            self.speedx = 5

        if key_states[pygame.K_UP]:
            self.speedy = -5

        if key_states[pygame.K_DOWN]:
            self.speedy = 5

        if key_states[pygame.K_SPACE]:
            self.shoot()

        # check for the borders
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            
        if self.rect.left < 0:
            self.rect.left = 0
            
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            
        if self.rect.top < 0:
            self.rect.top = 0

        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Paw(self.rect.centerx, self.rect.top)
                sprites.add(bullet)
                bullets.add(bullet)
            elif self.power == 2:
                bullet1 = Paw(self.rect.left, self.rect.centery)
                bullet2 = Paw(self.rect.right, self.rect.centery)
                sprites.add(bullet1)
                sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
            elif self.power >= 3:
                bullet1 = Paw(self.rect.left, self.rect.centery)
                bullet2 = Paw(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top)
                sprites.add(bullet1)
                sprites.add(bullet2)
                sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
            
            SHOOTING_SOUND.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


# ### Background

stars_small = []
stars_medium = []
stars_big = []

for _ in range(50): 
    star_loc_x = random.randrange(0, WIDTH)
    star_loc_y = random.randrange(0, HEIGHT)
    stars_small.append([star_loc_x, star_loc_y])

for _ in range(35):
    star_loc_x = random.randrange(0, WIDTH)
    star_loc_y = random.randrange(0, HEIGHT)
    stars_medium.append([star_loc_x, star_loc_y])

for _ in range(15):
    star_loc_x = random.randrange(0, WIDTH)
    star_loc_y = random.randrange(0, HEIGHT)
    stars_big.append([star_loc_x, star_loc_y])


# ### Play

def pause():
    image = pygame.Surface([WIDTH, HEIGHT])
    image.fill(BLACK)
    image.set_alpha(100)
    
    screen.blit(image, (0, 0))
    
    x = WIDTH / 2
    y = HEIGHT // 2
    font_size = 30
    
    draw_text(screen, '[ENTER] to continue', font_size, x, y-50, WHITE)
    draw_text(screen, '[Q] to main', font_size, x, y, WHITE)
    draw_text(screen, '[ESC] to quit', font_size, x, y+50, WHITE)
    
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit() 
                    exit()
                elif event.key == pygame.K_RETURN:
                    return False


def died():
    image = pygame.Surface([WIDTH, HEIGHT])
    image.fill(BLACK)
    image.set_alpha(100)
    
    screen.blit(image, (0, 0))
    
    x = WIDTH / 2
    y = HEIGHT // 2
    font_size = 30
    
    draw_text(screen, 'YOU DIED', 60, x, y-100, RED)
    draw_text(screen, '[ENTER] to main', font_size, x, y+50, WHITE)
    draw_text(screen, '[ESC] to quit', font_size, x, y+100, WHITE)
    
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False


def draw_shield_bar(surf, x, y, pct):
    pct = max(pct, 0)
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)

    if fill < 0.2 * BAR_LENGTH:
        pygame.draw.rect(surf, RED, fill_rect)
    elif fill < 0.6 * BAR_LENGTH:
        pygame.draw.rect(surf, ORANGE, fill_rect)
    else:
        pygame.draw.rect(surf, GREEN, fill_rect)
        
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def gen_monster():
    toy = Monster((3, 8))
    toys.add(toy)
    monsters.add(toy)
    sprites.add(toy)
    

running = True
paused = False
do_initialize = True

while running:
    # 초기 설정
    if do_initialize:
        do_initialize = False

        main_menu()
        
        # 게임 준비 화면
        READY_SOUND.play()

        for i in range(3, 0, -1):
            screen.fill(BLACK)
            draw_text(screen, str(i), 40, WIDTH/2, HEIGHT/2)
            pygame.display.update()
            pygame.time.wait(1000)

        GO_SOUND.play()

        # 음악 변경
        pygame.mixer.music.stop()
        set_music(THEME_SONG)
        pygame.mixer.music.play(-1)

        # groups
        # ## all sprites
        sprites = pygame.sprite.Group()

        # ## player
        player = Player()
        sprites.add(player)

        # ## monster
        monsters = pygame.sprite.Group()
        toys = pygame.sprite.Group()
        butterflies = pygame.sprite.Group()

        for i in range(8):
            gen_monster()

        # ## etc
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()

        # Setting
        score = 0
        time_butterfly = pygame.time.get_ticks()
        
    
    # Input Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if pause():
                    do_initialize = True
                    pygame.display.update()
                    continue
            elif event.type == pygame.K_RETURN:
                pass    # 필살기?
    
    # Game logic
    clock.tick(FPS)
    
    # ## Update
    sprites.update()
    
    # ## butterfly
    time_now = pygame.time.get_ticks()
    if time_now - time_butterfly > 3000:
        butterfly = Butterfly()
        butterflies.add(butterfly)
        monsters.add(butterfly)
        sprites.add(butterfly)
        time_butterfly = time_now 
    
    # ## monster와 bullet 충돌
    collisions = pygame.sprite.groupcollide(toys, bullets, True, True)
    for collision in collisions:
        score += 50 - collision.radius
        random.choice(expl_sounds).play()
        exp = Explosion(collision.rect.center, 'large')
        sprites.add(exp)
        
        if random.random() > 0.9:
            item = Potion(collision.rect.center)
            sprites.add(item)
            powerups.add(item)
        
        gen_monster()
        
    collisions = pygame.sprite.groupcollide(butterflies, bullets, False, True)
    for collision in collisions:
        is_alive = collision.change_color()

        if not is_alive:
            score += 50
            if random.random() > 0.5:
                item = Powerup(collision.rect.center)
                sprites.add(item)
                powerups.add(item)

    # ## item 획득
    collisions = pygame.sprite.spritecollide(player, powerups, True)
    for collision in collisions:
        ITEM_SOUND.play()
        if collision.type == 'fish':
            player.shield = min(100, player.shield + 20)
        elif collision.type == 'leaf':
            player.powerup()

    # ## player와 monster 충돌
    collisions = pygame.sprite.spritecollide(player, monsters, True, pygame.sprite.collide_circle)
    for collision in collisions:
        player.shield -= collision.radius
        exp = Explosion(collision.rect.center, 'small')
        sprites.add(exp)
        gen_monster()
        
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
    
    if player.lives == 0:
        player.hide()
        player.shield = 0
    
        if not death_explosion.alive():
            pygame.mixer.music.stop()
            if died():
                do_initialize = True
                pygame.display.update()
                continue
            else:
                running = False
        
    # Drawing
    # ## background
    screen.blit(BACKGROUND, (0, 0))
    
    for star in stars_small:
        star[1] += 1
        if star[1] > HEIGHT:
            star[0] = random.randrange(0, WIDTH)
            star[1] = random.randrange(-20, -5)
        pygame.draw.circle(screen, YELLOW, star, 1)

    for star in stars_medium:
        star[1] += 1
        if star[1] > HEIGHT:
            star[0] = random.randrange(0, WIDTH)
            star[1] = random.randrange(-20, -5)
        pygame.draw.circle(screen, MINT, star, 2)

    for star in stars_big:
        star[1] += 1
        if star[1] > HEIGHT:
            star[0] = random.randrange(0, WIDTH)
            star[1] = random.randrange(-20, -5)
        pygame.draw.circle(screen, SKYBLUE, star, 2)
        
    # ## sprite들
    sprites.draw(screen)
    
    # ## 상단 정보
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, PLAYER_MINI_IMG)
    
    pygame.display.flip()

pygame.quit() 

