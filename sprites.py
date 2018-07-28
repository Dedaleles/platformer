# --FICHIER DE CLASSE DES SPRITES--

from constantes import *
import pygame as pg #on raccourci pygame en pg
from random import choice
import os
vec = pg.math.Vector2

class Spritesheet:
    #charger et diviser les spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height, type=None):
        #prend une image avec ses coordonnnées dans la spritesheets
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0,0), (x, y, width, height))
        if type == 'plateforme':
            image = pg.transform.scale(image, (width *4, height*4))
        if type == 'perso':
            image = pg.transform.scale(image, (width *3, height*3))
        if type == 'dagger':
            image = pg.transform.scale(image, (int(width * 0.75), int(height*0.75)))
            image = pg.transform.rotate(image, 45)
            image.set_colorkey(DAGGER_BG)

        return image

class Joueur(pg.sprite.Sprite):
    def __init__(self, game, save):
        self.game=game
        pg.sprite.Sprite.__init__(self)
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frame
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(0, HEIGHT - 64)
        self.vel = vec(0, 0)
        self.acc = vec(0,0)
        self.jumping = False
        self.inventaire = Inventaire(self, self.game, save)
        self.weapon = self.inventaire.weapons[0]
        self.weapon_pos = 0
        self.game.weaponsGroup.add(self.weapon)
        self.throwing = False
        self.standing = False
        self.direction = 'droite'

    def load_images(self):
        #load image and anim
        self.standing_frame = self.game.rangerSpritesheet.get_image(56, 0, 16, 28, 'perso')
        self.standing_frame.set_colorkey(BLACK)
        self.back_frame = self.game.rangerSpritesheet.get_image(0, 0, 16, 28, 'perso')
        self.back_frame.set_colorkey(BLACK)
        self.walk_frames_d = [self.game.rangerSpritesheet.get_image(16, 27, 12, 27, 'perso'),
                              self.game.rangerSpritesheet.get_image(30, 0, 12, 26, 'perso'),
                              self.game.rangerSpritesheet.get_image(30, 26, 12, 26, 'perso')]
        for frame in self.walk_frames_d:
            frame.set_colorkey(BLACK)
        self.walk_frames_g = [self.game.rangerSpritesheet.get_image(56, 28, 12, 27, 'perso'),
                              self.game.rangerSpritesheet.get_image(72, 0, 12, 26, 'perso'),
                              self.game.rangerSpritesheet.get_image(72, 26, 12, 26, 'perso')]
        for frame in self.walk_frames_g:
            frame.set_colorkey(BLACK)
        self.jump_frame = self.game.rangerSpritesheet.get_image(56, 0, 16, 28, 'perso')
        self.jump_frame.set_colorkey(BLACK)


    def update(self):
        self.animate()
        self.acc = vec(0,PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
            self.direction = 'gauche'
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
            self.direction = 'droite'

        # on applique la friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # équation de mouvement
        self.vel += self.acc
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # bloque le sprite
        if self.pos.x < 0 + self.rect.width / 2:
            self.pos.x = self.rect.width / 2
        elif self.pos.x > WIDTH - self.rect.width / 2:
            self.pos.x = WIDTH - self.rect.width / 2



        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
            self.standing = False
        else:
            self.walking = False
        #walk animation
        if self.walking:
            if now - self.last_update > 120:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_d)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_d[self.current_frame]
                if self.vel.x < 0:
                    self.image = self.walk_frames_g[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        if self.standing:
            self.image = self.standing_frame
        if self.throwing == True:
            self
        self.mask = pg.mask.from_surface(self.image)

    def jump(self):
        #on verifie qu'on est sur une plateforme
        self.rect.x += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -=1
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -2:
                self.vel.y = -2

    def descend(self):
        pass

    def switch_weapon(self):
            if self.weapon_pos + 1 < len(self.inventaire.weapons):
                self.weapon_pos +=1
            else:
                self.weapon_pos = 0
            self.weapon = self.inventaire.weapons[self.weapon_pos]

class ennemi(pg.sprite.Sprite):
    def __init__(self, name, x, y, vit, direction, frame_droite, frame_gauche, lim_x, lim_y, friction):
        pg.sprite.Sprite.__init__(self)
        self.acc = vec(0,0)
        self.vel = vec(0,0)
        self.pos = vec(x,y)
        self.direction = direction
        self.name = name
        self.frame_droite = frame_droite
        self.frame_gauche = frame_gauche
        self.x = x
        self.y = y
        self.image = self.frame_droite[0]
        self.lim_x = lim_x
        self.friction = friction
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vit = vit
        self.last_update=0
        self.current_frame=0

    def update(self):
        self.animate()
        self.acc = vec(0,PLAYER_GRAV)
        if self.direction == 'droite':
            self.acc.x = self.vit
        if self.direction == 'gauche':
            self.acc.x = -self.vit

        self.acc.x += self.vel.x * self.friction
        # équation de mouvement
        self.vel += self.acc
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # bloque le sprite
        if self.pos.x - self.game.posSol.rect.x < self.x - self.lim_x + self.rect.width / 2:
            self.direction = 'droite'
        elif self.pos.x - self.game.posSol.rect.x> self.x + self.lim_x - self.rect.width / 2:

            self.direction = 'gauche'

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 200:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frame_droite)
            bottom = self.rect.bottom
            if self.vel.x > 0:
                self.image = self.frame_droite[self.current_frame]
            if self.vel.x < 0:
                self.image = self.frame_gauche[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom

class Serpent(ennemi):
    def __init__(self,x,game):
        self.frame_droite = []
        self.frame_gauche = []
        self.game = game
        self.frame_droite.append(self.game.envrnmtSpritesheet.get_image(128, 16, 18, 15, 'perso'))
        self.frame_droite.append(self.game.envrnmtSpritesheet.get_image(146, 16, 16, 15, 'perso'))

        for frame in self.frame_droite:
            frame.set_colorkey(BLACK)
            self.frame_gauche.append(pg.transform.flip(frame,True,False))
        ennemi.__init__(self, 'serpent', x, HEIGHT-16, SERPENT_VIT, 'droite', self.frame_droite, self.frame_gauche, LIM_X_SERPENT, 0, FRICTION_SERPENT)

class Weapon(pg.sprite.Sprite):
    def __init__(self, game, name, sprite, vit, range, joueur):
        pg.sprite.Sprite.__init__(self)
        self.joueur = joueur
        self.game = game
        self.name = name
        self.vit = vit
        self.image = sprite
        self.image.convert_alpha()
        self.image_copy = sprite
        self.rect = self.image.get_rect()
        self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.dist = 0
        self.go = False
        self.range = range
        self.grav = 0

    def update(self):
        if self.go:
            self.pos = vec(self.x, self.y)
            self.acc = vec(self.vit,self.grav)
            # équation de mouvement
            self.vel += self.acc
            if abs(self.vel.x) < 0.2:
                self.vel.x = 0
            self.pos += self.vel + 0.5 * self.acc
            self.dist += self.vit
            print(self.dist)
            self.rect.x = self.pos.x
            self.rect.y = self.pos.y
            if self.dist >= self.range or self.dist <= -self.range:
                self.grav = 5

            if self.pos.x < 0:
                self.stop()
            elif self.pos.x > WIDTH:
                self.stop()

    def use(self, x, y):
        if self.joueur.direction == 'droite':
            self. vit = VIT_CAILLOU
            self.image =  self.image_copy
        if self.joueur.direction == 'gauche':
            self.vit = -VIT_CAILLOU
            self.image = pg.transform.flip(self.image_copy, True, False)
        self.x = x
        self.y = y
        self.game.all_sprites.add(self)
        self.go = True
        print('use')

    def stop(self):
        self.joueur.throwing = False
        self.rect.x = 0
        self.rect.y = 0
        self.vel = vec(0, 0)
        self.go = False
        self.dist = 0
        self.grav = 0
        self.game.all_sprites.remove(self)
        print('stop')

class Inventaire():
    def __init__(self, joueur, game, save):
        self.joueur = joueur
        self.game = game
        self.load_images()
        self.dir = os.path.dirname(__file__)
        self.save = open(os.path.join(self.dir,'sauvegardes','save'+str(save)), 'r')
        self.vie = 0
        self.objet = []
        self.weapons = []
        i=0
        for ligne in self.save:
            index = ligne.find('Inventaire=[')
            if index == -1 and i == 0:
                open(os.path.join(self.dir,'sauvegardes','save'+str(save)), 'a').write('Inventaire=[]').close()
            else:
                ligne = ligne[index+12:]
                while ligne.find('\'') != -1:
                    ligne = ligne[ligne.find('\'')+1:]
                    ligneAjout = ligne[:ligne.find('\'')]
                    ligne = ligne[ligne.find('\'')+1:]
                    if ligneAjout == 'caillou':
                        self.weapons.append(Weapon(self.game, ligneAjout, self.caillou, VIT_CAILLOU, RANGE_CAILLOU, self.joueur))
                    else:
                        self.objet.append(ligneAjout)
                print(self.objet)
                print(ligne)
            i+=1

    def load_images(self):
        self.caillou = self.game.envrnmtSpritesheet.get_image(128, 0, 16, 16, 'perso')
        self.caillou.set_colorkey(BLACK)

    def add_weapon(self, item, type = 'objet'):
        self.weapons.append(item)

class Plateforme(pg.sprite.Sprite):
    def __init__(self, game, x, y, texture=None):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        if texture == None:
            images = [self.game.envrnmtSpritesheet.get_image(0, 16, 16, 16, 'plateforme'),
                      self.game.envrnmtSpritesheet.get_image(32, 32, 16, 16, 'plateforme')]
            texture = choice(images)

        self.image = texture
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coffre(pg.sprite.Sprite):
        def __init__(self, game, x, y, objet):
            self.objet = objet
            self.game = game
            pg.sprite.Sprite.__init__(self)
            self.images = [self.game.envrnmtSpritesheet.get_image(80, 48, 16, 16, 'plateforme'),
                           self.game.envrnmtSpritesheet.get_image(80, 64, 16, 16, 'plateforme'),
                           self.game.envrnmtSpritesheet.get_image(144, 0, 16, 16, 'plateforme')]
            self.image = self.images[0]
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.last_update = 0
            self.opened=False
            self.contenu()

        def contenu(self):
            if self.objet == 'daggerUn':
                self.img = self.game.dagerSpritesheet.get_image(0, 0, 48, 48, 'dagger')
                self.objet = Weapon(self.game, self.objet, self.img, DAGGER1_VIT, DAGGER1_RANGE, self.game.joueur )

        def update(self):
            pass

        def open(self):
            if not self.opened:
                self.animate()
                self.game.joueur.inventaire.add_weapon(self.objet)
                self.opened = True
        def animate(self):
            self.game.joueur.image = self.game.joueur.back_frame
            self.game.screen.fill(BGCOLOR)
            self.game.all_sprites.draw(self.game.screen)
            pg.display.flip()
            self.image = self.images[1]
            self.image.set_colorkey(BLACK)
            pg.time.wait(500)
            self.game.screen.fill(BGCOLOR)
            self.game.all_sprites.draw(self.game.screen)
            pg.display.flip()
            self.image = self.images[2]
            self.image.set_colorkey(BLACK)
            pg.time.wait(500)
            self.game.screen.fill(BGCOLOR)
            self.objet.rect.x = self.game.joueur.rect.x
            self.objet.rect.y = self.game.joueur.rect.y - self.objet.rect.height
            self.game.all_sprites.add(self.objet)
            self.game.all_sprites.draw(self.game.screen)
            pg.display.flip()
            pg.time.wait(1000)
            self.image = self.images[1]
            self.image.set_colorkey(BLACK)
            self.game.all_sprites.remove(self.objet)

class Objet(pg.sprite.Sprite):
    def __init__(self, game, name, sprite):
        pass
