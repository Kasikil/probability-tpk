import random

class Weapon:
    def __init__(self, name, damage_die, ability="Strength"):
        self.name = name
        self.damage_die = damage_die  # e.g., 12 for a d12
        self.ability = ability

    def roll_damage(self, modifier):
        roll = random.randint(1, self.damage_die)
        return roll + modifier