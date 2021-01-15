import pygame
import os
import sys


def load_image(name):
    fullname = os.path.join('data/' + name)
    image = pygame.image.load(fullname)
    return image


pygame.init()
screen_size = (500, 650)
screen = pygame.display.set_mode(screen_size)
FPS = 50

tile_images = {
    'empty': load_image('grass.png'),
    'river': load_image('river.png'),
    'coast1': load_image('coast1.png'),
    'coast2': load_image('coast2.png')
}

tile_width = tile_height = 50


class ScreenFrame(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.rect = (0, 0, 500, 500)


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class River(Tile):
    def __init__(self, pos_x, pos_y):
        super().__init__('river', pos_x, pos_y)
        self.frames = [load_image('river.png'), load_image('river2.png'),
                       load_image('river3.png'), load_image('river4.png')]
        self.cur_frame = 0
        self.k = 0

    def update(self):
        self.k += 1
        if self.k == 20:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.k = 0


roads = [[None for j in range(10)] for i in range(10)]


class Road(Sprite):
    def __init__(self, color, pos_x, pos_y):
        super().__init__(sprite_group)
        self.color = color
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.update()
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self):
        fn = ''
        if self.pos_y < 9:
            if roads[self.pos_y + 1][self.pos_x]:
                fn += 'S'
        if self.pos_x > 0:
            if roads[self.pos_y][self.pos_x - 1]:
                fn += 'W'
        if self.pos_y > 0:
            if roads[self.pos_y - 1][self.pos_x]:
                fn += 'N'
        if self.pos_x < 9:
            if roads[self.pos_y][self.pos_x + 1]:
                fn += 'E'
        self.image = load_image('roads/' + self.color + '/' + fn + '.png')


class PlayerCursor(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = load_image('cur3.png')
        self.cur_frame = 0
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.frames = [load_image('cur3.png'), load_image('cur2.png'), load_image('cur.png'),
                       load_image('cur.png'), load_image('cur.png'), load_image('cur2.png')]
        self.pos = (pos_x, pos_y)
        self.k = 0

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect().move(
            tile_width * self.pos[0], tile_height * self.pos[1])

    def update(self):
        self.k += 1
        if self.k == 10:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.k = 0


class Castle(Sprite):
    def __init__(self, color, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = load_image(color + 'town3.png')
        self.cur_frame = 0
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.frames = [load_image(color + 'town3.png'), load_image(color + 'town2.png'),
                       load_image(color + 'town.png'),
                       load_image(color + 'town.png'), load_image(color + 'town.png'),
                       load_image(color + 'town2.png')]
        self.pos = (pos_x, pos_y)
        self.k = 0

    def update(self):
        self.k += 1
        if self.k == 7:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.k = 0


player = None
clock = pygame.time.Clock()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()


def terminate():
    pygame.quit()
    sys.exit


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
    screen.blit(fon, (0, 0))

    new_game_button = load_image('newGameBtn.png')
    new_game_button_rect = new_game_button.get_rect(bottomleft=(19, 424))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if new_game_button_rect.collidepoint(pygame.mouse.get_pos()):
                    return
        screen.blit(new_game_button, new_game_button_rect)
        pygame.display.flip()
        clock.tick(FPS)


def load_level():
    level_name = 'map.txt'
    filename = level_name
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def blue_generation():
    new_cursor = PlayerCursor(0, 9)
    return new_cursor


def red_generation():
    new_cursor = PlayerCursor(9, 0)
    return new_cursor


def base_generation(level):
    level = level[0]
    new_castle, new_castle2, x, y = None, None, None, None
    river_tiles = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if y == x:
                river_tiles.append(River(x, y))
            elif y == x + 1:
                Tile('coast2', x, y)
            elif y == x - 1:
                Tile('coast1', x, y)
            elif y == 9 and x == 0:
                Tile('empty', x, y)
                new_castle = Castle('blue', x, y)
            elif y == 0 and x == 9:
                Tile('empty', x, y)
                new_castle2 = Castle('red', x, y)
            else:
                Tile('empty', x, y)
    return new_castle, new_castle2, river_tiles, x, y


def move(cursor, movement):
    x, y = cursor.pos
    if movement == "up":
        if y > 0 and level_map[0][y - 1][x] == ".":
            cursor.move(x, y - 1)
    elif movement == "down":
        if y < max_y and level_map[0][y + 1][x] == ".":
            cursor.move(x, y + 1)
    elif movement == "left":
        if x > 0 and level_map[0][y][x - 1] == ".":
            cursor.move(x - 1, y)
    elif movement == "right":
        if x < max_x and level_map[0][y][x + 1] == ".":
            cursor.move(x + 1, y)


def road_build(x, y):
    global roads
    roads[y][x] = Road(turns[1], x, y)
    for i in roads:
        for j in i:
            if j:
                j.update()


def build():
    road_button = load_image('buildingsBtns/road.png')
    road_button_rect = road_button.get_rect(bottomleft=(20, 590))
    arable_button = load_image('buildingsBtns/arable.png')
    arable_button_rect = arable_button.get_rect(bottomleft=(100, 590))
    manor_button = load_image('buildingsBtns/manor.png')
    manor_button_rect = manor_button.get_rect(bottomleft=(180, 590))
    castle_button = load_image('buildingsBtns/castle.png')
    castle_button_rect = castle_button.get_rect(bottomleft=(260, 590))
    church_button = load_image('buildingsBtns/church.png')
    church_button_rect = church_button.get_rect(bottomleft=(340, 590))
    fishing_grounds_button = load_image('buildingsBtns/fishing_grounds.png')
    fishing_grounds_button_rect = fishing_grounds_button.get_rect(bottomleft=(420, 590))
    back_button = load_image('backBtn.png')
    back_button_rect = back_button.get_rect(bottomleft=(20, 640))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move(cursor, "up")
                elif event.key == pygame.K_DOWN:
                    move(cursor, "down")
                elif event.key == pygame.K_LEFT:
                    move(cursor, "left")
                elif event.key == pygame.K_RIGHT:
                    move(cursor, "right")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if road_button_rect.collidepoint(pygame.mouse.get_pos()):
                    road_build(cursor.pos[0], cursor.pos[1])
                if back_button_rect.collidepoint(pygame.mouse.get_pos()):
                    running = False

        screen.fill(pygame.Color("black"))
        sprite_group.draw(screen)
        hero_group.draw(screen)
        for i in river_tiles:
            i.update()
        cursor.update()
        castle.update()
        castle2.update()
        screen.blit(panel, panel.get_rect(bottomright=(500, 650)))
        screen.blit(road_button, road_button_rect)
        screen.blit(arable_button, arable_button_rect)
        screen.blit(manor_button, manor_button_rect)
        screen.blit(castle_button, castle_button_rect)
        screen.blit(church_button, church_button_rect)
        screen.blit(fishing_grounds_button, fishing_grounds_button_rect)
        screen.blit(back_button, back_button_rect)
        clock.tick(FPS)
        pygame.display.flip()


start_screen()

level_map = [[[i for i in '..........']] * 10]
castle, castle2, river_tiles, max_x, max_y = base_generation(level_map)
cursor = blue_generation()
panel = load_image('panel.png')
end_turn_button = load_image('endTurnBtn.png')
end_turn_button_rect = end_turn_button.get_rect(bottomright=(480, 620))
build_button = load_image('buildBtn.png')
build_button_rect = build_button.get_rect(bottomright=(170, 620))
turns = ['red', 'blue']

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move(cursor, "up")
            elif event.key == pygame.K_DOWN:
                move(cursor, "down")
            elif event.key == pygame.K_LEFT:
                move(cursor, "left")
            elif event.key == pygame.K_RIGHT:
                move(cursor, "right")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if end_turn_button_rect.collidepoint(pygame.mouse.get_pos()):
                cursor.kill()
                cursor = red_generation() if turns[0] == 'red' else blue_generation()
                turns = turns[::-1]
            if build_button_rect.collidepoint((pygame.mouse.get_pos())):
                build()

    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    hero_group.draw(screen)
    for i in river_tiles:
        i.update()
    cursor.update()
    castle.update()
    castle2.update()
    screen.blit(panel, panel.get_rect(bottomright=(500, 650)))
    screen.blit(end_turn_button, end_turn_button_rect)
    screen.blit(build_button, build_button_rect)
    clock.tick(FPS)
    pygame.display.flip()
