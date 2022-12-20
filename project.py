import os
import pygame
import sys

BLACK = pygame.Color("black")
GREEN = pygame.Color("green")
SIZE = WIDTH, HEIGHT = 700, 800
SCREEN = pygame.display.set_mode(SIZE)
FPS = 60
all_sprites = pygame.sprite.Group()


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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, gun):
        super().__init__(all_sprites)
        self.image = pygame.Surface((2, 12))
        self.image.fill(GREEN)
        self.rect = pygame.Rect(0, 0, 2, 12)
        self.speed = 500 / FPS
        self.rect.centerx = gun.rect.centerx
        self.rect.top = gun.rect.top
        self.y = self.rect.y

    def update(self):
        self.y -= self.speed
        self.rect.y = self.y


class Enemy(pygame.sprite.Sprite):
    image = load_image("yellow.png").convert_alpha()

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Enemy.image
        self.rect = self.image.get_rect()
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height


def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((700, 800))
    pygame.display.set_caption("Space Invaders")
    gun = Gun(screen)
    emeny = Enemy()

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

        tick = clock.tick(FPS)
        screen.fill(BLACK)
        all_sprites.update()
        all_sprites.draw(SCREEN)
        pygame.display.flip()

main()
