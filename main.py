#!/usr/bin/python3
# coding: utf-8
import os, sys, pygame
from pygame.locals import *
from sources import *
from classes import *
from intelligence import *

class jeu(object):
    def __init__(self):
        pygame.init()
        # Fenêtre :
        os.environ["SDL_VIDEO_CENTERED"] = "1" # Centrage
        pygame.display.set_caption(nom_jeu) # Nom de la fenêtre
        pygame.display.set_icon(pygame.image.load(icone_jeu)) # Icone de la fenêtre
        self.screen = pygame.display.set_mode(dim_ecran) # Taille de la fenêtre
        self.fps = fps # Temps de rafraichissement écran
        self.clock = pygame.time.Clock() # Horloge
        self.intro = level(intro) # Chargement de l'écran d'accueil
        # Niveaux et personnages :
        self.actualLevel = 0
        self.level = level(niv[self.actualLevel]) # Chargement du niveau actuel
        self.pacman = pacman(self.level) # Chargement de Pacman
        self.fantome = [0, fantome(self.level, 1), fantome(self.level, 2), fantome(self.level, 3), fantome(self.level, 4)] # Chargement des fantomes
        self.graph = graph(self.level) # Création du graphe du niveau
        self.pos1 = self.pos2 = self.pos3 = self.pos4 = (-1, -1) # Pour le déplacement des fantomes
        self.posDef = [(1, 1), (28, 1), (28, 28), (1, 28), (7, 7), (22, 7), (22, 19), (7, 19)] # Pour les fantomes 2, 3 et 4
        self.done, self.go = False, False # Etats du jeu
        self.lastkey = self.newkey = self.i = self.j = self.k = 0 # Touches et paramètres
        # Sons :
        self.son_intro = pygame.mixer.Sound(son_intro)
        self.son_fin = pygame.mixer.Sound(son_fin)

    def reinitialiser(self):
        self.actualLevel += 1 # Niveau suivant
        self.level = level(niv[self.actualLevel]) # Chargement du niveau suivant
        self.pacman = pacman(self.level) # Chargement de Pacman
        self.fantome = [0, fantome(self.level, 1), fantome(self.level, 2), fantome(self.level, 3), fantome(self.level, 4)] # Chargement des fantomes
        self.graph = graph(self.level) # Création du graphe du niveau
        self.pos1 = self.pos2 = self.pos3 = self.pos4 = (-1, -1) # Pour le déplacement des fantomes
        self.posDef = [(1, 1), (28, 1), (28, 28), (1, 28), (7, 7), (22, 7), (22, 19), (7, 19)] # Pour les fantomes 2, 3 et 4
        self.done, self.go = False, False # Etats du jeu
        self.lastkey = self.newkey = self.i = self.j = self.k = 0 # Touches et paramètres

    def opening(self):
        self.son_intro.play() # Joue la musique
        self.intro.affiche(self.screen) # Ecran titre
        font = pygame.font.SysFont('Arial', 2 * taille_case);
        fontcredit = pygame.font.SysFont('Arial', taille_case);
        texte1 = font.render('APPUYEZ SUR UNE TOUCHE', True, (255, 0, 128));
        texte2 = font.render('POUR COMMENCER', True, (255, 174, 174));
        credit = fontcredit.render('Luminy 2017 - L2 Info - Projet python-pygame : "Pac-Man" par Arnaud Soulier', True, (255, 255, 0));
        self.screen.blit(texte1, (4 * taille_case, 21 * taille_case));
        self.screen.blit(texte2, (7 * taille_case, 23 * taille_case));
        self.screen.blit(credit, (taille_case, 28 * taille_case));
        self.screen.blit(self.pacman.sens, (18 * taille_case - taille_case//4, 26 * taille_case - taille_case//4))
        for i in range(1, 5): self.screen.blit(self.fantome[i].sens, ((2*i+7) * taille_case, 26 * taille_case))
        pygame.display.flip(); tap = False
        while not tap:
            event = pygame.event.poll()
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == KEYDOWN: tap = True; pygame.event.clear()
        self.son_intro.stop() # Arrête la musique
        print("-LET'S GO-")

    def event(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT: pygame.quit(); sys.exit() # Quitter
        elif event.type == KEYDOWN: # Surveillance des touches significatives
            self.newkey = event.key # Mise à jour de la touche en mémoire
            self.pacman.stop = False # Pacman rentre en mouvement

    def movePacman(self):
        change = 0
        if self.pacman.stop is True: return # Pacman s'arrête si obstacle
        else:
            if self.pacman.directionvalide(self.level, self.newkey): # Touche ignorée si obstacle
                if self.lastkey != self.newkey: self.lastkey = self.newkey; change = 1
        if self.lastkey == K_RIGHT: # Déplacement de Pacman
            #if change == 1: print("-FLECHE DROITE-")
            self.pacman.deplacer(self.screen, self.level, K_RIGHT); self.go = True
        elif self.lastkey == K_LEFT:
            #if change == 1: print("-FLECHE GAUCHE-")
            self.pacman.deplacer(self.screen, self.level, K_LEFT); self.go = True
        elif self.lastkey == K_DOWN:
            #if change == 1: print("-FLECHE BAS-")
            self.pacman.deplacer(self.screen, self.level, K_DOWN); self.go = True
        elif self.lastkey == K_UP:
            #if change == 1: print("-FLECHE HAUT-")
            self.pacman.deplacer(self.screen, self.level, K_UP); self.go = True
        else: self.go = False

    def fantomemort(self, x):
        pos = (-1, -1)
        if self.level.fantomepos[x] != self.level.fantomeposInit[x]:
            self.level.fantomepath[x] = LePlusCourtChemin(self.graph, self.level.fantomepos[x], self.level.fantomeposInit[x])
            pos = self.level.fantomepath[x].pop() # On dépile une coordonnée
        else: pos = self.level.fantomeposInit[x]; self.fantome[x].mort = 0
        return pos

    def moveFantomes(self):
        depart1, depart2, depart3, depart4 = 0, 40, 80, 160 # Horaires de départ
        if self.fantome[1].moveOver and self.pacman.nbMove > depart1: # Mise à jour chemin fantome 1
            if self.fantome[1].mort or self.level.vulnerable: # Si le fantome 1 est vulnérable ou mort, il retourne chez lui
                self.pos1 = self.fantomemort(1)
                if self.pos1 == self.level.fantomeposInit[1] and self.fantome[1].mort: self.fantome[1].mort = 0
            else: # Mise à jour normale
                if len(self.level.fantomepath[1]) < 2: # Si pile bientot vide, mise à  jour
                    self.level.fantomepath[1] = LePlusCourtChemin(self.graph, self.level.fantomepos[1], self.level.pacmanpos) # Calcul du chemin 1
                self.pos1 = self.level.fantomepath[1].pop() # On dépile une coordonnée
        if self.fantome[2].moveOver and self.pacman.nbMove > depart2: # Mise à jour chemin fantome 2
            if self.fantome[2].mort: self.pos2 = self.fantomemort(2) # Si le fantome 2 est mort, il retourne chez lui
            else: # Mise à jour normale
                if len(self.level.fantomepath[2]) < 2: # Si pile bientot vide, mise à  jour
                    self.i += 1
                    if self.i == 4: self.i = 0
                    self.level.fantomepath[2] = LePlusCourtChemin(self.graph, self.level.fantomepos[2], self.posDef[self.i]) # Calcul du chemin 2
                self.pos2 = self.level.fantomepath[2].pop() # On dépile une coordonnée
        if self.fantome[3].moveOver and self.pacman.nbMove > depart3: # Mise à jour chemin fantome 3
            if self.fantome[3].mort: self.pos3 = self.fantomemort(3) # Si le fantome 3 est mort, il retourne chez lui
            else: # Mise à jour normale
                if len(self.level.fantomepath[3]) < 2: # Si pile bientot vide, mise à  jour
                    self.j += 1
                    if self.j == 4: self.j = 0
                    self.level.fantomepath[3] = LePlusCourtChemin(self.graph, self.level.fantomepos[3], self.posDef[7-self.j]) # Calcul du chemin 3
                self.pos3 = self.level.fantomepath[3].pop() # On dépile une coordonnée
        if self.fantome[4].moveOver and self.pacman.nbMove > depart4: # Mise à jour chemin fantome 4
            if self.fantome[4].mort: self.pos4 = self.fantomemort(4) # Si le fantome 4 est mort, il retourne chez lui
            else: # Mise à jour normale
                if len(self.level.fantomepath[4]) < 2: # Si pile bientot vide, mise à  jour
                    self.k += 1
                    if self.k == 4: self.k = 0
                    self.level.fantomepath[4] = LePlusCourtChemin(self.graph, self.level.fantomepos[4], self.posDef[3-self.k]) # Calcul du chemin 4
                self.pos4 = self.level.fantomepath[4].pop() # On dépile une coordonnée
        if self.go:
            if self.pacman.nbMove > depart1: self.fantome[1].deplacer(self.screen, self.level, self.pos1) # Fantome 1 suit Pacman dès le début
            if self.pacman.nbMove > depart2: self.fantome[2].deplacer(self.screen, self.level, self.pos2) # Fantome 2 parcourt les coins
            if self.pacman.nbMove > depart3: self.fantome[3].deplacer(self.screen, self.level, self.pos3) # Fantome 3 tourne au milieu de la carte
            if self.pacman.nbMove > depart4: self.fantome[4].deplacer(self.screen, self.level, self.pos4) # Fantome 4 parcourt les coins dans un autre ordre

    def update(self):
        self.level.affiche(self.screen) # Nettoyage
        for i in range(1, 5): self.screen.blit(self.fantome[i].sens, (self.fantome[i].xR, self.fantome[i].yR)) # Affiche fantomes
        self.screen.blit(self.pacman.sens, (self.pacman.xR, self.pacman.yR)) # Affiche Pacman
        if self.pacman.nbMove == 0: self.leveltitle()
        pygame.display.flip() # Rafraichissement de l'écran
        self.clock.tick(self.fps) # Tic-tac de l'horloge
        if self.level.doneWin or self.level.doneLose: self.done = True # Condition de fin de niveau

    def leveltitle(self):
        font = pygame.font.SysFont('Arial', 5 * taille_case);
        title = font.render("LEVEL {0}".format(self.actualLevel+1), True, (37, 253, 233));
        self.screen.blit(title, (7 * taille_case, 15 * taille_case));

    def pause(self):
        if self.go == False and self.pacman.nbMove > 0:
            font = pygame.font.SysFont('Arial', 2 * taille_case);
            pause = font.render('PAUSE', True, (255, 140, 0));
            self.screen.blit(pause, (taille_case//2, 15 * taille_case));
            self.screen.blit(pause, (24 * taille_case, 15 * taille_case));
            pygame.display.flip(); tap = False; print("-PAUSE-")
            while not tap:
                event = pygame.event.poll()
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_UP or event.key == K_DOWN or event.key == K_LEFT or event.key == K_RIGHT:
                        self.newkey = event.key; self.pacman.stop = False; tap = True

    def fin(self):
        font = pygame.font.SysFont('Arial', 5 * taille_case);
        if self.level.doneWin:
            fin = font.render('  VICTORY !', True, (0, 255, 0))
            self.son_fin.play()
            print("-VICTORY !-")
        elif self.level.doneLose:
            fin = font.render('GAME OVER', True, (255, 0, 0))
            print("-GAME OVER-")
        self.screen.blit(fin, (3 * taille_case, 12 * taille_case));
        pygame.display.flip();
        if self.level.doneWin and self.actualLevel < len(niv)-1:
            pygame.time.wait(1000)
            font = pygame.font.SysFont('Arial', 3 * taille_case);
            nextlevel = font.render('Next Level', True, (255, 255, 255));
            self.screen.blit(nextlevel, (9 * taille_case, 17 * taille_case));
            pygame.display.flip();
            pygame.time.wait(1000)
            self.reinitialiser()
            self.main_loop()
        elif self.level.doneWin and self.actualLevel == len(niv)-1:
            pygame.time.wait(1000)
            font = pygame.font.SysFont('Arial', 3 * taille_case);
            merci = font.render('Merci d\'avoir jouer !', True, (255, 255, 255));
            self.screen.blit(merci, (5 * taille_case, 17 * taille_case));
            pygame.display.flip();

    def main_loop(self):
        print("-LEVEL {0}".format(self.actualLevel+1)+"-")
        while not self.done:
            self.event() # Surveillence du clavier
            self.movePacman() # Déplacement de Pacman
            self.moveFantomes() # Déplacement des fantomes
            self.update() # Mise à jour de l'affichage
            self.pause() # Pause si appui sur une touche non-significative
        self.fin()

if __name__ == "__main__":
    app = jeu()
    app.opening()
    app.main_loop()
    tap = False
    while not tap:
        event = pygame.event.poll()
        if event.type == pygame.QUIT or event.type == KEYDOWN: tap = True
    pygame.quit(); sys.exit()
