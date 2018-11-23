#!/usr/bin/python3
# coding: utf-8
import pygame
from pygame.locals import *
from sources import *
from intelligence import *

def formatimage(image_source, angle=0, dim=dim_case, sprite=(0, 0, 0)): # Fonction de formatage des images
    image = pygame.image.load(image_source).convert_alpha() # Chargement en mémoire
    if sprite[0] > 0: image = image.subsurface((16*sprite[1]+2, 16*sprite[2], sprite[0], sprite[0])) # Choix sprite
    image = pygame.transform.scale(image, dim) # Redimensionnement
    if angle != 0: image = pygame.transform.rotate(image, angle) # Orientation
    return image

class level:
    def __init__(self, niveau):
        # Récupération du niveau :
        with open(niveau, "r") as file:
            structure_level = []
            for ligne in file:
                ligne_level = []
                for case in ligne:
                    if case != '\n': ligne_level.append(case)
                structure_level.append(ligne_level)
            self.map =structure_level
        # Récupération de la position de Pacman et nombre de billes :
        self.pacmanpos = (-1, -1)
        self.billesrestantes = y = 0
        self.fantomepos = [0, (-1, -1), (-1, -1), (-1, -1), (-1, -1)]
        self.fantomeposInit = [0, (-1, -1), (-1, -1), (-1, -1), (-1, -1)]
        self.fantomepath = [0, [], [], [], []];
        for ligne in self.map:
            x = 0
            for case in ligne:
                if case == 'C': self.map[y][x] = '_'; self.pacmanpos = (x,y)
                elif case == '*': self.billesrestantes += 1
                elif case == '1': self.map[y][x] = '_'; self.fantomepos[1] = self.fantomeposInit[1] = (x,y)
                elif case == '2': self.map[y][x] = '_'; self.fantomepos[2] = self.fantomeposInit[2] = (x,y)
                elif case == '3': self.map[y][x] = '_'; self.fantomepos[3] = self.fantomeposInit[3] = (x,y)
                elif case == '4': self.map[y][x] = '_'; self.fantomepos[4] = self.fantomeposInit[4] = (x,y)
                x += 1
            y += 1
        self.vulnerable, self.time, self.blanc = 0, 0, 0 # Paramètres pour la vulnérabilité des fantomes
        self.doneWin, self.doneLose = False, False # Fin du niveau
        # Images :
        self.vide = formatimage(image_vide)
        self.pointjaune = formatimage(image_point)
        self.pointbonus = formatimage(image_point_bonus)
        self.murp = formatimage(image_mur_porte)
        self.murv = formatimage(image_mur)
        self.murh = formatimage(image_mur, 90)
        self.murn = formatimage(image_mur_angle)
        self.murw = formatimage(image_mur_angle, 90)
        self.murs = formatimage(image_mur_angle, 180)
        self.mure = formatimage(image_mur_angle, 270)
        self.murH = formatimage(image_mur_bord)
        self.murG = formatimage(image_mur_bord, 90)
        self.murB = formatimage(image_mur_bord, 180)
        self.murD = formatimage(image_mur_bord, 270)
        self.murN = formatimage(image_mur_bord_angle)
        self.murW = formatimage(image_mur_bord_angle, 90)
        self.murS = formatimage(image_mur_bord_angle, 180)
        self.murE = formatimage(image_mur_bord_angle, 270)
        self.murNe = formatimage(image_mur_bord_angle_ext)
        self.murWe = formatimage(image_mur_bord_angle_ext, 90)
        self.murSe = formatimage(image_mur_bord_angle_ext, 180)
        self.murEe = formatimage(image_mur_bord_angle_ext, 270)

    def affiche(self, fenetre): # Affichage carte
        num_ligne = 0
        for ligne in self.map:
            num_case = 0
            for case in ligne:
                x, y = num_case * taille_case, num_ligne * taille_case
                if case == '_': fenetre.blit(self.vide,(x,y))
                elif case == '-': fenetre.blit(self.vide,(x,y))
                elif case == '*': fenetre.blit(self.pointjaune,(x,y))
                elif case == '#': fenetre.blit(self.pointbonus,(x,y))
                elif case == 'p': fenetre.blit(self.murp,(x,y))
                elif case == 'v': fenetre.blit(self.murv,(x,y))
                elif case == 'h': fenetre.blit(self.murh,(x,y))
                elif case == 'n': fenetre.blit(self.murn,(x,y))
                elif case == 'e': fenetre.blit(self.mure,(x,y))
                elif case == 's': fenetre.blit(self.murs,(x,y))
                elif case == 'w': fenetre.blit(self.murw,(x,y))
                elif case == 'H': fenetre.blit(self.murH,(x,y))
                elif case == 'D': fenetre.blit(self.murD,(x,y))
                elif case == 'B': fenetre.blit(self.murB,(x,y))
                elif case == 'G': fenetre.blit(self.murG,(x,y))
                elif case == 'N': fenetre.blit(self.murN,(x,y))
                elif case == 'E': fenetre.blit(self.murE,(x,y))
                elif case == 'S': fenetre.blit(self.murS,(x,y))
                elif case == 'W': fenetre.blit(self.murW,(x,y))
                elif case == 'A': fenetre.blit(self.murNe,(x,y))
                elif case == 'Z': fenetre.blit(self.murEe,(x,y))
                elif case == 'R': fenetre.blit(self.murSe,(x,y))
                elif case == 'T': fenetre.blit(self.murWe,(x,y))
                num_case += 1
            num_ligne += 1

    def posvalide(self, pos):
        if self.map[pos[1]][pos[0]] == '_' or self.map[pos[1]][pos[0]] == '*' or self.map[pos[1]][pos[0]] == '#' or self.map[pos[1]][pos[0]] == 'p':
            return True
        return False

class pacman:
    def __init__(self, level):
        # Données perso :
        self.x, self.y = level.pacmanpos[0], level.pacmanpos[1] # Position sur la grille
        self.xR = self.x * taille_case - taille_case//4 + taille_case*2//3 # Position dans la fenêtre
        self.yR = self.y * taille_case - taille_case//4 + taille_case//10
        self.step, self.img = 0, 1 # étape et numéro image dans l'animation des sprites
        self.l = self.c = self.bord = self.nbMove = self.compt = 0 # Paramètres de déplacement
        self.stop = True # Pacman est-il en mouvement ?
        # Images :
        self.droite, self.haut, self.gauche, self.bas, self.mort = [], [], [], [], []
        self.droite.append(formatimage(image_sprites, 0, dim_perso, (32, 6, 1)))
        self.droite.append(formatimage(image_sprites, 0, dim_perso, (32, 4, 1)))
        self.droite.append(formatimage(image_sprites, 0, dim_perso, (32, 2, 1)))
        self.haut.append(formatimage(image_sprites, 90, dim_perso, (32, 6, 1)))
        self.haut.append(formatimage(image_sprites, 90, dim_perso, (32, 4, 1)))
        self.haut.append(formatimage(image_sprites, 90, dim_perso, (32, 2, 1)))
        self.gauche.append(formatimage(image_sprites, 180, dim_perso, (32, 6, 1)))
        self.gauche.append(formatimage(image_sprites, 180, dim_perso, (32, 4, 1)))
        self.gauche.append(formatimage(image_sprites, 180, dim_perso, (32, 2, 1)))
        self.bas.append(formatimage(image_sprites, 270, dim_perso, (32, 6, 1)))
        self.bas.append(formatimage(image_sprites, 270, dim_perso, (32, 4, 1)))
        self.bas.append(formatimage(image_sprites, 270, dim_perso, (32, 2, 1)))
        for i in range(0, 12): self.mort.append(formatimage(image_sprites, 0, dim_perso, (16, 2+i, 0)))
        self.sens = self.droite[1] # sprite courant
        # Sons :
        self.son_bille = pygame.mixer.Sound(son_bille)
        self.son_mort = pygame.mixer.Sound(son_mort)

    def directionvalide(self, level, direction): # Vérifie si Pacman peut aller par là
        l = c = bord = 0
        if self.y == 13 and self.x == 0 and direction == K_LEFT: bord = 30
        elif self.y == 13 and self.x == 29 and direction == K_RIGHT: bord = -30
        if direction == K_RIGHT: l += 1
        elif direction == K_LEFT: l -= 1
        elif direction == K_DOWN: c += 1
        elif direction == K_UP: c -= 1
        if level.map[self.y+c][self.x+l+bord] == '_' or level.map[self.y+c][self.x+l+bord] == '*' or level.map[self.y+c][self.x+l+bord] == '#':
            return True
        return False

    def deplacer(self, fenetre, level, direction): # Déplacement de Pacman
        if level.vulnerable: pass
        elif self.compt > 0 or level.pacmanpos == level.fantomepos[1] or level.pacmanpos == level.fantomepos[2] or level.pacmanpos == level.fantomepos[3] or level.pacmanpos == level.fantomepos[4]:
            self.sens = self.mort[self.compt]; self.compt += 1; # Conditions pour la collision avec un fantome = mort de Pacman
            if self.compt == 12: level.doneLose = True; self.son_mort.play() # Fin du niveau en cas de défaite
            return
        if self.step == 0: # Mise à jour de Pacman sur la grille si nécessaire
            self.l = self.c = self.bord = 0 # Paramètres de déplacement
            if self.y == 13 and self.x == 0 and direction == K_LEFT: self.bord = 30 # Saut coté gauche
            elif self.y == 13 and self.x == 29 and direction == K_RIGHT: self.bord = -30 # Saut coté droite
            if direction == K_RIGHT: self.l += 1 # Calcul de la direction
            elif direction == K_LEFT: self.l -= 1
            elif direction == K_DOWN: self.c += 1
            elif direction == K_UP: self.c -= 1
            if self.directionvalide(level, direction): # Si la case d'arrivée est bonne
                self.x += self.l + self.bord # Mise à jour des coordonnées de Pacman
                self.y += self.c
                level.pacmanpos = (self.x, self.y) # Mise à jour position de Pacman dans le level
            else: self.stop = True; return # Stop si Pacman butte sur un obstacle
        self.nbMove += 1 # Comptage des déplacements
        if self.step%3 == 0: self.img += 1 # Calcul du bon sprite pour le bon mouvement
        else: self.img -= 1
        if self.nbMove == 1 and direction == K_LEFT: self.xR -= taille_case*6//10 # Si 1er déplacement à gauche = Correction
        elif self.nbMove == 1 and direction == K_RIGHT: self.xR -= taille_case//10; self.step, self.img = 2, 0 # ou à droite = Correction
        elif self.step == 2: self.xR += self.bord * taille_case # Si Pacman doit passer d'un bord à l'autre = Correction pour le saut
        self.xR += self.l * taille_case//4 # Calcul nouveau xR
        self.yR += self.c * taille_case//4 # Calcul nouveau yR
        if level.map[self.y][self.x] == '*' and self.step == 3: # Comptage et effacement des points jaunes lors du passage de Pacman
            level.map[self.y][self.x] = '_'; level.billesrestantes -= 1; self.son_bille.play()
            if level.billesrestantes == 0: level.doneWin = True # Fin du niveau en cas de victoire
        elif level.map[self.y][self.x] == '#' and self.step == 3: # Comptage et effacement du point bonus lors du passage de Pacman
            level.map[self.y][self.x] = '_'; level.vulnerable = 1; level.time = self.nbMove # Les fantomes deviennent vulnérables
        if 0 < level.time and level.time+140 < self.nbMove: level.vulnerable = level.time = level.blanc = 0 # Fin de vulnérabilité
        elif 0 < level.time and level.time+100 < self.nbMove: # Fin de vulnérabilité imminente
            if self.nbMove%8 == 0 or (self.nbMove-1)%8 == 0 or (self.nbMove-2)%8 == 0 or (self.nbMove-3)%8 == 0: level.blanc = 2
            else: level.blanc = 0
        if direction == K_RIGHT: self.sens = self.droite[self.img] # Mise à jour du sprite actuel
        elif direction == K_LEFT: self.sens = self.gauche[self.img]
        elif direction == K_DOWN: self.sens = self.bas[self.img]
        elif direction == K_UP: self.sens = self.haut[self.img]
        if self.step <= 2 : self.step += 1 # Incrémentation étape animation
        else: self.step = 0

class fantome:
    def __init__(self, level, num):
        # Données perso :
        self.num = num # numéro du fantome
        self.x, self.y = level.fantomepos[num][0], level.fantomepos[num][1] # Position sur la grille
        self.xR, self.yR = self.x * taille_case, self.y * taille_case # Position dans la fenêtre
        self.l = self.c = self.step = self.img = self.moveOver = self.mort = 0 # Paramètres, étape et numéro-image dans l'animation des sprites
        # Images :
        self.droite, self.gauche, self.haut, self.bas, self.peur = [], [], [], [], []
        self.droite.append(formatimage(image_sprites, 0, dim_case, (16, 0, 3+num)))
        self.droite.append(formatimage(image_sprites, 0, dim_case, (16, 1, 3+num)))
        self.droite.append(formatimage(image_sprites, 0, dim_case, (16, 8, 5)))
        self.gauche.append(formatimage(image_sprites, 0, dim_case, (16, 2, 3+num)))
        self.gauche.append(formatimage(image_sprites, 0, dim_case, (16, 3, 3+num)))
        self.gauche.append(formatimage(image_sprites, 0, dim_case, (16, 9, 5)))
        self.haut.append(formatimage(image_sprites, 0, dim_case, (16, 4, 3+num)))
        self.haut.append(formatimage(image_sprites, 0, dim_case, (16, 5, 3+num)))
        self.haut.append(formatimage(image_sprites, 0, dim_case, (16, 10, 5)))
        self.bas.append(formatimage(image_sprites, 0, dim_case, (16, 6, 3+num)))
        self.bas.append(formatimage(image_sprites, 0, dim_case, (16, 7, 3+num)))
        self.bas.append(formatimage(image_sprites, 0, dim_case, (16, 11, 5)))
        self.peur.append(formatimage(image_sprites, 0, dim_case, (16, 8, 4)))
        self.peur.append(formatimage(image_sprites, 0, dim_case, (16, 9, 4)))
        self.peur.append(formatimage(image_sprites, 0, dim_case, (16, 10, 4)))
        self.peur.append(formatimage(image_sprites, 0, dim_case, (16, 11, 4)))
        self.sens = self.droite[0] # sprite courant
        # Sons :
        self.son_fantome = pygame.mixer.Sound(son_fantome)

    def deplacer(self, fenetre, level, pos): # Déplacement d'un fantome
        if not level.vulnerable and (level.pacmanpos == level.fantomepos[1] or level.pacmanpos == level.fantomepos[2] or level.pacmanpos == level.fantomepos[3] or level.pacmanpos == level.fantomepos[4]):
            return
        elif level.vulnerable and level.pacmanpos == level.fantomepos[self.num]:
            self.mort = 1; self.son_fantome.play()
        if level.posvalide(pos):
            if self.step == 0: # Quand on lit une nouvelle position
                self.l, self.c = pos[0]-self.x, pos[1]-self.y # Paramètres utiles
                self.x, self.y = pos[0], pos[1] # Mise à jour position du fantome dans sa classe
                level.fantomepos[self.num] = (self.x, self.y) # Mise à jour position du fantome dans le level
            if self.step <= 2: self.img = 1 # Choix sprite
            else: self.img = 0
            self.xR += self.l * taille_case//4 # Calcul nouveau xR
            self.yR += self.c * taille_case//4 # Calcul nouveau yR
            if self.l == 1: # Mise à jour des sprites actuels
                if self.mort: self.sens = self.droite[2] # si Etat mort
                elif level.vulnerable: self.sens = self.peur[self.img+level.blanc] # si Etat vulnérable
                else: self.sens = self.droite[self.img] # Si fantome vivant
            elif self.l == -1:
                if self.mort: self.sens = self.gauche[2] # si Etat mort
                elif level.vulnerable: self.sens = self.peur[self.img+level.blanc] # si Etat vulnérable
                else: self.sens = self.gauche[self.img] # Si fantome vivant
            elif self.c == 1:
                if self.mort: self.sens = self.haut[2] # si Etat mort
                elif level.vulnerable: self.sens = self.peur[self.img+level.blanc] # si Etat vulnérable
                else: self.sens = self.haut[self.img] # Si fantome vivant
            elif self.c == -1:
                if self.mort: self.sens = self.bas[2] # si Etat mort
                elif level.vulnerable: self.sens = self.peur[self.img+level.blanc] # si Etat vulnérable
                else: self.sens = self.bas[self.img] # Si fantome vivant
            elif self.l > 20 or self.l < -20: self.sens = level.vide
            else: self.sens = self.droite[0]
            if self.step <=2 : self.step += 1; self.moveOver = False # Incrémentation étape animation
            else: self.step = 0; self.moveOver = True
        else: self.moveOver = True
