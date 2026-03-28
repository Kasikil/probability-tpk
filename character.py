import math
import random

from weapon import Weapon

class Character:
    # Mapping classes to their hit die values
    CLASS_HIT_DIE = {
        "Barbarian": 12,
        "Fighter": 10, 
        "Paladin": 10, 
        "Ranger": 10,
        "Bard": 8, 
        "Cleric": 8, 
        "Druid": 8, 
        "Monk": 8, 
        "Rogue": 8, 
        "Warlock": 8,
        "Sorcerer": 6, 
        "Wizard": 6
    }

    def __init__(self, data):
        self.name = data.get("name", "Unknown Hero")
        self.char_class = data.get("char_class", "Fighter")
        self.level = data.get("level", 1)
        self.race = data.get("race", "Human")
        self.reactions = data.get("reactions", 1)
        self.legendary_actions = data.get("legenary_actions", 0)
        
        # Ability Scores (default to 10 if missing)
        self.scores = data.get("scores", {
            "Strength": 10, "Dexterity": 10, "Constitution": 10,
            "Intelligence": 10, "Wisdom": 10, "Charisma": 10
        })

        self.initative = 0

        # Handle Weapon logic from nested dictionary
        weapon_data = data.get("weapon")
        if weapon_data:
            self.equipped_weapon = Weapon(
                name=weapon_data["name"],
                damage_die=weapon_data["damage_die"],
                ability=weapon_data.get("ability", "Strength")
            )
        else:
            self.equipped_weapon = None

        self.skill_proficiencies = data.get("skill_proficiencies", [])
        
        # Calculate HP based on class and level
        self.hp_max = data.get("hp_max") or self.calculate_initial_hp()
        self.current_hp = data.get("current_hp", self.hp_max)

        self.roll_initative()

    def calculate_initial_hp(self):
        # (Using the logic from our previous steps)
        hit_die = self.CLASS_HIT_DIE.get(self.char_class, 8)
        con_mod = (self.scores["Constitution"] - 10) // 2
        return hit_die + con_mod + (self.level - 1) * (hit_die // 2 + 1 + con_mod)

    @property
    def proficiency_bonus(self):
        return math.ceil(1 + (self.level / 4))
    
    def set_scores(self, str, dex, con, int, wis, cha):
        """Bulk update ability scores."""
        self.scores["Strength"] = str
        self.scores["Dexterity"] = dex
        self.scores["Constitution"] = con
        self.scores["Intelligence"] = int
        self.scores["Wisdom"] = wis
        self.scores["Charisma"] = cha

    def get_modifier(self, ability):
        score = self.scores.get(ability, 10)
        return (score - 10) // 2

    def calculate_max_hp(self):
        """Standard 5e HP: Max die at lvl 1, then (average + CON) per level after."""
        con_mod = self.get_modifier("Constitution")
        # Level 1: Full Hit Die + CON
        hp = self.hit_die + con_mod
        # Levels 2+: Half die + 1 (average) + CON
        if self.level > 1:
            hp += (self.level - 1) * ((self.hit_die // 2 + 1) + con_mod)
        return hp

    def roll_d20(self, modifier=0):
        """Simulates a d20 roll with a modifier."""
        roll = random.randint(1, 20)
        return roll, roll + modifier
    
    def take_damage(self, amount):
        """Reduces current HP and checks for unconsciousness/death."""
        if amount < 0:
            # print("Damage cannot be negative. Use a healing method instead.")
            return

        self.current_hp -= amount
        
        # 5e Instant Death Rule: 
        # If damage reduces you to 0 and the remainder equals or exceeds your max HP.
        if self.current_hp <= -self.hp_max:
            self.current_hp = 0
            # print(f"CRITICAL: {self.name} took massive damage and died instantly!")
        elif self.current_hp <= 0:
            self.current_hp = 0
            # print(f"{self.name} has fallen unconscious (0 HP)!")
        else:
            return
            # print(f"{self.name} took {amount} damage. Current HP: {self.current_hp}/{self.hp_max}")

    def heal(self, amount):
        """Restores HP without exceeding the maximum."""
        self.current_hp += amount
        if self.current_hp > self.hp_max:
            self.current_hp = self.hp_max
        #print(f"{self.name} healed for {amount}. Current HP: {self.current_hp}/{self.hp_max}")

    def roll_initative(self):
        # returns natural_roll, total_result
        _, self.initative = self.roll_d20(self.get_modifier("Dexterity"))
    
    def skill_check(self, skill_name, base_ability):
        """Performs a skill check, adding proficiency if applicable."""
        modifier = self.get_modifier(base_ability)
        if skill_name in self.skill_proficiencies:
            modifier += self.proficiency_bonus
        
        natural, total = self.roll_d20(modifier)
        print(f"{self.name} rolls {skill_name} ({base_ability}): {natural} + {modifier} = {total}")
        return total
    
    def choose_action(self):
        """
        actions = {
            "1": "Attack",
            "2": "Cast a Spell",
            /"3": "Dash", #N/A This Version
            "4": "Disengage", # available to all classes as an action, bonus action for rogues
            "5": "Dodge",
            "6": "Help/Support",
            "7": "Hide",
            /"8": "Ready", #Future implementation
            /"9": "Search", #N/A
            /"10": "Use an Object"
            "11": Heal Self
        }
        """
        
        return

# --- Testing the Upgrades ---


print(f"Max HP: {grog.hp_max}") # (12+3) + 4*(7+3) = 15 + 40 = 55