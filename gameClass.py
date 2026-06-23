import pygame as pg
import random as rand
import sys


gs = 40
WIDTH, HEIGHT = 800, 600

class Star:
    def __init__(self, x, y):
        self.x = []
        self.y = []
        self.star = []
        self.speed =[]
        self.image = pg.image.load("star.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (20, 20))
       
        self.starco([0, 19], [0, 14], 15, x, y)
        for i in range(len(self.x)):
            px = self.x[i] * gs
            py = self.y[i] * gs
            image_rect = self.image.get_rect(topleft=(px, py))
            self.speed.append(rand.randint(100,150))
            self.star.append(image_rect)

    def starco(self, b, c, d, x, y):
        for i in range(d):
            self.x.append(rand.randint(b[0], b[1]))
            self.y.append(rand.randint(c[0], c[1]))
            if self.x[i] == x and self.y[i] == y:
                self.x.pop()
                self.y.pop()
        return [self.x, self.y]

    def Draw(self, window):
        for i in self.star[:]:
            # window.blit(self.image, (i.x, i.y))
            pg.draw.circle(window, (255,255,255), (i.x, i.y),3)

    def update_of_star(self, dt):
        temp = rand.randint(100,150)
        for rect in self.star:
            rect.y += int(temp* dt)
        self.star = [rect for rect in self.star if rect.y <= 610]

        while len(self.star) < 10:
            sy = -20
            sx = rand.randint(0, 19) * gs
            new_rect = self.image.get_rect(topleft=(sx, sy))
            self.star.append(new_rect)


class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = pg.image.load("player.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (60, 60))
        self.imagerect = self.image.get_rect(topleft=(self.x * gs, self.y * gs))
        self.laser = []
        self.laserIm = pg.image.load("laser.png").convert_alpha()
        self.laser_sound = pg.mixer.Sound("laser.wav")
        self.laser_sound.set_volume(0.3)

        self.health = 3
        self.alive = True

    def Draw(self, window):
        for laser in self.laser:
            window.blit(self.laserIm, (laser.x, laser.y))
        if self.alive:
            window.blit(self.image, (self.imagerect.x, self.imagerect.y))

    def move(self, speed, dt):
        keys = pg.key.get_pressed()
        move_x = speed * dt
        # keep x within grid columns 0..19 mapped to pixel positions
        if keys[pg.K_RIGHT] and self.x <= 18:
            self.x += move_x
        if keys[pg.K_LEFT] and self.x  > 0:
            self.x -= move_x

    def shoot(self):
        # called on KEYDOWN event for K_a
        laserX = self.x
        laserY = self.y
        self.laser_sound.play(loops=0)
        rect = self.laserIm.get_rect(topleft=(int(laserX * gs + 26), int(laserY * gs + 5)))
        self.laser.append(rect)

    def updateOf_l(self, dt):
        for laser in self.laser[:]:
            laser.y -= int(250 * dt)
            if laser.y < -10:
                self.laser.remove(laser)

    def update_rect(self):
        # Keep the player's image rect in sync with logical x,y
        self.imagerect.topleft = (int(self.x * gs), int(self.y * gs))


class Meteor:
    def __init__(self):
        self.meteor = []
        self.image = pg.image.load("meteor.png").convert_alpha()
        # self.image = pg.transform.scale(self.image,(100,84))
        self.explo = []
        self.explosion_sound = pg.mixer.Sound("explosion.wav")
        self.explosion_sound.set_volume(0.2)
        self.damage = pg.mixer.Sound("damage.ogg")
        self.damage.set_volume(0.2)

    def meco(self):
        while len(self.meteor) < 5:
            sy = -rand.randint(20, 200)
            sx = rand.randint(0, 19) * gs
            size = rand.randint(40, 90)
            angle = rand.uniform(-30, 30)
            image = pg.transform.rotozoom(self.image, angle, size / 100)
            rect = image.get_rect(topleft=(sx, sy))

            dir_x = rand.choice([-1, 1]) * rand.uniform(0.3, 0.8)
            dir_y = rand.uniform(1.0, 1.8)
            speed = rand.randint(150, 200)
            self.meteor.append({
                "rect": rect,
                "image": image,
                "dir_x": dir_x,
                "dir_y": dir_y,
                "speed": speed,
                "rotation": rand.uniform(-3, 3),
                "angle": angle,
                "ratio": size / 60
            })

    def Drew(self, window):
        for m in self.meteor:
            window.blit(m["image"], m["rect"].topleft)
        for exp in self.explo:
            exp.draw(window)

    def update(self, dt):
        for m in self.meteor:
            m["rect"].x += m["dir_x"] * m["speed"] * dt
            m["rect"].y += m["dir_y"] * m["speed"] * dt
            m["angle"] += m["rotation"] * dt * 10
            # regenerate image at the correct size (ratio preserved)
            m["image"] = pg.transform.rotozoom(self.image, m["angle"], m["ratio"])

        # remove off-screen meteors
        self.meteor = [m for m in self.meteor if m["rect"].y < HEIGHT + 100 and -100 < m["rect"].x < WIDTH + 100]

        # update explosions
        for i in self.explo[:]:
            i.update(dt)
            if not i.active:
                self.explo.remove(i)

        self.meco()

    def collide_with_laser(self, laser_list):
        for meto in self.meteor[:]:
            for l in laser_list[:]:
                if meto["rect"].colliderect(l):
                    center_x, center_y = meto["rect"].center
                    self.explo.append(Explosion(center_x, center_y))
                    self.explosion_sound.play(loops=0)
                    if meto in self.meteor:
                        self.meteor.remove(meto)
                    if l in laser_list:
                        laser_list.remove(l)
                        break

    def collide_with_self(self, dt):
        for i, m in enumerate(self.meteor):
            for j, other in enumerate(self.meteor):
                if i >= j:
                    continue
                if m["rect"].colliderect(other["rect"]):
                    damping = 0.8
                    m["dir_x"], other["dir_x"] = -m["dir_x"] * damping, -other["dir_x"] * damping
                    m["dir_y"], other["dir_y"] = -m["dir_y"] * damping, -other["dir_y"] * damping

                    overlap_x = (m["rect"].centerx - other["rect"].centerx)
                    overlap_y = (m["rect"].centery - other["rect"].centery)
                    separation_factor = 0.05
                    m["rect"].x += overlap_x * separation_factor
                    m["rect"].y += overlap_y * separation_factor
                    other["rect"].x -= overlap_x * separation_factor
                    other["rect"].y -= overlap_y * separation_factor

    def collide_with_player(self, pl):
        for i in self.meteor[:]:
            if i["rect"].colliderect(pl.imagerect) and pl.alive:
                center_x, center_y = i["rect"].center
                self.explo.append(Explosion(center_x, center_y))
                if i in self.meteor:
                    self.meteor.remove(i)
                self.damage.play(loops=0)
                pl.health -= 1
                if pl.health <= 0:
                    pl.alive = False


class Explosion:
    def __init__(self, x, y):
        self.images = []
        # load frames named 0.png .. 20.png or adjust path 
        for i in range(21):
            path = f"expo\{i}.png"
            image = pg.image.load(path).convert_alpha()
            image = pg.transform.scale(image, (60, 60))
            self.images.append(image)

        self.x, self.y = x, y
        self.current = 0
        self.frame_rate = 0.04
        self.timer = 0
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.timer >= self.frame_rate:
            self.timer = 0
            self.current += 1
        if self.current >= len(self.images):
            self.active = False

    def draw(self, window):
        if self.active:
            window.blit(self.images[int(self.current)], (self.x - 30, self.y - 30))