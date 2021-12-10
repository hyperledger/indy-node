import json
import sys

sha = sys.argv[1]

with open("apiResponse.json", "r") as apiResponse:
    data = json.loads(apiResponse.read())
    for i in data:
        if sha in i['metadata']['container']['tags']:
            print(i['id'])
