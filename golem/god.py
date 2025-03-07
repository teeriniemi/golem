#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 15:46:51 2023

@author: surrealpartisan
"""

import numpy as np
from golem import creature
from golem import item
from golem import utils


class God(creature.Creature):
    def __init__(self, world, world_i, sin):
        super().__init__(world, world_i)
        self.sin = sin
        self.factions = [np.random.choice(utils.enemyfactions)]
        self.firstname = utils.unpronounceablename(np.random.randint(2, 11))
        self.nickname = 'The ' + \
            np.random.choice(utils.godlynicknames[self.sin])
        self.name = self.firstname + ' ' + self.nickname
        self.power = np.random.choice(['weak', 'powerful'])
        self.attitude = np.random.choice(['mellow', 'irritable'])
        self.pronoun = np.random.choice(['he', 'she', 'they', 'it'])
        if self.pronoun == 'they':
            self.copula = 'are'
        else:
            self.copula = 'is'
        self.prayerclocks = {}

    def bless(self, creat):
        if self.sin == 'gluttony':
            gift = item.randomfood(creat.inventory, 0, 0)
        elif self.sin == 'wrath':
            gift = item.randomweapon(creat.inventory, 0, 0, creat.world_i)
        else:
            blessing = np.random.randint(5)
            if blessing == 0:
                gift = item.Cure(creat.inventory, 0, 0, creat.world.curetypes[np.random.randint(len(
                    creat.world.curetypes))], np.random.randint(max(1, creat.world_i), creat.world_i+3))
            if blessing == 1:
                gift = item.randomweapon(creat.inventory, 0, 0, creat.world_i)
            if blessing == 2:
                gift = item.randomarmor(creat.inventory, 0, 0, creat.world_i)
            if blessing == 3:
                gift = item.randomfood(creat.inventory, 0, 0)
            if blessing == 4:
                gift = item.randomUtilityItem(creat.inventory, 0, 0)
        creat.log().append(self.name + ' has blessed you with a ' + gift.name + '!')

    def smite(self, target):
        if self.sin == 'gluttony':
            if self.power == 'powerful':
                target.hunger = 100
                self.log().append('You starved the' + target.name + ' really badly!')
                target.log().append(self.name + ' starved you really badly!')
            else:
                target.hunger = 50
                self.log().append('You starved the' + target.name + '!')
                target.log().append(self.name + ' starved you!')
        elif (self.sin == 'lust' or self.sin == 'envy') and len([it[0] for part in target.bodyparts for it in part.worn.values() if len(it) > 0]) > 0:
            wornlist = [
                it[0] for part in target.bodyparts for it in part.worn.values() if len(it) > 0]
            if self.power == 'powerful':
                for it in wornlist:
                    it.owner.remove(it)
                self.log().append('You stripped away everything the' + target.name + ' was wearing!')
                target.log().append(self.name + ' stripped away everything you were wearing!')
            else:
                it = np.random.choice(wornlist)
                it.owner.remove(it)
                self.log().append('You stripped away the' + it.name +
                                  'the' + target.name + ' was wearing!')
                target.log().append(self.name + ' stripped away the ' + it.name + ' you were wearing!')
        else:
            targetbodypart = np.random.choice(
                [part for part in target.bodyparts if not part.destroyed() and not part.incapacitated()])
            target.lasthitter = self
            if self.power == 'powerful':
                totaldamage = np.random.randint(1, 20*(target.world_i+1) + 1)
            else:
                totaldamage = np.random.randint(1, 10*(target.world_i+1) + 1)
            damage = min(totaldamage, targetbodypart.hp())
            targetbodypart.damagetaken += damage
            if targetbodypart.parentalconnection != None:
                partname = list(targetbodypart.parentalconnection.parent.childconnections.keys())[list(
                    targetbodypart.parentalconnection.parent.childconnections.values()).index(targetbodypart.parentalconnection)]
            elif targetbodypart == target.torso:
                partname = 'torso'
            alreadyimbalanced = target.imbalanced()
            if 'leg' in targetbodypart.categories:
                numlegs = len([p for p in self.bodyparts if 'leg' in p.categories and not p.destroyed(
                ) and not p.incapacitated()])
                if np.random.rand() < 0.5 - 0.05*numlegs:
                    targetbodypart.imbalanceclock += 20*damage/targetbodypart.maxhp
            if not target.dying():
                if not targetbodypart.destroyed() and not targetbodypart.incapacitated():
                    if target.imbalanced() and not alreadyimbalanced:
                        self.log().append('You smote the ' + target.name + ' in the ' + partname +
                                          ', dealing ' + repr(damage) + ' damage and imbalancing it!')
                        target.log().append(self.name + ' smote you in the ' + partname +
                                            ', dealing ' + repr(damage) + ' damage and imbalancing you!')
                    else:
                        self.log().append('You smote the ' + target.name + ' in the ' +
                                          partname + ', dealing ' + repr(damage) + ' damage!')
                        target.log().append(self.name + ' smote you in the ' +
                                            partname + ', dealing ' + repr(damage) + ' damage!')
                elif targetbodypart.incapacitated() and not targetbodypart.destroyed():
                    if target.imbalanced() and not alreadyimbalanced:
                        self.log().append('You smote and incapacitated the ' +
                                          partname + ' of the ' + target.name + ', imbalancing it!')
                        target.log().append(self.name + ' smote and incapacitated your ' +
                                            partname + ', imbalancing you!')
                    else:
                        self.log().append('You smote and incapacitated the ' +
                                          partname + ' of the ' + target.name + '!')
                        target.log().append(self.name + ' smote and incapacitated your ' + partname + '!')
                else:
                    if target.imbalanced() and not alreadyimbalanced:
                        self.log().append('You smote and destroyed the ' + partname +
                                          ' of the ' + target.name + ', imbalancing it!!')
                        target.log().append(self.name + ' smote and destroyed your ' +
                                            partname + ', imbalancing you!')
                    else:
                        self.log().append('You smote and destroyed the ' +
                                          partname + ' of the ' + target.name + '!')
                        target.log().append(self.name + ' smote and destroyed your ' + partname + '!')
                    targetbodypart.on_destruction(False)
            else:
                self.log().append('You smote the ' + target.name +
                                  ' in the ' + partname + ', killing it!')
                target.log().append(self.name + ' smote you in the ' + partname + ', killing you!')
                target.log().append('You are dead!')
                if targetbodypart.destroyed():
                    targetbodypart.on_destruction(True)
                target.die()
                target.causeofdeath = ('smite', self)

    def answer_to_prayer(self, creat):
        if self.attitude == 'irritable':
            limit = 200/creat.godlylove()
        else:
            limit = 100/creat.godlylove()
        if not creat in self.prayerclocks or self.prayerclocks[creat] > limit:
            creat.log().append(self.name + ' is pleased by your prayer.')
            self.bless(creat)
        else:
            creat.log().append(self.name + ' is angered by your constant pleading.')
            self.smite(creat)
        self.prayerclocks[creat] = 0
