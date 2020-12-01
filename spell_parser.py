#!/usr/bin/python3

# not in project, but: get SSH pushing to work

# big TODO: add command line parameters (mostly path to the data directory and filename of the saved .CSV)
#           or a graphical prompt

# to be honest, it's not really that complicated
# but still a bit annoying to do
# and needs a lots and lots of polish

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
        elif (re.search(r'add_projectile', temp)):
            spell_data.append(temp)

    return spell_data

class Spell:
    # probably doesn't need to be initialized, but well. I'll see
    def __init__(self):
        self.id = None
        self.name = None
        self.description = None
        self.xml_file = None
        self.backup_xml_file = None
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

            try:
                if ( re.search(r'add_projectile', item.strip()) ):
                    temp = re.findall(quotes_re, item.strip())
                    self.xml_file = "".join(temp)
                    continue
                elif ( re.search(r'[{"]+.*,', split[1].strip()) ):
                    temp = re.findall(quotes_re, split[1].strip())

                elif ( re.search(r'^type', split[0].strip()) ):
                    temp = re.findall(r'([A-Z_]+),', split[1].strip())

                else:
                    temp = re.findall(r'([-+*]? [0-9.]+)', split[1])
            except IndexError as e:
                print (e)
                print (split)

            try:
                if ( temp ):
                    temp[0] = temp[0].replace("*", "x")
                    # workaround for comments in Lua files
                    # removes whitespace between the symbols for the int() function
                    # I don't really know if I even WANT to convert it to ints
                    temp[0] = temp[0].replace(" ", "")
                    values.append("".join(temp[0]).lower())
                    keys.append(split[0].strip())
            except IndexError as e:
                print (e)
                print (split)

        spell_dict = dict(zip(keys, values))

        # bunch of ifs, because I can't think of a more elegant way
        # probably could've been done with dicts, but oh well
        if ( "id" in spell_dict ):
            self.id = spell_dict["id"]
        if ( "name" in spell_dict ):
            self.name = spell_dict["name"].replace("$", "")
        if ( "description" in spell_dict):
            self.description = spell_dict["description"].replace("$", "")
        if ( "related_projectiles" in spell_dict ):
            self.backup_xml_file = spell_dict["related_projectiles"]
        if ( "type" in spell_dict ):
            self.type = spell_dict["type"]
        if ( "mana" in spell_dict ):
            self.mana_cost = int(spell_dict["mana"])
        if ( "max_uses" in spell_dict ):
            self.uses = int(spell_dict["max_uses"])
        else:
            # -1 uses, as in - infinity uses
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
        if ( "c.damage_critical_chance" in spell_dict ):
            self.critical_chance_modifier = str(spell_dict["c.damage_critical_chance"]) + "%"

        return 0

    # @brief: parses XML file that is describing the projectile
    def parseXML(self):
        if ( self.xml_file ):
            try:
                root = ET.parse(path_to_data + self.xml_file)
            # TODO: find a way to delete duplicate lines
            # probably a while loop that deletes the lines until it works?

            except ET.ParseError as e:
                print ("file:", self.xml_file)
                print (e)
                return 1
            # only the case when checking add_projectile() function instead of related_projectiles
            # mostly happeninng with "Summon Egg" (because of the concatenation of strings in Lua)
            # and "Fireworks", but I haven't looked into it yet

            except IsADirectoryError as e:
                print(e)
                print ("The path points to a directory. Trying a secondary path.")

                try:
                    root = ET.parse(path_to_data + self.backup_xml_file)
                except IsADirectoryError as e:
                    print(e)
                    print ("The secondary path points to a directory. Skipping spell:", self.id)
                    return 1
                except FileNotFoundError as e:
                    print(e)
                    print("The secondary file does not exist. Skipping spell:", self.id)
                    return 1
                except:
                    print("Secondary path doesn't work. Skipping spell:", self.id)
                    return 1

            except FileNotFoundError as e:
                print(e)
                print("The file does not exist. Trying a secondary path")

                try:
                    root = ET.parse(path_to_data + self.backup_xml_file)
                except IsADirectoryError as e:
                    print(e)
                    print ("The secondary path points to a directory. Skipping spell:", self.id)
                    return 1
                except FileNotFoundError as e:
                    print(e)
                    print("The secondary file does not exist. Skipping spell:", self.id)
                    return 1
                except:
                    print("Secondary path doesn't work. Skipping spell:", self.id)
                    return 1

            except:
                print ("Unknown error. Trying a secondary path.")


            # more ifs
            for projectile in root.iter("ProjectileComponent"):
                stat_dict = projectile.attrib
                if ( "damage" in stat_dict ):
                    self.damage[0] = round((float(stat_dict["damage"])*25))
                if ( "direction_random_rad" in stat_dict):
                    self.spread = round(float(stat_dict["direction_random_rad"])*180/math.pi, 1)
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

    # @brief: converts damage list into neat string:
    # e.g. [1, 0, 0, 0, 0, 0] will be changed into "Impact: 1"
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

        # TODO: add modifier as a signed int (+1 instead of 1, -1, etc.)
        for i, value in enumerate(self.damage_modifier):
            if ( value ):
                temp += "{0}: {1}\n".format(types[i], value)

        self.damage_modifier = temp.strip()

    # @brief: checks translation files for proper strings and descriptions
    # VERY INEFICIENT
    def fetchTranslations(self):
        found_translation = False
        with open(path_to_data + path_to_translations, 'r', newline='') as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                if ( self.name == row[0] ):
                    self.name = row[1]
                    found_translation = True
                elif ( self.description == row[0] ):
                    self.description = row[1]

    # @brief: was used when debugging
    def printInfo(self):
        print(self.__dict__)
        print('\n')



# @brief: saves all the spell data into a CSV file
# @param spell_container: list of Spell objects
# @param filename: where to save
def printToCSV(spell_container, filename):
    with open(filename, 'w', newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(spell_container[0].__dict__.keys()))
        for spell in spell_container:
            writer.writerow(list(spell.__dict__.values()))


# TODO: either ask for two paths or include two prompts 
path_to_translations = "data/translations/common.csv"
path_to_dev_translations = "data/translations/common_dev.csv"
path_to_data = "/home/gawenda/USB/Noita/"
path_to_gun = "data/scripts/gun/"
file_name = "gun_actions.lua"

translations_exist = False

try:
    with open(path_to_data + path_to_translations, 'r', newline='') as f:
        translations_exist = True
except FileNotFoundError as e:
    print("The translations file has not been found.")

i = 0

spell_container = []

with open(path_to_data + path_to_gun + file_name, "r") as f:
    # indicates a comment block
    comment = False
    # used for initialization
    temp = f.readline()
    temp = f.readline()
    temp = f.readline()

    # main loop
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
            if ( translations_exist ):
                spell.fetchTranslations()

            spell_container.append(spell)

        temp = f.readline()

printToCSV(spell_container, "spells.csv")
