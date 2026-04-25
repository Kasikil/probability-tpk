import math
import random

class Spell:

    def __init__(self, data):
        self.name = data.get("name", "Unknown Spell")
        self.level = data.get("level", 1)
        self.damage_type = data.get("damage_type", "Psychic")
        self.damage_die = data.get("damage_die", 6)
        self.die_count = data.get("die_count", 1)
        self.additional_damage = data.get("additional_damage", 0)
        self.spell_type = data.get("spell_type", "Damage")
        self.heal_die = data.get("heal_die", 8)
        self.heal_die_count = data.get("heal_die_count", 1)

    def calculate_single_target_damage(self, modifier, critical_mod=1):
        """
        Simulates a spell roll by rolling 'die_count' dice of size 'damage_die'
        and adding 'additional_damage' accounting for criticals if needed
        """
        # 1. Base Damage (e.g., 2d6)
        base_roll = sum(random.randint(1, int(self.damage_die)) for _ in range(int(self.die_count)))
        
        # 2. Add Modifier and Magic Bonus
        total_damage = base_roll*critical_mod + modifier + self.additional_damage

        return total_damage
    
    def calculate_healing(self, modifier, critical_mod=1):
        """
        Simulates a healing spell roll by rolling 'heal_die_count' dice of size 'heal_die'
        and adding 'modifier' accounting for criticals if needed
        """
        # 1. Base Healing (e.g., 2d8)
        base_heal = sum(random.randint(1, int(self.heal_die)) for _ in range(int(self.heal_die_count)))
        
        # 2. Add Modifier and Magic Bonus
        total_heal = base_heal*critical_mod + modifier

        return total_heal