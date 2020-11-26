#!/usr/bin/python3

# to be honest, it's not really that complicated

# bunch of stuff, I don't really know why I have 'os' imported
import os
import csv
import math
import re
import xml.etree.ElementTree as ET

# @brief: gets data from between curly braces ('{' and '}') as long as they are in seperate lines
# it's all thanks to Nolla Games' extremely well done code <3
# @param f: file object in read mode
def getSpellBlock(f):
    spell_data = []
    temp = ""

    while ( True ):
        temp = f.readline().strip()
        # quits the loop when the read line indicates an end of the block
        # - a simple "}," at the beginning of the line
        if ( re.search(r'^},', temp)):
            break
        elif (re.search(r'.*=.*', temp)):
            spell_data.append(temp)

    return spell_data

class Spell:
    # LOTS OF SHIT
    # probably doesn't need to be initialized, but well. We'll see.
    def __init__(self):
        self.id = None
        self.name = None
        self.description = None
        self.xml_file = None
        self.type = None
        self.mana_cost = None
        self.uses = None
        # list for all damage types (if it = 0, won't be included)
        self.damage = [0, # IMPACT DAMAGE
                       0, # SLICE DAMAGE
                       0, # DRILL DAMAGE
                       0, # FIRE DAMAGE
                       0, # ELECTRICITY DAMAGE
                       0, # EXPLOSION DAMAGE
                       ]
        # list for all damage modifier types (if it = 0, won't be included)
        # this one is probably needed
        self.damage_modifier = [0, # IMPACT DAMAGE
                       0, # SLICE DAMAGE
                       0, # DRILL DAMAGE
                       0, # FIRE DAMAGE
                       0, # ELECTRICITY DAMAGE
                       0, # EXPLOSION DAMAGE
                       ]
        self.radius = None
        # radius for all damage types:
        # same here
        # self.radius = [0, # IMPACT DAMAGE
        #                0, # SLICE DAMAGE
        #                0, # DRILL DAMAGE
        #                0, # FIRE DAMAGE
        #                0, # ELECTRICITY DAMAGE
        #                0, # EXPLOSION DAMAGE
        #                ]
        self.spread = None
        self.speed_min = None
        self.speed_max = None
        self.speed_modifier = None
        self.lifetime = None
        self.lifetime_modifier = None
        self.cast_delay = None
        self.recharge_time = None
        self.spread_modifier = None
        self.critical_chance_modifier = None
        self.terrain_destroy = None
        self.liquid_destroy = None

    # @brief: parses a given Lua code to extract variables and their values
    # @param spell_block: block extracted by getSpellBlock()
    def parseSpellBlock(self, spell_block):
        # a regex for extracting strings - text between two (") quotes
        quotes_re = r'"([^"]*)"'

        keys = []
        values = []

        # going through each line in spell_block
        for item in spell_block:
            split = item.split("=")

            if ( re.search(r'[{"]+.*', split[1].strip()) ):
                temp = re.findall(quotes_re, split[1].strip())

                if ( temp ):
                    temp[0] = temp[0].replace(" ", "")
                    values.append("".join(temp[0]).lower())
                    keys.append(split[0].strip())

            elif ( split[0].strip() == "type" ):
                # temp = re.findall(r'_([A-Z]+),', split[1].strip())
                # values.append(temp[0].lower())

                values.append(split[1].strip())
                keys.append(split[0].strip())
            else:
                temp = re.findall(r'([-+*]? [0-9.]+)', split[1])

                if ( temp ):
                    temp[0] = temp[0].replace("*", "x")
                    # workaround for comments in Lua files
                    # removes whitespace between the symbols for the int() function
                    # I don't really know if I even WANT to convert it to ints
                    temp[0] = temp[0].replace(" ", "")
                    values.append("".join(temp[0]).lower())
                    keys.append(split[0].strip())

        spell_dict = dict(zip(keys, values))

        #BUNCH OF IFS BECAUSE FUCK YOU
        # probably could've been done with dicts, but oh well
        if ( "id" in spell_dict ):
            self.id = spell_dict["id"]
        if ( "name" in spell_dict ):
            self.name = spell_dict["name"].replace("$", "")
        if ( "description" in spell_dict):
            self.description = spell_dict["description"].replace("$", "")
        if ( "related_projectiles" in spell_dict ):
            self.xml_file = spell_dict["related_projectiles"]
        if ( "type" in spell_dict ):
            self.type = spell_dict["type"]
        if ( "mana" in spell_dict ):
            self.mana_cost = int(spell_dict["mana"])
        if ( "max_uses" in spell_dict ):
            self.uses = int(spell_dict["max_uses"])
        else:
            self.uses = -1
        if ( "c.lifetime_add" in spell_dict):
            self.lifetime_modifier = int(spell_dict["c.lifetime_add"])
        if ( "c.damage_projectile_add" in spell_dict ):
            self.damage_modifier[0] = round(float(spell_dict["c.damage_projectile_add"])*25)
        if ( "c.damage_explosion_add" in spell_dict ):
            self.damage_modifier[5] = round(float(spell_dict["c.damage_explosion_add"])*100)
        if ( "c.damage_electricity_add" in spell_dict ):
            self.damage_modifier[4] = round(float(spell_dict["c.damage_electricity_add"])*25)
        if ( "c.fire_rate_wait" in spell_dict ):
            self.cast_delay = round(float(spell_dict["c.fire_rate_wait"])/60, 2)
        if( "current_reload_time" in spell_dict ):
            self.recharge_time = round(float(spell_dict["current_reload_time"])/60, 2)
        if ( "c.spread_degrees" in spell_dict ):
            self.spread_modifier = float(spell_dict["c.spread_degrees"])
        if ( "c.speed_multiplier" in spell_dict ):
            self.speed_modifier = spell_dict["c.speed_multiplier"]
        if ( "c.critical_damage_chance" in spell_dict ):
            self.critical_chance_modifier = int(spell_dict["c.critical_damage_chance"])

        return 0

    def parseXML(self):
        if ( self.xml_file ):
            try:
                root = ET.parse(path_to_data + self.xml_file)
            except ET.ParseError as e:
                print ("duplicate attributes in:", self.xml_file)
                print (e)
                return 1

            # projectile_dict = {}

            for projectile in root.iter("ProjectileComponent"):
                stat_dict = projectile.attrib
                if ( "damage" in stat_dict ):
                    self.damage[0] = round((float(stat_dict["damage"])*25))
                if ( "speed_min" in stat_dict ):
                    self.speed_min = int(stat_dict["speed_min"])
                if ( "speed_max" in stat_dict ):
                    self.speed_max = int(stat_dict["speed_max"])
                if ( "lifetime" in stat_dict ):
                    self.lifetime = int(stat_dict["lifetime"])

            for explosion in root.iter("config_explosion"):
                explosion_dict = explosion.attrib

                if ( "damage" in explosion_dict ):
                    self.damage[5] = round(float(explosion_dict["damage"])*100)
                if ( "explosion_radius" in explosion_dict ):
                    self.radius = float(explosion_dict["explosion_radius"])
                if ( "hole_enabled" in explosion_dict ):
                    self.terrain_destroy = float(explosion_dict["hole_enabled"])
                if ( "hole_destroy_liquid" in explosion_dict ):
                    self.liquid_destroy = float(explosion_dict["hole_destroy_liquid"])

            for damage in root.iter("damage_by_type"):
                damage_dict = damage.attrib

                if ( "slice" in damage_dict ):
                    self.damage[1] = round(float(damage_dict["slice"])*25)
                if ( "drill" in damage_dict ):
                    self.damage[2] = round(float(damage_dict["drill"])*25)
                if ( "fire" in damage_dict ):
                    self.damage[3] = round(float(damage_dict["fire"])*25)
                if ( "electricity" in damage_dict ):
                    self.damage[4] = round(float(damage_dict["electricity"])*25)

            for lifetime in root.iter("LifetimeComponent"):
                lifetime_dict = lifetime.attrib
                if ( "lifetime" in lifetime_dict):
                    self.lifetime = lifetime_dict["lifetime"]

            return 0

        return 1

    def convertDamageToString(self):
        types = [ "Impact",
                 "Slice",
                 "Drill",
                 "Fire",
                 "Electricity",
                 "Explosion",
                 ]

        temp = ""
        more_than_one = False
        for i, value in enumerate(self.damage):
            if ( value ):
                temp += "{0}: {1}\n".format(types[i], value)

        self.damage = temp.strip()

        temp = ""

        for i, value in enumerate(self.damage_modifier):
            if ( value ):
                temp += "{0}: {1}\n".format(types[i], value)

        self.damage_modifier = temp.strip()

    def fetchTranslations(self):
        with open(path_to_data + path_to_translations, 'r', newline='') as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                if ( self.name == row[0] ):
                    self.name = row[1]
                elif ( self.description == row[0] ):
                    self.description = row[1]

    def printInfo(self):
        print(self.__dict__)
        print('\n')



def printToCSV(spell_container, filename):
    with open(filename, 'w', newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(spell_container[0].__dict__.keys()))
        for spell in spell_container:
            writer.writerow(list(spell.__dict__.values()))


path_to_translations = "data/translations/common.csv"
path_to_data = "/home/gawenda/USB/Noita/"
path_to_gun = "data/scripts/gun/"
file_name = "gun_actions.lua"

i = 0

spell_container = []

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
            spell = Spell()
            spell_block = getSpellBlock(f)#.split('\n')

            spell.parseSpellBlock(spell_block)
            spell.parseXML()
            spell.convertDamageToString()
            spell.fetchTranslations()

            spell_container.append(spell)

        temp = f.readline()

printToCSV(spell_container, "spells.csv")
