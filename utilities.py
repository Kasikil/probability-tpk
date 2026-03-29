import json
import random
import time

from character import Character

def load_characters(filename):
    """Loads a list of characters from a single JSON file."""
    party_members = []
    
    try:
        with open(filename, 'r') as f:
            data_list = json.load(f)  # This is now a list, not a dict
            
            for char_data in data_list:
                # Create a character instance using the dictionary
                new_char = Character(char_data)
                party_members.append(new_char)
                
        return party_members
    
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: {filename} is not formatted correctly.")
        return []
    
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
