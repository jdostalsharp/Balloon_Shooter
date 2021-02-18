# Author Jeremy Dostal-Sharp
# A simple balloon shooter  game

import pygame
import sys
import os
from time import time

from random import (
    seed,
    randint
)

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    KEYUP,
    QUIT
)

GREY = (128, 128, 128)

# Set RANDOM_CHANCE to whatever ratio is appropriate
# Whatever is set will be a 1 in RANDOM_CHANCE chance of happening every FRAMES
RANDOM_CHANCE = 5
FRAMES = 25

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
balloongroup = pygame.sprite.Group()
seed(time())

def random_start_direction():
    if randint(0, 1):
        return 1
    else:
        return -1

def load_png(name):
    ''' Load image and return image object.
        Taken from pygame.org '''
    fullname = os.path.join('images', name)
    image = pygame.image.load(fullname)
    if image.get_alpha() is None:
        image = image.convert()
    else:
        image = image.convert_alpha()
    return image, image.get_rect()

class Balloon(pygame.sprite.Sprite):
    """ A balloon that will move up and down the left side of the screen
        and be able to be shot
    Returns: Balloon Object
    Functions: move, random_direction, update
    Attributes: area, speed, direction_up, move_count"""
    def __init__(self, vector):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('balloon.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.vector = vector
        self.move_count = 0
        self.rect.midleft = self.area.midleft

    def update(self):
        newpos = self.calcnewpos(self.rect, self.vector)
        self.rect = newpos
        (angle, z) = self.vector

        if not self.area.contains(newpos):
            tl = not self.area.collidepoint(newpos.topleft)
            tr = not self.area.collidepoint(newpos.topright)
            bl = not self.area.collidepoint(newpos.bottomleft)
            br = not self.area.collidepoint(newpos.bottomright)
            if tr and tl or (br and bl):
                angle = -angle

        self.vector = (angle,z)
        self.move_count += 1

    def calcnewpos(self, rect, vector):
        (angle, z) = vector
        if self.move_count >= FRAMES:
            if self.random_direction():
                self.vector = (-angle, z)
            self.move_count = 0
        (dx, dy) = (z * 0, z * angle)
        return rect.move(dx, dy)

    def random_direction(self):
        if randint(0, RANDOM_CHANCE) == 0:
            return True

        
class Player(pygame.sprite.Sprite):
    """ A player that will move up and down at a certain point of the
        screen and be able to shoot one bullet at a time
    Returns: player object
    Functions: move_up, move_down, update
    Attributes: area,.bullet_reloaded, speed"""

    def __init__(self, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('player.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = speed
        self.movepos = [0, 0]
        self.rect.midright = self.area.midright
        self.state = 'still'
        self.bullet_reloaded = True
        self.shots_fired = 0

    def update(self):
        # Change the rect to new position
        newpos = self.rect.move(self.movepos)
        if self.area.contains(newpos):
            self.rect = newpos
        pygame.event.pump()

    def move_up(self):
        # Move the player up
        self.movepos[1] = self.movepos[1] - (self.speed)
        self.state = "moveup"

    def move_down(self):
        # Move the player down
        self.movepos[1] = self.movepos[1] + (self.speed)
        self.state = "movedown"

    def shoot(self):
        # Create a bullet from position of gun
        if self.bullet_reloaded:
            self.shots_fired = self.shots_fired + 1
            # self.bullet_reloaded = False
            bullet = Bullet(self.speed, self.rect.centery, self.rect.left)
            all_sprites.add(bullet) 
            bullets.add(bullet)
            self.bullet_reloaded = False

    def reload(self):
        self.bullet_reloaded = True


class Bullet(pygame.sprite.Sprite):
    """ A Bullet object that can collide with a balloon the bullet moves in the (x) plane only.
    Returns: Bullet object
    Functions: move, update
    Attributes: area, speed"""
    def __init__(self, speed, y, x):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10,10))
        self.image.fill(GREY)
        self.rect = self.image.get_rect()
        self.speed = -(speed * 1.5)
        self.rect.centery = y
        self.rect.right = x

    def update (self):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()


def main():

    # Initialize the screen
    pygame.init()
    size = width, height = 640, 480
    screen = pygame.display.set_mode((size))
    pygame.display.set_caption("Balloon Shooter")

    # Fill Background
    background_colour = (255, 255, 255)
    background = pygame.Surface(screen.get_size())
    background.fill(background_colour)

    # Set the game speed and random generator
    speed = 3
    seed(time())

    # initialize player
    global player
    player = Player(speed)

    # Initilize ball
    balloon = Balloon((random_start_direction(), speed))

    # Initialize Sprites
    #playersprite = pygame.sprite.RenderPlain(player)
    #balloonsprite = pygame.sprite.RenderPlain(balloon)

    # Blit everything onto the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialize clock
    clock = pygame.time.Clock()

    all_sprites.add(player)
    all_sprites.add(balloon)
    balloongroup.add(balloon)

    # Run game loop forever
    while 1:
        # Make sure game does not run at more than 60 frames per second
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    player.move_up()
                if event.key == K_DOWN:
                    player.move_down()
                if event.key == K_SPACE:
                    player.shoot()
            elif event.type == KEYUP:
                if event.key == K_UP or event.key == K_DOWN:
                    player.movepos = [0, 0]
                    player.state = "still"

        screen.blit(background, balloon.rect, balloon.rect)
        screen.blit(background, player.rect, player.rect)

        # Update sprites
        all_sprites.update()

        # Check to see if bullet hits balloon
        hit = pygame.sprite.groupcollide(balloongroup, bullets, True, True)

        if hit:
            return

        if len(bullets) == 0:
            player.reload()

        screen.fill(background_colour)
        all_sprites.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()