import requests
import csv
import json

def get_all_characters():
    """
    Fetches all characters from the Rick and Morty API who are:
    - Human
    - Alive
    - Origin is Earth
    """
    all_matching_characters = []
    page = 1
    has_more_pages = True
    
    print("Fetching characters from the Rick and Morty API...")
    
    # Let's fetch only alive humans and inspect their origins
    while has_more_pages:
        url = f"https://rickandmortyapi.com/api/character/?page={page}&status=alive&species=human"
        print(f"Fetching page {page}...")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            characters = data['results']
            
            # Debug: print the first character on this page (only on first page)
            if characters and page == 1:
                print(f"Sample character data: {json.dumps(characters[0], indent=2)}")
            
            # Print all origins to see what we're dealing with (only on first page)
            if page == 1:
                print("\nOrigins found on page 1:")
                origins = set(char['origin']['name'] for char in characters)
                for origin in origins:
                    print(f"- {origin}")
                print()
            
            # Filter for characters with Earth origin (case insensitive)
            earth_variations = ["earth", "earth (c-137)", "earth (replacement dimension)"]
            for character in characters:
                if character['origin']['name'].lower() in earth_variations:
                    all_matching_characters.append({
                        'name': character['name'],
                        'location': character['location']['name'],
                        'image': character['image']
                    })
            
            # Check if there are more pages
            if 'info' in data and data['info']['next']:
                page += 1
            else:
                has_more_pages = False
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            has_more_pages = False
        except (KeyError, ValueError) as e:
            print(f"Error processing data: {e}")
            has_more_pages = False
    
    return all_matching_characters

def save_to_csv(characters, filename="rick_and_morty_characters.csv"):
    """
    Saves the character data to a CSV file
    """
    # Ensure no newlines in any of the data fields
    sanitized_characters = []
    for character in characters:
        sanitized_characters.append({
            'name': character['name'].replace('\n', ' ').replace('\r', ''),
            'location': character['location'].replace('\n', ' ').replace('\r', ''),
            'image': character['image'].replace('\n', ' ').replace('\r', '')
        })
        
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Location', 'Image']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        
        writer.writeheader()
        for character in sanitized_characters:
            writer.writerow({
                'Name': character['name'],
                'Location': character['location'],
                'Image': character['image']
            })
    
    print(f"Successfully saved {len(characters)} characters to {filename}")

def main():
    characters = get_all_characters()
    print(f"Found {len(characters)} characters that match the criteria")
    
    if characters:
        save_to_csv(characters)
        print("\nFirst few characters found:")
        for i, character in enumerate(characters[:5]):
            print(f"{i+1}. {character['name']} - {character['location']}")
    else:
        print("No characters found matching the criteria.")

if __name__ == "__main__":
    main() 