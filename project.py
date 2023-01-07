import os
import pygame
import sys
import time
import random
import pyganim as pyganim

BLACK = pygame.Color("black")
GREEN = pygame.Color("green")
WHITE = pygame.Color("white")
SIZE = WIDTH, HEIGHT = 800, 800
SCREEN = pygame.display.set_mode(SIZE)
FPS = 60
bullets = []
enemy_bullets = []
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
FILE_DIR = os.path.dirname(__file__)
ANIMATION_DESTROY = [("data\obstacle1.png"), ("data\obstacle2.png"),
                     ("data\obstacle3.png"), ("data\obstacle4.png"),
                     ("data\obstacle5.png"), ("data\obstacle6.png"),
                     ("data\obstacle7.png"), ("data\obstacle8.png")]


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
    def __init__(self, SCREEN):
        super().__init__(all_sprites)
        self.screen = SCREEN
        self.image = load_image("ship.png")
        self.rect = self.image.get_rect()
        self.screen_rect = SCREEN.get_rect()
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom
        self.right = False
        self.left = False

    def update(self, *args):
        if self.right and self.rect.right < self.screen_rect.right:
            self.rect.centerx += 250 / FPS
        if self.left and self.rect.left > self.screen_rect.left:
            self.rect.centerx -= 250 / FPS
        if pygame.sprite.spritecollideany(self, enemies):
            time.sleep(2)
            main()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, gun):
        if bullets:
            return
        super().__init__(all_sprites)
        self.image = pygame.Surface((2, 12))
        self.image.fill(GREEN)
        self.rect = pygame.Rect(0, 0, 2, 12)
        self.speed = 500 / FPS
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
    image = load_image("yellow.png").convert_alpha()
    image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))

    def __init__(self, coord_x, coord_y):
        super().__init__(all_sprites)
        self.image = Enemy.image
        self.rect = self.image.get_rect(topleft=(coord_x, coord_y))
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.vx = 1
        self.add(enemies)

    def update(self):
        self.rect.x += self.vx
        if self.rect.x + self.rect[2] >= WIDTH or self.rect.x <= 0:
            for raw in all_aliens:
                # if self in raw:
                for alien in raw:
                    alien.vx *= -1
                    alien.rect.y += alien.rect[3]

        if bullets and pygame.sprite.collide_rect(self, bullets[0]):
            bullets[0].kill()
            bullets.pop(0)
            for i in all_aliens:
                if self in i:
                    i.pop(i.index(self))
            self.kill()


class Enemy_bullets(pygame.sprite.Sprite):
    def __init__(self, gun):
        if enemy_bullets:
            return
        super().__init__(all_sprites)
        self.image = pygame.Surface((2, 12))
        self.image.fill(GREEN)
        self.rect = pygame.Rect(0, 0, 2, 12)
        self.speed = 500 / FPS
        self.rect.centerx = gun.rect.centerx
        self.rect.top = gun.rect.bottom
        self.y = self.rect.y
        enemy_bullets.append(self)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        if self.rect.y > HEIGHT:
            enemy_bullets.pop(enemy_bullets.index(self))
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    image = load_image("obstacle1.png").convert_alpha()
    image = pygame.transform.scale(image, (CELL_SIZE * 2.75, CELL_SIZE * 2.75))

    def __init__(self, coord_x, coord_y):
        super().__init__(all_sprites)
        self.image = Obstacle.image
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        boltAnim = []
        for anim in ANIMATION_DESTROY:
            boltAnim.append((anim, 100))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.scale((CELL_SIZE * 2.75, CELL_SIZE * 2.75))
        self.boltAnim.play()
        self.rect = self.image.get_rect(topleft=(coord_x, coord_y))
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.add(obstacles)

    def update(self):
        if enemy_bullets:
            i = enemy_bullets[0]
            if pygame.sprite.collide_mask(self, i):
                self.image.fill(BLACK)
                self.boltAnim.blit(self.image, (0, 0))
                i.kill()
                enemy_bullets.pop(0)


def main():
    global all_aliens, bullets, enemies, all_sprites, bars, entities, all_obstacles, gun
    all_sprites = pygame.sprite.Group()
    bullets = []
    enemies = pygame.sprite.Group()
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Space Invaders")
    gun = Gun(SCREEN)

    all_aliens = []
    all_obstacles = []
    bars = []
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
                bar = Obstacle(coord_x, coord_y)
                bars.append(bar)
                obstacles.add(bars)
        all_aliens.append(a)
    all_aliens = [i for i in all_aliens if i]

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

        if not enemy_bullets:
            random_enemies = random.choice(all_aliens[-1])
            Enemy_bullets(random_enemies)
        tick = clock.tick(FPS)
        SCREEN.fill(BLACK)
        all_sprites.update()
        all_sprites.draw(SCREEN)
        pygame.display.flip()


main()
