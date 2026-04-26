import requests
import json
import time

BASE_URL = "https://www.dnd5eapi.co"
LIST_URL = f"{BASE_URL}/api/2014/spells"
headers = {'Accept': 'application/json'}

def fetch_all_spells():
    print("Fetching the spell list...")
    list_response = requests.get(LIST_URL, headers=headers)
    
    if list_response.status_code != 200:
        print("Failed to get the list.")
        return

    spell_list = list_response.json()['results']
    full_spell_data = []

    print(f"Found {len(spell_list)} spells. Starting detailed download...")

    for spell in spell_list:
        # Get the specific URL for this spell (e.g., /api/2014/spells/acid-arrow)
        detail_url = f"{BASE_URL}{spell['url']}"
        
        detail_response = requests.get(detail_url, headers=headers)
        
        if detail_response.status_code == 200:
            full_spell_data.append(detail_response.json())
            print(f"Done: {spell['name']}")
        else:
            print(f"Error fetching: {spell['name']}")
        
        # Optional: Short pause to be kind to the API server
        time.sleep(0.1)

    # Save the massive list to one JSON file
    with open("full_spells_data.json", "w", encoding="utf-8") as f:
        json.dump(full_spell_data, f, indent=4)

    print("\nSuccess! All spells saved to 'full_spells_data.json'.")

if __name__ == "__main__":
    fetch_all_spells()