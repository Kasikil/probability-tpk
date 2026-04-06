import json
import random
import time

from character import Character
from spell import Spell

def load_characters(filename, spells):
    """Loads a list of characters from a single JSON file."""
    party_members = []
    
    try:
        with open(filename, 'r') as f:
            data_list = json.load(f)  # This is now a list, not a dict
            
            for char_data in data_list:
                # Create a character instance using the dictionary
                new_char = Character(char_data, spells)
                party_members.append(new_char)
                
        return party_members
    
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: {filename} is not formatted correctly.")
        return []
    
def load_spells(filename):
    """Loads a list of spells from a single JSON file."""
    try:
        with open(filename, 'r') as f:
            data_list = json.load(f)
            
            # Create a dictionary where the KEY is the name 
            # and the VALUE is the instantiated Spell object
            return {d["name"]: Spell(d) for d in data_list}
            
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return {} # Return empty dict instead of list for consistency
    except json.JSONDecodeError:
        print(f"Error: {filename} is not formatted correctly.")
        return {}
    
_start_time = None

def tic():
    global _start_time
    _start_time = time.perf_counter()

def toc():
    if _start_time is None:
        print("Error: tic() was never called.")
        return
    elapsed = time.perf_counter() - _start_time
    print(f"Elapsed time is {elapsed:.6f} seconds.")
    return elapsed

def select_target(all_characters, acting_character, action_type="Attack"):
    # Filter for living characters only
    living = [c for c in all_characters if c.current_hp > 0]

    if action_type == "Attack":
        # Heroes attack Enemies (status 0), Enemies attack Heroes (status 1)
        targets = [c for c in living if c.hero_status != acting_character.hero_status]
        return random.choice(targets) if targets else None

    if action_type == "Heal":
        # Target allies (same hero_status) who are below max HP
        allies = [c for c in living if c.hero_status == acting_character.hero_status and c.current_hp < c.hp_max]
        return random.choice(allies) if allies else acting_character

    return None

def process_death_saves(character):
    if character.is_conscious or character.is_dead:
        return
    
    if character.allowed_death_saves == 0:
        character.is_dead = True
        return

    roll = random.randint(1, 20)
    
    if roll == 20:
        character.hp = 1
        character.is_conscious = True
        character.death_successes = 0
        character.death_failures = 0
        #print(f"✨ {character.name} rolled a 20 and regained consciousness!")
    elif roll >= 10:
        character.death_successes += 1
        #print(f"👍 {character.name} saved (S:{character.death_successes} F:{character.death_failures})")
    else:
        # Natural 1 counts as two failures
        character.death_failures += (2 if roll == 1 else 1)
        #print(f"💀 {character.name} failed (S:{character.death_successes} F:{character.death_failures})")

    # Check terminal conditions
    if character.death_successes >= 3:
        character.is_conscious = False # Stable but unconscious
        character.death_successes = 0
        character.death_failures = 0
        #print(f"💤 {character.name} is now stable.")
        
    if character.death_failures >= 3:
        character.is_dead = True
        #print(f"❌ {character.name} has died.")