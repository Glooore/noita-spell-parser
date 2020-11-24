#!/usr/bin/python3

import os
import re
import xml.etree.ElementTree as ET

def getNumberFromEquation(equation):
    pass

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
        self.lifetime = 0
        self.speed_modifier = 0
        self.cast_delay = 0
        self.recharge_time = 0
        self.spread_modifier = 0
        self.critical_chance_modifier = 0
        self.terrain_destroy = 0
        self.liquid_destroy = 0

    def printInfo(self):
        print("SPELL NAME:", self.id)
        print("Mana cost:", self.mana_cost)
        print("Max uses:", self.uses)
        print("Impact damage:", self.damage[0])

        print("Cast delay:", self.cast_delay)
        print("Recharge time:", self.recharge_time)
        print('\n')

    def parseSpellBlock(self, spell_block):
        quotes_re = r'"([^"]*)"'

        del spell_block[-1]
        keys = []
        values = []
        for item in spell_block:
            split = item.split("=")

            keys.append(split[0].strip())
            
            if ( re.search(r'[{"]+.*', split[1].strip()) ):
                values.append( "".join(re.findall(quotes_re, split[1].strip())).lower() )
            else:
                values.append( "".join(re.findall(r'([-+]?[0-9]*)[,]?', split[1].strip())).lower() )

        spell_dict = dict(zip(keys, values))

        #BUNCH OF IFS BECAUSE FUCK YOU
        if ( "id" in spell_dict ):
            self.id = spell_dict["id"]
        if ( "name" in spell_dict ):
            self.name = spell_dict["name"]
        if ( "related_projectiles" in spell_dict ):
            self.xml_file = spell_dict["related_projectiles"]
        if ( "type" in spell_dict ):
            self.type = spell_dict["type"]
        if ( "mana" in spell_dict ):
            self.mana_cost = spell_dict["mana"]
        if ( "max_uses" in spell_dict ):
            self.uses = spell_dict["max_uses"]
        if ( "c.damage_projectile_add" in spell_dict ):
            self.damage_modifier[0] = spell_dict["c.damage_projectile_add"]
        if ( "c.damage_explosion_add" in spell_dict ):
            self.damage_modifier[5] = spell_dict["c.damage_explosion_add"]
        if ( "c.damage_electricity_add" in spell_dict ):
            self.damage_modifier[4] = spell_dict["c.damage_electricity_add"]
        if ( "c.fire_rate_wait" in spell_dict ):
            self.cast_delay = spell_dict["c.fire_rate_wait"]
        if( "current_reload_time" in spell_dict ):
            self.recharge_time = spell_dict["current_reload_time"]
        if ( "c.spread_degrees" in spell_dict ):
            self.spread_modifier = spell_dict["c.spread_degrees"]
        if ( "c.speed_multiplier" in spell_dict ):
            self.speed_multiplier = spell_dict["c.speed_multiplier"]
        if ( "c.critical_damage_chance" in spell_dict ):
            self.critical_chance_modifier = spell_dict["c.critical_damage_chance"]

        return 0

    def parseXML(self):
        if ( self.xml_file ):
            try:
                root = ET.parse(path_to_data + self.xml_file)
            except ET.ParseError as e:
                print ("duplicate attributes in:", self.xml_file)
                print (e)
                return 1

            for projectile in root.iter("ProjectileComponent"):
                stat_dict = projectile.attrib
                if ( "damage" in stat_dict ):
                    self.damage[0] = float(stat_dict["damage"])*25
                if ( "speed_min" in stat_dict ):
                    self.speed_min = float(stat_dict["speed_min"])
                if ( "speed_max" in stat_dict ):
                    self.speed_max = float(stat_dict["speed_max"])

            for explosion in root.iter("config_explosion"):
                explosion_dict = explosion.attrib

                if ( "damage" in explosion_dict ):
                    self.damage[5] = float(explosion_dict["damage"])

                if ( "explosion_radius" in explosion_dict ):
                    self.radius[5] = float(explosion_dict["explosion_radius"])

                if ( "hole_enabled" in explosion_dict ):
                    self.terrain_destroy = float(explosion_dict["hole_enabled"])

                if ( "hole_destroy_liquid" in explosion_dict ):
                    self.liquid_destroy = float(explosion_dict["hole_destroy_liquid"])

            for damage in root.iter("damage_by_type"):
                damage_dict = damage.attrib

                if ( "slice" in damage_dict ):
                    self.damage[1] = float(damage_dict["slice"])*25

                if ( "drill" in damage_dict ):
                    self.damage[2] = float(damage_dict["drill"])*25

                if ( "fire" in damage_dict ):
                    self.damage[3] = float(damage_dict["fire"])*25

                if ( "electricity" in damage_dict ):
                    self.damage[4] = float(damage_dict["electricity"])*25

            return 0

        return 1





path_to_data = "/home/gawenda/USB/Noita/"
path_to_gun = "data/scripts/gun/"
file_name = "gun_actions.lua"

i = 0

with open(path_to_data + path_to_gun + file_name, "r") as f:
    comment = False
    temp = f.readline()
    temp = f.readline()
    temp = f.readline()

    while ( temp != "" ):
        if ( re.search(r'--\[\[', temp )):
            comment = True
        elif ( re.search(r'\]\]--+', temp)):
            comment = False
        elif ( re.search(r'\t{', temp ) and (not comment)):
            test = Spell()
            spell_block = getSpellBlock(f).split('\n')

            test.parseSpellBlock(spell_block)
            test.parseXML()
            test.printInfo()

        temp = f.readline()
