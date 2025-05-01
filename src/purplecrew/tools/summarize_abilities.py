import requests
import os

# Environment Variables
CALDERA_URL = os.environ['CALDERA_URL']
API_KEY = os.environ['CALDERA_API_KEY']
HEADERS = {'KEY': API_KEY, 'Content-Type': 'application/json'}

# Provided Ability IDs
ability_ids = [
    '1afaec09315ab71fdfb167175e8a019a', '0a69420bec84b02bd47464f6835653b1',
    '623806a6fd4d832b6692eb275535f636', '98adc43648b0e4ea6e90a88ad5ae4b3d',
    'f71199dcf1e307fc37c5a0cb9e4031b9', 'ab1b50880382b06d48d3d23ad1786239',
    'a45769d74eb1c75ff916b121023bde31', 'cde814c61dcd8b0fbeeb14f005c2432f',
    'dac0bc35f2b7e7183206259c97b03976', '431121fe12b6fd82938a9a52526b3423',
    'ca3c058554276f34ac84b996af0caf0d', '7056c67b753322231014ae123147a629',
    '03a80d4a4c02d99295b5901ee695cc79', '7575d3d5ae97ee568d49afbd0f878fe2',
    'bc456ce28da22e33b96257b6ae020391', '9c955a373154a7090d4b4396b561f5da',
    '42302f7d89c15f8070f83e743771d567', 'f2131e45dbd95e3057bd3494b5aeed41',
    '95f9e48ea1fbdac2f1c7c656b655ae4c', '69b202bf0bb7b4ff43d4abb8867c1784',
    '45f462c09f28d5b0819af7b1ed0913e1', '6e214f0f17e5d4988aa1085ad4291f46',
    '2f58053a0b7f76ab83218a7748642330', '067e8e2af70cd299e52d6a0136fc437b',
    'f49909057fa568660a6f268b7261e446'
]

# Fetch all abilities
response = requests.get(f"{CALDERA_URL}/api/v2/abilities", headers=HEADERS)
if response.status_code != 200:
    raise Exception(f"Failed to fetch abilities: {response.text}")
abilities = response.json()

# Filter and display relevant abilities
results = []
for ability in abilities:
    if ability['ability_id'] in ability_ids:
        results.append({
            "Ability ID": ability['ability_id'],
            "Technique ID": ability.get('technique_id', 'N/A'),
            "Ability Name": ability.get('name', 'N/A')
        })

# Display results
for res in results:
    print(f"Ability ID: {res['Ability ID']}, Technique ID: {res['Technique ID']}, Name: {res['Ability Name']}")
