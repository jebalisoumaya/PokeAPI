# Pokeverse 
PokéVerse, a Flask-based web app that allows user to fetch statistics for Pokémon, compare two Pokémon, and simulate battles between them using PokéApi to retrieve Pokémon data, including their stats and type effectiveness.

Pour que ca marche ( apres clone)
1-	Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
2-	Install the required packages:
pip install Flask requests aiohttp
3-	python app.py
Get Pokémon Stats
•	GET /pokemon/<name_or_id>
•	Retrieves the stats (HP, Attack, Defense) of a Pokémon based on its name or ID.
Compare Two Pokémon
•	POST /compare
•	Compares two Pokémon and returns their stats and the stronger one.
Get Pokémon by Type
•	GET /type/<type_name>
•	Retrieves Pokémon of a specific type and calculates the average HP.
Simulate Pokémon Battle
•	POST /battle
•	Simulates a battle between two Pokémon and returns the total damage and the winner.

Simulate Load
•	GET /simulate-load
•	Simulates load by fetching multiple URLs asynchronously.
