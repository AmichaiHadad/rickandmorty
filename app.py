from flask import Flask, jsonify
import requests
import csv
import json
import os

app = Flask(__name__)

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
    
    # Let's fetch only alive humans and filter by Earth origins
    while has_more_pages:
        url = f"https://rickandmortyapi.com/api/character/?page={page}&status=alive&species=human"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            characters = data['results']
            
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

# Save the data to CSV file for persistence
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

# Set response headers for all API responses
@app.after_request
def add_headers(response):
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Define API endpoints
@app.route('/', methods=['GET'])
def index():
    """Root endpoint that provides API information"""
    return jsonify({
        'name': 'Rick and Morty Characters API',
        'description': 'API for retrieving Rick and Morty characters that are Human, Alive, and from Earth',
        'endpoints': {
            '/characters': 'Get all matching characters',
            '/healthcheck': 'Check API health status'
        }
    })

@app.route('/characters', methods=['GET'])
def characters():
    """Return all characters meeting the criteria as JSON"""
    # First, check if we have a cached CSV file
    csv_file = "rick_and_morty_characters.csv"
    characters_data = []
    
    if os.path.exists(csv_file):
        # Read from the CSV file
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                characters_data.append({
                    'name': row['Name'],
                    'location': row['Location'],
                    'image': row['Image']
                })
    
    # If we don't have cached data or it's empty, fetch new data
    if not characters_data:
        characters_data = get_all_characters()
        # Cache the data
        save_to_csv(characters_data)
    
    return jsonify({
        'count': len(characters_data),
        'characters': characters_data
    })

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Health check endpoint to verify the API is running"""
    return jsonify({
        'status': 'ok',
        'message': 'The Rick and Morty API service is running'
    })

if __name__ == "__main__":
    # Fetch and cache data on startup
    print("Starting Rick and Morty API service...")
    print("Fetching character data...")
    characters_data = get_all_characters()
    save_to_csv(characters_data)
    print(f"Found {len(characters_data)} characters that match the criteria")
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port) 