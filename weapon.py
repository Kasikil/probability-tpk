import random

class Weapon:
    def __init__(self, name, damage_die, die_count=1, ability="Strength", magic_bonus=0, extra_damage=None, weapon_type="Melee"):
        """
        :param damage_die: The size of the die (e.g., 6 for d6).
        :param die_count: Number of dice (e.g., 2 for 2d6 Greatsword).
        :param ability: The ability score used for the attack.
        :param magic_bonus: Flat bonus (e.g., +1 for a +1 Weapon).
        :param extra_damage: Dictionary of elemental damage {die_size: "type"} 
                             e.g., {4: "Fire"} for an extra 1d4 fire.
        """
        self.name = name
        self.damage_die = damage_die  # e.g., 12 for a d12
        self.die_count = die_count
        self.ability = ability
        self.magic_bonus = magic_bonus
        self.extra_damage = extra_damage if extra_damage else {}
        self.type = weapon_type

    def roll_damage(self, modifier, critical_mod=1):
        """Calculates total damage: (XdY + mod + magic) + (Elemental dice)."""
        # 1. Base Damage (e.g., 2d6)
        base_roll = sum(random.randint(1, self.damage_die) for _ in range(self.die_count))
        
        # 2. Add Modifier and Magic Bonus
        total_physical = base_roll*critical_mod + modifier + self.magic_bonus
        
        # 3. Add Elemental Damage (e.g., 1d4 Cold)
        elemental_total = 0
        elemental_breakdown = []
        
        for die_size, damage_type in self.extra_damage.items():
            roll = random.randint(1, int(die_size))
            elemental_total += roll
            elemental_breakdown.append(f"{roll} {damage_type}")

        # For logging purposes, you might return a dict or a string, 
        # but for simulation math, we usually just need the integer sum.
        return total_physical + elemental_total*critical_mod