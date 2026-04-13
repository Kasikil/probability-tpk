import json
import random

from utilities import load_characters, select_target, process_death_saves
from character import Character



def combat_loop(characters_data, spells):
    # Initialize variables
    characters = []
    enemies = []
    heroes = []
    unconcious_heroes = []
    unconcious_enemies = []
    state = {
        "round": 0,
        "enemies_present": 0,
        "heroes_present": 0,
        "target_hp_low": 0,
        "primary_enemy": 0
    }
    reportables = []

    # Initialize characters, enemies & populate their variables - JSON - this also rolls initative
    characters = load_characters(characters_data, spells)

    # Organize characters by initative
    characters.sort(key=lambda c: (c.initiative, c.scores['Dexterity']), reverse=True)

    # Main Turn loop until exit condition met - Enemies All Dead, Party all Dead (Future Iterations Might Include Retreat Options)
    while True:
        state["round"] =+ 1
        for char in characters:
            if char.is_dead: continue # Skip dead characters

            if not char.is_conscious and char.current_hp == 0:
                # If they haven't reached 3 successes/failures yet
                process_death_saves(char)
                continue

            # 1. Update State
            enemies = [c for c in characters if c.hero_status == 0 and c.current_hp > 0]
            heroes = [c for c in characters if c.hero_status == 1 and c.current_hp > 0]
            unconcious_heroes = [c for c in characters if c.hero_status == 1 and c.current_hp <= 0 and not c.is_dead]
            unconcious_enemies = [c for c in characters if c.hero_status == 0 and c.current_hp <= 0 and not c.is_dead]

            # Check Win/Loss Conditions
            if not enemies or not heroes:
                return "Heroes Win" if heroes else "TPK"

            state["enemies_present"] = len(enemies)
            state["heroes_present"] = len(heroes)
            if char.hero_status == 1:
                state["target_hp_low"] = any(e.current_hp / e.hp_max < 0.3 for e in enemies)
                state["primary_enemy"] = enemies[0] if enemies else None
            if char.hero_status == 0:
                state["target_hp_low"] = any(h.current_hp / h.hp_max < 0.3 for h in heroes)
                state["primary_enemy"] = heroes[0] if heroes else None
            state["unconcious_heroes"] = len(unconcious_heroes)
            state["unconcious_enemies"] = len(unconcious_enemies)

            # 2. Decide and Act
            action = char.decide_action(state)
            target = select_target(characters, char, action)
            
            log = char.perform_action(action, target)
            #print(log)

            # # Choice Bonus Action or Action first
            # # Choose Available Character Action - character.choose_action()
            # # Choose Available Character Bonus Action
            # # Check if reaction is triggered (Future)
            # # Legendary Actions If Available (Random chance to use until automatically utilized before running out at character's turn)


    # Create a list of all possible team actions/character actions with a weighting formula for characters choosing them

    # Character should have primary choices
    # Optomize for Damage Done - support actions weighted too
    # Choose heal when below a certain percentage?