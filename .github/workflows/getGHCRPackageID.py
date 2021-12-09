import json
import sys

sha = sys.argv[1]

with open("apiResponse.json", "r") as api:
    jsonApi = json.loads(api.read())
    for i in jsonApi:
        if sha in i['metadata']['container']['tags']:
            print(i['id'])
