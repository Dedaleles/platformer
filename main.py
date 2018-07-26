# --FICHIER PRINCIPAL--
# on importe les librairies
from constantes import *
import pygame as pg #on raccourci pygame en pg
from sprites import *
import random
from os import path
vec = pg.math.Vector2
# on crée la classe du jeux
class Game:

    def __init__(self):
        # on initialise la fenetre, les modules de pygame, le temp etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.lenNiv = vec(0, 0)
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        self.rangerSpritesheet = Spritesheet(path.join(img_dir, RANGER_SPRITESHEET))
        self.envrnmtSpritesheet = Spritesheet(path.join(img_dir, ENVRNMT_SPRITESHEET))
        self.dagerSpritesheet = Spritesheet(path.join(img_dir, DAGGER_SPRITESHEET))

    def new(self):
        # pour démarrer une nouvelle partie
        self.all_sprites = pg.sprite.Group()
        self.entities = pg.sprite.Group()
        self.coffres = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.sol = pg.sprite.Group()
        self.weaponsGroup = pg.sprite.Group()
        self.ennemis = pg.sprite.Group()
        self.serpent = Serpent(500,self)
        self.joueur = Joueur(self, 1)
        self.posSol = 0
        self.lenNiv = vec(0, 0)
        self.build_niveau(1)
        self.all_sprites.add(self.joueur)
        self.entities.add(self.joueur)
        self.all_sprites.add(self.serpent)
        self.entities.add(self.serpent)
        self.ennemis.add(self.serpent)
        self.run()


    def run(self):
        # boucle principale
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.update()
            self.events()
            self.draw()

    def update(self):
        # boucle principale - update
        self.all_sprites.update()
        #collisions
        for entitie in self.entities:
            if entitie.vel.y > 0:
                hits = pg.sprite.spritecollide(entitie, self.platforms, False)
                if hits:
                    if entitie.pos.y < hits[0].rect.bottom:
                        entitie.pos.y = hits[0].rect.top
                        entitie.vel.y = 0
                        entitie.jumping = False

        if self.joueur.weapon.go:
            hits = pg.sprite.spritecollide(self.joueur.weapon, self.platforms, False)
            if hits:
                self.joueur.weapon.stop()
        #scrolling horizontal

        if self.joueur.pos.x >= WIDTH * 3/4 and self.joueur.vel.x > 0 and self.posSol.rect.x > -self.lenNiv.x +  WIDTH * 5/4:
            self.joueur.pos.x -= abs(self.joueur.vel.x)
            for plat in self.platforms:
                plat.rect.x -= abs(int(self.joueur.vel.x + 0.5 * self.joueur.acc.x - self.joueur.acc.x))
            for coffre in self.coffres:
                coffre.rect.x -= abs(int(self.joueur.vel.x + 0.5 * self.joueur.acc.x - self.joueur.acc.x))

        if self.joueur.pos.x <= WIDTH / 4 and self.joueur.vel.x < 0 and -(self.posSol.rect.x) > 0:
            self.joueur.pos.x += abs(self.joueur.vel.x)
            for plat in self.platforms:
                plat.rect.x += abs(int(self.joueur.vel.x - 0.5 * self.joueur.acc.x - self.joueur.acc.x))
            for coffre in self.coffres:
                coffre.rect.x += abs(int(self.joueur.vel.x + 0.5 * self.joueur.acc.x - self.joueur.acc.x))

    def events(self):
        # boucle principale - événements
        for event in pg.event.get(): # on traite les événements
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.joueur.jump()
                    if event.key == pg.K_s:
                        self.joueur.switch_weapon()
                if event.type == pg.KEYUP:
                    if event.key == pg.K_SPACE:
                        self.joueur.jump_cut()
                    if event.key == pg.K_o:
                        touch = pg.sprite.spritecollide(self.joueur, self.coffres, False)
                        if touch:
                            touch[0].open()
                    if event.key == pg.K_u:
                        if self.joueur.throwing == False:
                            self.joueur.throwing = True
                            self.joueur.weapon.use(self.joueur.rect.x, self.joueur.rect.y)

                    if event.key == pg.K_DOWN:
                        self.joueur.standing = True

    def draw(self):
        # boucle principal - affiche les sprites à l'écran
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def build_niveau(self, niveau):
        niveau_en_cours = open(path.join(self.dir, 'niveau', 'niv{}'.format(niveau)), 'r')
        i=0
        j=0
        for ligne in niveau_en_cours:
            i=0
            for carac in ligne:
                if carac == '0':
                    texture = self.envrnmtSpritesheet.get_image(0, 0, 16, 16, 'plateforme')
                    texture_width = texture.get_rect().width
                    texture_height = texture.get_rect().height
                    sol = Plateforme(self, i*texture_width, j*texture_width, texture)
                    self.all_sprites.add(sol)
                    self.platforms.add(sol)
                    if i == 0 and j == 13:
                        self.posSol = sol

                if carac == '1':
                    print(ligne)
                    texture = self.envrnmtSpritesheet.get_image(0, 16, 16, 16, 'plateforme')
                    texture_width = texture.get_rect().width
                    texture_height = texture.get_rect().height
                    sol = Plateforme(self, i*texture_width, j*texture_width, texture)
                    self.all_sprites.add(sol)
                    self.platforms.add(sol)
                    if i == 0 and j == 14:
                        self.posSol = sol
                    print(ligne)

                if carac == '2':
                    texture = self.envrnmtSpritesheet.get_image(0, 32, 16, 16, 'plateforme')
                    texture_width = texture.get_rect().width
                    texture_height = texture.get_rect().height
                    sol = Plateforme(self, i*texture_width, j*texture_width, texture)
                    self.all_sprites.add(sol)
                    self.platforms.add(sol)
                    if i == 0 and j == 14:
                        self.posSol = sol

                if carac == '3':
                    texture = self.envrnmtSpritesheet.get_image(32, 96, 16, 16, 'plateforme')
                    texture_width = texture.get_rect().width
                    texture_height = texture.get_rect().height
                    sol = Plateforme(self, i*texture_width, j*texture_width, texture)
                    self.all_sprites.add(sol)
                    self.platforms.add(sol)
                    if i == 0 and j == 14:
                        self.posSol = sol

                if carac == 'C':
                    contenu = ligne[i+2:]
                    print(contenu)
                    contenu = contenu[:contenu.find(')')]
                    print(contenu)
                    ligne= ligne.replace('('+contenu+')', '')
                    print(ligne)
                    c = Coffre(self, i*64, j*64, contenu)
                    self.all_sprites.add(c)
                    self.coffres.add(c)

                i+=1
            j+=1
        self.lenNiv.x =i*texture_width
        print(i)
        self.lenNiv.y = j*texture_height


    def show_start_screen(self):
        # écran d'acceuil
        pass

    def show_go_screen(self):
        #écran de game over
        pass

g = Game()
g.new()

pg.quit()
