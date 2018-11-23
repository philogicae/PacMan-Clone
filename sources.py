
"""Constantes du jeu"""

# Fenetre :
nom_jeu = "Pac-Man"
icone_jeu = "images/icone.png"
intro = "niveaux/intro.txt"
indice = 6 # Chiffre à modifier si on veut déterminer la taille du jeu
cote_grille = 30
taille = 120*indice
dim_ecran = (taille, taille)
taille_case = taille//cote_grille
dim_case = (taille_case, taille_case)
dim_perso = (taille_case*4//3, taille_case*4//3)
fps = 20

# Images :
image_sprites = "images/sprites.png"
image_vide = "images/vide.png"
image_point = "images/point_jaune.png"
image_point_bonus = "images/point_bonus.png"
image_mur = "images/mur.png"
image_mur_angle = "images/mur_angle.png"
image_mur_bord = "images/mur_bord.png"
image_mur_bord_angle = "images/mur_bord_angle.png"
image_mur_bord_angle_ext = "images/mur_bord_angle_ext.png"
image_mur_porte = "images/mur_porte.png"

# Sons :
son_bille = "sons/mange_bille.wav"
son_mort = "sons/pacman_mort.wav"
son_fantome = "sons/mange_fantome.wav"
son_intro = "sons/musique_intro.wav"
son_fin = "sons/fin.wav"

# Niveaux du jeu :
niv = []
niv.append("niveaux/niveau1.txt")
niv.append("niveaux/niveau2.txt")
niv.append("niveaux/niveau3.txt")

""" Notice création de niveaux :
      C = position initiale de Pacman
1/2/3/4 = position initiale des fantomes
  -/_/p = case morte/case vide/case porte
    */# = point jaune/point bonus
    v/h = mur vertical/horizontal
H/D/B/G = mur bord haut/droite/bas/gauche
n/e/s/w = mur angle nord/est/sud/ouest, orienté vers (0,0)
N/E/S/W = mur bord angle nord/est/sud/ouest
A/Z/R/T = mur bord ext angle nord/est/sud/ouest """
