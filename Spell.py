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
        self.critical_chance = 0

