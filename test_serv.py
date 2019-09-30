import json

import requests

url = 'http://localhost:5001'

data = {
    'data': {
        'mission': {
            'projectManager': {
                'student': {
                    'firstName': 'Paul',
                    'lastName': 'Leveau'
                }
            },
            "documentReference(\"DDE\")":"DAT REF"
        }
    },
    'document_name': 'DDE',
    'filename': 'jeb/test.docx',
    'type': 'mission'
}


r = requests.post(url+'/publipost', json=data)
print(r.text)
