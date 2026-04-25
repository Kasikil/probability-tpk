import math
import random

from spell import Spell
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

    # Defines how often a spell will be cast when the caster has the option between a physical weapon and a spell

    def __init__(self, data, spells):
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
        self.has_advantage = False
        self.has_disadvantage = False
        
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
                extra_damage=weapon_data.get("extra_damage",None),
                weapon_type=weapon_data.get("weapon_type","Melee")
            )
        else:
            self.equipped_weapon = None

        self.skill_proficiencies = data.get("skill_proficiencies", [])
        
        # Calculate HP based on class and level
        self.hp_max = data.get("hp_max") or self.calculate_initial_hp()
        self.current_hp = data.get("current_hp", self.hp_max)

        self.roll_initiative()

        self.target_choice_weights = data.get("target_choice_weights", {}) #TODO: Implementation

        self.possible_actions = [
            {"name": "Attack", "base_weight": data.get("action_preference_weights", {}).get("Attack", 10), "logic": self._score_attack},
            {"name": "Heal Self", "base_weight": data.get("action_preference_weights", {}).get("Heal Self", 0), "logic": self._score_heal},
            {"name": "Heal Others", "base_weight": data.get("action_preference_weights", {}).get("Heal Others", 0), "logic": self._score_heal_others},
            {"name": "Buff", "base_weight": data.get("action_preference_weights", {}).get("Buff", -50), "logic": self._score_buff}, #TODO: update inital weight
            {"name": "Nerf", "base_weight": data.get("action_preference_weights", {}).get("Nerf", -50), "logic": self._score_nerf} #TODO: update initial weight
        ]

        self.spell_slots = data.get("spell_slots", []) # Access via self.spell_slots["1st"]["max"]
        self.spellcasting_ability = data.get("spellcasting_ability","Wisdom")
        self.spell_list_names = data.get("spell_list", [])
        self.spell_list = [spells[name] for name in self.spell_list_names if name in spells]
        self.spellcaster_spell_attack = data.get("spellcaster_spell_attack", 0)

    def _score_attack(self, state):
        score = 0
        if (state['enemies_present'] > 0 or state['unconcious_enemies'] > 0) and self.hero_status == 1 :
            score += 15
        if (state['heroes_present'] > 0 or state['unconcious_heroes'] > 0) and self.hero_status == 0:
            score += 15
        if state['target_hp_low']:
            score += 10 # Prioritize finishing off enemies
        return score

    def _score_heal(self, state):
        # Highly weighted only if the character is hurt
        hp_percent = self.current_hp / self.hp_max
        potion_count = self.current_potion_count()
        heal_spell_count = self.current_castable_spell_count(spell_type='Heal')
        if hp_percent < 0.3 and (potion_count > 0 or heal_spell_count > 0):
            return 60  # Emergency healing
        if hp_percent < 0.7  and (potion_count > 0 or heal_spell_count > 0):
            return 20  # Moderate need
        return -50     # Don't heal if healthy
    
    def _score_heal_others(self, state):
        # Weighted if allies are hurt, but less than self-heal
        potion_count = self.current_potion_count()
        if potion_count == 0 and self.current_castable_spell_count(spell_type='Heal') == 0:
            return -50 # Can't heal others if you have no potions or healing spells

        if self.hero_status == 1 and state['heroes_present'] > 0:
            avg_ally_hp_percent = sum(hp.current_hp / hp.hp_max for hp in state['heroes']) / state['heroes_present']
            if avg_ally_hp_percent < 0.5:
                return 20  # Allies are in trouble
            
        elif self.hero_status == 0 and state['enemies_present'] > 0:
            avg_ally_hp_percent = sum(hp.current_hp / hp.hp_max for hp in state['enemies']) / state['enemies_present']
            if avg_ally_hp_percent < 0.5:
                return 20  # Allies are in trouble
        
        if self.hero_status == 1 and state['heroes_present'] > 0:
            for hp in state['heroes']:
                if hp.current_hp / hp.hp_max < 0.3 and hp != self and hp.is_dead == False and hp.is_conscious == True:
                    return 30 # Prioritize critically hurt allies
                elif hp.current_hp == 0 and not hp.is_conscious and not hp.is_dead:
                    return 50 # Prioritize unconcious allies for healing to stabilize them
        elif self.hero_status == 0 and state['enemies_present'] > 0:
            for hp in state['enemies']:
                if hp.current_hp / hp.hp_max < 0.3 and hp != self and hp.is_dead == False and hp.is_conscious == True:
                    return 30 # Prioritize critically hurt allies
                elif hp.current_hp == 0 and not hp.is_conscious and not hp.is_dead:
                    return 50 # Prioritize unconcious allies for healing to stabilize them

        return -50  # Don't prioritize healing others if they are relatively healthy
    
    def _score_buff(self, state):
        return -50
        #TODO: Implement

    def _score_nerf(self, state):
        return -50
        #TODO: Implement

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

    def perform_action(self, action_name, target=None):
        if action_name == "Attack" and target:
            return self.execute_attack(target)
        elif action_name == "Heal Self":
            self.heal(self)
        elif action_name == "Heal Others" and target:
            return self.heal(target)
        elif action_name == "Buff":
            self.buff()
        elif action_name == "Nerf":
            self.nerf()
        return f"{self.name} used {action_name}"

    def execute_attack(self, target):
        
        can_cast = hasattr(self, 'spell_slots') and any(s['current'] > 0 for s in self.spell_slots.values())


        if can_cast and random.random() < self.spellcaster_spell_attack:
            return self.execute_spell_attack(target)
        
        if not self.equipped_weapon:
            return f"{self.name} has no weapon!"

        # Roll to hit: d20 + Ability Mod + Proficiency
        if not target.is_conscious and target.current_hp == 0:
            if self.equipped_weapon.type == "Melee":
                death_save_fails = 2
            else:
                death_save_fails = 1
            target.take_damage(0, death_save_fails=death_save_fails)
            return f"{self.name} auto-CRITS {target.name} for {death_save_fails} failed death saves!"
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

    def execute_spell_attack(self, target):
        # Find the highest available slot
        #TODO: Implement some fuziness in choosing available level spells
        available_levels = [lvl for lvl, data in self.spell_slots.items() if data['current'] > 0]
        best_slot = available_levels[-1] # Grabs the highest string, e.g., "2nd"
        
        # Use the slot
        self.spell_slots[best_slot]['current'] -= 1
        
        spell_mod = self.get_modifier(self.spellcasting_ability)
        base_roll, total_to_hit = self.roll_d20(spell_mod + self.proficiency_bonus)
        
        # Critical Check
        crit_mod = 1
        if base_roll == 20:
            crit_mod = 2
        
        if total_to_hit >= target.ac:
            # Example: Scale damage by slot level (Level 1 = 2d6, Level 2 = 3d6, etc.)
            slot_int = int(best_slot[0])

            # Filter spells to find one matching the slot level
            # We use next() to grab the first spell that matches the level
            matching_spells = [s for s in self.spell_list if s.level == slot_int]

            if not matching_spells:
                # Fallback if no spell of that level exists in your data
                return f"{self.name} tried to cast a {best_slot} level spell, but knows no spells of that level!"

            damage = matching_spells[0].calculate_single_target_damage(spell_mod, crit_mod)
            target.take_damage(damage)
            return f"{self.name} casts a {best_slot} level spell! HITS {target.name} for {damage} damage."
        
        return f"{self.name} fires a spell at {target.name} but MISSES."

    def heal(self, target):
        healing_hp = 0

        # Always heal with spells before potions if available
        if self.current_castable_spell_count('Heal') == 0:
            if self.current_potion_count() == 0:
                return f"{self.name} has no healing spells or potions left to heal {target.name}!"
            else:
                healing_hp = self.drink_potion()
        else:
            healing_hp = self.cast_healing()

        target.recieve_healing(healing_hp)
        return f"{self.name} heals {target.name} for {healing_hp} HP!"


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
        if self.has_advantage and not self.has_disadvantage:
            roll = max(random.randint(1, 20), random.randint(1, 20))
        elif self.has_disadvantage and not self.has_advantage:
            roll = min(random.randint(1, 20), random.randint(1, 20))
        else:
            roll = random.randint(1, 20)
        return roll, roll + modifier
    
    def take_damage(self, amount, death_save_fails=0):
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
        
        if death_save_fails >= 0:
            self.death_failures += death_save_fails
            if self.death_failures >= self.allowed_death_saves:
                self.is_dead = True
                # print(f"{self.name} has died due to failed death saves.")

    def recieve_healing(self, amount):
        """Recieves healing from an external source (like a spell or ally's action)."""
        if self.is_dead:
            # print(f"{self.name} cannot be healed because they are dead.")
            return
        elif not self.is_conscious and self.current_hp == 0:
            self.is_conscious = True
            self.death_successes = 0
        
        self.current_hp = min(self.hp_max, self.current_hp + amount)

    def buff(self):
        #TODO: Implement buff functionality with magic
        pass

    def nerf(self):
        #TODO: Implement nerf functionality with magic
        pass

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
    
    def set_advantage(self, has_advantage=False, has_disadvantage=False):
        """Sets advantage/disadvantage status. Both True results in a cancel-out (False)."""
        if has_advantage and has_disadvantage:
            # Rules-as-written: they cancel each other out entirely
            self.has_advantage = False
            self.has_disadvantage = False
        else:
            self.has_advantage = has_advantage
            self.has_disadvantage = has_disadvantage
    
    def current_potion_count(self):
        potion_count = self.health_potions["supreme_potion_of_healing"] + self.health_potions["superior_potion_of_healing"] + self.health_potions["greater_potion_of_healing"] + self.health_potions["potion_of_healing"]
        return potion_count
    
    def drink_potion(self):
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

        return amount
    
    def current_castable_spell_count(self, spell_type='Damage'):
        spells = [
            s for s in self.spell_list 
            if s.spell_type == spell_type and self.spell_slots.get(s.level, {}).get('current', 0) > 0]
        return len(spells)
    
    def cast_healing(self):
        healing_spells = [
            s for s in self.spell_list 
            if s.spell_type == "Heal" and self.spell_slots.get(s.level, {}).get('current', 0) > 0]
        
        healing_spells = sorted(healing_spells, key=lambda s: s.level, reverse=True) # Cast the highest level heal available

        if len(healing_spells) == 0:
            return 0
        
        # Use the slot
        best_spell = healing_spells[0]  
        self.spell_slots[best_spell.level]['current'] -= 1
        return best_spell.calculate_healing(self.get_modifier(self.spellcasting_ability))