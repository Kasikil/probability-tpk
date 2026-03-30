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

    FUZZ = True

    def __init__(self, data):
        self.name = data.get("name", "Unknown Hero")
        self.char_class = data.get("char_class", "Fighter")
        self.level = data.get("level", 1)
        self.race = data.get("race", "Human")
        self.reactions = data.get("reactions", 1)
        self.legendary_actions = data.get("legenary_actions", 0)
        self.ac = data.get("ac", 10) # Default to 10
        self.hero_status = data.get("hero", 1) # 1 for Hero, 0 for Enemy
        self.health_potions = data.get("health_potions", [])
        self.allowed_death_saves = data.get("allowed_death_saves", 1)
        self.is_conscious = True
        self.is_dead = False
        self.death_successes = 0
        self.death_failures = 0
        
        # Ability Scores (default to 10 if missing)
        self.scores = data.get("scores", {
            "Strength": 10, "Dexterity": 10, "Constitution": 10,
            "Intelligence": 10, "Wisdom": 10, "Charisma": 10
        })

        self.initiative = 0

        # Handle Weapon logic from nested dictionary
        weapon_data = data.get("weapon")
        if weapon_data:
            self.equipped_weapon = Weapon(
                name=weapon_data["name"],
                damage_die=weapon_data["damage_die"],
                die_count=weapon_data["die_count"],
                ability=weapon_data.get("ability", "Strength"),
                magic_bonus=weapon_data.get("magic_bonus", 0),
                extra_damage=weapon_data.get("extra_damage",None)
            )
        else:
            self.equipped_weapon = None

        self.skill_proficiencies = data.get("skill_proficiencies", [])
        
        # Calculate HP based on class and level
        self.hp_max = data.get("hp_max") or self.calculate_initial_hp()
        self.current_hp = data.get("current_hp", self.hp_max)

        self.roll_initiative()

        self.possible_actions = [
            {"name": "Attack", "base_weight": 10, "logic": self._score_attack},
            {"name": "Heal", "base_weight": 0, "logic": self._score_heal}
        ]

    def _score_attack(self, state):
        score = 0
        if state['enemies_present'] > 0:
            score += 15
        if state['target_hp_low']:
            score += 10 # Prioritize finishing off enemies
        return score

    def _score_heal(self, state):
        # Highly weighted only if the character is hurt
        hp_percent = self.current_hp / self.hp_max
        potion_count = self.health_potions["supreme_potion_of_healing"] + self.health_potions["superior_potion_of_healing"] + self.health_potions["greater_potion_of_healing"] + self.health_potions["potion_of_healing"]
        if hp_percent < 0.3 and potion_count > 0:
            return 40  # Emergency healing
        if hp_percent < 0.7  and potion_count > 0:
            return 10  # Moderate need
        return -50     # Don't heal if healthy

    def decide_action(self, encounter_state):
        if self.FUZZ:
            return self.get_fuzzy_action(encounter_state)

        best_action = None
        highest_score = -float('inf')

        for action in self.possible_actions:
            # Calculate the 'utility' of this action
            current_score = action["logic"](encounter_state) + action["base_weight"]
            
            if current_score > highest_score:
                highest_score = current_score
                best_action = action["name"]

        return best_action
    
    def get_fuzzy_action(self, state):
        actions = []
        weights = []
        
        for action in self.possible_actions:
            score = max(0, action["base_weight"] + action["logic"](state))
            actions.append(action["name"])
            weights.append(score)
    
        # Returns a random action, but higher scores have a much higher chance
        return random.choices(actions, weights=weights, k=1)[0]

    def take_turn(self, encounter_state):
        chosen_name = self.decide_action(encounter_state)
        # print(f"{self.name} decides to: {chosen_name}")
        self.perform_action(chosen_name, target=encounter_state.get('primary_enemy'))

    def perform_action(self, action_name, target=None):
        if action_name == "Attack" and target:
            return self.execute_attack(target)
        elif action_name == "Heal":
            self.heal()
        return f"{self.name} used {action_name}"

    def execute_attack(self, target):
        if not self.equipped_weapon:
            return f"{self.name} has no weapon!"

        # Roll to hit: d20 + Ability Mod + Proficiency
        mod = self.get_modifier(self.equipped_weapon.ability)
        base_roll, total_to_hit = self.roll_d20(mod + self.proficiency_bonus + self.equipped_weapon.magic_bonus)

        # Critical Check
        crit_mod = 1
        if base_roll == 20:
            crit_mod = 2

        # 5e Logic: Check against Target Armor Class
        if total_to_hit >= target.ac:
            damage = self.equipped_weapon.roll_damage(mod, crit_mod)
            target.take_damage(damage)
            return f"{self.name} HITS {target.name} for {damage} damage (Roll: {total_to_hit} vs AC {target.ac})"
        
        return f"{self.name} MISSES {target.name} (Roll: {total_to_hit} vs AC {target.ac})"

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
            self.is_dead = True
            self.is_conscious = False
            # print(f"CRITICAL: {self.name} took massive damage and died instantly!")
        elif self.current_hp <= 0:
            self.current_hp = 0
            if self.is_conscious:
                #print(f"--- {self.name} has fallen unconscious! ---")
                self.is_conscious = False
            # print(f"{self.name} has fallen unconscious (0 HP)!")
        else:
            return
            # print(f"{self.name} took {amount} damage. Current HP: {self.current_hp}/{self.hp_max}")

    def heal(self):
        """Restores HP without exceeding the maximum."""
        amount = 0

        if self.health_potions["supreme_potion_of_healing"] > 0:
            amount = sum([random.randint(1, 4) for _ in range(10)]) + 20
            self.health_potions["supreme_potion_of_healing"] -= 1
        elif self.health_potions["superior_potion_of_healing"] > 0:
            amount = sum([random.randint(1, 4) for _ in range(8)]) + 8
            self.health_potions["superior_potion_of_healing"] -= 1
        elif self.health_potions["greater_potion_of_healing"] > 0:
            amount = sum([random.randint(1, 4) for _ in range(4)]) + 4
            self.health_potions["greater_potion_of_healing"] -= 1
        elif self.health_potions["potion_of_healing"] > 0:
            amount = sum([random.randint(1, 4) for _ in range(2)]) + 2
            self.health_potions["potion_of_healing"] -= 1
        
        self.current_hp += amount
        if self.current_hp > self.hp_max:
            self.current_hp = self.hp_max
        #print(f"{self.name} healed for {amount}. Current HP: {self.current_hp}/{self.hp_max}")

    def roll_initiative(self):
        # returns natural_roll, total_result
        _, self.initiative = self.roll_d20(self.get_modifier("Dexterity"))
    
    def skill_check(self, skill_name, base_ability):
        """Performs a skill check, adding proficiency if applicable."""
        modifier = self.get_modifier(base_ability)
        if skill_name in self.skill_proficiencies:
            modifier += self.proficiency_bonus
        
        natural, total = self.roll_d20(modifier)
        #print(f"{self.name} rolls {skill_name} ({base_ability}): {natural} + {modifier} = {total}")
        return total
