import json

import requests

url = 'http://localhost:5000'

data = {
    'data': {
        'mission': {
            'projectManager': {
                'student': {
                    'firstName': 'Paul',
                    'lastName': 'Leveau'
                }
            }
        }
    },
    'document_name': 'DDE',
    'filename': 'test.docx',
    'type': 'mission'
}


r = requests.post(url+'/publipost', json=data)
print(r.text)
