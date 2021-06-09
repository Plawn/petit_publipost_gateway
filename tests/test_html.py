import json

import requests

url = 'http://localhost:5000'


def test(document_name: str, output_name: str, _type: str, data: dict):
    data = {
        'data': data,
        'template_name': document_name,
        'templator_name': "kiwi",
        'output_filename': output_name,
        'type': _type,
    }

    r = requests.post(url+'/publipost', json=data)
    print(r.text)


data = {
    'service.get("now")': "Mardi",
    'invoice.color': "red",
}

test('invoice', 'temporary/test.pdf', 'kiwi', data)

# test('ndf', 'jeb/test.xlsx', 'mission', {
#     'date': 'OUAIPS'
# })
