from pygamezavr import*
import pygamezavr as pz


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
        if sprite.spritecollide(self, walls, False):
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
    def __init__(self, img, pos, recoil, speed, mode, damage):
        super().__init__(img, pos)
        self.recoil = 0
        self.max_recoil = recoil
        self.speed = speed
        self.mode = mode
        self.look = 1
        self.damage = damage
        self.side = 1
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
        if self.mode == 'auto' and keys[K_SPACE] and self.recoil == 0:
            self.recoil = self.max_recoil
            if self.look == 1:
                self.right_shoot()
            elif self.look == -1:
                self.left_shoot()
        elif self.mode == 'semi' and self.recoil == 0:
            global eventkeys
            for e in eventkeys:
                if e.key == K_SPACE:
                    self.recoil = self.max_recoil
                    if self.look == 1:
                        self.right_shoot()
                    elif self.look == -1:
                        self.left_shoot()
        sprite.groupcollide(bullets, walls, True, False)


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
        enemies.add(self)

    def idle_move(self):
        if len(sprite.spritecollide(self, walls, False)) != 0:
            self.x += self.speed * -self.look*2
            self.look = 0
        self.x += self.speed * self.look
        if pz.FRAMES % 120 == 0:
            self.look = 0
        if pz.FRAMES % 240 == 0:
            self.look = choice([-1, 1])
        if self.look in [1, -1]:
            self.moving = True

    def alarm_move(self):
        if len(sprite.spritecollide(self, walls, False)) != 0:
            self.x += self.speed * -self.look
            self.y += self.speed * -self.look_y

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
            self.moving = True
        elif abs(player.x - self.x) < 290:
            self.x += self.speed * -self.look
            self.moving = True

        self.y += self.speed * self.look_y
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
                dir=self.look, speed=15, damage=10)
        else:
            Bullet(
                bullet_img,
                (self.rect.left - 25, self.rect.centery),
                dir=self.look, speed=15, damage=10)

    def check_dead(self):
        for i in sprite.spritecollide(self, bullets, True):
            self.alarm = True
            self.hp -= i.damage
            if self.hp <= 0:
                enemies.remove(self)
                dead.add(self)
                bottom = self.rect.bottom
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
        self.check_dead()

        self.moving = False
        if self.alarm:
            self.alarm_move()
        else:
            self.idle_move()

        if self.look == 1:
            self.side = 'right'
        elif self.look == -1:
            self.side = 'left'

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
    Image('images/environment/Platform_Thin.png', (32, 64)),
    Image('images/environment/Platform.png', (64, 64))]
sand_img = Image('images/environment/sand.png')
pistol_img = Image('images/weapons/handgun.png', (32, 32))
smg_img = Image('images/weapons/modernMachineGun.png', (64, 32))
bullet_img = Image('images/weapons/tile_0000.png', (24, 9))
enemy_dead_img = Image('images/enemies/dead_gunner.png', (70, 28))
ui_img = Image('images/environment/Platform.png', (pz.win_w//10, 100))
great_wall_img = Image('images/environment/Platform.png', (pz.win_w, 100))
spawner_img = Image('images/environment/shadow.png')


walls = Group()
enemies = Group()
bullets = Group()
weapons = Group()
tiles = Group()
dead = Group()
players = Group()
for x in range(pz.win_w*3//64+1):
    for y in range(pz.win_h//64+1):
        SimpleSprite(sand_img, (x*64, y*64)).add(tiles)

pistol = Weapon(pistol_img, (-100, -100), recoil=15, speed=15, mode='semi', damage=15)
smg = Weapon(smg_img, (-100, -100), recoil = 5, speed = 20, mode='auto', damage=5)
player = Player(player_idle_img[0], (pz.center_x, pz.center_y))
player.add(players)
car = SimpleSprite(Image('images/environment/car.png', (144, 48)), (pz.win_w * 1.6, pz.center_y - 24))
shadow = SimpleSprite(Image('images/environment/car_shadow.png', (144, 48)), (car.rect.midbottom))
great_wall = SimpleSprite(great_wall_img, (0, pz.win_h - 100))
great_wall.add(walls)

fps_txt = SimpleText((win_w-26, 0), color=white,background=black)
health_txt = SimpleText((win_w-26, 0), size=48, color=red, background=gray, f='Fifaks10Dev1.ttf')
mark_txt = SimpleText((-100, -100), size = 50, text = '!', color = red)

def spawn_walls(n = 10):
    for i in range(n):
        x = randint(0, pz.win_w)
        y = randint(0, pz.win_h)
        s = SimpleSprite(choice(walls_img), (x, y))
        while not len(sprite.spritecollide(s, walls, False)) == 0:
            x = randint(0, pz.win_w)
            y = randint(0, pz.win_h)
            s.rect.topleft = x, y
            s.replace(x, y)
        s.add(walls)
spawn_walls(20)

cutscene = False
eventkeys = event.get(eventtype=KEYDOWN)
def game():
    global cutscene
    everything = walls.sprites() + dead.sprites() + enemies.sprites() + bullets.sprites() + [player, car, shadow]
    if cutscene and car.x > center_x:
        for i in tiles.sprites() + everything:
            i.x -= 10
    if player.x >= pz.win_w:
        cutscene = True
    global eventkeys
    eventkeys = event.get(eventtype=KEYDOWN)
    for e in eventkeys:
        if e.key == K_1:
            player.take(pistol)
        elif e.key == K_2:
            player.take(smg)
    sprite.groupcollide(bullets, walls, True, False)
    fill_window(white)
    tiles.reset()
    walls.reset()
    dead.reset()

    enemies.update()
    enemies.reset()
    players.update()
    players.reset()
    weapons.update()
    weapons.reset()
    bullets.update()
    bullets.reset()
    shadow.replace(car.x, car.y+15)
    shadow.reset()
    car.reset()

    for e in enemies.sprites():
        if e.alarm and e.hp > 0:
            mark_txt.rect.center = e.rect.centerx, e.rect.top - mark_txt.rect.height/2
            mark_txt.x, mark_txt.y = mark_txt.rect.topleft
            mark_txt.reset()

    ''' cool but not working
    everything = walls.sprites() + dead.sprites() + enemies.sprites()  + [player, car, shadow]
    everything_sorted = []
    for e in everything:
        everything_sorted.append(e.rect.bottom)
    everything_sorted.sort()
    for es in everything_sorted:
        for e in everything:
            if es == e.rect.bottom:
                e.reset()
                everything.remove(e)
    '''



    fps_txt.setText(str(int(clock.get_fps())))
    fps_txt.reset()
    health_txt.setText(' ' + str(player.hp) + ' ')
    health_txt.replace(pz.center_x - health_txt.rect.width/2, 0)
    health_txt.reset()
    for x in range(pz.win_w//10):
        pz.window.blit(ui_img, (x*pz.win_w//10, pz.win_h-100))

    if pz.FRAMES %180 == 0 and not cutscene:
        x = randint(200, pz.win_w - 200)
        y = randint(100, pz.win_h - 100)
        e = Enemy(enemy_idle_img[0], (x, y))


run_game(game)
