import json

import requests

url = 'http://localhost:5000'


def test(document_name: str, output_name: str, _type: str, data: dict):
    data = {
        'data': data,
        'document_name': document_name,
        'filename': output_name,
        'type': _type,
    }

    r = requests.post(url+'/publipost', json=data)
    print(r.text)


data = {
    'mission': {
        'projectManager': {
            'student': {
                'firstName': 'Paul',
                'lastName': 'Leveau'
            }
        },
        "documentReference(\"DDE\")": "DAT REF"
    }
}

test('DDE', 'jeb/test.docx', 'mission', data)

test('ndf', 'jeb/test.xlsx', 'mission', {
    'date':'OUAIPS'
})