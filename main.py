import sys
import pygame
import math
from pygame.locals import Color
from pygame.math import Vector2
import numpy as np
class spritesheet(object):
    def __init__(self, filename):
           self.sheet = pygame.image.load(filename).convert()
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


class SpriteStripAnim(object):
    """sprite strip animator

    This class provides an iterator (iter() and next() methods), and a
    __add__() method for joining strips which comes in handy when a
    strip wraps to the next row.
    """

    def __init__(self, filename, rect, count, colorkey=None, loop=False, frames=1,loopframes=None):
        """construct a SpriteStripAnim

        filename, rect, count, and colorkey are the same arguments used
        by spritesheet.load_strip.

        loop is a boolean that, when True, causes the next() method to
        loop. If False, the terminal case raises StopIteration.

        frames is the number of ticks to return the same image before
        the iterator advances to the next image.
        """
        self.filename = filename
        ss = spritesheet(filename)
        self.images = ss.load_strip(rect, count, colorkey)
        self.i = 0
        self.loop = loop
        self.loopframes = loopframes
        self.frames = frames
        self.f = frames
        self.image = None
    def iter(self):
        self.i = 0
        self.f = self.frames
        return self

    def next(self):

        if self.i >= len(self.images):
            if self.loopframes is not None:
                self.i = self.loopframes
            else:
                self.i = 0
        image = self.images[self.i]
        self.f -= 1
        if self.f == 0:
            self.i += 1
            self.f = self.frames
        return image

    def __add__(self, ss):
        self.images.extend(ss.images)
        return self
    def reset(self):
        self.loopframes = None
        return self.next()

def length(x, y):
    return (x ** 2 + y ** 2) ** .5

def norm(x, y):
    _len    = length(x, y)
    return x / _len, y / _len

lol22 = False
class Player(pygame.sprite.Sprite):
    """
    Spawn a player
    """

    def __init__(self):
        self.images = [
            SpriteStripAnim('images/links.gif', (0, 0, 32, 50), 8, 1, True, frames=frames),
            SpriteStripAnim('images/links.gif', (512, 0, 32, 50), 8, 1, False, loopframes=4, frames=frames),
            SpriteStripAnim('images/links.gif', (256, 0, 32, 50), 8, 1, False, loopframes=4, frames=frames)
        ]
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0 # move along X
        self.movey = 0 # move along Y
        self.frame = 0 # count frames
        self.image = self.images[0].next()
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0
        self.last_shot = pygame.time.get_ticks()
    def control(self,x,y):
        """
        control player movement
        """
        self.x = x
        self.y = y
        self.movex += x
        self.movey += y

    def update(self):
            if self.x and self.y <= 0:
                self.image = self.images[0].next()
            self.rect.x = self.rect.x + self.movex
            self.rect.y = self.rect.y + self.movey
            if self.rect.x > 400:
                self.rect.x = 400
            if self.rect.y < 0:
                self.rect.y = 0
            if self.rect.x < 0:
                self.rect.x = 0
            # moving left
            if self.movex < 0:
                self.frame += 1
                self.image = pygame.transform.flip(self.images[1].next(),True, False)

            # moving right
            if self.movex > 0:
                self.frame += 1
                self.image = pygame.transform.flip(self.images[2].next(), True, False)
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/YuukaKazamiBoss.png")
        self.rect = self.image.get_rect()
        self.counter = 0
    def update(self):
        '''
        enemy movement
        '''
        distance = 300
        speed = 1.25
        if self.counter >= 0 and self.counter <= distance:
            self.rect.x += speed
        elif self.counter >= distance and self.counter <= distance*2:
            self.rect.x -= speed
        else:
            self.counter = 0

        self.counter += 1

class SuperBullet(pygame.sprite.Sprite):


    def __init__(self,playerx=0,playery=0,spin=0,gotoPlayer=False):
        self.gotoplayer = gotoPlayer
        pygame.sprite.Sprite.__init__(self,)
        self.spin = spin
        self.image = pygame.image.load("images/bullet.png")
        self.image.set_colorkey((120,120,120))
        self.rect = self.image.get_rect()
        self.rect.center = (0,0)
        self.angle = 120
        self.counter = 0
        self.rect.x = playerx
        self.rect.y = playery
        self.pos = Vector2(self.rect.center)
        self.spin1 = 0

    def update(self):
        if lol22 is False:
            self.velocity = Vector2(0.25, 0).rotate(self.spin*100-90) * 5
            self.pos += self.velocity
            self.rect.center = self.pos
            if (self.rect.right > 400 or self.rect.left < 0
                    or self.rect.bottom > 600 or self.rect.top < 0):
                self.kill()

        else:
                (dx, dy) = ((player.rect.x - self.rect.x) / math.sqrt(
                    (player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2),
                            (player.rect.y - self.rect.y) / math.sqrt(
                                (player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2))
                self.rect.x = self.rect.x + dx * 3
                self.rect.y = self.rect.y + dy * 3
                collide = self.rect.collidepoint((player.rect.x,player.rect.y))
                if collide:
                    self.kill()



class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self,x,time=1):
        pygame.sprite.Sprite.__init__(self,)
        self.image = pygame.Surface((20, 600))
        self.image.fill((0,22,122))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.time = time
        self.counter = 0
    def update(self):
        self.counter += 1
        if self.counter >= 300:
            self.kill()
            self.counter = 0


surface = pygame.display.set_mode((800,600))
FPS = 120
frames = FPS / 12
all_sprites_list = pygame.sprite.Group()

# List of each block in the game
block_list = pygame.sprite.Group()

# List of each bullet
bullet_list = pygame.sprite.Group()
player = Player()
player.rect.x = 2  # go to x
player.rect.y = 2  # go to y
player_list = pygame.sprite.Group()
boss_list = pygame.sprite.Group()
player_list.add(player)
steps = 1
yuukakazami = Boss()
black = Color('black')
clock = pygame.time.Clock()
image = SpriteStripAnim('images/links.gif', (0, 0, 32, 50), 8, 1, True, frames=frames)
bulletcounter = 0
dt = 0
shootTime = 0
shootTime1 = 0
pygame.mixer.init()
pygame.mixer.music.load('yuuka.wav')
pygame.mixer.music.play(-1)
shooting = 0
n = 0
omegapower = 1
firerate = 10
while True:
    pygame.sprite.spritecollide(Boss(), bullet_list, True)
    shootTime1 +=1
    if shootTime1 >= 22:
        #bullet_list.add(SuperBullet(playerx=yuukakazami.rect[0],playery=yuukakazami.rect[1], spin=180))
        shootTime1 = 0
    if pygame.time.get_ticks() in range(2000,2010):
        print("lol")
        boss_list.add(yuukakazami)
    if bullet_list.sprites() == []:
        lol22 = False


    current_time = pygame.time.get_ticks()
    shootTime += 1
    dt += clock.tick(120) / 1000
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == ord('z'):
                lol22 = False
                bullet_list.remove(SuperBullet())
                shooting = 1
            if event.key == ord('x'):
               lol22 = True
               bullet_list.add(EnemyLaser(x=player.rect.x, time=1))
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(-steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(steps, 0)
            if event.key == pygame.K_UP or event.key == ord('w'):
                player.control(0, -steps)
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                player.control(0, steps)

        if event.type == pygame.KEYUP:

            if event.key == ord('z'):
                shooting = 0
                n = 0
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(-steps, 0)
            if event.key == pygame.K_UP or event.key == ord('w'):
                player.control(0, steps)
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                player.control(0, -steps)


            if event.key == ord('q'):
                pygame.quit()
                sys.exit()
    shootTime += 1
    if omegapower == 1:
        firerate = 5
    else:
        firerate = 20
    if shootTime >= firerate and shooting == 1:
        n += 1
        if n == 40:
            n = 0
        Fs = 8000
        f = 200
        f1 = 200
        sample = 1000
        x = np.arange(sample)
        y = np.sin(2 * np.pi * f * x / Fs)
        y1 = -np.sin(2 * np.pi * f1 * x / Fs)
        y2 = -np.sin(2 * np.pi * f1-200 * x / Fs)
        # Fire a bullet if the user clicks the mouse button
        # Set the bullet so it is where the player is
        # Add the bullet to the listsd
        bullet_list.add(SuperBullet(player.rect.x,player.rect.y,spin=y1[n]))
        bullet_list.add(SuperBullet(player.rect.x, player.rect.y, 0))


        if omegapower == 1:
            bullet_list.add(SuperBullet(player.rect.x,player.rect.y,spin=y[n]))
            bullet_list.add(SuperBullet(player.rect.x, player.rect.y, spin=y2[n]))
            bullet_list.add(SuperBullet(player.rect.x, player.rect.y, spin=-y2[n]))
        shootTime = 0
    for bullet in bullet_list:


        # Remove the bullet if it flies up off the screen
        if bullet.rect.y < -10:
            bullet_list.remove(bullet)
            all_sprites_list.remove(bullet)
    surface.fill(black)
    player.update()
    bullet_list.update()
    player_list.draw(surface)
    boss_list.update()
    boss_list.draw(surface)

    bullet_list.draw(surface)
    pygame.display.flip()
