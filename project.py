import os
from pygame import *
import pygame
import sys
import time
import random
import pyganim as pyganim
import pygame_menu

clock = pygame.time.Clock()
BLACK = pygame.Color("black")
GREEN = pygame.Color("green")
WHITE = pygame.Color("white")
YELLOW = pygame.Color("yellow")
SIZE = WIDTH, HEIGHT = 700, 900
SCREEN = pygame.display.set_mode(SIZE)
FPS = 60
bullets = []
enemy_bullets = []
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
FILE_DIR = os.path.dirname(__file__)
ANIMATION_MOVE_ENEMIES = [("data/enemies1.png"), ("data/enemies2.png")]
ANIMATION_MOVE_OCTAVIUS = [("data/octavius1.png"), ("data/octavius2.png")]


def load_image(name: str, colorkey=None) -> pygame.Surface:
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def loadLevel(level_num):
    """
    Загрузка уровня
    """
    levelFile = open(f'%s/data/{"aliens.txt"}' % FILE_DIR)
    line = " "
    commands = []
    while line[0] != "/":  # пока не нашли символ завершения файла
        line = levelFile.readline()  # считываем построчно
        if line and line[0] == "[":  # если нашли символ начала уровня
            while line[0] != "]":  # то, пока не нашли символ конца уровня
                line = levelFile.readline()  # считываем построчно уровень
                if line[0] != "]":  # и если нет символа конца уровня
                    aliens.append(line)  # и добавляем в уровень строку от начала до символа "|"


aliens = []
loadLevel('')
CELL_SIZE = WIDTH / (len(aliens[0]))


class Gun(pygame.sprite.Sprite):
    image = load_image("ship.png")
    image = pygame.transform.scale(image, (CELL_SIZE * 2.25, CELL_SIZE * 2.25))

    def __init__(self, SCREEN):
        super().__init__(all_sprites)
        self.screen = SCREEN
        self.image = Gun.image
        self.life = 3
        self.rect = self.image.get_rect()
        self.screen_rect = SCREEN.get_rect()
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom
        self.right = False
        self.left = False
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):

        if self.right and self.rect.right < self.screen_rect.right:
            self.rect.centerx += 250 / FPS
        if self.left and self.rect.left > self.screen_rect.left:
            self.rect.centerx -= 250 / FPS
        if enemy_bullets and pygame.sprite.collide_rect(self, enemy_bullets[0]):
            self.life -= 1
            enemy_bullets[0].kill()
            enemy_bullets.pop(0)
            pygame.time.wait(1000)
            if self.life == 0:
                death_screen()
        if pygame.sprite.spritecollideany(self, enemies):
            time.sleep(2)
            main()


class Bullet(pygame.sprite.Sprite):
    """класс создания нашей пули"""

    def __init__(self, gun):
        if bullets:
            return
        super().__init__(all_sprites)
        self.image = pygame.Surface((3, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.speed = 1000 / FPS
        self.rect.centerx = gun.rect.centerx
        self.rect.top = gun.rect.top
        self.y = self.rect.y
        bullets.append(self)

    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
        if self.rect.y < 0:
            bullets.pop(bullets.index(self))
            self.kill()


class Enemy(pygame.sprite.Sprite):
    image = load_image("enemies1.png").convert_alpha()
    image = pygame.transform.scale(image, (CELL_SIZE * 1.5, CELL_SIZE * 1.5))

    def __init__(self, coord_x, coord_y):
        super().__init__(all_sprites)
        self.image = Enemy.image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        boltAnim = []
        # анимация разрушения преградыa
        for anim in ANIMATION_MOVE_ENEMIES:
            boltAnim.append((anim, 300))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.scale((self.rect.width, self.rect.height))
        self.boltAnim.play()

        self.startY = coord_y
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.move_counter = 0
        self.move_direction = 1
        self.counter = 0
        self.add(enemies)

    def update(self):

        self.rect.x -= self.move_direction
        self.move_counter += 1
        self.counter += 1
        if not self.counter % 10:
            self.image.fill(BLACK)
            self.boltAnim.blit(self.image, (0, 0))

        if abs(self.move_counter) > 20:
            self.move_direction *= -1
            self.rect.y += 4
            self.move_counter = -self.move_counter

        if self.rect.y + self.rect.height > gun.rect.y:
            pygame.quit()

        if bullets and pygame.sprite.collide_rect(self, bullets[0]):
            bullets[0].kill()
            bullets.pop(0)
            for i in range(len(all_aliens)):
                if self in all_aliens[i]:
                    all_aliens[i].pop(all_aliens[i].index(self))
            self.kill()


class Enemy_bullets(pygame.sprite.Sprite):
    """класс создания вражеской пули"""

    def __init__(self, gun):
        if enemy_bullets:
            return
        super().__init__(all_sprites)
        self.image = pygame.Surface((3, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.speed = 650 / FPS
        self.rect.centerx = gun.rect.centerx
        self.rect.top = gun.rect.bottom
        self.y = self.rect.y
        enemy_bullets.append(self)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        if self.rect.y > HEIGHT:
            self.kill()
            enemy_bullets.pop(0)

        if bullets:
            if pygame.sprite.collide_rect(self, bullets[0]):
                self.kill()
                bullets[0].kill()
                bullets.pop(0)
                enemy_bullets.pop(0)


class Octavius(pygame.sprite.Sprite):
    image = load_image("octavius1.png").convert_alpha()
    image = pygame.transform.scale(image, (CELL_SIZE * 1.5, CELL_SIZE * 1.5))

    def __init__(self, coord_x, coord_y):
        super().__init__(all_sprites)
        self.image = Octavius.image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        boltAnim = []
        # анимация разрушения преградыa
        for anim in ANIMATION_MOVE_OCTAVIUS:
            boltAnim.append((anim, 300))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.scale((self.rect.width, self.rect.height))
        self.boltAnim.play()

        self.startY = coord_y
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.move_counter = 0
        self.move_direction = 1
        self.counter = 0
        self.add(enemies)

    def update(self):

        self.rect.x -= self.move_direction
        self.move_counter += 1
        self.counter += 1
        if not self.counter % 10:
            self.image.fill(BLACK)
            self.boltAnim.blit(self.image, (0, 0))

        if abs(self.move_counter) > 20:
            self.move_direction *= -1
            self.rect.y += 4
            self.move_counter = -self.move_counter

        if self.rect.y + self.rect.height > gun.rect.y:
            pygame.quit()

        if bullets and pygame.sprite.collide_rect(self, bullets[0]):
            bullets[0].kill()
            bullets.pop(0)
            for i in range(len(all_aliens)):
                if self in all_aliens[i]:
                    all_aliens[i].pop(all_aliens[i].index(self))
            self.kill()


class Explosion(pygame.sprite.Sprite):
    image = load_image("dead.png").convert_alpha()
    image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))

    def __init__(self, coord_x, coord_y):
        super().__init__(all_sprites)
        self.image = Explosion.image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.y = coord_y
        self.rect.x = coord_x
        self.rect.center = [self.rect.x, self.rect.y]
        self.counter = 0

    def update(self):
        pass


def collide_en_bul_with_obst(en_bul, bars):
    for i in range(len(bars)):
        for j in range(len(bars[i])):
            if pygame.sprite.collide_rect(bars[i][j], en_bul):
                bars[i][j].kill()
                bars[i].pop(j)
                enemy_bullets.pop(0)
                en_bul.kill()
                break


class Block(pygame.sprite.Sprite):
    def __init__(self, size: tuple, x, y):
        super().__init__(all_sprites)
        self.image = pygame.Surface(size)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.image = pygame.transform.scale(self.image, (self.rect.width + 2, self.rect.height + 2))


shape = [
    '  xxxxxxx  ',
    ' xxxxxxxxx ',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxx     xxx',
    'xx       xx']


def death_screen() -> None:
    bg = Surface(SIZE)
    bg.fill(BLACK)
    SCREEN.blit(bg, (0, 0))

    img = load_image('you_died.png')
    img = pygame.transform.scale(img, (300 * 2, 178 * 3))
    img_rect = img.get_rect()
    img_rect.x = (WIDTH - img_rect[2]) / 2
    img_rect.top = HEIGHT * 2 / 6 - img_rect[3] / 2
    SCREEN.blit(img, img_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render('Press <SPACE> to continue', True, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 3 / 4 - intro_rect[3] / 2
    SCREEN.blit(string_rendered, intro_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                main()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


def main():
    global all_aliens, bullets, enemies, all_sprites, bars, entities, all_obstacles, gun, enemy_bullets, octavies
    all_sprites = pygame.sprite.Group()
    bullets = []
    enemy_bullets = []
    enemies = pygame.sprite.Group()
    octavies = pygame.sprite.Group()

    pygame.init()
    pygame.display.set_caption("Space Invaders")
    gun = Gun(SCREEN)
    all_aliens = []
    all_obstacles = []
    bars = []
    width = CELL_SIZE * (4 / 11) / 1.5
    height = width * 2

    img = pygame.transform.scale(load_image('heart.png'), (CELL_SIZE * 1.5, CELL_SIZE * 1.5))
    img.set_colorkey(BLACK)

    for y in range(len(aliens)):
        a = []
        for x in range(len(aliens[0])):
            coord_x = x * CELL_SIZE
            coord_y = y * CELL_SIZE
            if aliens[y][x] == "-":
                pt = Enemy(coord_x, coord_y)
                a.append(pt)
                enemies.add(pt)
            if aliens[y][x] == 'x':
                bar = []
                for i in range(len(shape)):
                    for j in range(len(shape[i])):
                        if shape[i][j] == 'x':
                            b = Block((width, height), coord_x + j * width, coord_y + i * height)
                            bar.append(b)
                bars.append(bar)
            if aliens[y][x] == '@':
                pt1 = Octavius(coord_x, coord_y)
                a.append(pt1)
                enemies.add(pt1)
        all_aliens.append(a)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    gun.right = True
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    gun.left = True
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(gun)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    gun.right = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    gun.left = False

        all_aliens = [i for i in all_aliens if i]

        if not enemy_bullets:
            random_enemies = random.choice(all_aliens[-1])
            Enemy_bullets(random_enemies)

        if enemy_bullets:
            collide_en_bul_with_obst(enemy_bullets[0], bars)
        SCREEN.fill(BLACK)
        all_sprites.update()
        all_sprites.draw(SCREEN)
        for i in range(gun.life):
            SCREEN.blit(img, (i * CELL_SIZE * 1.5, 0))

        tick = clock.tick(FPS)
        pygame.display.flip()


main()
