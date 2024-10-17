from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pokemon/<name_or_id>', methods=['GET'])
def get_pokemon(name_or_id):
    url = f'https://pokeapi.co/api/v2/pokemon/{name_or_id}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        stats = {
            "name": data['name'],
            "hp": data['stats'][0]['base_stat'],
            "attack": data['stats'][1]['base_stat'],
            "defense": data['stats'][2]['base_stat'],
        }
        return jsonify(stats)
    else:
        return jsonify({"error": "Pokémon non trouvé"}), 404

@app.route('/compare', methods=['POST'])
def compare_pokemons():
    data = request.json
    pokemon1 = data.get('pokemon1')
    pokemon2 = data.get('pokemon2')

    def get_stats(pokemon):
        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data['name'],
                "hp": data['stats'][0]['base_stat'],
                "attack": data['stats'][1]['base_stat']
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



if __name__ == '__main__':
    app.run(debug=True)
