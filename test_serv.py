import requests
import json

url = 'http://localhost:5000'

data = {
    'data': {
        'mission': {
            'projectManager_student_firstName': 'Heb'
        }},
    'document_name': 'DDE',
    'filename': 'test.docx',
    'type': 'mission'
}

r = requests.post(url+'/publipost', json=data)
print(r.text)
