import json

from utilities import load_characters
from character import Character

# Initialize variables
characters = []

# Initialize characters, enemies & populate their variables - JSON - this also rolls initative
characters = load_characters("characters.json")

# Organize characters by initative
characters.sort(key=lambda c: (c.initiative, c.scores['Dexterity']), reverse=True)

# Main Turn loop until exit condition met - Enemies All Dead, Party all Dead (Future Iterations Might Include Retreat Options)
while True:
    for character in characters:
        # # Movement (Future)
        pass
        # # Choice Bonus Action or Action first
        # # Choose Available Character Action - character.choose_action()
        # # Choose Available Character Bonus Action
        # # Legendary Actions If Available (Random chance to use until automatically utilized before running out at character's turn)
    # # Check if exit conditions met


# Create a list of all possible team actions/character actions with a weighting formula for characters choosing them

# Character should have primary choices
# Optomize for Damage Done - support actions weighted too
# Choose heal when below a certain percentage?

