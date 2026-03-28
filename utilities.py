import json

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