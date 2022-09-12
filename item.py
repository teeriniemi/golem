# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 20:48:19 2022

@author: SurrealPartisan
"""

class Item():
    def __init__(self, owner, x, y, name, char, color):
        self.owner = owner # A list, such as inventory or list of map items
        self.owner.append(self)
        self.x = x
        self.y = y
        self.name = name
        self.char = char
        self.color = color
        self.consumable = False
        self.wieldable = False
        self.weapon = False

class Consumable(Item):
    def __init__(self, owner, x, y, name, char, color):
        super().__init__(owner, x, y, name, char, color)
        self.consumable = True
        self.hpgiven = 0
    
    def consume(self, user):
        user.heal(self.hpgiven)
        self.owner.remove(self)

def create_medication(owner, x, y):
    drugs = Consumable(owner, x, y, 'packet of drugs', '!', (0, 255, 255))
    drugs.hpgiven = 10