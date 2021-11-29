import json

with open('weatherSRC.json') as f:
    data = json.load(f)

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}


for d in data:
    #print(d['data'])
    d['data']['speed'] = 1
    d['data']['deg'] = 45

for d in data:
    print(d)




with open('weatherFORGED.json', 'w') as json_file:
    json.dump(data, json_file)