from flask import Flask, render_template, jsonify, request
import requests
import time
import aiohttp
import asyncio

app = Flask(__name__)

def make_request_with_retry(url, max_retries=5, delay=1):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)

            if response.status_code == 200:
                return response  # Success, return the response

            elif response.status_code == 429:
                print("Too many requests. Waiting before retry...")
                time.sleep(2 ** retries)  # Exponential backoff (2^retries seconds)

            elif response.status_code in [500, 503]:
                print(f"Server error {response.status_code}. Retrying after delay...")
                time.sleep(delay)  # Pause before retrying

            elif response.status_code in [400, 401, 403, 404]:
                print(f"Error {response.status_code}: {response.reason}")
                break  # Client errors or access denied, no point in retrying

        except requests.exceptions.RequestException as e:
            print(f"Exception: {e}")
            break  # Stop on request exception

        retries += 1

    return None  # Failure after all retries

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pokemon/<name_or_id>', methods=['GET'])
def get_pokemon(name_or_id):
    url = f'https://pokeapi.co/api/v2/pokemon/{name_or_id}'
    
    # Use the request handling function
    response = make_request_with_retry(url)
    
    if response and response.status_code == 200:
        data = response.json()
        stats = {
            "name": data['name'],
            "hp": data['stats'][0]['base_stat'],
            "attack": data['stats'][1]['base_stat'],
            "defense": data['stats'][2]['base_stat'],
        }
        return jsonify(stats)
    else:
        return jsonify({"error": "Pokémon not found"}), 404

@app.route('/compare', methods=['POST'])
def compare_pokemons():
    data = request.json
    pokemon1 = data.get('pokemon1')
    pokemon2 = data.get('pokemon2')

    def get_stats(pokemon):
        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon}'
        response = make_request_with_retry(url)  # Use the request handling function
        if response and response.status_code == 200:
            data = response.json()
            return {
                "name": data['name'],
                "hp": data['stats'][0]['base_stat'],
                "attack": data['stats'][1]['base_stat'],
                "defense": data['stats'][2]['base_stat']
            }
        return None

    stats1 = get_stats(pokemon1)
    stats2 = get_stats(pokemon2)

    if stats1 and stats2:
        stronger = pokemon1 if stats1['hp'] > stats2['hp'] and stats1['attack'] > stats2['attack'] else pokemon2
        return jsonify({
            "pokemon1": stats1,
            "pokemon2": stats2,
            "stronger": stronger
        })
    return jsonify({"error": "Un ou les deux Pokémon n'ont pas été trouvés"}), 404

@app.route('/type/<type_name>', methods=['GET'])
def get_pokemon_by_type(type_name):
    url = f'https://pokeapi.co/api/v2/type/{type_name}'
    response = make_request_with_retry(url)  # Use the request handling function
    if response and response.status_code == 200:
        data = response.json()
        pokemon_count = len(data['pokemon'])
        total_hp = 0
        for p in data['pokemon']:
            pokemon_url = p['pokemon']['url']
            pokemon_response = make_request_with_retry(pokemon_url)  # Use the request handling function
            if pokemon_response and pokemon_response.status_code == 200:
                pokemon_data = pokemon_response.json()
                total_hp += pokemon_data['stats'][0]['base_stat']
        
        average_hp = total_hp / pokemon_count if pokemon_count > 0 else 0
        
        effectiveness = {
            "double_damage_to": [t['name'] for t in data['damage_relations']['double_damage_to']],
            "half_damage_to": [t['name'] for t in data['damage_relations']['half_damage_to']],
            "no_damage_to": [t['name'] for t in data['damage_relations']['no_damage_to']]
        }

        return jsonify({
            "type": type_name,
            "pokemon_count": pokemon_count,
            "average_hp": average_hp,
            "effectiveness": effectiveness
        })
    else:
        return jsonify({"error": "Type non trouvé"}), 404

# Asynchronous request handling
async def fetch(session, url):
    try:
        async with session.get(url) as response:
            return await response.json() if response.status == 200 else None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

@app.route('/simulate-load', methods=['GET'])
async def simulate_load():
    urls = [
        "https://api.example.com/data1",
        "https://api.example.com/data2",
        "https://api.example.com/data3"
    ]
    
    results = await fetch_all(urls)
    
    return jsonify({
        "results": results,
    })

# New route to simulate a battle between two Pokémon
@app.route('/battle', methods=['POST'])
def battle_pokemons():
    data = request.json
    pokemon1_name = data.get('pokemon1')
    pokemon2_name = data.get('pokemon2')

    stats1 = get_stats(pokemon1_name)
    stats2 = get_stats(pokemon2_name)

    if stats1 is None or stats2 is None:
        return jsonify({"error": "Un ou les deux Pokémon n'ont pas été trouvés"}), 404

    turns = 5
    pokemon1_damage = 0
    pokemon2_damage = 0

    for turn in range(turns):
        # Calculate damage based on attack and defense
        damage1 = max(0, stats1['attack'] - stats2['defense'])  # Pokémon 1 attacks Pokémon 2
        damage2 = max(0, stats2['attack'] - stats1['defense'])  # Pokémon 2 attacks Pokémon 1
        
        pokemon1_damage += damage1
        pokemon2_damage += damage2

    winner = pokemon1_name if pokemon1_damage > pokemon2_damage else pokemon2_name

    return jsonify({
        "pokemon1": stats1,
        "pokemon2": stats2,
        "damage": {
            "pokemon1_total_damage": pokemon1_damage,
            "pokemon2_total_damage": pokemon2_damage
        },
        "winner": winner
    })

if __name__ == '__main__':
    app.run(debug=True)
