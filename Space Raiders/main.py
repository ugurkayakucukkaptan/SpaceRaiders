import os
import random
import pygame

pygame.font.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Raiders")

SPACE_SHIP = pygame.image.load(os.path.join("assets", "player_ship.png"))

RED_ALIEN = pygame.image.load(os.path.join("assets", "ship_red_small.png"))
GREEN_ALIEN = pygame.image.load(os.path.join("assets", "ship_green_small.png"))
BLUE_ALIEN = pygame.image.load(os.path.join("assets", "ship_blue_small.png"))


RED_LASER = pygame.image.load(os.path.join("assets", "laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "laser_yellow.png"))


BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.jpg")), (WIDTH, HEIGHT))


class Ship:
    FIRECOOLDOWN = 25

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.lasers = []
        self.ship_img = None
        self.laser_img = None

        self.cool_down_counter = 0
        self.health = health

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_laser(self, velocity, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def cooldown(self):
        if self.cool_down_counter >= self.FIRECOOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=150):
        super().__init__(x, y, health)
        self.ship_img = SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_laser(self, velocity, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (200, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 200, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_ALIEN, RED_LASER),
                "green": (GREEN_ALIEN, GREEN_LASER),
                "blue": (BLUE_ALIEN, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, velocity):
        self.y += velocity

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
class  Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y += velocity

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return overlap(self, obj)



def overlap(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 60)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 8
    enemy_velocity = 1

    player_velocity = 5
    laser_velocity = 5

    player = Player(300, 600)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))

        lives_label = main_font.render(f"Lives: {lives}", 1, (240,240,240))
        level_label = main_font.render(f"Stage: {level}", 1, (240,240,240))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (240,240,240))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "green","blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player.y - player_velocity > 0:
            player.y -= player_velocity

        if keys[pygame.K_DOWN] and player.y + player_velocity + player.get_height() + 15 < HEIGHT:
            player.y += player_velocity

        if keys[pygame.K_LEFT] and player.x - player_velocity > 0:
            player.x -= player_velocity

        if keys[pygame.K_RIGHT] and player.x + player_velocity + player.get_width() < WIDTH:
            player.x += player_velocity

        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_laser(laser_velocity, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if overlap(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_laser(-laser_velocity, enemies)

def start_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:

        title_label = title_font.render("Press the mouse to begin!", 1, (255,255,255))
        WIN.blit(BG, (0, 0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


start_menu()