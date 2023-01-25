import os
import sqlite3
from pygame import *
import pygame
import sys
import time
import random
import pyganim as pyganim
import pygame_menu

pygame.init()
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()
BLACK = pygame.Color("black")
GREEN = pygame.Color("green")
WHITE = pygame.Color("white")
YELLOW = pygame.Color("yellow")
SIZE = WIDTH, HEIGHT = 700, 900
SCREEN = pygame.display.set_mode(SIZE)
FPS = 60
level_num = 1
user_name = 'Unnamed'
level = []
all_score = 0
bullets = []
enemy_bullets = []
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
FILE_DIR = os.path.dirname(__file__)
ANIMATION_MOVE_ENEMIES = [("data/enemies1.png"), ("data/enemies2.png")]
ANIMATION_MOVE_OCTAVIUS = [("data/octavius1.png"), ("data/octavius2.png")]


def sound_load(sound_path: str = 'sounds') -> dict:
    """Загружает словарь звуков"""
    sound_files = [f for f in os.listdir(sound_path) if os.path.isfile(os.path.join(sound_path, f))]
    return {file_name.split('.')[0]: pygame.mixer.Sound(os.path.join(sound_path, file_name)) for
            file_name in
            sound_files}


# чтоб не мучатся с пробросом звуков делаем глобально
sounds = sound_load()


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
    global all_score
    levelFile = open(f'%s/data/{level_num}.txt' % FILE_DIR)
    line = " "
    aliens = []
    all_score = 0
    while line[0] != "/":  # пока не нашли символ завершения файла
        line = levelFile.readline()  # считываем построчно
        if line and line[0] == "[":  # если нашли символ начала уровня
            while line[0] != "]":  # то, пока не нашли символ конца уровня
                line = levelFile.readline()  # считываем построчно уровень
                if line[0] != "]":  # и если нет символа конца уровня
                    aliens.append(line)  # и добавляем в уровень строку от начала до символа "|"
    return aliens


aliens = loadLevel(1)
CELL_SIZE = WIDTH // (len(aliens[0]))


class Gun(pygame.sprite.Sprite):
    image = load_image("ship.png")
    image = pygame.transform.scale(image, (CELL_SIZE * 2.25, CELL_SIZE * 2.25))

    def __init__(self, SCREEN):
        super().__init__(all_sprites)
        self.SCREEN = SCREEN
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
        sounds['laser'].play()
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

    def __init__(self, coord_x, coord_y, v, vy):
        super().__init__(all_sprites)
        self.image = Enemy.image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        boltAnim = []
        # анимация передвижения
        for anim in ANIMATION_MOVE_ENEMIES:
            boltAnim.append((anim, 300))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.scale((self.rect.width, self.rect.height))
        self.boltAnim.play()

        self.startY = coord_y
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.move_counter = 0
        self.move_direction = v
        self.move_down = vy
        self.add(enemies)

    def update(self):
        global all_score
        self.move_counter += 1
        self.rect.x += self.move_direction
        if self.rect.x + self.rect[2] > WIDTH or self.rect.x < 0:
            for alien in enemies.sprites():
                alien.rect.y += self.move_down
                alien.move_direction *= -1

        for i in range(len(all_aliens)):
            for j in range(len(all_aliens[i]) - 1):
                if not isinstance(all_aliens[i][j], str):
                    c = 1
                    while j + c < len(all_aliens):
                        if all_aliens[i][j + c] == ' ':
                            c += 1
                        if all_aliens[i][j + c] != ' ':
                            break
                    if not isinstance(all_aliens[i][j + c], str) and all_aliens[i][j].rect.x + CELL_SIZE * 2 * c < \
                            all_aliens[i][j + c].rect.x:
                        all_aliens[i][j].rect.x = all_aliens[i][j + c].rect.x - 2 * CELL_SIZE * c

        if not self.move_counter % 20:
            self.image.fill(BLACK)
            self.boltAnim.blit(self.image, (0, 0))

        if self.rect.y + self.rect.height > gun.rect.y:
            death_screen()

        if bullets and pygame.sprite.collide_rect(self, bullets[0]):
            bullets[0].kill()
            bullets.pop(0)
            for i in range(len(all_aliens)):
                if self in all_aliens[i]:
                    all_aliens[i][all_aliens[i].index(self)] = ' '
            self.kill()
            sounds['death_alien'].play()
            all_score += 10


class Enemy_bullets(pygame.sprite.Sprite):
    """
    класс создания вражеской пули
    """

    def __init__(self, gun):
        if enemy_bullets:
            return
        sounds['laser_enemy'].play()
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

    def __init__(self, coord_x, coord_y, v, vy):
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
        self.move_direction = v
        self.move_down = vy
        self.counter = 0
        self.add(enemies)

    def update(self):
        global all_score
        self.move_counter += 1
        self.rect.x += self.move_direction

        for i in range(len(all_aliens)):
            for j in range(len(all_aliens[i]) - 1):
                if not isinstance(all_aliens[i][j], str):
                    c = 1
                    while j + c < len(all_aliens):
                        if all_aliens[i][j + c] == ' ':
                            c += 1
                        if all_aliens[i][j + c] != ' ':
                            break
                    if not isinstance(all_aliens[i][j + c], str) and all_aliens[i][j].rect.x + CELL_SIZE * 2 * c < \
                            all_aliens[i][j + c].rect.x:
                        all_aliens[i][j].rect.x = all_aliens[i][j + c].rect.x - 2 * CELL_SIZE * c

        if not self.move_counter % 20:
            self.image.fill(BLACK)
            self.boltAnim.blit(self.image, (0, 0))

        if self.rect.y + self.rect.height > gun.rect.y:
            death_screen()

        if bullets and pygame.sprite.collide_rect(self, bullets[0]):
            bullets[0].kill()
            bullets.pop(0)
            for i in range(len(all_aliens)):
                if self in all_aliens[i]:
                    all_aliens[i][all_aliens[i].index(self)] = ' '
            self.kill()
            sounds['death_alien'].play()
            all_score += 10


def collide_en_bul_with_obst(en_bul, bars):
    for i in range(len(bars)):
        for j in range(len(bars[i])):
            if pygame.sprite.collide_rect(bars[i][j], en_bul):
                bars[i][j].kill()
                bars[i].pop(j)
                enemy_bullets.pop(0)
                en_bul.kill()
                break

            if pygame.sprite.spritecollideany(bars[i][j], enemies):
                bars[i][j].kill()
                bars[i].pop(j)
                break


def collide_bul_with_obst(bul, bars):
    for i in range(len(bars)):
        for j in range(len(bars[i])):
            if pygame.sprite.collide_rect(bars[i][j], bul):
                bars[i][j].kill()
                bars[i].pop(j)
                bullets.pop(0)
                bul.kill()
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


def score_w(all_score):
    font = pygame.font.Font(None, 30)
    string_rendered = font.render('score ' + str(all_score), True, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2])
    intro_rect.top = 0
    SCREEN.blit(string_rendered, intro_rect)


def change_name(value: str) -> None:
    """
    Меняем глобальное имя пользователя, опять же чтоб не мучаться с пробром имени между меню и игрой.
    """
    global user_name
    user_name = value


def menu_start() -> None:
    """
    стартовое меню игры
    """

    ABOUT = ['pygame project от ученика Яндекс Лицея',
             'Author: Andrei Borisov', ]

    HELP = ['Управление кнопками <A>, <D> и <SPACE>.']

    # menu ABOUT
    about_theme = pygame_menu.themes.THEME_DARK.copy()
    about_theme.widget_margin = (0, 0)
    about_menu = pygame_menu.Menu(
        height=HEIGHT * 0.6,
        theme=about_theme,
        title='About',
        width=WIDTH * 0.6,
        mouse_enabled=True
    )

    for m in ABOUT:
        about_menu.add.label(m, align=pygame_menu.locals.ALIGN_CENTER, font_size=20)
    about_menu.add.vertical_margin(30)
    about_menu.add.button('Return to menu', pygame_menu.events.BACK)

    # menu HELP
    help_theme = pygame_menu.themes.THEME_DARK.copy()
    help_theme.widget_margin = (0, 0)
    help_menu = pygame_menu.Menu(
        height=HEIGHT * 0.9,
        theme=help_theme,
        title='Help',
        width=WIDTH * 0.7,
        mouse_enabled=True
    )
    for m in HELP:
        help_menu.add.label(m, margin=(30, 0), align=pygame_menu.locals.ALIGN_LEFT, font_size=20)
    help_menu.add.vertical_margin(30)
    help_menu.add.button('Return to menu', pygame_menu.events.BACK)

    # menu SCORES
    scores_theme = pygame_menu.themes.THEME_DARK
    scores_theme.widget_margin = (0, 0)
    scores_menu = pygame_menu.Menu(
        height=HEIGHT * 0.9,
        theme=scores_theme,
        title='High scores',
        width=WIDTH * 0.7,
        mouse_enabled=True
    )
    c = 0
    for n, s in get_results():
        if c == 10:
            break
        scores_menu.add.label(f'{n} --------- {s * 100}')
        c += 0
    scores_menu.add.vertical_margin(30)
    scores_menu.add.button('Return to menu', pygame_menu.events.BACK)

    # main MENU
    menu = pygame_menu.Menu(height=HEIGHT,
                            width=WIDTH,
                            title='SPACE INVADERS',
                            theme=pygame_menu.themes.THEME_DARK,
                            mouse_enabled=True
                            )

    # img = os.path.join('data/img', 'logo.png')
    # menu.add.image(img, scale=(0.6, 0.6), scale_smooth=True)

    menu.add.button('Play', menu_level)
    menu.add.text_input('Name: ', default=user_name, onchange=change_name)
    menu.add.button('High scores', scores_menu)
    menu.add.button('Help', help_menu)
    menu.add.button('About', about_menu)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(SCREEN)


def menu_level() -> None:
    """
    menu Levels/Play
    """
    update_name(user_name)

    level_theme = pygame_menu.themes.THEME_DARK.copy()
    level_theme.widget_margin = (0, 0)
    level_menu = pygame_menu.Menu(height=HEIGHT,
                                  width=WIDTH,
                                  title='LEVELS',
                                  theme=level_theme,
                                  mouse_enabled=True
                                  )

    levels = get_levels(user_name)[0]
    for i in range(1, levels + 1):
        level_menu.add.button(f'Level {i}', main, i)
    # if get_all_score(user_name)[0] >= 18:
    #     level_menu.add.button(f'Boss Level', boss_level)
    level_menu.add.vertical_margin(30)
    level_menu.add.button('Return to menu', menu_start)
    level_menu.mainloop(SCREEN)


def get_levels(user_name: str) -> tuple:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT open_levels FROM results
                        WHERE name = '{user_name}'""").fetchone()

    con.close()

    return result


def get_all_score(user_name: str) -> tuple:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT all_score FROM results
                            WHERE name = '{user_name}'""").fetchone()

    con.close()

    return result


def update_name(user_name: str) -> None:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT * FROM results
                            WHERE name = '{user_name}'""").fetchone()
    if not result:
        cur.execute(f"""INSERT INTO
                        results(name, open_levels, all_score, level1, level2, level3, level4, boss_level)
                        VALUES('{user_name}', 1, 0, 0, 0, 0, 0, 0)""")

    con.commit()
    con.close()


def update_bd(user_name: str, level_num: str, all_score: int) -> None:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    # if level_num == '5':
    #     cur.execute(f"""UPDATE results
    #                     SET boss_level = 1
    #                     WHERE name = '{user_name}'""")
    #
    #     result = cur.execute(f"""SELECT * FROM results
    #                                 WHERE name = '{user_name}'""").fetchone()
    #
    #     cur.execute(f"""UPDATE results
    #                     SET all_score = {sum(list(result[4:]))}
    #                     WHERE name = '{user_name}'""")
    #
    #     con.commit()
    #     con.close()
    #
    #     return

    result = cur.execute(f"""SELECT level{level_num} FROM results
                                WHERE name = '{user_name}'""").fetchone()

    if result[0] < all_score:
        cs = all_score
    else:
        cs = result[0]

    cur.execute(f"""UPDATE results
                SET level{level_num} = {cs}
                WHERE name = '{user_name}'""")

    if get_levels(user_name)[0] == int(level_num) and int(level_num) < all_aliens - 1:
        ln = int(level_num) + 1
    else:
        ln = get_levels(user_name)[0]

    cur.execute(f"""UPDATE results
                    SET open_levels = {ln}
                    WHERE name = '{user_name}'""")

    result = cur.execute(f"""SELECT * FROM results
                            WHERE name = '{user_name}'""").fetchone()

    cur.execute(f"""UPDATE results
                SET all_score = {sum(list(result[4:]))}
                WHERE name = '{user_name}'""")

    con.commit()
    con.close()


def get_results() -> list:
    con = sqlite3.connect('data/results.sqlite')
    cur = con.cursor()

    result = cur.execute(f"""SELECT name, all_score FROM results""").fetchall()

    result.sort(key=lambda x: x[1], reverse=True)

    con.close()

    return result[:10]


def start_screen() -> None:
    fon = Surface(SIZE)
    fon.fill(BLACK)
    SCREEN.blit(fon, (0, 0))

    img = load_image('logo.png')
    img_rect = img.get_rect()
    img_rect.x = (WIDTH - img_rect[2]) / 2
    img_rect.top = HEIGHT * 2 / 6 - img_rect[3] / 2
    SCREEN.blit(img, img_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render('Press any button to start', True, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 3 / 4 - intro_rect[3] / 2
    SCREEN.blit(string_rendered, intro_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                menu_start()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


def result_screen() -> None:
    global level_num

    sounds['win'].play()

    bg = Surface(SIZE)
    bg.fill(BLACK)
    SCREEN.blit(bg, (0, 0))

    img = load_image('win.png')
    img = pygame.transform.scale(img, (150, 150))
    img_rect = img.get_rect()
    img_rect.x = (WIDTH - img_rect[2]) / 2
    img_rect.top = HEIGHT * 2 / 6 - img_rect[3] / 2
    SCREEN.blit(img, img_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render(f'Level {level_num}', True, WHITE)
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 0.15 - intro_rect[3] / 2
    SCREEN.blit(string_rendered, intro_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render(f'all_score {all_score}', True, WHITE)
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 1 / 2 - intro_rect[3] / 2
    SCREEN.blit(string_rendered, intro_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render('Press <SPACE> to continue', True, WHITE)
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 0.8 - intro_rect[3] / 2
    SCREEN.blit(string_rendered, intro_rect)

    font = pygame.font.Font(None, 30)
    string_rendered = font.render('Press <M> to menu', True, WHITE)
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 0.9 - intro_rect[3] / 2
    SCREEN.blit(string_rendered, intro_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == K_SPACE:
                if level_num != '4' and level_num != '5':
                    sounds['win'].stop()
                    level_num = str(int(level_num) + 1)
                    main(level_num)
            if event.type == pygame.KEYDOWN and event.key == K_m:
                sounds['win'].stop()
                menu_level()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


def death_screen() -> None:
    sounds['lose'].play()

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
    string_rendered = font.render('all_score ' + str(all_score), True, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = (WIDTH - intro_rect[2]) / 2
    intro_rect.top = HEIGHT * 2 / 4 - intro_rect[3] / 2
    SCREEN.blit(string_rendered, intro_rect)

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
                main(level_num)

        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


def main(level_num):
    global all_aliens, bullets, enemies, all_sprites, bars, entities, all_obstacles, gun, enemy_bullets, octavies, all_score, CELL_SIZE
    all_sprites = pygame.sprite.Group()
    bullets = []
    enemy_bullets = []
    enemies = pygame.sprite.Group()
    octavies = pygame.sprite.Group()
    aliens = loadLevel(level_num)
    CELL_SIZE = WIDTH // (len(aliens[0]))
    all_score = 0

    gun = Gun(SCREEN)
    all_aliens = []
    all_obstacles = []
    bars = []
    width = CELL_SIZE * (4 / 11) / 1.5
    height = width * 2

    img = pygame.transform.scale(load_image('heart.png'), (CELL_SIZE * 1.5, CELL_SIZE * 1.5))
    img.set_colorkey(BLACK)

    v = 0
    vy = 0

    if level_num == 1:
        v = 1
        vy = 3.5
    if level_num == 2:
        v = 1
        vy = 4.5

    if level_num == 3:
        v = 1
        vy = 5.5

    if level_num == 4:
        v = 1
        vy = 6.5

    if level_num == 5:
        v = 1
        vy = 10.5

    for y in range(len(aliens)):
        a = []
        for x in range(len(aliens[0])):
            coord_x = x * CELL_SIZE
            coord_y = y * CELL_SIZE
            if aliens[y][x] == "-":
                pt = Enemy(coord_x, coord_y, v, vy)
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
                pt1 = Octavius(coord_x, coord_y, v, vy)
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

        all_aliens = [i for i in all_aliens if i and i != [' '] * len(i)]

        if not all_aliens:
            result_screen()

        if not enemy_bullets:
            random_enemies = random.choice(all_aliens[-1])
            while isinstance(random_enemies, str):
                random_enemies = random.choice(all_aliens[-1])
            Enemy_bullets(random_enemies)

        if enemy_bullets:
            collide_en_bul_with_obst(enemy_bullets[0], bars)
        if bullets:
            collide_bul_with_obst(bullets[0], bars)
        SCREEN.fill(BLACK)
        score_w(all_score)
        all_sprites.update()
        all_sprites.draw(SCREEN)
        for i in range(gun.life):
            SCREEN.blit(img, (i * CELL_SIZE * 1.5, 0))

        tick = clock.tick(FPS)
        pygame.display.flip()


menu_start()
