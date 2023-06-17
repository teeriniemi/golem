import sys

import pygame
from pygame.locals import *
import pygcurse
import numpy as np

import item
import creature
import world
import bodypart

pygame.init()

mapwidth, mapheight = 80, 40
logheight = 8
statuslines = 1
win = pygcurse.PygcurseWindow(mapwidth, mapheight + statuslines + logheight, 'Golem: A Self-Made Person')
win.font = pygame.font.Font('Hack-Regular.ttf', 12)
win.autoupdate = False
cave = world.World(mapwidth, mapheight)
cave.rooms()

player = creature.Creature(cave)
player.torso = bodypart.HumanTorso(player.bodyparts, 0, 0)
player.bodyparts[0].connect('left arm', bodypart.HumanArm(player.bodyparts, 0, 0))
player.bodyparts[0].connect('right arm', bodypart.HumanArm(player.bodyparts, 0, 0))
player.bodyparts[0].connect('left leg', bodypart.HumanLeg(player.bodyparts, 0, 0))
player.bodyparts[0].connect('right leg', bodypart.HumanLeg(player.bodyparts, 0, 0))
player.bodyparts[0].connect('heart', bodypart.HumanHeart(player.bodyparts, 0, 0))
player.bodyparts[0].connect('head', bodypart.HumanHead(player.bodyparts, 0, 0))
player.bodyparts[-1].connect('brain', bodypart.HumanBrain(player.bodyparts, 0, 0))
player.bodyparts[-2].connect('left eye', bodypart.HumanEye(player.bodyparts, 0, 0))
player.bodyparts[-3].connect('right eye', bodypart.HumanEye(player.bodyparts, 0, 0))
player.faction = 'player'
while cave.walls[player.x, player.y] != 0:
    player.x= np.random.randint(mapwidth)
    player.y = np.random.randint(mapheight)
cave.creatures.append(player)

for i in range(10):
    x = y = 0
    while cave.walls[x, y] != 0:
        x = np.random.randint(mapwidth)
        y = np.random.randint(mapheight)
    item.create_medication(cave.items, x, y)

x = y = 0
while cave.walls[x, y] != 0:
    x = np.random.randint(mapwidth)
    y = np.random.randint(mapheight)
item.HumanIronDagger(cave.items, x, y)

for i in range(10):
    x = y = 0
    while cave.walls[x, y] != 0:
        x = np.random.randint(mapwidth)
        y = np.random.randint(mapheight)
    cave.creatures.append(creature.Blind_zombie(cave, x, y))

player.log = ['Welcome to the cave!', "Press 'h' for help."]
log = player.log
logback = 0 # How far the log has been scrolled
chosen = 0 # Used for different item choosing gamestates
target = None # Target of an attack

gamestate = 'free'

def sees(x1, y1, x2, y2, sight):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2) <= sight

def draw():
    # Background
    win.setscreencolors(None, 'black', clear=True)
    for i in range(mapwidth):
        for j in range(mapheight):
            if sees(player.x, player.y, i, j, player.sight()):
                if cave.walls[i,j] == 1:
                    win.putchars(' ', x=i, y=j, bgcolor='white')
                else:
                    win.putchars(' ', x=i, y=j, bgcolor=(64,64,64))
                player.seen[i,j] = 1
            elif player.seen[i,j] == 1:
                if cave.walls[i,j] == 1:
                    win.putchars(' ', x=i, y=j, bgcolor=(128,128,128))
    # Items
    for it in cave.items:
        if sees(player.x, player.y, it.x, it.y, player.sight()):
            win.putchars(it.char, x=it.x, y=it.y, 
                 bgcolor=(64,64,64), fgcolor=it.color)
        elif player.seen[it.x,it.y] == 1:
            win.putchars('?', x=it.x, y=it.y, 
                 bgcolor='black', fgcolor=(128,128,128))
    
    # Creatures
    for npc in [creature for creature in cave.creatures if creature.faction != 'player']:
        if sees(player.x, player.y, npc.x, npc.y, player.sight()):
            win.putchars(npc.char, npc.x, npc.y, bgcolor=(64,64,64),
                         fgcolor='white')
    win.putchars(player.char, x=player.x, y=player.y, 
                 bgcolor=(64,64,64), fgcolor='white')
    
    # Status
    for i in range(mapwidth):
        win.putchars(' ', x=i, y=mapheight, bgcolor=((128,128,128)))
    # win.putchars('hp: ' + repr(player.hp), x=2, y=mapheight, bgcolor=((128,128,128)), fgcolor=(0, 255, 0))
    win.putchars('items in inventory: ' + repr(len(player.inventory)), x=15, y=mapheight, bgcolor=((128,128,128)), fgcolor=(0, 255, 0))
    win.putchars('items in the cave: ' + repr(len(cave.items)), x=40, y=mapheight, bgcolor=((128,128,128)), fgcolor=(0, 255, 0))
    
    # Log
    if gamestate == 'free' or gamestate == 'dead':
        logrows = min(logheight,len(log))
        for i in range(logrows):
            j = i-logrows-logback
            c = 255 + (max(j+1, -logheight))*128//logheight
            win.write(log[j], x=0, y=mapheight+statuslines+i, fgcolor=(c,c,c))
            
    elif gamestate == 'mine':
        minemessage = 'Choose the direction to mine!'
        win.write(minemessage, x=0, y=mapheight+statuslines, fgcolor=(255,255,255))

    elif gamestate == 'pick':
        pickmessage = 'Choose the item to pick:'
        win.write(pickmessage, x=0, y=mapheight+statuslines, fgcolor=(0,255,255))
        picklist = [it for it in cave.items if it.x == player.x and it.y == player.y]
        logrows = min(logheight-1,len(picklist))
        for i in range(logrows):
            if len(picklist) <= logheight-1:
                j = i
            else:
                j = len(picklist)+i-logrows-logback
            if j != chosen:
                win.write(picklist[j].name, x=0, y=mapheight+statuslines+i+1, fgcolor=(255,255,255))
            if j == chosen:
                win.write(picklist[j].name, x=0, y=mapheight+statuslines+i+1, bgcolor=(255,255,255), fgcolor=(0,0,0))

    elif gamestate == 'drop':
        dropmessage = 'Choose the item to drop:'
        win.write(dropmessage, x=0, y=mapheight+statuslines, fgcolor=(0,255,255))
        logrows = min(logheight-1,len(player.inventory))
        for i in range(logrows):
            if len(player.inventory) <= logheight-1:
                j = i
            else:
                j = len(player.inventory)+i-logrows-logback
            if j != chosen:
                win.write(player.inventory[j].name, x=0, y=mapheight+statuslines+i+1, fgcolor=(255,255,255))
            if j == chosen:
                win.write(player.inventory[j].name, x=0, y=mapheight+statuslines+i+1, bgcolor=(255,255,255), fgcolor=(0,0,0))

    elif gamestate == 'consume':
        consumemessage = 'Choose the item to consume:'
        win.write(consumemessage, x=0, y=mapheight+statuslines, fgcolor=(0,255,255))
        logrows = min(logheight-1,len([item for item in player.inventory if item.consumable]))
        for i in range(logrows):
            if len([item for item in player.inventory if item.consumable]) <= logheight-1:
                j = i
            else:
                j = len([item for item in player.inventory if item.consumable])+i-logrows-logback
            if j != chosen:
                win.write([item for item in player.inventory if item.consumable][j].name, x=0, y=mapheight+statuslines+i+1, fgcolor=(255,255,255))
            if j == chosen:
                win.write([item for item in player.inventory if item.consumable][j].name, x=0, y=mapheight+statuslines+i+1, bgcolor=(255,255,255), fgcolor=(0,0,0))
    
    elif gamestate == 'wieldchooseitem':
        wieldmessage = 'Choose the item to wield:'
        win.write(wieldmessage, x=0, y=mapheight+statuslines, fgcolor=(0,255,255))
        logrows = min(logheight-1,len([item for item in player.inventory if item.wieldable]))
        for i in range(logrows):
            if len([item for item in player.inventory if item.wieldable]) <= logheight-1:
                j = i
            else:
                j = len([item for item in player.inventory if item.wieldable])+i-logrows-logback
            if j != chosen:
                win.write([item for item in player.inventory if item.wieldable][j].name, x=0, y=mapheight+statuslines+i+1, fgcolor=(255,255,255))
            if j == chosen:
                win.write([item for item in player.inventory if item.wieldable][j].name, x=0, y=mapheight+statuslines+i+1, bgcolor=(255,255,255), fgcolor=(0,0,0))
    
    elif gamestate == 'wieldchoosebodypart':
        wieldmessage = 'Choose where to wield the ' + selecteditem.name + ':'
        win.write(wieldmessage, x=0, y=mapheight+statuslines, fgcolor=(0,255,255))
        logrows = min(logheight-1,len([part for part in player.bodyparts if part.capableofwielding]))
        for i in range(logrows):
            if len([part for part in player.bodyparts if part.capableofwielding]) <= logheight-1:
                j = i
            else:
                j = len([part for part in player.bodyparts if part.capableofwielding])+i-logrows-logback
            if j != chosen:
                win.write([part for part in player.bodyparts if part.capableofwielding][j].name, x=0, y=mapheight+statuslines+i+1, fgcolor=(255,255,255))
            if j == chosen:
                win.write([part for part in player.bodyparts if part.capableofwielding][j].name, x=0, y=mapheight+statuslines+i+1, bgcolor=(255,255,255), fgcolor=(0,0,0))
    
    elif gamestate == 'chooseattack':
        attackmessage = 'Choose how to attack the ' + target.name + ':'
        win.write(attackmessage, x=0, y=mapheight+statuslines, fgcolor=(0,255,255))
        logrows = min(logheight-1,len(player.attackslist()))
        for i in range(logrows):
            if len(player.attackslist()) <= logheight-1:
                j = i
            else:
                j = len(player.attackslist())+i-logrows-logback
            if j != chosen:
                win.write(player.attackslist()[j].name, x=0, y=mapheight+statuslines+i+1, fgcolor=(255,255,255))
            if j == chosen:
                win.write(player.attackslist()[j].name, x=0, y=mapheight+statuslines+i+1, bgcolor=(255,255,255), fgcolor=(0,0,0))

    elif gamestate == 'choosetargetbodypart':
        attackmessage = 'Choose where to attack the ' + target.name + ':'
        win.write(attackmessage, x=0, y=mapheight+statuslines, fgcolor=(0,255,255))
        logrows = min(logheight-1,len([part for part in target.bodyparts if not part.destroyed()]))
        for i in range(logrows):
            if len([part for part in target.bodyparts if not part.destroyed()]) <= logheight-1:
                j = i
            else:
                j = len([part for part in target.bodyparts if not part.destroyed()])+i-logrows-logback
            targetbodypart = [part for part in target.bodyparts if not part.destroyed()][j]
            if targetbodypart.parentalconnection != None:
                partname = list(targetbodypart.parentalconnection.parent.childconnections.keys())[list(targetbodypart.parentalconnection.parent.childconnections.values()).index(targetbodypart.parentalconnection)]
            elif targetbodypart == target.torso:
                partname = 'torso'
            if j != chosen:
                win.write(partname, x=0, y=mapheight+statuslines+i+1, fgcolor=(255,255,255))
            if j == chosen:
                win.write(partname, x=0, y=mapheight+statuslines+i+1, bgcolor=(255,255,255), fgcolor=(0,0,0))
    
    win.update()

def updatetime(time):
    for npc in [creature for creature in cave.creatures if creature.faction != 'player']:
        npc.update(time)

def checkitems(x,y):
    for it in cave.items:
        if it.x == x and it.y == y:
            log.append('There is a ' + it.name + ' here.')
            logback = 0

draw()
while True:
    for event in pygame.event.get():
        try:
            if event.type == KEYDOWN:
                if gamestate == 'free':
                    # Player movements. This code needs some drying.
                    if event.key == K_UP or event.key == K_KP8:
                        targets = [creature for creature in cave.creatures if creature.x == player.x+0 and creature.y == player.y-1]
                        if len(targets) > 0:
                            target = targets[0]
                            gamestate = 'chooseattack'
                            chosen = 0
                            logback = len(player.attackslist()) - logheight + 1
                        elif player.move(0, -1):
                            updatetime(player.steptime())
                            checkitems(player.x,player.y)
                        else:
                            log.append("There's a wall in your way.")
                            logback = 0
                    if event.key == K_DOWN or event.key == K_KP2:
                        targets = [creature for creature in cave.creatures if creature.x == player.x+0 and creature.y == player.y+1]
                        if len(targets) > 0:
                            target = targets[0]
                            gamestate = 'chooseattack'
                            chosen = 0
                            logback = len(player.attackslist()) - logheight + 1
                        elif player.move(0, 1):
                            updatetime(player.steptime())
                            checkitems(player.x,player.y)
                        else:
                            log.append("There's a wall in your way.")
                            logback = 0
                    if event.key == K_LEFT or event.key == K_KP4:
                        targets = [creature for creature in cave.creatures if creature.x == player.x-1 and creature.y == player.y]
                        if len(targets) > 0:
                            target = targets[0]
                            gamestate = 'chooseattack'
                            chosen = 0
                            logback = len(player.attackslist()) - logheight + 1
                        elif player.move(-1, 0):
                            updatetime(player.steptime())
                            checkitems(player.x,player.y)
                        else:
                            log.append("There's a wall in your way.")
                            logback = 0
                    if event.key == K_RIGHT or event.key == K_KP6:
                        targets = [creature for creature in cave.creatures if creature.x == player.x+1 and creature.y == player.y]
                        if len(targets) > 0:
                            target = targets[0]
                            gamestate = 'chooseattack'
                            chosen = 0
                            logback = len(player.attackslist()) - logheight + 1
                        elif player.move(1, 0):
                            updatetime(player.steptime())
                            checkitems(player.x,player.y)
                        else:
                            log.append("There's a wall in your way.")
                            logback = 0
                    if event.key == K_KP7:
                        targets = [creature for creature in cave.creatures if creature.x == player.x-1 and creature.y == player.y-1]
                        if len(targets) > 0:
                            target = targets[0]
                            gamestate = 'chooseattack'
                            chosen = 0
                            logback = len(player.attackslist()) - logheight + 1
                        elif player.move(-1, -1):
                            updatetime(player.steptime() * np.sqrt(2))
                            checkitems(player.x,player.y)
                        else:
                            log.append("There's a wall in your way.")
                            logback = 0
                    if event.key == K_KP9:
                        targets = [creature for creature in cave.creatures if creature.x == player.x+1 and creature.y == player.y-1]
                        if len(targets) > 0:
                            target = targets[0]
                            gamestate = 'chooseattack'
                            chosen = 0
                            logback = len(player.attackslist()) - logheight + 1
                        elif player.move(1, -1):
                            updatetime(player.steptime() * np.sqrt(2))
                            checkitems(player.x,player.y)
                        else:
                            log.append("There's a wall in your way.")
                            logback = 0
                    if event.key == K_KP1:
                        targets = [creature for creature in cave.creatures if creature.x == player.x-1 and creature.y == player.y+1]
                        if len(targets) > 0:
                            target = targets[0]
                            gamestate = 'chooseattack'
                            chosen = 0
                            logback = len(player.attackslist()) - logheight + 1
                        elif player.move(-1, 1):
                            updatetime(player.steptime() * np.sqrt(2))
                            checkitems(player.x,player.y)
                        else:
                            log.append("There's a wall in your way.")
                            logback = 0
                    if event.key == K_KP3:
                        targets = [creature for creature in cave.creatures if creature.x == player.x+1 and creature.y == player.y+1]
                        if len(targets) > 0:
                            target = targets[0]
                            gamestate = 'chooseattack'
                            chosen = 0
                            logback = len(player.attackslist()) - logheight + 1
                        elif player.move(1, 1):
                            updatetime(player.steptime() * np.sqrt(2))
                            checkitems(player.x,player.y)
                        else:
                            log.append("There's a wall in your way.")
                            logback = 0
                    
                    if event.key == K_m:
                        gamestate = 'mine'
                    
                    # Items
                    if event.key == K_COMMA:
                        picklist = [it for it in cave.items if it.x == player.x and it.y == player.y]
                        if len(picklist) == 0:
                            log.append('Nothing to pick up here.')
                            logback = 0
                        elif len(picklist) == 1:
                            it = picklist[0]
                            cave.items.remove(it)
                            player.inventory.append(it)
                            it.owner = player.inventory
                            log.append('You pick up the ' + it.name + '.')
                            logback = 0
                            updatetime(0.5)
                        else:
                            gamestate = 'pick'
                            logback = len(picklist) - logheight + 1
                            chosen = 0
                    if event.key == K_d:
                        if len(player.inventory) > 0:
                            gamestate = 'drop'
                            logback = len(player.inventory) - logheight + 1
                            chosen = 0
                        else:
                            log.append('You have nothing to drop!')
                    if event.key == K_i:
                        log.append('Items in your backpack:')
                        if len(player.inventory) == 0:
                            log.append('  - nothing')
                            logback = 0
                        else:
                            for it in player.inventory:
                                log.append('  - a ' + it.name)
                                if len(player.inventory) > logheight - 1:
                                    logback = len(player.inventory) - logheight + 1
                                else:
                                    logback = 0
                    if event.key == K_c:
                        if len([item for item in player.inventory if item.consumable]) > 0:
                            gamestate = 'consume'
                            logback = len([item for item in player.inventory if item.consumable]) - logheight + 1
                            chosen = 0
                        else:
                            log.append("You don't have anything to consume.")
                    if event.key == K_w and not (event.mod & pygame.KMOD_SHIFT):
                        if len([item for item in player.inventory if item.wieldable]) > 0:
                            gamestate = 'wieldchooseitem'
                            logback = len([item for item in player.inventory if item.wieldable]) - logheight + 1
                            chosen = 0
                        else:
                            log.append("You don't have anything to consume.")
                    if event.key == K_w and (event.mod & pygame.KMOD_SHIFT):
                        log.append('Wearing not yet implemented!')
                    
                    # Help
                    if event.key == K_h:
                        log.append('Commands:')
                        log.append('  - arrows: move')
                        log.append('  - comma: pick up an item')
                        log.append('  - i: check your inventory')
                        log.append('  - c: take some medication')
                        log.append('  - page up, page down, home, end: explore the log')
                        log.append('  - h: this list of commands')
                        logback = 0 # Increase when adding commands
                    
                    # Log scrolling
                    if event.key == K_PAGEUP:
                        if len(log) >= logheight:
                            logback = min(logback+1, len(log)-logheight)
                    if event.key == K_PAGEDOWN:
                        logback = max(logback-1, 0)
                    if event.key == K_HOME:
                        if len(log) >= logheight:
                            logback = len(log)-logheight
                    if event.key == K_END:
                        logback = 0
                        
                elif gamestate == 'mine':
                    if event.key == K_UP or event.key == K_KP8:
                        if player.y-1 == 0:
                            log.append('That is too hard for you to mine.')
                            logback = 0
                        elif cave.walls[player.x, player.y-1] == 1:
                            log.append('You mined north.')
                            logback = 0
                            cave.walls[player.x, player.y-1] = 0
                            updatetime(3)
                        else:
                            log.append("There's no wall there.")
                            logback = 0
                        gamestate = 'free'
                    if event.key == K_DOWN or event.key == K_KP2:
                        if player.y+1 == mapheight-1:
                            log.append('That is too hard for you to mine.')
                            logback = 0
                        elif cave.walls[player.x, player.y+1] == 1:
                            log.append('You mined south.')
                            logback = 0
                            cave.walls[player.x, player.y+1] = 0
                            updatetime(3)
                        else:
                            log.append("There's no wall there.")
                            logback = 0
                        gamestate = 'free'
                    if event.key == K_LEFT or event.key == K_KP4:
                        if player.x-1 == 0:
                            log.append('That is too hard for you to mine.')
                            logback = 0
                        elif cave.walls[player.x-1, player.y] == 1:
                            log.append('You mined west.')
                            logback = 0
                            cave.walls[player.x-1, player.y] = 0
                            updatetime(3)
                        else:
                            log.append("There's no wall there.")
                            logback = 0
                        gamestate = 'free'
                    if event.key == K_RIGHT or event.key == K_KP6:
                        if player.x+1 == mapwidth-1:
                            log.append('That is too hard for you to mine.')
                            logback = 0
                        elif cave.walls[player.x+1, player.y] == 1:
                            log.append('You mined east.')
                            logback = 0
                            cave.walls[player.x+1, player.y] = 0
                            updatetime(3)
                        else:
                            log.append("There's no wall there.")
                            logback = 0
                        gamestate = 'free'
                    if event.key == K_ESCAPE:
                        logback = 0
                        gamestate = 'free'
                
                elif gamestate == 'pick':
                    picklist = [it for it in cave.items if it.x == player.x and it.y == player.y]
                    if event.key == K_UP:
                        chosen = max(0, chosen-1)
                        if chosen == len(picklist) - logback - (logheight - 1) - 1:
                            logback += 1
                    if event.key == K_DOWN:
                        chosen = min(len(picklist)-1, chosen+1)
                        if chosen == len(picklist) - logback:
                            logback -= 1
                    if event.key == K_RETURN:
                        selected = picklist[chosen]
                        selected.owner = player.inventory
                        player.inventory.append(selected)
                        cave.items.remove(selected)
                        log.append('You picked up the ' + selected.name + '.')
                        logback = 0
                        gamestate = 'free'
                        updatetime(0.5)
                    if event.key == K_ESCAPE:
                        logback = 0
                        gamestate = 'free'
                
                elif gamestate == 'drop':
                    if event.key == K_UP:
                        chosen = max(0, chosen-1)
                        if chosen == len(player.inventory) - logback - (logheight - 1) - 1:
                            logback += 1
                    if event.key == K_DOWN:
                        chosen = min(len(player.inventory)-1, chosen+1)
                        if chosen == len(player.inventory) - logback:
                            logback -= 1
                    if event.key == K_RETURN:
                        selected = player.inventory[chosen]
                        selected.owner = cave.items
                        cave.items.append(selected)
                        player.inventory.remove(selected)
                        selected.x = player.x
                        selected.y = player.y
                        log.append('You dropped the ' + selected.name + '.')
                        logback = 0
                        gamestate = 'free'
                        updatetime(0.5)
                    if event.key == K_ESCAPE:
                        logback = 0
                        gamestate = 'free'
                
                elif gamestate == 'consume':
                    if event.key == K_UP:
                        chosen = max(0, chosen-1)
                        if chosen == len([item for item in player.inventory if item.consumable]) - logback - (logheight - 1) - 1:
                            logback += 1
                    if event.key == K_DOWN:
                        chosen = min(len([item for item in player.inventory if item.consumable])-1, chosen+1)
                        if chosen == len([item for item in player.inventory if item.consumable]) - logback:
                            logback -= 1
                    if event.key == K_RETURN:
                        selected = [item for item in player.inventory if item.consumable][chosen]
                        part, healed = selected.consume(player)
                        if part.parentalconnection != None:
                            partname = list(part.parentalconnection.parent.childconnections.keys())[list(part.parentalconnection.parent.childconnections.values()).index(part.parentalconnection)]
                        elif part == player.torso:
                            partname = 'torso'
                        log.append('You consumed a ' + selected.name + ', healing your ' + partname + ' ' + repr(selected.hpgiven()) + ' points.')
                        logback = 0
                        gamestate = 'free'
                        updatetime(1)
                    if event.key == K_ESCAPE:
                        logback = 0
                        gamestate = 'free'
                
                elif gamestate == 'wieldchooseitem':
                    if event.key == K_UP:
                        chosen = max(0, chosen-1)
                        if chosen == len([item for item in player.inventory if item.wieldable]) - logback - (logheight - 1) - 1:
                            logback += 1
                    if event.key == K_DOWN:
                        chosen = min(len([item for item in player.inventory if item.wieldable])-1, chosen+1)
                        if chosen == len([item for item in player.inventory if item.wieldable]) - logback:
                            logback -= 1
                    if event.key == K_RETURN:
                        selecteditem = [item for item in player.inventory if item.wieldable][chosen]
                        logback = len([part for part in player.bodyparts if part.capableofwielding]) - logheight + 1
                        gamestate = 'wieldchoosebodypart'
                        chosen = 0
                    if event.key == K_ESCAPE:
                        logback = 0
                        gamestate = 'free'
                
                elif gamestate == 'wieldchoosebodypart':
                    if event.key == K_UP:
                        chosen = max(0, chosen-1)
                        if chosen == len([part for part in player.bodyparts if part.capableofwielding]) - logback - (logheight - 1) - 1:
                            logback += 1
                    if event.key == K_DOWN:
                        chosen = min(len([part for part in player.bodyparts if part.capableofwielding])-1, chosen+1)
                        if chosen == len([part for part in player.bodyparts if part.capableofwielding]) - logback:
                            logback -= 1
                    if event.key == K_RETURN:
                        selected = [part for part in player.bodyparts if part.capableofwielding][chosen]
                        player.inventory.remove(selecteditem)
                        selected.wielded.append(selecteditem)
                        selecteditem.owner = selected.wielded
                        log.append('You are now wielding ' + selecteditem.name)
                        logback = 0
                        gamestate = 'free'
                    if event.key == K_ESCAPE:
                        logback = 0
                        gamestate = 'free'
                
                elif gamestate == 'chooseattack':
                    if event.key == K_UP:
                        chosen = max(0, chosen-1)
                        if chosen == len(player.attackslist()) - logback - (logheight - 1) - 1:
                            logback += 1
                    if event.key == K_DOWN:
                        chosen = min(len(player.attackslist())-1, chosen+1)
                        if chosen == len(player.attackslist()) - logback:
                            logback -= 1
                    if event.key == K_RETURN:
                        selectedattack = player.attackslist()[chosen]
                        gamestate = 'choosetargetbodypart'
                        logback = len([part for part in target.bodyparts if not part.destroyed()]) - logheight + 1
                        chosen = 0
                    if event.key == K_ESCAPE:
                        logback = 0
                        gamestate = 'free'
                
                elif gamestate == 'choosetargetbodypart':
                    if event.key == K_UP:
                        chosen = max(0, chosen-1)
                        if chosen == len([part for part in target.bodyparts if not part.destroyed()]) - logback - (logheight - 1) - 1:
                            logback += 1
                    if event.key == K_DOWN:
                        chosen = min(len([part for part in target.bodyparts if not part.destroyed()])-1, chosen+1)
                        if chosen == len([part for part in target.bodyparts if not part.destroyed()]) - logback:
                            logback -= 1
                    if event.key == K_RETURN:
                        selected = [part for part in target.bodyparts if not part.destroyed()][chosen]
                        updatetime(selectedattack[6])
                        player.fight(target, selected, selectedattack)
                        logback = 0
                        gamestate = 'free'
                    if event.key == K_ESCAPE:
                        logback = 0
                        gamestate = 'free'
                
                if player.dying():
                    gamestate = 'dead'
                
                # Update window after any command or keypress
                draw()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        
        # Make sure the window is closed if the game crashes
        except Exception as e:
            pygame.quit()
            sys.exit()
            raise e