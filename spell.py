import math
import random

class Spell:

    def __init__(self, data):
        self.name = data.get("name", "Unknown Spell")
        self.level = data.get("level", 1)
        self.damage_type = data.get("damage_type", None)
        self.damage_die = data.get("damage_die", 0)
        self.die_count = data.get("die_count", 1)
        self.additional_damage = data.get("additional_damage", 0)
        self.spell_type = data.get("spell_type", "Unknown")
        self.heal_die = data.get("heal_die", 0)
        self.heal_die_count = data.get("heal_die_count", 1)
        self.components = data.get("components", []) #TODO: Implement
        self.casting_time = data.get("casting_time", "1 Action")  #TODO: Implement
        self.range = data.get("range", 0) #TODO: Implement
        self.duration = data.get("duration", 0) # Rounds  #TODO: Implement
        self.is_melee_spell_attack = data.get("is_melee_spell_attack", False) #TODO: Implement
        self.requires_weapon_attack = data.get("requires_weapon_attack", True) #TODO: Implement
        self.hitpoint_block = data.get("hitpoint_block", "Next Turn Start") #TODO: Implement
        self.gives_disadvantage = data.get("gives_disadvantage", "Undead") #TODO: Implement
        self.upcast_type = data.get("upcast_type", "character_level") #TODO: Implement
        self.upcast = data.get("upcast", {}) #TODO: Implement
        self.multi_attack = data.get("multi-attack", False) #TODO: Implement
        self.target_next_saving_throw_penalty = data.get("target_next_saving_throw_penalty", 0) #TODO: Implement
        self.speed_reduction = data.get("speed_reduction", 0) #TODO: Implement
        self.speed_reduction_duration = data.get("speed_reduction_duration", 0) #TODO: Implement - Measured to the start of next turn
        self.drop_prone = data.get("drop_prone", False) #TODO: Implement
        self.resistances_granted = data.get("resistances_granted", []) #TODO: Implement
        self.ends = data.get("ends", None) #TODO: Implement
        self.persistant_hazard = data.get("persistant_hazard", False) #TODO: Implement
        self.damage_per_round = data.get("damage_per_round", False) #TODO: Implement
        self.concentration = data.get("concentration", False) #TODO: Implement
        self.different_damage_on_secondary_target = data.get("different_damage_on_secondary_target", False) #TODO: Implement
        self.secondary_target_damage_die = data.get("secondary_target_damage_die", "0") #TODO: Implement
        self.secondary_target_die_count = data.get("secondary_target_die_count", 0) #TODO: Implement
        self.secondary_target_damage_type = data.get("secondary_target_damage_type", None) #TODO: Implement
        self.secondary_target_additional_damage = data.get("secondary_target_additional_damage", "0") #TODO: Implement
        self.description = data.get("description", "No description available.")
        self.move_target = data.get("move_target", None) #TODO: Implement

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