#!/usr/bin/python3

import os
import re

def getSpellBlock(f):
    spell_data = ""
    temp = ""

    while ( True ):
        temp = f.readline().strip()
        if ( re.search(r'end', temp)):
            break
        elif (re.search(r'.*=.*', temp)):
            spell_data += temp + '\n'

    return spell_data

class Spell:
    # LOTS OF SHIT
    # probably doesn't need to be initialized, but well. We'll see
    def __init__(self):
        self.id = ""
        self.name = ""
        self.description = ""
        self.xml_file = ""
        self.type = ""
        self.mana_cost = 0
        self.uses = 0
        # list for all damage types (if it = 0, won't be included)
        self.damage = [0, # IMPACT DAMAGE
                       0, # SLICE DAMAGE
                       0, # DRILL DAMAGE
                       0, # FIRE DAMAGE
                       0, # ELECTRICITY DAMAGE
                       0, # EXPLOSION DAMAGE
                       ]
        # list for all damage modifier types (if it = 0, won't be included)
        self.damage_modifier = [0, # IMPACT DAMAGE
                       0, # SLICE DAMAGE
                       0, # DRILL DAMAGE
                       0, # FIRE DAMAGE
                       0, # ELECTRICITY DAMAGE
                       0, # EXPLOSION DAMAGE
                       ]
        # radius for all damage types:
        self.radius = [0, # IMPACT DAMAGE
                       0, # SLICE DAMAGE
                       0, # DRILL DAMAGE
                       0, # FIRE DAMAGE
                       0, # ELECTRICITY DAMAGE
                       0, # EXPLOSION DAMAGE
                       ]
        self.spread = 0
        self.speed_min = 0
        self.speed_max = 0
        self.cast_delay = 0
        self.recharge_time = 0
        self.spread_modifier = 0
        self.critical_chance_modifier = 0

    def parseSpellBlock(self, spell_block):
        quotes_re = r'"([^"]*)"'

        del spell_block[-1]
        keys = []
        values = []
        for item in spell_block:
            split = item.split("=")
            keys.append(split[0].strip())
            
            values.append( "".join(re.findall(quotes_re, split[1].strip())).lower() )

        spell_dict = dict(zip(keys, values))

        #BUNCH OF IFS BECAUSE FUCK YOU
        if ( "id" in spell_dict ):
            self.id = spell_dict["id"]
        if ( "name" in spell_dict ):
            self.name = spell_dict["name"]
        if ( "related_projectiles" in spell_dict ):
            self.xml_file = spell_dict["id"]
        if ( "type" in spell_dict ):
            self.type = spell_dict["type"]
        if ( "mana" in spell_dict ):
            self.mana_cost = spell_dict["mana"]
        if ( "max_uses" in spell_dict ):
            self.uses = spell_dict["max_uses"]
        if ( "c.damage_projectile_add" in spell_dict ):
            self.damage_modifier[0] += spell_dict["c.damage_projectile_add"]
        if ( "c.damage_explosion_add" in spell_dict ):
            self.damage_modifier[5] += spell_dict["c.damage_explosion_add"]
        if ( "c.fire_rate_wait" in spell_dict ):
            self.cast_delay = spell_dict["c.fire_rate_wait"]
        if( "current_reload_time" in spell_dict ):
            self.recharge_time = spell_dict["current_reload_time"]
        if ( "c.spread_degrees" in spell_dict ):
            self.spread_modifier = spell_dict["c.spread_degrees"]
        if ( "c.critical_damage_chance" in spell_dict ):
            self.critical_chance_modifier = spell_dict["c.critical_damage_chance"]


path_to_data = "/home/gawenda/USB/Noita/"
path_to_gun = "data/scripts/gun/"
file_name = "gun_actions.lua"

i = 1
test = Spell()

with open(path_to_data + path_to_gun + file_name, "r") as f:
    temp = f.readline()
    temp = f.readline()
    temp = f.readline()

    while ( temp != "" ):

        if ( re.search(r'[^\[]+{$', temp) ):
            spell_block = getSpellBlock(f).split('\n')
            if ( i == 1):
                test.parseSpellBlock(spell_block)
                i = 2

        temp = f.readline()
