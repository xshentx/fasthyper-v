import os
import json
from flask import request
def get_root_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

def read(name):
    with open(f'{get_root_path()}data/{name}.json', encoding='utf-8') as file:
                data = file.read()
                return json.loads(data, strict=False)

def Write(name, data):
    with open(f'{get_root_path()}data/{name}.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(data))
        
def get_request_parameter(request):
    data = {}
    if request.method == 'GET':
        data = request.args
    elif request.method == 'POST':
        data = request.form
        if not data:
            data = request.get_json()
    return dict(data)