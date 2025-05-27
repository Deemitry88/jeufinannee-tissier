# Partie 4 : Ajout des collisions

import pygame
import time
from pygame.locals import *

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1200
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('The Celestial Brothers')
pygame.mixer.music.load("audio/music.wav")
hurtsound = pygame.mixer.Sound("audio/hurt.mp3")
hurtsound.set_volume(0.5)
getsound = pygame.mixer.Sound("audio/get.mp3")
getsound.set_volume(0.5)

# Variables du jeu
tile_size=25

#Chargement du fond d'écran
bg_img = pygame.image.load('image/misc/background_ai.png')
bg_img1 = pygame.transform.scale(bg_img,(screen_width,screen_height))

class Player():
    def __init__(self,x,y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1,4):
            img_right = pygame.image.load(f'image/entities/mario{num}.png')
            img_right = pygame.transform.scale(img_right, (40,40))
            #flip construit l'image symétrique par rapport à la verticale
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.img_hook = pygame.image.load(f'image/entities/mariohook.png')
        self.img_hook = pygame.transform.scale(self.img_hook, (40,40))
        self.img_hook_left = pygame.transform.flip(self.img_hook, True, False)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.vel_x = 0
        self.jumped = False
        self.direction = 0
        self.health = 10
        self.invicibility = False
        self.current = 0
        self.onroof = False
        self.pushed = False
        self.goomba_direction = 0
        self.points = 0

    def pushed_by(self,direction):
        self.goomba_direction = direction
        self.pushed = True

    def hurt(self):
        self.invicibility = True
        hurtsound.play()
        self.health -= 1
        self.current = pygame.time.get_ticks()

    def update(self):
        #Variables pour les déplacements
        global run
        dx=0
        dy=0
        walk_cooldown = 5

        if self.health <= 0:
            run = False

        if pygame.time.get_ticks() - self.current > 1000:
            self.invicibility = False

        if pygame.time.get_ticks() - self.current < 700:
            if ((pygame.time.get_ticks() - self.current) // 100) % 2:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

        #Réaction aux touches pressées
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and self.jumped == False :
            self.vel_y = -13
            self.jumped = True
        if key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
            dx -= 4
            self.counter += 1
            self.direction = -1
        if key[pygame.K_RIGHT] and not key[pygame.K_LEFT]:
            dx += 4
            self.counter += 1
            self.direction = 1
        if key[pygame.K_RIGHT] and key[pygame.K_LEFT]:
            dx += 4
            self.counter += 1
            self.direction = -1

        if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
            self.counter = 0
            self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]

        #animation du personnage
        if self.counter > walk_cooldown :
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]

        #Ajout de la gravité
        self.vel_y += 1
        if self.vel_y > 4:
            self.jumped = True
        if self.vel_y > 14:
            self.vel_y = 14
        dy += self.vel_y 

        if self.pushed:
            if self.goomba_direction == 1:
                dx += self.vel_x
            else:
                dx -= self.vel_x
            if abs(self.vel_x) > 8:
                self.vel_x = 0
                self.pushed = False
            self.vel_x += 1  
    
        #Vérification des collisions
        for tile in world.tile_list:
            # test des collisions horizontales
            if tile[1].colliderect(self.rect.x + dx,self.rect.y,self.width,self.height):
                dx = 0

            # test des collisions verticales
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                #test si on monte (saut sous un bloc)
                if self.vel_y < 0:
                    self.onroof = True
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = -15
                    if self.direction == 1:
                        self.image = self.img_hook
                    if self.direction == -1:
                        self.image = self.img_hook_left
                #test si on descend (saut vers le bas)
                elif self.vel_y > 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.jumped = False
                
            if pygame.sprite.spritecollide(self,spike_group, False) and self.invicibility == False:
                player.hurt()

        #Mise à jour des coordonnées du personnage
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0
            self.jumped = False
        if self.rect.x > screen_width - self.width:
            self.rect.x = screen_width - self.width
        if self.rect.x < 0:
            self.rect.x = 0

        #Trace le personnage sur l'écran
        screen.blit(self.image,self.rect)

class World():
    def __init__(self,data):
        self.tile_list = []
        #chargement des images
        murs = {x: pygame.image.load(f'image/terrain/mur{x}.png') for x in range(1, 14)}

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile in range(1, 14):
                    img = pygame.transform.scale(murs[tile],(tile_size,tile_size))
                    img_rect = img.get_rect()
                    img_rect.x= col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img,img_rect)
                    self.tile_list.append(tile)
                if tile == 15:
                    spike = Spike(col_count * tile_size, row_count * tile_size)
                    spike_group.add(spike)
                if tile == 16:
                    goomba = Enemy(col_count * tile_size, row_count * tile_size)
                    goomba_group.add(goomba)
                if tile == 17:
                    berry = Berry(col_count * tile_size, row_count * tile_size)
                    berry_group.add(berry)
                if tile == 18:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 19:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                col_count += 1
            row_count += 1

    def ecrire_message(self, message, message_rectangle,couleur):
        font = pygame.font.SysFont('lato', 40, False)
        message = font.render(message, True, couleur)
        screen.blit(message,message_rectangle)

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('image/terrain/platform.png')
        self.image = pygame.transform.scale(self.image, (tile_size * 3, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y
    
    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Spike(pygame.sprite.Sprite):
    def __init__(self, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.imageslist = []
        self.index = 0
        self.counter = 0
        for num in range(1,3):
            img = pygame.image.load(f'image/terrain/spike{num}.png')
            img = pygame.transform.scale(img,(tile_size,tile_size))
            self.imageslist.append(img)
        self.image = self.imageslist[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        cooldown = 20
        self.counter += 1
        if self.counter > cooldown*2-1:
            self.counter = 0
        self.image = self.imageslist[self.counter//cooldown]


class Berry(pygame.sprite.Sprite):
    def __init__(self, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.imageslist = []
        self.index = 0
        self.counter = 0
        for num in range(1,5):
            img = pygame.image.load(f'image/entities/berry{num}.png')
            img = pygame.transform.scale(img,(tile_size*2.5,tile_size))
            self.imageslist.append(img)
        self.image = self.imageslist[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        cooldown = 15
        self.counter += 1
        if self.counter > cooldown*4-1:
            self.counter = 0
        self.image = self.imageslist[self.counter//cooldown]
        if self.image == self.imageslist[2]:
            self.rect.y -= 1
        elif self.image == self.imageslist[0]:
            self.rect.y += 1

        if player.rect.colliderect(self.rect):
            berry_group.remove(self)
            pygame.mixer.Sound.play(getsound)
            player.points += 10

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.imageslist = []
        self.index = 0
        self.counter = 0
        for num in range(1,3):
            img = pygame.image.load(f'image/entities/goomba{num}.png')
            img = pygame.transform.scale(img,(30,30))
            self.imageslist.append(img)
        self.image = self.imageslist[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y-5
        self.move_direction = 1
        self.move_counter = 0
        self.dead = False

    def update(self):
        cooldown = 15
        self.counter += 1
        if self.counter > cooldown*2-1:
            self.counter = 0
        self.image = self.imageslist[self.counter//cooldown]

        
        self.rect.x += self.move_direction
        self.move_counter += 0.5
        if abs(self.move_counter) > 25:
            self.move_direction *= -1
            self.move_counter = 0
        for enemy in goomba_group:
            if player.rect.colliderect(self.rect):
        # si le joueur touche le haut de l'ennemi et est en train de tomber
                if player.rect.bottom <= self.rect.top + 10 and player.vel_y > 0:
                    player.vel_y = -10  # effet rebond
                    self.dead = True
                    goomba_group.remove(self)  # ou enemy.kill() si tu utilises Sprite
                    player.points += 5
                else:
            # collision sur le côté = dégâts (à adapter selon ton système)
                    if not player.invicibility and not self.dead:
                        player.pushed_by(self.move_direction)
                        player.vel_y = -6
                        player.hurt()


world_data = [
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,17,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,16,0,0,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,11,12,12,12,12,13,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,11,12,12,13,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
[3,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,5,0,0,0,6,7,4,5,0,0,0,0,0,0,0,0,0,0,17,0,0,0,0,0,0,0,0,0,0,0],
[6,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,6,7,0,0,0,6,7,1,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[8,10,0,0,16,0,0,0,0,0,0,16,0,0,0,0,8,8,10,15,15,15,8,10,9,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

player = Player(100, screen_height - 130)
goomba_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
berry_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
world = World(world_data)

run = True
pygame.mixer.music.play(-1)

while run:
    clock.tick(fps)
    screen.blit(bg_img1,(0,0))

    world.draw()
    player.update()
    goomba_group.update()
    goomba_group.draw(screen)
    spike_group.update()
    spike_group.draw(screen)
    berry_group.update()
    berry_group.draw(screen)
    platform_group.update()
    platform_group.draw(screen)

    world.ecrire_message(f"Health : {player.health}", (10, 10), (255, 0, 0))
    world.ecrire_message(f"Points : {player.points}", (10, 50), (255, 255, 0))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()