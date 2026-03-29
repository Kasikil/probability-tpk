import json

from utilities import load_characters, select_target
from character import Character



def combat_loop(input_file_path):
    # Initialize variables
    characters = []
    enemies = []
    heroes = []
    state = {
        "round": 0,
        "enemies_present": 0,
        "heroes_present": 0,
        "target_hp_low": 0,
        "primary_enemy": 0
    }
    reportables = []

    # Initialize characters, enemies & populate their variables - JSON - this also rolls initative
    characters = load_characters(input_file_path)

    # Organize characters by initative
    characters.sort(key=lambda c: (c.initiative, c.scores['Dexterity']), reverse=True)

    # Main Turn loop until exit condition met - Enemies All Dead, Party all Dead (Future Iterations Might Include Retreat Options)
    while True:
        state["round"] =+ 1
        for char in characters:
            if char.current_hp <= 0: continue # Skip dead characters

            # 1. Update State
            enemies = [c for c in characters if c.hero_status == 0 and c.current_hp > 0]
            heroes = [c for c in characters if c.hero_status == 1 and c.current_hp > 0]

            # Check Win/Loss Conditions
            if not enemies or not heroes:
                return "Heroes Win" if heroes else "TPK"

            state["enemies_present"] = len(enemies)
            state["heroes_present"] = len(heroes)
            state["target_hp_low"] = any(e.current_hp / e.hp_max < 0.3 for e in enemies)
            state["primary_enemy"] = enemies[0] if enemies else None

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