#!/usr/bin/python3
# coding: utf-8
import pygame
from pygame.locals import *
from sources import *
from classes import *
from collections import defaultdict

class graph:
    def __init__(self, niveau):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}
        self.build(niveau)

    def add_node(self, pos):
        self.nodes.add(pos)

    def add_edge(self, node1, node2):
        self.edges[node1].append(node2)
        self.edges[node2].append(node1)
        self.distances[(node1, node2)] = 1
        self.distances[(node2, node1)] = 1

    def build(self, niveau):
        for j in range(cote_grille):
            for i in range(cote_grille):
                if niveau.posvalide((i, j)):
                    self.add_node((i, j))
                    right = down = 1
                    if i+right == cote_grille: right -= cote_grille
                    if j+down == cote_grille: down -= cote_grille
                    if niveau.posvalide((i+right, j)): self.add_edge((i, j), (i+right, j))
                    if niveau.posvalide((i, j+down)): self.add_edge((i, j), (i, j+down))

def Dijkstra(graph, initial):
    visited, path = {initial: 0}, {}
    nodes = set(graph.nodes)
    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None: min_node = node
                elif visited[node] < visited[min_node]: min_node = node
        if min_node is None: break
        nodes.remove(min_node)
        current_weight = visited[min_node]
        for edge in graph.edges[min_node]:
            weight = current_weight + graph.distances[(min_node, edge)]
            if edge not in visited or weight < visited[edge]:
                visited[edge], path[edge] = weight, min_node
    return path

def LePlusCourtChemin(graph, debut, fin):
    path = Dijkstra(graph, debut)
    solution = []; solution.append(fin);
    courant = solution[0]
    while path.get(courant) != debut:
        solution.append(path.get(courant))
        courant = solution[len(solution)-1]
    return solution
