import json
import requests

url = 'https://parseapi.back4app.com/classes/Car_Model_List?limit=10'
headers = {
    'X-Parse-Application-Id': 'hlhoNKjOvEhqzcVAJ1lxjicJLZNVv36GdbboZj3Z',
    'X-Parse-Master-Key': 'SNMJJF0CZZhTPhLDIqGhTlUNV9r60M2Z5spyWfXW'
}
data = json.loads(requests.get(url, headers=headers).content.decode('utf-8'))
print(json.dumps(data, indent=2))
