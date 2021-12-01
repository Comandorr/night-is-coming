from pygamezavr import*
import pygamezavr as pz
from texts import*


class Player(SimpleSprite):
    def __init__(self, img, pos):
        super().__init__(img, pos)
        self.speed = 5
        self.armed = False
        self.recoil = 0
        self.weapon = None
        self.look = 1
        self.look_y = 1
        self.side = 1
        self.hp = 100
        self.idle = Animation(player_idle_img, 30)
        self.run = Animation(player_run_img, 6)
        self.ammo = {
            'type-0': 0,
            'type-1': 10,
            'type-2': 10
        }
        self.weapons = [knife]

    def up(self):
        self.look_y = -1
        self.y += self.speed * self.look_y
    def down(self):
        self.look_y = 1
        self.y += self.speed * self.look_y
    def left(self):
        self.x -= self.speed
        if self.side == 1:
            self.image = transform.flip(self.image,  True, False)
            if self.armed:
                self.weapon.image = transform.flip(self.weapon.image,  True, False)
                self.weapon.side = self.weapon.look = -1
        self.look = self.side = -1
    def right(self):
        self.x += self.speed
        if self.side == -1:
            self.image = transform.flip(self.image,  True, False)
            if self.armed:
                self.weapon.image = transform.flip(self.weapon.image,  True, False)
                self.weapon.side = self.weapon.look = 1
        self.look = self.side = 1

    def control(self):
        if sprite.spritecollide(self, walls, False) or sprite.spritecollide(self, crates, False):
            self.x += self.speed * -self.look
            self.y += self.speed * -self.look_y
        keys = key.get_pressed()
        if keys[K_d] or keys[K_a] or keys[K_w] or keys[K_s]:
            self.look = 0
            if keys[K_d]:
                self.right()
            elif keys[K_a]:
                self.left()
            self.look_y = 0
            if keys[K_w]:
                self.up()
            elif keys[K_s]:
                self.down()
            self.run.update()
            self.image = self.run.animate()
        else:
            self.idle.update()
            self.image = self.idle.animate()
        if self.side == -1:
            self.image = transform.flip(self.image, True, False)
        if keys[K_1] and knife in self.weapons:
            self.take(knife)
        if keys[K_2] and pistol in self.weapons:
            self.take(pistol)
        if keys[K_3] and smg in self.weapons:
            self.take(smg)
        if keys[K_4] and rifle in self.weapons:
            self.take(rifle)

    def update(self):
        self.control()
        if self.armed:
            if self.side == -1:
                self.weapon.replace(self.rect.left - self.weapon.rect.width/2, self.rect.centery - 5)
            elif self.side == 1:
                self.weapon.replace(self.rect.right - self.weapon.rect.width/2 , self.rect.centery - 5)
            self.weapon.look = self.side
            self.weapon.shoot()
        if self.image.get_alpha() != 255:
            self.image.set_alpha(255)
        for i in sprite.spritecollide(self, bullets, True):
            self.hp -= i.damage
            self.image.set_alpha(100)
            if self.hp <= 0:
                self.kill()

    def take(self, weapon):
        if self.armed:
            self.weapon.replace(-100, -100)
        self.weapon = weapon
        self.armed = True
        if self.weapon.side != self.side:
            self.weapon.image = transform.flip(self.weapon.image, True, False)
            self.weapon.side = self.side


class Bullet(SimpleSprite):
    def __init__(self, img, pos, dir, speed, damage):
        super().__init__(img, pos)
        self.dir = dir
        self.speed = speed
        if self.dir == -1:
            self.image = transform.flip(self.image, True, False)
        self.damage = damage
        bullets.add(self)
    def update(self):
        self.x += self.speed * self.dir
        if not self.visible:
            self.kill()


class Weapon(SimpleSprite):
    def __init__(self, img, pos, recoil, speed, mode, damage, ammo_type):
        super().__init__(img, pos)
        self.recoil = 0
        self.max_recoil = recoil
        self.speed = speed
        self.mode = mode
        self.look = 1
        self.damage = damage
        self.side = 1
        self.ammo_type = ammo_type
        weapons.add(self)

    def update(self):
        if self.recoil > 0:
            self.recoil -= 1

    def right_shoot(self):
        b = Bullet(bullet_img, (self.rect.topright), self.look, self.speed, self.damage)
        b.x = b.rect.right - b.rect.width - 5
        b.y = b.rect.top + b.rect.height
        b.rect.topleft = b.x, b.y

    def left_shoot(self):
        b = Bullet(bullet_img, (self.rect.topleft), self.look, self.speed, self.damage)
        b.x = b.rect.left - b.rect.width + 5
        b.y = b.rect.top + b.rect.height
        b.rect.topleft = b.x, b.y

    def shoot(self):
        keys = key.get_pressed()
        if self.mode == 'auto' and keys[K_SPACE] and self.recoil == 0 and player.ammo[self.ammo_type] > 0:
            player.ammo[self.ammo_type] -= 1
            self.recoil = self.max_recoil
            if self.look == 1:
                self.right_shoot()
            elif self.look == -1:
                self.left_shoot()
        elif self.mode == 'semi' and self.recoil == 0 and player.ammo[self.ammo_type] > 0:

            global eventkeys
            for e in eventkeys:
                if e.key == K_SPACE:
                    player.ammo[self.ammo_type] -= 1
                    self.recoil = self.max_recoil
                    if self.look == 1:
                        self.right_shoot()
                    elif self.look == -1:
                        self.left_shoot()
        sprite.groupcollide(bullets, walls, True, False)


class ColdWeapon(SimpleSprite):
    def __init__(self, img, pos, damage, max_swing):
        super().__init__(img, pos)
        self.look = 1
        self.damage = damage
        self.side = 1
        self.swing = 0
        self.max_swing = max_swing
        weapons.add(self)

    def update(self):
        if self.swing > 0:
            self.swing -= .5
        self.x += self.swing * self.look

    def shoot(self):
        global eventkeys
        for e in eventkeys:
            if e.key == K_SPACE and self.swing == 0:
                self.swing = self.max_swing


class Enemy(SimpleSprite):
    def __init__(self, img, pos, attack = 5, speed = 2, recoil = 7):
        super().__init__(img, pos)
        self.look = 0
        self.look_y = 0
        self.speed = speed
        self.hp = 100
        self.alarm = False
        self.side = 'right'
        self.attack = attack
        self.recoil = 0
        self.max_recoil = recoil
        self.idle = Animation(enemy_idle_img, 20)
        self.run = Animation(enemy_run_img, 15)
        self.moving = False

    def idle_move(self):
        if sprite.spritecollide(self, walls, False) or sprite.spritecollide(self, crates, False):
            self.x += self.speed * -self.look*2
            self.look = 0
        if self.side == 'right':
            vision = Rect(self.rect.centerx, self.y+1, 300, self.rect.height-2)
            for w in walls.sprites() + crates.sprites():
                if vision.colliderect(w.rect):
                    if vision.width > abs(vision.x - w.x):
                        vision.width = abs(vision.x - w.x)
        elif self.side == 'left':
            vision = Rect(self.rect.centerx-300, self.y+1, 200, self.rect.height-2)
            for w in walls.sprites() + crates.sprites():
                if vision.colliderect(w.rect):
                    if vision.width > abs(vision.x - w.rect.right):
                        vision.width = abs(vision.x - w.x)
                        vision.right = self.rect.centerx

        if vision.colliderect(player.rect) or self.rect.colliderect(player.rect):
            self.alarm = True

        self.x += self.speed * self.look
        if pz.FRAMES % 120 == 0:
            self.look = 0
        if pz.FRAMES % 240 == 0:
            self.look = choice([-1, 1])
        if self.look in [1, -1]:
            self.moving = True

    def alarm_move(self):
        self.look = 0
        if player.x >= self.x:
            self.look = 1
        else:
            self.look = -1

        self.look_y = 0
        if abs(player.y - self.y) > 20:
            self.moving = True
            if player.y >= self.y:
                self.look_y = 1
            else:
                self.look_y = -1

        if abs(player.x - self.x) > 310:
            self.x += self.speed * self.look
            self.rect.topleft = self.x, self.y
            self.moving = True
            if sprite.spritecollide(self, walls, False) or sprite.spritecollide(self, crates, False):
                self.x += self.speed * -self.look
                self.moving = False

        elif abs(player.x - self.x) < 290:
            self.x += self.speed * -self.look
            self.rect.topleft = self.x, self.y
            self.moving = True
            if sprite.spritecollide(self, walls, False) or sprite.spritecollide(self, crates, False):
                self.x += self.speed * self.look
                self.moving = False


        self.y += self.speed * self.look_y
        self.rect.topleft = self.x, self.y
        if sprite.spritecollide(self, walls, False) or sprite.spritecollide(self, crates, False):
            self.y += self.speed * -self.look_y
            self.look_y = 0
            #self.moving = False

        if self.recoil > 0:
            self.recoil -= 1
        if self.recoil == 0 and abs(self.y - player.y) <= 25 and player.hp > 0:
            self.shoot()
            self.recoil = self.max_recoil

    def shoot(self):
        if self.look == 1:
            Bullet(
                bullet_img,
                (self.rect.midright),
                dir=self.look, speed=15, damage=5)
        else:
            Bullet(
                bullet_img,
                (self.rect.left - 25, self.rect.centery),
                dir=self.look, speed=15, damage=5)

    def check_dead(self, i):
        self.alarm = True
        self.hp -= i.damage
        if self.hp <= 0:
            enemies.remove(self)
            dead.add(self)

            pos = (self.rect.centerx-self.rect.width/4, self.rect.centery)
            if len(player.weapons) > 1:
                type = str(randint(0, len(player.weapons)-2))
            else:
                type = '0'
            w = AmmoItem(pos, 'type-'+type, 10)
            w.rect.center = self.rect.center
            w.replace(w.rect.x, w.rect.y)
            w.add(items)

            bottom = self.rect.bottom
            if self.image != night and self.image != transform.flip(night, True, False):
                if self.look in [0, 1]:
                    self.image = enemy_dead_img
                else:
                    self.image = transform.flip(enemy_dead_img, True, False)
            self.y = bottom - self.rect.height/2
        else:
            self.image.set_alpha(100)

    def image_update(self):
        if self.image.set_alpha() != 255:
            self.image.set_alpha(255)
        if self.image != night and self.image != transform.flip(night, True, False):
            if self.moving:
                self.run.update()
                self.image = self.run.animate()
            else:
                self.idle.update()
                self.image = self.idle.animate()
        if self.side == 'left':
            self.image = transform.flip(self.image, True, False)

    def update(self):
        self.image_update()
        for i in sprite.spritecollide(self, bullets, True):
            self.check_dead(i)
        if self.rect.colliderect(knife.rect) and knife.swing > knife.max_swing-1:
            self.check_dead(knife)

        self.moving = False
        if self.alarm:
            self.alarm_move()
        else:
            self.idle_move()

        if self.look == 1:
            self.side = 'right'
        elif self.look == -1:
            self.side = 'left'


class Crate(SimpleSprite):
    def __init__(self, img, pos, loot='ammo', hp=50):
        super().__init__(img, pos)
        self.hp = hp
        self.loot = loot
    def check_dead(self, i):
        self.hp -= i.damage
        if self.hp <= 0:
            crates.remove(self)
            dead.add(self)
            self.image = crate_broken_img
            pos = (self.rect.centerx-self.rect.width/4, self.rect.centery)
            if self.loot == 'pistol':
                w = WeaponItem(pistol_img, pos, pistol)
                w.rect.center = self.rect.center
                w.replace(w.rect.x, w.rect.y)
            if self.loot == 'smg':
                w = WeaponItem(smg_img, pos, smg)
                w.rect.center = self.rect.center
                w.replace(w.rect.x, w.rect.y)
            if self.loot == 'rifle':
                w = WeaponItem(rifle_img, pos, rifle)
                w.rect.center = self.rect.center
                w.replace(w.rect.x, w.rect.y)
            elif self.loot == 'heal':
                w = HealItem(pos)
                w.rect.center = self.rect.center
                w.replace(w.rect.x, w.rect.y)
            elif self.loot == 'ammo':
                if len(player.weapons) > 1:
                    type = str(randint(0, len(player.weapons)-2))
                else:
                    type = '0'
                w = AmmoItem(pos, 'type-'+type, 10)
                w.rect.center = self.rect.center
                w.replace(w.rect.x, w.rect.y)
            w.add(items)
        else:
            self.image.set_alpha(100)

    def update(self):
        if self.image.set_alpha() != 255:
            self.image.set_alpha(255)
        for i in sprite.spritecollide(self, bullets, True):
            self.check_dead(i)
        if self.rect.colliderect(knife.rect) and knife.swing > knife.max_swing-1:
            self.check_dead(knife)


class AmmoItem(SimpleSprite):
    def __init__(self, pos, item, amount = 1):
        super().__init__(ammo_box_img, pos)
        self.item = item
        self.amount = amount
    def update(self):
        if self.rect.colliderect(player.rect):
            player.ammo[self.item] += self.amount
            self.kill()


class WeaponItem(SimpleSprite):
    def __init__(self, img, pos, item):
        super().__init__(img, pos)
        self.item = item
    def update(self):
        if self.rect.colliderect(player.rect):
            if self.item not in player.weapons:
                player.weapons.append(self.item)
            self.kill()


class HealItem(SimpleSprite):
    def __init__(self, pos):
        super().__init__(heal_img, pos)
    def update(self):
        if self.rect.colliderect(player.rect):
            player.hp += 25
            self.kill()



player_idle_img = [
    Image('images/player/idle_1.png'),
    Image('images/player/idle_2.png')]
player_run_img = [
    Image('images/player/run_1.png'),
    Image('images/player/run_2.png'),
    Image('images/player/run_3.png'),
    Image('images/player/run_4.png')]
enemy_idle_img = [
    Image('images/enemies/idle_1.png', (56, 68)),
    Image('images/enemies/idle_2.png', (56, 68))]
enemy_run_img = [
    Image('images/enemies/idle_1.png', (56, 68)),
    Image('images/enemies/run_2.png', (56, 68)),
    Image('images/enemies/run_3.png', (56, 68)),
    Image('images/enemies/run_4.png', (56, 68)),
    Image('images/enemies/run_5.png', (56, 68)) ]
walls_img = [
    Image('images/environment/Platform_Thin.png', (48, 96)),
    Image('images/environment/Platform.png', (96, 96))]
friend_img = [
    Image('images/friend/1.png', (240, 164)),
    Image('images/friend/12.png', (240, 164)),
    Image('images/friend/29.png', (240, 164)),
    Image('images/friend/31.png', (240, 164)),
    Image('images/friend/29.png', (240, 164)),
    Image('images/friend/12.png', (240, 164))]
cars = [
    Image('images/environment/car1.png', (160, 70)),
    Image('images/environment/car2.png', (160, 70)),
    Image('images/environment/car3.png', (160, 70)),
    Image('images/environment/car4.png', (160, 70))
]
friend_speak = Animation(friend_img, 15)
night = Image('images/environment/ultimate.png', (190, 80))
sand_img = Image('images/environment/sand.png')
prison_img = Image('images/environment/crate_11.png', (128, 128))
base_img = Image('images/environment/ground_06.png', (128, 128))
pistol_img = Image('images/weapons/handgun.png', (32, 32))
smg_img = Image('images/weapons/modernMachineGun.png', (64, 32))
rifle_img = Image('images/weapons/autoShotgun.png', (64, 32))
knife_img = Image('images/weapons/knife.png', (32, 32))
bullet_img = Image('images/weapons/tile_0000.png', (24, 9))
enemy_dead_img = Image('images/enemies/dead_gunner.png', (70, 28))
crate_img = Image('images/environment/crate_02.png', (48, 48))
crate_broken_img = Image('images/environment/crate_32.png', (48, 48))
ui_img = Image('images/environment/Platform.png', (pz.win_w//10, 100))
ui_2_img = Image('images/environment/crate_11.png', (240, 164))
great_wall_img = Image('images/environment/Platform.png', (pz.win_w*3, 100))
spawner_img = Image('images/environment/shadow.png')
ammo_box_img = Image('images/weapons/safelock.png', (32, 32))
heart_img = Image('images/other/heart.png', (50, 50))
heal_img = Image('images/other/heal.png', (32, 32))

items = Group()
crates = Group()
walls = Group()
enemies = Group()
bullets = Group()
weapons = Group()
tiles = Group()
dead = Group()
players = Group()

'''--- ALL WEAPONS HERE ---'''
pistol = Weapon(pistol_img, (-100, -100),
    recoil=10, speed=15, mode='semi',
    damage=15, ammo_type = 'type-0')
smg = Weapon(smg_img, (-100, -100),
    recoil = 3, speed = 25, mode='auto',
    damage=5, ammo_type = 'type-1')
rifle = Weapon(rifle_img, (-100, -100),
    recoil = 7, speed = 15, mode='auto',
    damage=15, ammo_type = 'type-2')
knife = ColdWeapon(knife_img, (-100, -100),
    damage = 50, max_swing=30)

player = Player(player_idle_img[0], (100, pz.center_y-27))
player.add(players)

car = SimpleSprite(Image('images/environment/car.png', (180, 70)), (pz.win_w * 5.5, pz.win_h*0.80))
shadow = SimpleSprite(Image('images/environment/car_shadow.png', (160, 70)), (car.rect.midbottom))
great_wall = SimpleSprite(great_wall_img, (0, pz.win_h - 100))
great_wall.add(walls)

fps_txt = SimpleText((0, 0), color=white,background=black)
health_txt = SimpleText((pz.win_w//10, pz.win_h-75), size=50, color=red, f='Fifaks10Dev1.ttf')
mark_txt = SimpleText((-100, -100), size = 50, text = '!', color = red)
ammo_txt = SimpleText((-100, -100), size = 40, f='Fifaks10Dev1.ttf')
task_txt = SimpleText((pz.win_w//10 * 6.07, pz.win_h-75), size = 40, f='Fifaks10Dev1.ttf', background=white)
current_task = ''
final_txt = SimpleText((-100, -100), size = 100, f='Fifaks10Dev1.ttf', background=black, color=white, text = ' ты проиграл ')
final_txt.rect.center = pz.center_x, pz.center_y
final_txt.replace(final_txt.rect.x, final_txt.rect.y)
final_2_txt = SimpleText((-100, -100), size = 30, f='Fifaks10Dev1.ttf', background=gray, color=black, text = ' ESC - выход ')
final_2_txt.rect.center = pz.center_x, pz.center_y + 65
final_2_txt.replace(final_2_txt.rect.x, final_2_txt.rect.y)
speak_1 = SimpleText((pz.win_w-240, 10), f='Fifaks10Dev1.ttf', background = white, text = '')
speak_2 = SimpleText((pz.win_w-240, 45), f='Fifaks10Dev1.ttf', background = white, text = '')
speak_3 = SimpleText((pz.win_w-240, 80), f='Fifaks10Dev1.ttf', background = white, text = '')
speak = [speak_1, speak_2, speak_3]
line1 = SimpleText((-100, 100), f='Fifaks10Dev1.ttf', color = white, text = ' код:')
line2 = SimpleText((-100, 150), f='Fifaks10Dev1.ttf', color = white, text = ' Comandorr')
line3 = SimpleText((-100, 250), f='Fifaks10Dev1.ttf', color = white, text = ' графика:')
line4 = SimpleText((-100, 300), f='Fifaks10Dev1.ttf', color = white, text = ' Pixel Frog, Secret Hideout, Kenney.nl')
line5 = SimpleText((-100, 400), f='Fifaks10Dev1.ttf', color = white, text = ' шрифт:')
line6 = SimpleText((-100, 450), f='Fifaks10Dev1.ttf', color = white, text = ' Fifaks')
line7 = SimpleText((-100, 550), f='Fifaks10Dev1.ttf', color = white, text = ' музыка ')
line8 = SimpleText((-100, 600), f='Fifaks10Dev1.ttf', color = white, text = ' Daniel Syrov')
titres = [line1, line2, line3, line4, line5, line6, line7, line8]
for i in titres:
    i.x = pz.center_x-i.rect.width/2


def spawn_walls(n=10, location=0, img = walls_img):
    for i in range(n):
        x = randint(pz.win_w*location + 150, pz.win_w*location + pz.win_w-300)
        y = randint(100, pz.win_h-150)
        img1 = choice(img)
        if chance(50):
            img1 = transform.flip(img1, True, False)
        s = SimpleSprite(img1, (x, y))
        while len(sprite.spritecollide(s, walls, False))!=0 or len(sprite.spritecollide(s, crates, False))!=0 or s.rect.colliderect(player.rect):
            x = randint(pz.win_w*location + 150, pz.win_w*location + pz.win_w-300)
            y = randint(100, pz.win_h-150)
            s.rect.topleft = x, y
            s.replace(x, y)
        s.add(walls)

def spawn_crates(n=10, location=0, loot='ammo'):
    for i in range(n):
        x = randint(pz.win_w*location + 100, pz.win_w*location + pz.win_w-200)
        y = randint(100, pz.win_h-100)
        s = Crate(crate_img, (x, y), loot)
        while len(sprite.spritecollide(s, walls, False))!=0 or len(sprite.spritecollide(s, crates, False))!=0 or s.rect.colliderect(player.rect):
            x = randint(pz.win_w*location + 100, pz.win_w*location + pz.win_w-200)
            y = randint(100, pz.win_h-100)
            s.rect.topleft = x, y
            s.replace(x, y)
        s.add(crates)

def spawn_enemies(n=10, location=0):
    for i in range(n):
        x = randint(pz.win_w*location + 200, pz.win_w*location + pz.win_w-200)
        y = randint(100, pz.win_h-100)
        s = Enemy(enemy_idle_img[0], (x, y))
        while len(sprite.spritecollide(s, walls, False))!=0 or len(sprite.spritecollide(s, crates, False))!=0 or s.rect.colliderect(player.rect) or len(sprite.spritecollide(s, enemies, False))!=0:
            x = randint(pz.win_w*location + 200, pz.win_w*location + pz.win_w-200)
            y = randint(100, pz.win_h-100)
            s.rect.topleft = x, y
            s.replace(x, y)
        s.add(enemies)

spawn_walls(20, 0)
spawn_crates(1, 0, 'ammo')
spawn_crates(1, 0, 'heal')
spawn_enemies(1, 0)


for x in range(pz.win_w//128+1):
    for y in range(pz.win_h//128+1):
        SimpleSprite(prison_img, (x*128, y*128)).add(tiles)

for x in range(pz.win_w//128, pz.win_w*3//128+1):
    for y in range(pz.win_h//128+1):
        SimpleSprite(base_img, (x*128, y*128)).add(tiles)

for x in range(pz.win_w*3//64, pz.win_w*6//64+1):
    for y in range(pz.win_h//64+1):
        SimpleSprite(sand_img, (x*64, y*64)).add(tiles)

for x in range(pz.win_w*4//96):
    SimpleSprite(walls_img[1], (x*96, 0)).add(walls)
for i in range(4):
    for y in range(pz.win_h//96+1):
        if abs(y*96 - pz.win_h//2) > 96:
            SimpleSprite(walls_img[1], (i*pz.win_w, y*96)).add(walls)
            SimpleSprite(walls_img[1], (i*pz.win_w + pz.win_w-96, y*96)).add(walls)
        if i == 0 and abs(y*96 - pz.win_h//2) < 96:
            SimpleSprite(walls_img[1], (i*pz.win_w, y*96)).add(walls)

change = 0
everything = []
def change_scene():
    global change, everything, cutscene, LOCATION
    if change > 10:
        change -= 10
        for i in tiles.sprites() + everything:
            i.x -= 10
    elif change < -10:
        change += 10
        for i in tiles.sprites() + everything:
            i.x += 10
    else:
        for i in tiles.sprites() + everything:
            i.x -= change
        change = 0
        cutscene = False

boss = Enemy(night, (-200, pz.center_y), attack=10, speed = 1, recoil = 10)
cutscene = False
eventkeys = event.get(eventtype=KEYDOWN)
start_dialog = pz.FRAMES
dialog = 0
word = 0
LOCATION = 0
def game():
    global cutscene, everything, change, current_task, start_dialog, dialog, word, LOCATION, boss
    everything = walls.sprites() + dead.sprites() + enemies.sprites() + bullets.sprites() + crates.sprites() + items.sprites() + [player, car]

    if player.x > pz.win_w and not cutscene:
        cutscene = True
        change = pz.win_w
        LOCATION += 1
        if LOCATION == 1:
            spawn_walls(30, 1)
            spawn_crates(5, 1, 'ammo')
            spawn_crates(1, 1, 'heal')
            spawn_crates(1, 1, 'pistol')
            spawn_enemies(15, 1)
        if LOCATION == 2:
            spawn_walls(30, 1)
            spawn_crates(6, 1, 'ammo')
            spawn_crates(1, 1, 'smg')
            spawn_crates(2, 1, 'heal')
            spawn_enemies(12, 1)
        if LOCATION == 3:
            spawn_walls(7, 1, cars)
            spawn_walls(15, 1)
            spawn_crates(7, 1, 'ammo')
            spawn_crates(1, 1, 'rifle')
            spawn_crates(2, 1, 'heal')
            spawn_enemies(10, 1)
        if LOCATION == 4:
            walls.empty()
            enemies.empty()
            boss = Enemy(night, (-200, pz.center_y), attack=10, speed = 1, recoil = 10)
            boss.look = 1
            boss.alarm = True
            enemies.add(boss)
            spawn_crates(7, 1, 'ammo')
            spawn_crates(2, 1, 'heal')
            spawn_walls(10, 1)

        if LOCATION == 2:
            dialog = 0
            word = 0
            mixer.music.unload()
            mixer.music.load('sounds/game_2.mp3')
            mixer.music.play(10)
        if LOCATION == 3 and smg in player.weapons and current_task == ' найди автомат и выбирайся ':
            current_task = ''
            dialog = 0
            word = 0
        if LOCATION == 4:
            mixer.music.unload()
            mixer.music.load('sounds/boss.mp3')
            mixer.music.play(10)
            if current_task == ' перебей охранников и найди выход ':
                current_task = ''
                dialog = 0
                word = 0

    elif player.x < -0 and not cutscene:
        LOCATION -= 1
        cutscene = True
        change = -pz.win_w
    if cutscene:
        change_scene()

    global eventkeys
    eventkeys = event.get(eventtype=KEYDOWN)

    fill_window(white)
    tiles.reset()
    walls.reset()
    dead.reset()
    crates.update()
    crates.reset()
    items.update()
    items.reset()
    if not cutscene:
        enemies.update()
        players.update()
    enemies.reset()
    players.reset()
    weapons.update()
    weapons.reset()
    bullets.update()
    bullets.reset()
    shadow.replace(car.x, car.y+15)
    shadow.reset()
    car.reset()
    sprite.groupcollide(bullets, walls, True, False)

    for e in enemies.sprites():
        if e.alarm and e.hp > 0:
            mark_txt.rect.center = e.rect.centerx, e.rect.top - mark_txt.rect.height/2
            mark_txt.x, mark_txt.y = mark_txt.rect.topleft
            mark_txt.reset()

    fps_txt.setText(str(int(clock.get_fps())))
    fps_txt.reset()

    for x in range(pz.win_w//10):
        pz.window.blit(ui_img, (x*pz.win_w//10, pz.win_h-100))

    img = transform.scale(player.image, (player.rect.width*3, player.rect.height*3))
    pz.window.blit(img, (pz.win_w//50, pz.win_h - 95))
    health_txt.setText(' ' + str(player.hp) + ' ')
    health_txt.reset()
    pz.window.blit(heart_img, (health_txt.rect.right - 20, health_txt.rect.top-3))
    img = transform.scale(knife_img, (96, 96))
    pz.window.blit(img, (pz.win_w//10*2 + 50, pz.win_h - 110))

    if pistol in player.weapons:
        img = transform.scale(pistol_img, (96, 96))
        pz.window.blit(img, (pz.win_w//10*3 + 50, pz.win_h - 110))
        ammo_txt.setText('[ ' + str(player.ammo['type-0']) + ' ]')
        ammo_txt.x = pz.win_w//10*3.5 - ammo_txt.rect.width/2
        ammo_txt.y = pz.win_h - 36
        ammo_txt.reset()
    if smg in player.weapons:
        img = transform.scale(smg_img, (160, 80))
        pz.window.blit(img, (pz.win_w//10*4 + 35, pz.win_h - 105))
        ammo_txt.setText('[ ' + str(player.ammo['type-1']) + ' ]')
        ammo_txt.x = pz.win_w//10*4.5 - ammo_txt.rect.width/2
        ammo_txt.y = pz.win_h - 36
        ammo_txt.reset()
    if rifle in player.weapons:
        img = transform.scale(rifle_img, (160, 80))
        pz.window.blit(img, (pz.win_w//10*5 + 25, pz.win_h - 105))
        ammo_txt.setText('[ ' + str(player.ammo['type-2']) + ' ]')
        ammo_txt.x = pz.win_w//10*5.5 - ammo_txt.rect.width/2
        ammo_txt.y = pz.win_h - 36
        ammo_txt.reset()

    task_txt.setText(current_task)
    task_txt.reset()


    if LOCATION == 1 and dialog < len(friend_dialog_1):
        current_task = ' проберись через комнату с охраной '
        dialog = len(friend_dialog_1)-1
        for s in speak:
            s.setText('')

    if dialog < len(friend_dialog_1) and LOCATION == 0:
        if pz.FRAMES % 3 == 0:
            word+=1
        len1 = len(friend_dialog_1[dialog][0])
        len2 = len(friend_dialog_1[dialog][1])
        len3 = len(friend_dialog_1[dialog][2])
        speak_1.setText(friend_dialog_1[dialog][0][:word])
        if word > len1:
            speak_2.setText(friend_dialog_1[dialog][1][:word-len1])
        if word > len1+len2:
            speak_3.setText(friend_dialog_1[dialog][2][:word-len1-len2])
        if word >= len1+len2+len3 + len3:
            word = 0
            dialog += 1
            if dialog == len(friend_dialog_1):
                current_task = ' проберись через комнату с охраной '
            for s in speak:
                s.setText('')
        for s in speak:
            s.x = pz.win_w - 240 - s.rect.width
            s.reset()
        friend_speak.update()
        img = friend_speak.animate()
        pz.window.blit(ui_2_img, (pz.win_w-240, 0 ))
        pz.window.blit(img, (pz.win_w-240, 0))

    if LOCATION == 2 and dialog < len(friend_dialog_2):
        if pz.FRAMES % 3 == 0:
            word+=1
        len1 = len(friend_dialog_2[dialog][0])
        len2 = len(friend_dialog_2[dialog][1])
        len3 = len(friend_dialog_2[dialog][2])
        speak_1.setText(friend_dialog_2[dialog][0][:word])
        if word > len1:
            speak_2.setText(friend_dialog_2[dialog][1][:word-len1])
        if word > len1+len2:
            speak_3.setText(friend_dialog_2[dialog][2][:word-len1-len2])
        if word >= len1+len2+len3 + len3 or smg in player.weapons:
            word = 0
            dialog += 1
            if dialog >= len(friend_dialog_2):
                current_task = ' найди автомат и выбирайся '
            for s in speak:
                s.setText('')
        for s in speak:
            s.x = pz.win_w - 240 - s.rect.width
            s.reset()
        friend_speak.update()
        img = friend_speak.animate()
        pz.window.blit(ui_2_img, (pz.win_w-240, 0 ))
        pz.window.blit(img, (pz.win_w-240, 0))

    if LOCATION == 3 and dialog < len(friend_dialog_3):
        if pz.FRAMES % 3 == 0:
            word+=1
        len1 = len(friend_dialog_3[dialog][0])
        len2 = len(friend_dialog_3[dialog][1])
        len3 = len(friend_dialog_3[dialog][2])
        speak_1.setText(friend_dialog_3[dialog][0][:word])
        if word > len1:
            speak_2.setText(friend_dialog_3[dialog][1][:word-len1])
        if word > len1+len2:
            speak_3.setText(friend_dialog_3[dialog][2][:word-len1-len2])
        if word >= len1+len2+len3 + len3:
            word = 0
            dialog += 1
            if dialog >= len(friend_dialog_3):
                current_task = ' перебей охранников и найди выход '
            for s in speak:
                s.setText('')
        for s in speak:
            s.x = pz.win_w - 240 - s.rect.width
            s.reset()
        friend_speak.update()
        img = friend_speak.animate()
        pz.window.blit(ui_2_img, (pz.win_w-240, 0 ))
        pz.window.blit(img, (pz.win_w-240, 0))

    if LOCATION == 4 and dialog < len(friend_dialog_4):
        if pz.FRAMES % 3 == 0:
            word+=1
        len1 = len(friend_dialog_4[dialog][0])
        len2 = len(friend_dialog_4[dialog][1])
        len3 = len(friend_dialog_4[dialog][2])
        speak_1.setText(friend_dialog_4[dialog][0][:word])
        if word > len1:
            speak_2.setText(friend_dialog_4[dialog][1][:word-len1])
        if word > len1+len2:
            speak_3.setText(friend_dialog_4[dialog][2][:word-len1-len2])
        if word >= len1+len2+len3 + len3:
            word = 0
            dialog += 1
            if dialog >= len(friend_dialog_4):
                current_task = ' победи Ночь '
                boss.x = -200
                boss.hp = 300
            for s in speak:
                s.setText('')
        for s in speak:
            s.x = pz.win_w - 240 - s.rect.width
            s.reset()
        friend_speak.update()
        img = friend_speak.animate()
        pz.window.blit(ui_2_img, (pz.win_w-240, 0 ))
        pz.window.blit(img, (pz.win_w-240, 0))

    if player.hp <= 0:
        final_txt.reset()
        final_2_txt.reset()
        player.hp = 0
        for e in eventkeys:
            if e.key == K_ESCAPE:
                stop_game()

    if boss.hp <= 0:
        while car.x >= pz.center_x-car.rect.width/2:
            fill_window(black)
            for i in titres:
                i.reset()
            for e in event.get():
                if e.type == QUIT:
                    stop_game()
                    break
            tiles.reset()
            for e in everything:
                e.x -= 10
                e.update()
                e.reset()
            display.update()
            clock.tick(60)
        for e in everything + tiles.sprites():
            e.fade_out()



mixer.music.load('sounds/game_3.mp3')
mixer.music.play(10)
run_game(game)
